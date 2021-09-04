# pylint: disable=C0103
# pylint: disable=C0301

import sys
import datetime
import os
import json
import shutil
import argparse
import logging
import itertools
from itertools import product
import collections
import copy
from typing import Dict, Generator, List, Optional, Sequence

import AddonImporter

from settings import settings

try:
    from settings_local import settings
except ImportError:
    pass
from profile import Profile
from specdata import get_analyzer_data
import splitter
from i18n import _, UntranslatedFileHandler
from permutation import generate_permutations, max_permutation_count
from simc import get_simc_version, download_simc, get_latest_simc_version
from utils import chop_microseconds, cleanup_subdir, file_checksum, stable_unique, str2bool

__version__ = "9.1.0"

gem_ids = {"16haste": 311865,
           "haste": 311865,  # always contains available maximum quality
           "16crit": 311863,
           "crit": 311863,  # always contains available maximum quality
           "16vers": 311859,
           "vers": 311859,  # always contains available maximum quality
           "16mast": 311864,
           "mast": 311864,  # always contains available maximum quality
           }

# Global logger instance
logger = logging.getLogger()


def get_additional_input(additionalFileName: str) -> str:
    input_encoding = 'utf-8'
    options = []
    try:
        with open(additionalFileName, "r", encoding=input_encoding) as f:
            for line in f:
                if not line.startswith("#"):
                    options.append(line)

    except UnicodeDecodeError as e:
        raise RuntimeError("""AutoSimC could not decode your additional input file '{file}' with encoding '{enc}'.
        Please make sure that your text editor encodes the file as '{enc}',
        or as a quick fix remove any special characters from your character name.""".format(file=additionalFileName,
                                                                                            enc=input_encoding)) from e

    return "".join(options)


def build_gem_list(gem_lists):
    """Build list of unique gem ids from --gems argument"""
    sorted_gem_list = []
    for gems in gem_lists:
        splitted_gems = gems.split(",")
        for gem in splitted_gems:
            if gem not in gem_ids.keys():
                raise ValueError("Unknown gem '{}' to sim, please check your input. Valid gems: {}".
                                 format(gem, gem_ids.keys()))
        # Convert parsed gems to list of gem ids
        gems = [gem_ids[gem] for gem in splitted_gems]

        # Unique by gem id, so that if user specifies eg. 200haste,haste there will only be 1 gem added.
        gems = stable_unique(gems)
        sorted_gem_list += gems
    logging.debug("Parsed gem list to permutate: {}".format(sorted_gem_list))
    return sorted_gem_list


def parse_command_line_args():
    """Parse command line arguments using argparse. Also provides --help functionality, and default values for args"""

    parser = argparse.ArgumentParser(
        prog='AutoSimC',
        description=_(
            'Python script to create multiple profiles for SimulationCraft to '
            'find Best-in-Slot and best enchants/gems/talents combinations.'),
        epilog=_("Don't hesitate to go on the SimcMinMax Discord "
                 "(https://discordapp.com/invite/tFR2uvK) "
                 "in the #autosimc Channel to ask about specific stuff."),
        formatter_class=argparse.
        ArgumentDefaultsHelpFormatter  # Show default arguments
    )

    parser.add_argument(
        '-i',
        '--input_file',
        dest="inputfile",
        default=settings.default_inputFileName,
        required=False,
        help=_(
            'Input file describing the permutation of SimC profiles to generate. See README for more '
            'details.'))

    parser.add_argument(
        '-o',
        '--output_file',
        dest="outputfile",
        default=settings.default_outputFileName,
        required=False,
        help=
        _('Output file containing the generated profiles used for the simulation.'
          ))

    parser.add_argument(
        '-a',
        '--additional_file',
        dest="additionalfile",
        default=settings.default_additionalFileName,
        required=False,
        help=
        _('Additional input file containing the options to add to each profile.'
          ))

    parser.add_argument(
        '-s',
        '--sim',
        dest='sim',
        required=False,
        nargs=1,
        default=[settings.default_sim_start_stage],
        choices=[
            'permute_only', 'all', 'stage1', 'stage2', 'stage3', 'stage4',
            'stage5', 'stage6'
        ],
        help=
        _("Enables automated simulation and ranking for the top 3 dps-gear-combinations. "
          "Might take a long time, depending on number of permutations. "
          "Edit the simcraft-path in settings.py to point to your simc-installation. The result.html "
          "will be saved in results-subfolder."
          "There are 2 modes available for calculating the possible huge amount of permutations: "
          "Static and dynamic mode:"
          "* Static uses a fixed amount of simc-iterations at the cost of quality; default-settings are "
          "100, 1000 and 10000 for each stage."
          "* Dynamic mode lets you set the target_error-parameter from simc, resulting in a more "
          "accurate ranking. Stage 1 can be entered at the beginning in the wizard. Stage 2 is set to "
          "target_error=0.2, and 0.05 for the final stage 3."
          "(These numbers might be changed in future versions)"
          "You have to set the simc path in the settings.py file."
          "- Resuming: It is also possible to resume at a stage, e.g. if simc.exe crashed during "
          "stage1, by launching with the parameter -sim stage1 (or stage2/3)."
          "- Parallel Processing: By default multiple simc-instances are launched for stage1 and 2, "
          "which is a major speedup on modern multicore-cpus like AMD Ryzen. If you encounter problems "
          "or instabilities, edit settings.py and change the corresponding parameters or even disable it."
          ))

    parser.add_argument('-S',
                        '--stages',
                        dest="stages",
                        required=False,
                        type=int,
                        default=settings.num_stages,
                        help=_("Number of stages to simulate."))

    parser.add_argument(
        '-g',
        '--gems',
        dest='gems',
        required=False,
        nargs='*',
        help=
        _('Enables permutation of gem-combinations in your gear. With e.g. gems crit,haste,int '
          'you can add all combinations of the corresponding gems (epic gems: 200, rare: 150, uncommon '
          'greens are not supported) in addition to the ones you have currently equipped.\n'
          'Valid gems: {}'
          '- Example: You have equipped 1 int and 2 mastery-gems. If you enter <-gems "crit,haste,int"> '
          '(without <>) into the commandline, the permutation process uses the single int- '
          'and mastery-gem-combination you have currrently equipped and adds ALL combinations from the '
          'ones in the commandline, therefore mastery would be excluded. However, adding mastery to the '
          'commandline reenables that.\n'
          '- Gems have to fulfil the following syntax in your profile: gem_id=123456[[/234567]/345678] '
          'Simpermut usually creates this for you.\n'
          '- WARNING: If you have many items with sockets and/or use a vast gem-combination-setup as '
          'command, the number of combinations will go through the roof VERY quickly. Please be cautious '
          'when enabling this.'
          '- additonally you can specify a empty list of gems, which will permutate the existing gems'
          'in your input gear.').format(list(gem_ids.keys())))

    parser.add_argument(
        '--unique_jewelry',
        dest='unique_jewelry',
        action='store_true',
        default="true",
        help=
        'Assume ring and trinkets are unique-equipped, and only a single item id can be equipped.'
    )

    parser.add_argument('-d',
                        '--debug',
                        dest="debug",
                        action='store_true',
                        help='Write debug information to log file.')

    # TODO Handle quiet argument in the code
    parser.add_argument('-quiet',
                        '--quiet',
                        dest='quiet',
                        action='store_true',
                        help='Run quietly. /!\ Not implemented yet')

    parser.add_argument('-version',
                        '--version',
                        action='version',
                        version='%(prog)s {}'.format(__version__))

    return parser.parse_args()


# Manage command line parameters
def handleCommandLine():
    args = parse_command_line_args()

    # Sim stage is always a list with 1 element, eg. ["all"], ['stage1'], ...
    args.sim = args.sim[0]
    if args.sim == 'permute_only':
        args.sim = None
    return args


def copy_result_file(last_subdir):
    result_folder = os.path.abspath(settings.result_subfolder)
    if not os.path.exists(result_folder):
        logging.info(_("Result-subfolder '{}' does not exist. Creating it.").format(result_folder))
        os.makedirs(result_folder)

    # Copy html files from last subdir to results folder
    found_html = False
    if os.path.exists(last_subdir):
        for _root, _dirs, files in os.walk(last_subdir):
            for file in files:
                if file.endswith(".html"):
                    src = os.path.join(last_subdir, file)
                    dst = os.path.join(result_folder, file)
                    logging.info(_("Moving file: {} to {}").format(src, dst))
                    shutil.move(src, dst)
                    found_html = True
    if not found_html:
        logging.warning(_("Could not copy html result file, since there was no file found in '{}'.")
                        .format(last_subdir))


def cleanup(num_stages):
    logging.info(_("Cleaning up"))
    subdirs = [get_subdir(stage) for stage in range(1, num_stages + 1)]
    copy_result_file(subdirs[-1])
    for subdir in subdirs:
        cleanup_subdir(subdir)


def validateSettings(args):
    """Check input arguments and settings.py options"""
    # Check simc executable availability.
    if args.sim:
        if not os.path.exists(settings.simc_path):
            raise FileNotFoundError(_("Simc executable at '{}' does not exist.").format(settings.simc_path))
        else:
            logging.debug(_("Simc executable exists at '{}', proceeding...").format(settings.simc_path))
        if os.name == "nt":
            if not settings.simc_path.endswith("simc.exe"):
                raise RuntimeError(_("Simc executable must end with 'simc.exe', and '{}' does not."
                                     "Please check your settings.py simc_path options.").format(settings.simc_path))

        analyzer_path = os.path.join(os.getcwd(), settings.analyzer_path, settings.analyzer_filename)
        if os.path.exists(analyzer_path):
            logging.info(_("Analyzer-file found at '{}'.").format(analyzer_path))
        else:
            raise RuntimeError(_("Analyzer-file not found at '{}', make sure you have a complete AutoSimc-Package.").
                               format(analyzer_path))

    # use a "safe mode", overwriting the values
    if settings.simc_safe_mode:
        logging.info(_("Using Safe Mode as specified in settings."))
        settings.simc_threads = 1

    if settings.default_error_rate_multiplier <= 0:
        raise ValueError(_("Invalid default_error_rate_multiplier ({}) <= 0").
                         format(settings.default_error_rate_multiplier))

    valid_grabbing_methods = (_("target_error"), _("top_n"))
    if settings.default_grabbing_method not in valid_grabbing_methods:
        raise ValueError(_("Invalid settings.default_grabbing_method '{}'. Valid options: {}").
                         format(settings.default_grabbing_method, valid_grabbing_methods))


def permutate(args, profile: Profile) -> int:
    max_nperm = max_permutation_count(profile)
    logging.info(_("Generating up to {:n} loadouts...").format(max_nperm))
    max_perm_strlen = len(str(max_nperm))
    valid_profiles = 0

    with open(args.outputfile, 'w') as output_file:
        for perm in generate_permutations(profile):
            profile_id = str(valid_profiles).rjust(max_perm_strlen, '0')
            output_file.write(f'''\
{profile.player_class}="{profile.profile_name}_{profile_id}"
{profile.general_options}
{perm.simc_input}
''')
            valid_profiles += 1

    result = _("Finished permutations. Valid: {:n} of {:n} processed. ({:.2f}%)"). \
        format(valid_profiles,
               max_nperm,
               100.0 * valid_profiles / max_nperm if max_nperm else 0.0)
    logging.info(result)

    # Print checksum so we can check for equality when making changes in the code
    outfile_checksum = file_checksum(args.outputfile)
    logging.info(_("Output file checksum: {}").format(outfile_checksum))

    return valid_profiles


def checkResultFiles(subdir):
    """Check the SimC result files of a previous stage for validity."""
    subdir = os.path.join(os.getcwd(), subdir)
    logging.info("Checking Files in subdirectory: {}".format(subdir))

    if not os.path.exists(subdir):
        raise FileNotFoundError("Subdir '{}' does not exist.".format(subdir))

    files = os.listdir(subdir)
    if len(files) == 0:
        raise FileNotFoundError("No files in: " + str(subdir))

    files = [f for f in files if f.endswith(".result")]
    files = [os.path.join(subdir, f) for f in files]
    for file in files:
        if os.stat(file).st_size <= 0:
            raise RuntimeError("Result file '{}' is empty.".format(file))

    logging.debug("{} valid result files found in {}.".format(len(files), subdir))
    logging.info("Checked all files in " + str(subdir) + " : Everything seems to be alright.")


def get_subdir(stage):
    subdir = "stage_{:n}".format(stage)
    subdir = os.path.join(settings.temporary_folder_basepath, subdir)
    subdir = os.path.abspath(subdir)
    return subdir


def grab_profiles(player_profile: Profile, stage: int, num_stages: int, output_file_name: str) -> int:
    """Parse output/result files from previous stage and get number of profiles to simulate"""
    subdir_previous_stage = get_subdir(stage - 1)
    if stage == 1:
        num_generated_profiles = splitter.split(output_file_name, get_subdir(stage),
                                                settings.splitting_size, player_profile.player_class)
    else:
        try:
            checkResultFiles(subdir_previous_stage)
        except Exception as e:
            msg = "Error while checking result files in {}: {}\nPlease restart AutoSimc at a previous stage.". \
                format(subdir_previous_stage, e)
            raise RuntimeError(msg) from e
        if settings.default_grabbing_method == _("target_error"):
            filter_by = "target_error"
            filter_criterium = None
        elif settings.default_grabbing_method == _("top_n"):
            filter_by = "count"
            filter_criterium = settings.default_top_n[stage - num_stages - 1]
        is_last_stage = (stage == num_stages)
        num_generated_profiles = splitter.grab_best(filter_by, filter_criterium, subdir_previous_stage,
                                                    get_subdir(stage), output_file_name, not is_last_stage)
    if num_generated_profiles:
        logging.info("Found {} profile(s) to simulate.".format(num_generated_profiles))
    return num_generated_profiles


def check_profiles(stage: int) -> int:
    subdir = get_subdir(stage)
    if not os.path.exists(subdir):
        return False
    files = os.listdir(subdir
                       )
    files = [f for f in files if f.endswith(".simc")]
    files = [f for f in files if not f.endswith("arguments.simc")]
    files = [f for f in files if os.stat(os.path.join(subdir, f)).st_size > 0]
    return len(files)


def static_stage(player_profile: Profile, stage: int, num_stages: int, output_file_name: str) -> None:
    if stage > num_stages:
        return
    print("\n")
    logging.info(_("***Entering static mode, STAGE {}***").format(stage))
    num_generated_profiles = grab_profiles(
        player_profile=player_profile, stage=stage, num_stages=num_stages, output_file_name=output_file_name)
    is_last_stage = (stage == num_stages)
    try:
        num_iterations = settings.default_iterations[stage]
    except Exception:
        num_iterations = None
    if not num_iterations:
        if settings.skip_questions:
            raise ValueError(_("Cannot run static mode and skip questions without default iterations set for stage {}.")
                             .format(stage))
        iterations_choice = input(_("Please enter the number of iterations to use (q to quit): "))
        if iterations_choice == "q":
            logging.info(_("Quitting application"))
            sys.exit(0)
        num_iterations = int(iterations_choice)
    splitter.simulate(get_subdir(stage), "iterations", num_iterations,
                      player_profile, stage, is_last_stage, num_generated_profiles)
    static_stage(player_profile, stage + 1, num_stages, output_file_name)


def dynamic_stage(player_profile: Profile,
                  output_file_name: str,
                  stage: int,
                  num_stages: int,
                  previous_target_error: Optional[float] = None) -> None:
    if stage > num_stages:
        return
    print("\n")
    logging.info(_("***Entering dynamic mode, STAGE {}***").format(stage))

    num_generated_profiles = grab_profiles(player_profile, stage, num_stages, output_file_name)

    # Display estimated simulation time information to user
    result_data = get_analyzer_data(player_profile.class_spec)
    print(_("Estimated calculation times for stage {} based on your data:").format(stage))
    for i, (target_error, iterations, elapsed_time_seconds) in enumerate(result_data):
        elapsed_time = datetime.timedelta(seconds=elapsed_time_seconds)
        estimated_time = chop_microseconds(elapsed_time * num_generated_profiles) if num_generated_profiles else None
        print(_("({:2n}): Target Error: {:6.3f}%:  Est. calc. time: {} (time/profile: {:5.2f}s iterations: {:5n}) ").
              format(i,
                     target_error,
                     estimated_time,
                     elapsed_time.total_seconds(),
                     iterations)
              )

    try:
        target_error = float(settings.default_target_error[stage])
    except Exception:
        target_error = None

    # If we do not have a target_error in settings, get target_error from user input
    if target_error is None:
        if settings.skip_questions:
            raise ValueError(
                _("Cannot run dynamic mode and skip questions without default target_error set for stage {}.")
                    .format(stage))
        else:
            calc_choice = input(_("Please enter the type of calculation to perform (q to quit): "))
            if calc_choice == "q":
                logging.info(_("Quitting application"))
                sys.exit(0)
        calc_choice = int(calc_choice)
        if calc_choice >= len(result_data) or calc_choice < 0:
            raise ValueError(_("Invalid calc choice '{}' can only be from 0 to {}").format(calc_choice,
                                                                                           len(result_data) - 1))
        logging.info(_("Sim: Number of permutations: ") + str(num_generated_profiles))
        logging.info(_("Sim: Chosen calculation: {}").format(calc_choice))

        target_error, _iterations, _elapsed_time_seconds = result_data[calc_choice]

    # if the user chose a target_error which is higher than one chosen in the previous stage
    # he is given an option to adjust it.
    if previous_target_error is not None and previous_target_error <= target_error:
        print(_("Warning Target_Error chosen in stage {}: {} <= Default_Target_Error for stage {}: {}").
              format(stage - 1, previous_target_error, stage, target_error))
        new_value = input(
            _("Do you want to continue anyway (Enter), quit (q) or enter a new target_error"
              " for the current stage (n)?: "))
        logging.info(_("User chose: ") + str(new_value))
        if new_value == "q":
            logging.info(_("Quitting application"))
            sys.exit(0)
        if new_value == "n":
            target_error = float(input(_("Enter new target_error (Format: 0.3): ")))
            logging.info(_("User entered target_error_secondpart: ") + str(target_error))

    # Show estimated sim time based on users chosen target_error
    if num_generated_profiles:
        result_data = get_analyzer_data(player_profile.class_spec)
        for i, (te, _iterations, elapsed_time_seconds) in enumerate(result_data):
            if target_error <= te:
                elapsed_time = datetime.timedelta(seconds=elapsed_time_seconds)
                estimated_time = chop_microseconds(
                    elapsed_time * num_generated_profiles) if num_generated_profiles else None
                logging.info(
                    _("Chosen Target Error: {:.3f}% <= {:.3f}%:  Time/Profile: {:5.2f} sec => Est. calc. time: {}").
                        format(target_error,
                               te,
                               elapsed_time.total_seconds(),
                               estimated_time)
                )
                if not settings.skip_questions:
                    if estimated_time and estimated_time.total_seconds() > 43200:  # 12h
                        if input(_("Warning: This might take a *VERY* long time ({}) (q to quit, Enter to continue: )").
                                         format(estimated_time)) == "q":
                            logging.info(_("Quitting application"))
                            sys.exit(0)
                break
        else:
            logging.warning(_("Could not provide any estimated calculation time."))
    is_last_stage = (stage == num_stages)
    splitter.simulate(get_subdir(stage), "target_error", target_error, player_profile,
                      stage, is_last_stage, num_generated_profiles)

    if not is_last_stage:
        dynamic_stage(player_profile=player_profile,
                    previous_target_error=target_error,
                    stage=stage + 1,
                    num_stages=num_stages,
                    output_file_name=output_file_name)


def start_stage(player_profile: Profile, stage: int, num_stages: int, output_file_name: str):
    logging.info(_("Starting at stage {}").format(stage))
    logging.info(_("You selected grabbing method '{}'.").format(settings.default_grabbing_method))
    print("")
    print(_("You have to choose one of the following modes for calculation:"))
    print(_("1) Static mode uses a fixed number of iterations, with varying error per profile ({num_iterations})").
          format(num_iterations=settings.default_iterations))
    print(_("   It is however faster if simulating huge amounts of profiles"))
    print(_(
        "2) Dynamic mode (preferred) lets you choose a specific 'correctness' of the calculation, but takes more time."))
    print(
        _("   It uses the chosen target_error for the first part; in stage2 onwards, the following values are used: {}")
            .format(settings.default_target_error))
    if settings.skip_questions:
        mode_choice = int(settings.auto_choose_static_or_dynamic)
    else:
        mode_choice = input(_("Please choose your mode (Enter to exit): "))
        if not len(mode_choice):
            logging.info(_("User exit."))
            sys.exit(0)
        mode_choice = int(mode_choice)
    valid_modes = (1, 2)
    if mode_choice not in valid_modes:
        raise RuntimeError(_("Invalid simulation mode '{}' selected. Valid modes: {}.")
                           .format(mode_choice, valid_modes))
    if mode_choice == 1:
        static_stage(player_profile=player_profile, stage=stage, num_stages=num_stages, output_file_name=output_file_name)
    elif mode_choice == 2:
        dynamic_stage(player_profile=player_profile, stage=stage, num_stages=num_stages, output_file_name=output_file_name)
    else:
        raise Exception('unknown mode choice')


def addFightStyle(profile: Profile) -> None:
    filepath = os.path.join(os.getcwd(), settings.file_fightstyle)
    filepath = os.path.abspath(filepath)
    logging.debug(_("Opening fight types data file at '{}'.").format(filepath))
    with open(filepath, encoding="utf-8") as file:
        try:
            profile.fightstyle = None
            fights = json.load(file)
            if len(fights) > 0:
                # generate table to choose fightstyle
                if settings.choose_fightstyle:
                    print("")
                    print(_("Choose fightstyle:"))
                    for i, f in enumerate(fights):
                        print("({index:2n}) - {name}: {desc}"
                              .format(index=i,
                                      name=f["name"],
                                      desc=f["description"]))
                    fightstylechoose = int(input(_("Enter the number for your fightstyle: ")))
                    if fightstylechoose < 0 or fightstylechoose >= len(fights):
                        raise ValueError(_("Wrong number ({}) for fightstyles chosen."
                                           " Must be greater between {} and {}.")
                                         .format(fightstylechoose, 0, len(fights)))
                    profile.fightstyle = fights[fightstylechoose]
                else:
                    # fetch default_profile
                    for f in fights:
                        if f["name"] == settings.default_fightstyle:
                            profile.fightstyle = f  # add the whole json-object, files will get created later
                    if profile.fightstyle is None:
                        raise ValueError(_("No fightstyle found in .json with name: {}, exiting.")
                                         .format(settings.default_fightstyle))
            else:
                raise RuntimeError(_("Did not find entries in fight_style.json."))
        except json.decoder.JSONDecodeError as error:
            logging.error(_("Error while decoding JSON file: {}").format(error), exc_info=True)
            sys.exit(1)

    if profile.fightstyle is None:
        raise Exception('No fightstyle set')
    logging.info(_("Found fightstyle >>>{name}<<< in {file}")
                .format(name=profile.fightstyle["name"],
                        file=settings.file_fightstyle))


########################
#     Program Start    #
########################


def main():
    error_handler = UntranslatedFileHandler(settings.errorFileName)
    error_handler.setLevel(logging.ERROR)

    # Handler to log messages to file
    log_handler = UntranslatedFileHandler(settings.logFileName)
    log_handler.setLevel(logging.DEBUG)

    # Handler for logging to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(level=logging.DEBUG, handlers=[error_handler,
                                                       log_handler,
                                                       stdout_handler], force=True)
    logging.debug("----------------------------------------------------------------------------")
    logging.info(_("AutoSimC - Supported WoW-Version: {}").format(__version__))

    args = handleCommandLine()
    if args.debug:
        log_handler.setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.DEBUG)

    logging.debug(_("Parsed command line arguments: {}").format(args))
    logging.debug(_("Parsed settings: {}").format(vars(settings)))

    if args.sim:
        if not settings.auto_download_simc:
            if settings.check_simc_version:
                filename, latest = get_latest_simc_version()
                ondisc = get_simc_version()
                if latest != ondisc:
                    logging.info(_("A newer SimCraft-version might be available for download! Version: {}").
                                 format(filename))
        download_simc()
    validateSettings(args)

    player_profile = AddonImporter.build_profile_simc_addon(args)

    # can always be rerun since it is now deterministic
    outputGenerated = False
    num_generated_profiles = None
    if args.sim == "all" or args.sim is None:
        start = datetime.datetime.now()
        num_generated_profiles = permutate(args, player_profile)
        logging.info(_("Permutating took {}.").format(datetime.datetime.now() - start))
        outputGenerated = True
    elif args.sim == "stage1":
        if input(_("Do you want to generate {outfile} again? Press y to regenerate: ").format(
                outfile=args.outputfile)) == "y":
            num_generated_profiles = permutate(args, player_profile)
            outputGenerated = True

    if outputGenerated:
        if num_generated_profiles == 0:
            raise RuntimeError(_("No valid profile combinations found."
                                 " Please check the 'Invalid profile statistics' output and adjust your"
                                 " input.txt and settings.py."))
        if args.sim:
            if not settings.skip_questions:
                if num_generated_profiles and num_generated_profiles > 50000:
                    if input(_(
                            "Beware: Computation with Simcraft might take a VERY long time with this amount of profiles!"
                            "(Press Enter to continue, q to quit)")) == "q":
                        logging.info(_("Program exit by user"))
                        sys.exit(0)

    if args.sim:
        addFightStyle(player_profile)
        if args.sim == "stage1" or args.sim == "all":
            start_stage(player_profile=player_profile,
                        stage=1,
                        num_stages=args.stages,
                        output_file_name=args.outputfile)
        if args.sim == "stage2":
            start_stage(player_profile=player_profile,
                        stage=2,
                        num_stages=args.stages,
                        output_file_name=args.outputfile)
        if args.sim == "stage3":
            start_stage(player_profile,
                        stage=3,
                        num_stages=args.stages,
                        output_file_name=args.outputfile)

        if settings.clean_up:
            cleanup(num_stages=args.stages)
    logging.info(_("AutoSimC finished correctly."))


if __name__ == "__main__":
    try:
        main()
        logging.shutdown()
    except Exception as e:
        logging.error("Error: {}".format(e), exc_info=True)
        sys.exit(1)
