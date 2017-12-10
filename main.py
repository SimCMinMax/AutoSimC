# pylint: disable=C0103
# pylint: disable=C0301

import configparser
import sys
import datetime
import os
import glob
import json
import shutil
import argparse
import logging
import itertools
import collections
import copy
import subprocess
import hashlib
import re
from urllib.request import urlopen, urlretrieve
import platform

from settings import settings
import specdata
import splitter

__version__ = "0.0.1"

if __name__ == "__main__":
    try:
        filename = "settings.py"
        source = open(filename, 'r').read()
        compile(source, filename, 'exec')
    except SyntaxError:
        print("Error in settings.py, pls check for syntax-errors")
        sys.exit(1)

# Var init with default value
t19min = int(settings.default_equip_t19_min)
t19max = int(settings.default_equip_t19_max)
t20min = int(settings.default_equip_t20_min)
t20max = int(settings.default_equip_t20_max)
t21min = int(settings.default_equip_t21_min)
t21max = int(settings.default_equip_t21_max)

gem_ids = {"150haste":  130220,
           "200haste":  151583,
           "haste":     151583,  # always contains maximum quality
           "150crit":   130219,
           "200crit":   151580,
           "crit":      151580,  # always contains maximum quality
           "150vers":   130221,
           "200vers":   151585,
           "vers":      151585,  # always contains maximum quality
           "150mast":   130222,
           "200mast":   151584,
           "mast":      151584,  # always contains maximum quality
           "200str":    130246,
           "str":       130246,
           "200agi":    130247,
           "agi":       130247,
           "200int":    130248,
           "int":       130248,
           }

# Global logger instance
logger = logging.getLogger()


#   Error handle
def printLog(stringToPrint):
    logging.info(stringToPrint)


def stable_unique(seq):
    """
    Filter sequence to only contain unique elements, in a stable order
    This is a replacement for x = list(set(x)), which does not lead to
    deterministic or 'stable' output.
    Credit to https://stackoverflow.com/a/480227
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def add_legendary(legendary_split, gear_list):
    """
    Parse --legendaries arguments, create Items and add them to gear list for permutation.
    """
    logging.info("Adding legendary: {}".format(legendary_split))
    try:
        slot, item_id, *tail = legendary_split
        bonus_id = tail[0] if len(tail) > 0 else None
        enchant_id = tail[1] if len(tail) > 1 else None
        gem_id = tail[2] if len(tail) > 2 else None

        legendary_string = "L,id={}".format(item_id)
        if bonus_id:
            legendary_string += ",bonus_id={}".format(bonus_id)
        if enchant_id:
            legendary_string += ",enchant_id={}".format(enchant_id)
        if gem_id:
            legendary_string += ",gem_id={}".format(gem_id)

        logging.debug("Legendary string: {}".format(legendary_string))
        if slot in gear_list.keys():
            gear_list[slot].append(Item(slot, legendary_string))
            logging.info("Added legendary '{}' to {}.".format(legendary_string,
                                                              slot))
        else:
            raise ValueError("Invalid legendary gear slot '{}' not in {}".format(slot,
                                                                                 list(gear_list.keys())))
    except Exception as e:
        raise Exception("Could not add legendary: {}".format(e)) from e


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


# Antorus trinket item ids
antorusTrinkets = {154172, 154173, 154174, 154175, 154176, 154177}


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def parse_command_line_args():
    """Parse command line arguments using argparse. Also provides --help functionality, and default values for args"""

    parser = argparse.ArgumentParser(prog="AutoSimC",
                                     description="Python script to create multiple profiles for SimulationCraft to "
                                     "find Best-in-Slot and best enchants/gems/talents combinations.",
                                     epilog="Don't hesitate to go on the SimcMinMax Discord "
                                     "(https://discordapp.com/invite/tFR2uvK) "
                                     "in the #simpermut-autosimc Channel to ask about specific stuff.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter  # Show default arguments
                                     )

    parser.add_argument('-i', '--inputfile',
                        default=settings.default_inputFileName,
                        required=False,
                        help="Inputfile describing the permutation of SimC profiles to generate. See README for more "
                        "details.")

    parser.add_argument('-o', '--outputfile',
                        default=settings.default_outputFileName,
                        required=False,
                        help='Output file containing the generated profiles used for the simulation.')

    parser.add_argument('-sim',
                        required=False,
                        nargs=1,
                        default=[settings.default_sim_start_stage],
                        choices=['permutate_only', 'all', 'stage1', 'stage2', 'stage3', 'stage4',
                                 'stage5', 'stage6'],
                        help="Enables automated simulation and ranking for the top 3 dps-gear-combinations. "
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
                        "- Resuming: It is also possible to resume a broken stage, e.g. if simc.exe crashed during "
                        "stage1, by launching with the parameter -sim stage2 (or stage3). You will have to enter the "
                        "amount of iterations or target_error of the broken simulation-stage. "
                        "(See logs.txt for details)"
                        "- Parallel Processing: By default multiple simc-instances are launched for stage1 and 2, "
                        "which is a major speedup on modern multicore-cpus like AMD Ryzen. If you encounter problems "
                        "or instabilities, edit settings.py and change the corresponding parameters or even disable it."
                        )

    parser.add_argument('--stages',
                        required=False,
                        type=int,
                        default=settings.num_stages,
                        help="Number of stages to simulate.")

    parser.add_argument('-gems', '--gems',
                        required=False,
                        nargs="*",
                        help='Enables permutation of gem-combinations in your gear. With e.g. gems crit,haste,int '
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
                        'in your input gear.'.format(list(gem_ids.keys())))

    parser.add_argument('-l', '--legendaries',
                        required=False,
                        help='List of legendaries to add to the template. Format:\n'
                        '"leg1/id/bonus/gem/enchant,leg2/id2/bonus2/gem2/enchant2,..."')

    parser.add_argument('-min_leg', '--legendary_min',
                        default=settings.default_leg_min,
                        type=int,
                        required=False,
                        help='Minimum number of legendaries in the permutations.')

    parser.add_argument('-max_leg', '--legendary_max',
                        default=settings.default_leg_max,
                        type=int,
                        required=False,
                        help='Maximum number of legendaries in the permutations.')

    parser.add_argument('--unique_jewelry',
                        type=str2bool,
                        default="true",
                        help='Assume ring and trinkets are unique-equipped, and only a single item id can be equipped.')

    parser.add_argument('--debug',
                        action='store_true',
                        help='Write debug information to log file.')

    # TODO Handle quiet argument in the code
    parser.add_argument('-quiet',
                        action='store_true',
                        help='Run quietly. /!\ Not implemented yet')

    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))

    return parser.parse_args()


# Manage command line parameters
def handleCommandLine():
    args = parse_command_line_args()

    # Sim stage is always a list with 1 element, eg. ["all"], ['stage1'], ...
    args.sim = args.sim[0]
    if args.sim == "permutate_only":
        args.sim = None

    # For now, just write command line arguments into globals
    global outputFileName
    outputFileName = args.outputfile
    
    global num_stages
    num_stages = args.stages

    return args


def get_analyzer_data(class_spec):
    """
    Get precomputed analysis data (target_error, iterations, elapsed_time_seconds) for a given class_spec
    """
    result = []
    filename = os.path.join(os.getcwd(), settings.analyzer_path, settings.analyzer_filename)
    with open(filename, "r") as f:
        file = json.load(f)
        for variant in file[0]:
            for p in variant["playerdata"]:
                if p["specialization"] == class_spec:
                    for s in range(len(p["specdata"])):
                        item = (float(variant["target_error"]),
                                int(p["specdata"][s]["iterations"]),
                                float(p["specdata"][s]["elapsed_time_seconds"])
                                )
                        result.append(item)
    return result


def autoDownloadSimc():
    if not settings.auto_download_simc:
        return
    try:
        if settings.auto_download_simc:
            if platform.system() != "Windows" or not platform.machine().endswith('64'):
                print("Sorry autodownloading only supported for 64bit windows")
                return
    except AttributeError:
        return

    logging.info("Starting auto download check of SimulationCraft.")

    # Application root path, and destination path
    rootpath = os.path.dirname(os.path.realpath(__file__))
    download_dir = os.path.join(rootpath, "auto_download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Get filename of latest build of simc
    html = urlopen('http://downloads.simulationcraft.org/?C=M;O=D').read().decode('utf-8')
    filename = re.search(r'<a href="(simc.+win64.+7z)">', html).group(1)
    print("Latest simc:", filename)

    # Download latest build of simc
    filepath = os.path.join(download_dir, filename)
    if not os.path.exists(filepath):
        url = 'http://downloads.simulationcraft.org/' + filename
        logging.info("Retrieving simc from url {} to {}.".format(url,
                                                                 filepath))
        urlretrieve(url, filepath)
    else:
        logging.debug("Latest simc version already downloaded at {}.".format(filename))

    # Unpack downloaded build and set simc_path
    settings.simc_path = os.path.join(download_dir, filename[:filename.find("win64") + len("win64")], "simc.exe")
    splitter.simc_path = settings.simc_path
    if not os.path.exists(settings.simc_path):
        seven_zip_executables = ["7z.exe", "C:/Program Files/7-Zip/7z.exe"]
        for seven_zip_executable in seven_zip_executables:
            try:
                if not os.path.exists(seven_zip_executable):
                    logging.info("7Zip exetuable at '{}' does not exist.".format(seven_zip_executable))
                    continue
                cmd = seven_zip_executable + ' x "' + filepath + '" -aoa -o"' + download_dir + '"'
                logging.debug("Running unpack command '{}'".format(cmd))
                subprocess.call(cmd)

                # keep the latest 7z to remember current version, but clean up any other ones
                files = glob.glob(download_dir + '/simc*win64*7z')
                for f in files:
                    if not os.path.basename(f) == filename:
                        print("Removing old simc:", os.path.basename(f))
                        os.remove(f)
                break
            except Exception as e:
                print("Exception when unpacking: {}".format(e))
        else:
            raise RuntimeError("Could not unpack the auto downloaded SimulationCraft executable."
                               "Please note that you need 7Zip installed at one of the following locations: {}.".
                               format(seven_zip_executables))
    else:
        print("simc_path={}".format(repr(settings.simc_path)))


def cleanup_subdir(subdir):
    if os.path.exists(subdir):
        if not settings.delete_temp_default and not settings.skip_questions:
            if input("Do you want to remove subfolder: " + subdir + "? (Press y to confirm): ") != "y":
                return
        printLog("Removing: {}".format(subdir))
        shutil.rmtree(subdir)


def copy_result_file(last_subdir):
    result_folder = os.path.join(os.getcwd(), settings.result_subfolder)
    if not os.path.exists(result_folder):
        logging.info("Result-subfolder '{}' does not exist. Creating it.".format(result_folder))
        os.makedirs(result_folder)

    # Copy html files from last subdir to results folder
    found_html = False
    if os.path.exists(last_subdir):
        for _root, _dirs, files in os.walk(last_subdir):
            for file in files:
                if file.endswith(".html"):
                    src = os.path.join(last_subdir, file)
                    dst = os.path.join(result_folder, file)
                    printLog("Moving file: {} to {}".format(src, dst))
                    shutil.move(src, dst)
                    found_html = True
    if not found_html:
        logging.warning("Could not copy html result file, since there was no file found in '{}'.".format(last_subdir))


def cleanup():
    printLog("Cleaning up")
    subdirs = [get_subdir(stage) for stage in range(1, num_stages + 1)]
    copy_result_file(subdirs[-1])
    for subdir in subdirs:
        cleanup_subdir(subdir)


def validateSettings(args):
    """Check input arguments and settings.py options"""
    # Check simc executable availability.
    if args.sim:
        if not os.path.exists(settings.simc_path):
            raise FileNotFoundError("Simc executable at '{}' does not exist.".format(settings.simc_path))
        else:
            logging.debug("Simc executable exists at '{}', proceeding...".format(settings.simc_path))
        if os.name == "nt":
            if not settings.simc_path.endswith("simc.exe"):
                raise RuntimeError("Simc executable must end with 'simc.exe', and '{}' does not."
                                   "Please check your settings.py simc_path options.".format(settings.simc_path))

        analyzer_path = os.path.join(os.getcwd(), settings.analyzer_path, settings.analyzer_filename)
        if os.path.exists(analyzer_path):
            logging.info("Analyzer-file found at '{}'.".format(analyzer_path))
        else:
            raise RuntimeError("Analyzer-file not found at '{}', make sure you have a complete AutoSimc-Package.".
                               format(analyzer_path))

    # validate amount of legendaries
    if args.legendary_min > args.legendary_max:
        raise ValueError("Legendary min '{}' > legendary max '{}'".format(args.legendary_min, args.legendary_max))
    if args.legendary_max > 3:
        raise ValueError("Legendary Max '{}' too large (>3).".format(args.legendary_max))
    if args.legendary_min > 3:
        raise ValueError("Legendary Min '{}' too large (>3).".format(args.legendary_min))
    if args.legendary_min < 0:
        raise ValueError("Legendary Min '{}' is negative.".format(args.legendary_min))
    if args.legendary_max < 0:
        raise ValueError("Legendary Max '{}' is negative.".format(args.legendary_max))

    # validate tier-set
    min_tier_sets = 0
    max_tier_sets = 6
    tier_sets = {"Tier19": (t19min, t19max),
                 "Tier20": (t20min, t20max),
                 "Tier21": (t21min, t21max),
                 }

    total_min = 0
    for tier_name, (tier_set_min, tier_set_max) in tier_sets.items():
        if tier_set_min < min_tier_sets:
            raise ValueError("Invalid tier set minimum ({} < {}) for tier '{}'".
                             format(tier_set_min, min_tier_sets, tier_name))
        if tier_set_max > max_tier_sets:
            raise ValueError("Invalid tier set maximum ({} > {}) for tier '{}'".
                             format(tier_set_max, max_tier_sets, tier_name))
        if tier_set_min > tier_set_max:
            raise ValueError("Tier set min > max ({} > {}) for tier '{}'".format(tier_set_min, tier_set_max, tier_name))
        total_min += tier_set_min

    if total_min > max_tier_sets:
        raise ValueError("All tier sets together have too much combined min sets ({}=sum({}) > {}).".
                         format(total_min, [t[0] for t in tier_sets.values()], max_tier_sets))

    # use a "safe mode", overwriting the values
    if settings.simc_safe_mode:
        printLog("Using Safe Mode")
        settings.simc_threads = 1

    if settings.default_error_rate_multiplier <= 0:
        raise ValueError("Invalid default_error_rate_multiplier ({}) <= 0".
                         format(settings.default_error_rate_multiplier))

    valid_grabbing_methods = ("target_error", "top_n")
    if settings.default_grabbing_method not in valid_grabbing_methods:
        raise ValueError("Invalid settings.default_grabbing_method '{}'. Valid options: {}".
                         format(settings.default_grabbing_method, valid_grabbing_methods))


def file_checksum(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def get_gem_combinations(gems_to_use, num_gem_slots):
    if num_gem_slots <= 0:
        return []
    combinations = itertools.combinations_with_replacement(gems_to_use, r=num_gem_slots)
    return list(combinations)


def permutate_talents(talents_list):
    talents_list = talents_list.split('|')
    all_talent_combinations = []  # List for each talents input
    for talents in talents_list:
        current_talents = []
        for talent in talents:
            if talent == "0":
                # We permutate the talent row, adding ['1', '2', '3'] to that row
                current_talents.append([str(x) for x in range(1, 4)])
            else:
                # Do not permutate the talent row, just add the talent from the profile
                current_talents.append([talent])
        all_talent_combinations.append(current_talents)
        logging.debug("Talent combination input: {}".format(current_talents))

    # Use some itertools magic to unpack the product of all talent combinations
    product = [itertools.product(*t) for t in all_talent_combinations]
    product = list(itertools.chain(*product))

    # Format each permutation back to a nice talent string.
    permuted_talent_strings = ["".join(s) for s in product]
    permuted_talent_strings = stable_unique(permuted_talent_strings)
    logging.debug("Talent combinations: {}".format(permuted_talent_strings))
    return permuted_talent_strings


def chop_microseconds(delta):
    """Chop microseconds from a timedelta object"""
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def print_permutation_progress(valid_profiles, current, maximum, start_time, max_profile_chars, progress, max_progress):
    # output status every 5000 permutations, user should get at least a minor progress shown; also does not slow down
    # computation very much
    print_every_n = max(int(50000 / (maximum / max_progress)), 1)
    if progress % print_every_n == 0 or progress == max_progress:
        pct = 100.0 * current / maximum
        elapsed = datetime.datetime.now() - start_time
        bandwith = current / 1000 / elapsed.total_seconds() if elapsed.total_seconds() else 0.0
        bandwith_valid = valid_profiles / 1000 / elapsed.total_seconds() if elapsed.total_seconds() else 0.0
        elapsed = chop_microseconds(elapsed)
        remaining_time = elapsed * (100.0 / pct - 1.0) if current else "nan"
        if current > maximum:
            remaining_time = datetime.timedelta(seconds=0)
        if type(remaining_time) is datetime.timedelta:
            remaining_time = chop_microseconds(remaining_time)
        valid_pct = 100.0 * valid_profiles / current if current else 0.0
        logging.info("Processed {}/{} ({:5.2f}%) valid {} ({:5.2f}%) elapsed_time {} remaining {} bw {:.0f}k/s bw(valid) {:.0f}k/s".
                     format(str(current).rjust(max_profile_chars),
                            maximum,
                            pct,
                            valid_profiles,
                            valid_pct,
                            elapsed,
                            remaining_time,
                            bandwith,
                            bandwith_valid))


class Profile:
    """Represent global profile data"""
    pass


class TierCheck:

    def __init__(self, n, minimum, maximum):
        self.name = "T{}".format(n)
        self.n = n
        self.minimum = minimum
        self.maximum = maximum
        self.count = 0


class PermutationData:
    """Data for each permutation"""

    def __init__(self, items, profile, max_profile_chars):
        self.profile = profile
        self.max_profile_chars = max_profile_chars
        self.items = items

    def permutate_gems(self, items, gem_list):
        gems_on_gear = []
        gear_with_gems = {}
        for slot, gear in items.items():
            gems_on_gear += gear.gem_ids
            gear_with_gems[slot] = len(gear.gem_ids)

        # logging.debug("gems on gear: {}".format(gems_on_gear))
        if len(gems_on_gear) == 0:
            return

        # Combine existing gems of the item with the gems supplied by --gems
        combined_gem_list = gems_on_gear
        combined_gem_list += gem_list
        combined_gem_list = stable_unique(combined_gem_list)
        # logging.debug("Combined gem list: {}".format(combined_gem_list))
        new_gems = get_gem_combinations(combined_gem_list, len(gems_on_gear))
        # logging.debug("New Gems: {}".format(new_gems))
        new_combinations = []
        for gems in new_gems:
            new_items = copy.deepcopy(items)
            gems_used = 0
            for _i, (slot, num_gem_slots) in enumerate(gear_with_gems.items()):
                copied_item = copy.deepcopy(new_items[slot])
                copied_item.gem_ids = gems[gems_used:gems_used + num_gem_slots]
                new_items[slot] = copied_item
                gems_used += num_gem_slots
            new_combinations.append(new_items)
#         logging.debug("Gem permutations:")
#         for i, comb in enumerate(new_combinations):
#             logging.debug("Combination {}".format(i))
#             for slot, item in comb.items():
#                 logging.debug("{}: {}".format(slot, item))
#             logging.debug("")
        return new_combinations

    def update_talents(self, talents):
        self.talents = talents

    def count_leg_and_tier(self):
        self.legendaries = []
        self.t19 = 0
        self.t20 = 0
        self.t21 = 0
        for item in self.items.values():
            if item.is_legendary:
                self.legendaries.append(item)
                continue
            if item.tier_19:
                self.t19 += 1
            elif item.tier_20:
                self.t20 += 1
            elif item.tier_21:
                self.t21 += 1

    def check_usable_before_talents(self):
        self.count_leg_and_tier()
        """Check if profile is un-usable. Return None if ok, otherwise return reason"""
        if len(self.legendaries) < self.profile.args.legendary_min:
            return "too few legendaries {} < {}".format(len(self.legendaries), self.profile.args.legendary_min)
        if len(self.legendaries) > self.profile.args.legendary_max:
            return "too many legendaries"

        trinket1itemID = self.items["trinket1"].item_id
        trinket2itemID = self.items["trinket2"].item_id

        # check if amanthuls-trinket is the 3rd trinket; otherwise its an invalid profile
        # because 3 other legs have been equipped
        if len(self.legendaries) == 3:
            if not trinket1itemID == 154172 and not trinket2itemID == 154172:
                return " 3 legs equipped, but no Amanthul-Trinket found"

        if self.t19 < t19min:
            return "too few tier 19 items"
        if self.t19 > t19max:
            return "too many tier 19 items"
        if self.t20 < t20min:
            return "too few tier 20 items"
        if self.t20 > t20max:
            return "too many tier 20 items"
        if self.t21 < t21min:
            return "too few tier 21 items"
        if self.t21 > t21max:
            return "too many tier 21 items"

        return None

    def get_profile_name(self, valid_profile_number):
        # namingdata contains info for the profile-name
        namingData = {"Leg0": "None",
                      "Leg1": "None",
                      "Leg2": "None",
                      "T19": "",
                      "T20": "",
                      "T21": ""}
        # if a valid profile was detected, fill namingData; otherwise its pointless
        for i in range(1, 4):
            if len(self.legendaries) == i:
                for j in range(i):
                    namingData['Leg' + str(j)] = specdata.getAcronymForID(str(self.legendaries[j].item_id))

        for tier in (19, 20, 21):
            count = getattr(self, "t" + str(tier))
            tiername = "T" + str(tier)
            if count:
                pieces = 0
                if count >= 2:
                    pieces = 2
                if count >= 4:
                    pieces = 4
                    namingData[tiername] = "_{}_{}p".format(tiername, pieces)

        # example: "Uther_Soul_T19-2p_T20-2p_T21-2p"
        # scpout later adds a increment for multiple versions of this
        template = "{Leg0}_{Leg1}_{Leg2}{T19}{T20}{T21}_".\
            format(**namingData)

        return template + str(valid_profile_number).rjust(self.max_profile_chars, "0")

    def get_profile(self):
        items = []
        # Hack for now to get Txx and L strings removed from items
        for item in self.items.values():
            items.append(item.output_str)
        return "\n".join(items)

    def write_to_file(self, filehandler, valid_profile_number):
        profile_name = self.get_profile_name(valid_profile_number)
        filehandler.write("{}={}\n".format(self.profile.wow_class, profile_name))
        filehandler.write(self.profile.general_options)
        filehandler.write("\ntalents={}\n".format(self.talents))
        filehandler.write(self.get_profile())
        filehandler.write("\n\n")


def build_profile(args):
    # Read input.txt to init vars
    config = configparser.ConfigParser()

    # use read_file to get a error when input file is not available

    input_encoding = 'utf-8'
    try:
        with open(args.inputfile, encoding=input_encoding) as f:
            config.read_file(f)
    except UnicodeDecodeError as e:
        raise RuntimeError("""AutoSimC could not decode your input file '{file}' with encoding '{enc}'.
Please make sure that your text editor encodes the file as '{enc}',
or as a quick fix remove any special characters from your character name.""".format(file=args.inputfile,
                                                                                    enc=input_encoding)) from e

    profile = config['Profile']

    if 'class' in profile:
        raise RuntimeError("You input class format is wrong, please update SimPermut or your input file.")

    # Read input.txt
    #   Profile
    valid_classes = ["priest",
                     "druid",
                     "warrior",
                     "paladin",
                     "hunter",
                     "deathknight",
                     "demonhunter",
                     "mage",
                     "monk",
                     "rogue",
                     "shaman",
                     "warlock",
                     ]
    for wow_class in valid_classes:
        if config.has_option('Profile', wow_class):
            c_class = wow_class
            c_profilename = profile[wow_class]
            break
    else:
        raise RuntimeError("No valid wow class found in Profile section of input file. Valid classes are: {}".
                           format(valid_classes))
    player_profile = Profile()
    player_profile.args = args
    player_profile.config = config
    player_profile.simc_options = {}
    player_profile.wow_class = c_class
    player_profile.profile_name = c_profilename

    # Parse general profile options
    simc_profile_options = ["race",
                            "level",
                            "spec",
                            "role",
                            "position",
                            "artifact",
                            "crucible",
                            "potion",
                            "flask",
                            "food",
                            "augmentation"]
    for opt in simc_profile_options:
        if opt in profile:
            player_profile.simc_options[opt] = profile[opt]

    player_profile.class_spec = specdata.getClassSpec(c_class, player_profile.simc_options["spec"])
    player_profile.class_role = specdata.getRole(c_class, player_profile.simc_options["spec"])

    # Build 'general' profile options which do not permutate once into a simc-string
    logging.info("SimC options: {}".format(player_profile.simc_options))
    player_profile.general_options = "\n".join(["{}={}".format(key, value) for key, value in
                                                player_profile.simc_options.items()])
    logging.debug("Built simc general options string: {}".format(player_profile.general_options))

    return player_profile


class Item:
    """WoW Item"""
    tiers = [19, 20, 21]

    def __init__(self, slot, input_string=""):
        self._slot = slot
        self.name = ""
        self.item_id = 0
        self.bonus_ids = []
        self.enchant_ids = []
        self._gem_ids = []
        self.relic_ids = []
        self.tier_set = {}
        self.extra_options = {}
        self.is_legendary = False
        if self.name.startswith("L"):
            self.is_legendary = True
            self.name = self.name[1:]

        for tier in self.tiers:
            n = "T{}".format(tier)
            if self.name.startswith(n):
                setattr(self, "tier_{}".format(tier), True)
                self.name = self.name[len(n):]
            else:
                setattr(self, "tier_{}".format(tier), False)
        if len(input_string):
            self.parse_input(input_string)

        self._build_output_str()  # Pre-Build output string as good as possible

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, value):
        self._slot = value
        self._build_output_str()

    @property
    def gem_ids(self):
        return self._gem_ids

    @gem_ids.setter
    def gem_ids(self, value):
        self._gem_ids = value
        self._build_output_str()

    def parse_input(self, input_string):
        parts = input_string.split(",")
        self.name = parts[0]
        if self.name.startswith("L"):
            self.is_legendary = True
            self.name = self.name[1:]

        for tier in self.tiers:
            n = "T{}".format(tier)
            if self.name.startswith(n):
                setattr(self, "tier_{}".format(tier), True)
                self.name = self.name[len(n):]
            else:
                setattr(self, "tier_{}".format(tier), False)

        splitted_name = self.name.split("--")
        if len(splitted_name) > 1:
            self.name = splitted_name[1]

        for s in parts[1:]:
            name, value = s.split("=")
            name = name.lower()
            if name == "id":
                self.item_id = int(value)
            elif name == "bonus_id":
                self.bonus_ids = [int(v) for v in value.split("/")]
            elif name == "enchant_id":
                self.enchant_ids = [int(v) for v in value.split("/")]
            elif name == "gem_id":
                self.gem_ids = [int(v) for v in value.split("/")]
            elif name == "relic_id":
                self.relic_ids = [v for v in value.split("/")]
            else:
                if name not in self.extra_options:
                    self.extra_options[name] = []
                self.extra_options[name].append(value)

    def _build_output_str(self):
        self.output_str = "{}={},id={}".\
            format(self.slot,
                   self.name,
                   self.item_id)
        if len(self.bonus_ids):
            self.output_str += ",bonus_id=" + "/".join([str(v) for v in self.bonus_ids])
        if len(self.enchant_ids):
            self.output_str += ",enchant_id=" + "/".join([str(v) for v in self.enchant_ids])
        if len(self.gem_ids):
            self.output_str += ",gem_id=" + "/".join([str(v) for v in self.gem_ids])
        if len(self.relic_ids):
            self.output_str += ",relic_id=" + "/".join([str(v) for v in self.relic_ids])
        for name, values in self.extra_options.items():
            for value in values:
                self.output_str += ",{}={}".format(name, value)

    def __str__(self):
        return "Item({})".format(self.output_str)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        # We are just lazy and use __str__ to avoid all the complexity about having mutable members, etc.
        return hash(str(self.__dict__))


def product(*iterables):
    """
    Custom product function as a generator, instead of itertools.product
    This uses way less memory than itertools.product, because it is a generator only yielding a single item at a time.
    requirement for this is that each iterable can be restarted.
    Thanks to https://stackoverflow.com/a/12094519
    """
    if len(iterables) == 0:
        yield ()
    else:
        iterables = iterables
        it = iterables[0]
        for item in iter(it):
            for items in product(*iterables[1:]):
                yield (item,) + items


def permutate(args, player_profile):
    # Items to parse. First entry is the "correct" name
    gear_slots = [("head",),
                  ("neck",),
                  ("shoulders", "shoulder"),
                  ("back",),
                  ("chest",),
                  ("wrists", "wrist"),
                  ("hands",),
                  ("waist",),
                  ("legs",),
                  ("feet",),
                  ("finger", "finger1", "finger2"),
                  ("trinket", "trinket1", "trinket2",),
                  ("main_hand",),
                  ("off_hand",)]

    # Parse gear
    gear = player_profile.config['Gear']
    parsed_gear = collections.OrderedDict({})
    for gear_slot in gear_slots:
        slot_base_name = gear_slot[0]  # First mentioned "correct" item name
        parsed_gear[slot_base_name] = []
        for entry in gear_slot:
            if entry in gear:
                for s in gear[entry].split("|"):
                    parsed_gear[slot_base_name].append(Item(slot_base_name, s))
        if len(parsed_gear[slot_base_name]) == 0:
            # We havent found any items for that slot, add empty dummy item
            parsed_gear[slot_base_name] = [Item(slot_base_name, "")]

    logging.debug("Parsed gear before legendaries: {}".format(parsed_gear))

    if args.gems is not None:
        splitted_gems = build_gem_list(args.gems)

    # Filter each slot to only have unique items, before doing any gem/legendary permutation.
    for key, value in parsed_gear.items():
        parsed_gear[key] = stable_unique(value)

    # Add legendaries
    if args.legendaries is not None:
        for legendary in args.legendaries.split(','):
            add_legendary(legendary.split("/"), parsed_gear)

    logging.info("Parsed gear including legendaries:")
    for slot, item in parsed_gear.items():
        logging.info("{:10s}: {}".format(slot, item))

    # This represents a dict of all options which will be permutated fully with itertools.product
    normal_permutation_options = collections.OrderedDict({})

    # Add talents to permutations
    l_talents = player_profile.config['Profile'].get("talents", "")
    talent_permutations = permutate_talents(l_talents)

    # Calculate max number of gem slots in equip. Will be used if we do gem permutations.
    if args.gems is not None:
        max_gem_slots = 0
        for _slot, items in parsed_gear.items():
            max_gem_on_item_slot = 0
            for item in items:
                if len(item.gem_ids) > max_gem_on_item_slot:
                    max_gem_on_item_slot = len(item.gem_ids)
            max_gem_slots += max_gem_on_item_slot

    # Add 'normal' gear to normal permutations, excluding trinket/rings
    gear_normal = {k: v for k, v in parsed_gear.items() if (not k == "finger" and not k == "trinket")}
    normal_permutation_options.update(gear_normal)

    # Calculate normal permutations
    normal_permutations = product(*normal_permutation_options.values())
    logging.debug("Building permutations matrix finished.")

    special_permutations_config = {"finger": ("finger1", "finger2"),
                                   "trinket": ("trinket1", "trinket2")
                                   }
    special_permutations = {}
    for name, values in special_permutations_config.items():
        # Get entries from parsed gear, exclude empty finger/trinket lines
        entries = [v for k, v in parsed_gear.items() if k.startswith(name)]
        entries = list(itertools.chain(*entries))

        # Remove empty (id=0) items from trinket/rings, except if there are 0 ring/trinkets specified. Then we need
        # the single dummy item
        remove_empty_entries = [item for item in entries if item.item_id != 0]
        if len(remove_empty_entries):
            entries = remove_empty_entries

        logging.debug("Input list for special permutation '{}': {}".format(name,
                                                                           entries))
        if args.unique_jewelry:
            # Unique finger/trinkets.
            permutations = itertools.combinations(entries, len(values))
        else:
            permutations = itertools.combinations_with_replacement(entries, len(values))
        permutations = list(permutations)
        for i, (item1, item2) in enumerate(permutations):
            new_item1 = copy.deepcopy(item1)
            new_item1.slot = values[0]
            new_item2 = copy.deepcopy(item2)
            new_item2.slot = values[1]
            permutations[i] = (new_item1, new_item2)

        logging.debug("Got {} permutations for {}.".format(len(permutations),
                                                           name))
        for p in permutations:
            logging.debug(p)

        # Remove equal id's
        if args.unique_jewelry:
            permutations = [p for p in permutations if p[0].item_id != p[1].item_id]
            logging.debug("Got {} permutations for {} after id filter.".format(len(permutations),
                                                                               name))
            for p in permutations:
                logging.debug(p)
        # Make unique
        permutations = stable_unique(permutations)
        logging.info("Got {} permutations for {} after unique filter.".format(len(permutations),
                                                                              name))
        for p in permutations:
            logging.debug(p)

        entry_dict = {v: None for v in values}
        special_permutations[name] = [name, entry_dict, permutations]

    # Exclude antorus trinkets
    p_trinkets = special_permutations["trinket"][2]
    p_trinkets = [p for p in p_trinkets if p[0].item_id not in antorusTrinkets or p[1].item_id not in antorusTrinkets]
    special_permutations["trinket"][2] = p_trinkets
    logging.info("Got {} permutations for trinkets after Antorus filter.".
                 format(len(special_permutations["trinket"][2])))
    for p in special_permutations["trinket"][2]:
        logging.debug(p)

    # Calculate & Display number of permutations
    max_nperm = 1
    for name, perm in normal_permutation_options.items():
        max_nperm *= len(perm)
    permutations_product = {"normal gear&talents":  "{} ({})".format(max_nperm,
                                                                     {name: len(items) for name, items in
                                                                      normal_permutation_options.items()}
                                                                     )
                            }
    for name, _entries, opt in special_permutations.values():
        max_nperm *= len(opt)
        permutations_product[name] = len(opt)
    max_nperm *= len(talent_permutations)
    gem_perms = 1
    if args.gems is not None:
        max_num_gems = max_gem_slots + len(splitted_gems)
        gem_perms = len(list(itertools.combinations_with_replacement(range(max_gem_slots), max_num_gems)))
        max_nperm *= gem_perms
        permutations_product["gems"] = gem_perms
    permutations_product["talents"] = len(talent_permutations)
    logging.info("Max number of normal permutations: {}".format(max_nperm))
    logging.info("Number of permutations: {}".format(permutations_product))
    max_profile_chars = len(str(max_nperm))  # String length of max_nperm

    # Start the permutation!
    processed = 0
    progress = 0  # Separate progress variable not counting gem and talent combinations
    max_progress = max_nperm / gem_perms / len(talent_permutations)
    valid_profiles = 0
    start_time = datetime.datetime.now()
    unusable_histogram = {}  # Record not usable reasons
    with open(args.outputfile, 'w') as output_file:
        for perm_normal in normal_permutations:
            for perm_finger in special_permutations["finger"][2]:
                for perm_trinket in special_permutations["trinket"][2]:
                    entries = perm_normal
                    entries += perm_finger
                    entries += perm_trinket
                    items = {e.slot: e for e in entries if type(e) is Item}
                    data = PermutationData(items, player_profile, max_profile_chars)
                    is_unusable_before_talents = data.check_usable_before_talents()
                    if not is_unusable_before_talents:
                        # add gem-permutations to gear
                        if args.gems is not None:
                            gem_permutations = data.permutate_gems(items, splitted_gems)
                        else:
                            gem_permutations = (items,)
                        for gem_permutation in gem_permutations:
                            data.items = gem_permutation
                            # Permutate talents after is usable check, since it is independent of the talents
                            for t in talent_permutations:
                                data.update_talents(t)
                                # Additional talent usable check could be inserted here.
                                data.write_to_file(output_file, valid_profiles)
                                valid_profiles += 1
                                processed += 1
                    else:
                        processed += len(talent_permutations) * gem_perms
                        if args.debug:
                            if is_unusable_before_talents not in unusable_histogram:
                                unusable_histogram[is_unusable_before_talents] = 0
                            unusable_histogram[is_unusable_before_talents] += len(talent_permutations) * gem_perms
                    progress += 1
                    print_permutation_progress(valid_profiles, processed, max_nperm, start_time, max_profile_chars,
                                               progress, max_progress)

    result = "Finished permutations. Valid: {:n} of {:n} processed. ({:.2f}%)".\
        format(valid_profiles,
               processed,
               100.0 * valid_profiles / max_nperm if max_nperm else 0.0)
    logging.info(result)

    # Not usable histogram debug output
    if logger.isEnabledFor(logging.DEBUG):
        unusable_string = []
        for key, value in unusable_histogram.items():
            unusable_string.append("'{}': {} ({:.2f}%)".
                                   format(key, value, value * 100.0 / max_nperm if max_nperm else 0.0))
        logging.debug("Not usable histogram: {}".format(unusable_string))

    # Print checksum so we can check for equality when making changes in the code
    outfile_checksum = file_checksum(args.outputfile)
    logging.info("Output file checksum: {}".format(outfile_checksum))

    return valid_profiles


def checkResultFiles(subdir):
    """Check the SimC result files of a previous stage for validity."""
    subdir = os.path.join(os.getcwd(), subdir)
    printLog("Checking Files in subdirectory: {}".format(subdir))

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


def grab_profiles(player_profile, stage):
    """Parse output/result files from previous stage and get number of profiles to simulate"""
    subdir_previous_stage = get_subdir(stage - 1)
    if stage == 1:
        num_generated_profiles = splitter.split(outputFileName, get_subdir(stage),
                                                settings.splitting_size, player_profile.wow_class)
    else:
        try:
            checkResultFiles(subdir_previous_stage)
        except Exception as e:
            msg = "Error while checking result files in {}: {}\nPlease restart AutoSimc at a previous stage.".\
                format(subdir_previous_stage, e)
            raise RuntimeError(msg) from e
        if settings.default_grabbing_method == "target_error":
            filter_by = "target_error"
            filter_criterium = None
        elif settings.default_grabbing_method == "top_n":
            filter_by = "count"
            filter_criterium = settings.default_top_n[stage - num_stages - 1]
        is_last_stage = (stage == num_stages)
        num_generated_profiles = splitter.grab_best(filter_by, filter_criterium, subdir_previous_stage,
                                                    get_subdir(stage), outputFileName, not is_last_stage)
    if num_generated_profiles:
        logging.info("Found {} profile(s) to simulate.".format(num_generated_profiles))
    return num_generated_profiles


def static_stage(player_profile, stage):
    if stage > num_stages:
        return

    printLog("\n\n***Entering static mode, STAGE {}***".format(stage))
    num_generated_profiles = grab_profiles(player_profile, stage)
    is_last_stage = (stage == num_stages)
    try:
        num_iterations = settings.default_iterations[stage]
    except Exception:
        num_iterations = None
    if not num_iterations:
        if settings.skip_questions:
            raise ValueError("Cannot run static mode and skip questions without default iterations set for stage {}.".format(stage))
        iterations_choice = input("Please enter the number of iterations to use (q to quit): ")
        if iterations_choice == "q":
            printLog("Quitting application")
            sys.exit(0)
        num_iterations = int(iterations_choice)
    splitter.sim(get_subdir(stage), "iterations", num_iterations,
                 player_profile, stage, is_last_stage, num_generated_profiles)
    static_stage(player_profile, stage + 1)


def dynamic_stage(player_profile, num_generated_profiles, previous_target_error=None, stage=1):
    if stage > num_stages:
        return
    printLog("\n\n***Entering dynamic mode, STAGE {}***".format(stage))

    num_generated_profiles = grab_profiles(player_profile, stage)

    # Display estimated simulation time information to user
    result_data = get_analyzer_data(player_profile.class_spec)
    print("Estimated calculation times for stage {} based on your data:".format(stage))
    for i, (target_error, iterations, elapsed_time_seconds) in enumerate(result_data):
        elapsed_time = datetime.timedelta(seconds=elapsed_time_seconds)
        estimated_time = chop_microseconds(elapsed_time * num_generated_profiles) if num_generated_profiles else None
        print("({:2n}): Target Error: {:6.3f}%:  Est. calc. time: {} (time/profile: {:5.2f}s iterations: {:5n}) ".
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
            raise ValueError("Cannot run dynamic mode and skip questions without default target_error set for stage {}.".format(stage))
        else:
            calc_choice = input("Please enter the type of calculation to perform (q to quit): ")
            if calc_choice == "q":
                printLog("Quitting application")
                sys.exit(0)
        calc_choice = int(calc_choice)
        if calc_choice >= len(result_data) or calc_choice < 0:
            raise ValueError("Invalid calc choice '{}' can only be from 0 to {}".format(calc_choice,
                                                                                        len(result_data) - 1))
        printLog("Sim: Number of permutations: " + str(num_generated_profiles))
        printLog("Sim: Chosen calculation: {}".format(calc_choice))

        target_error, _iterations, _elapsed_time_seconds = result_data[calc_choice]

    # if the user chose a target_error which is higher than one chosen in the previous stage
    # he is given an option to adjust it.
    if previous_target_error is not None and previous_target_error <= target_error:
        print("Warning Target_Error chosen in stage {}: {} <= Default_Target_Error for stage {}: {}".
              format(stage - 1, previous_target_error, stage, target_error))
        new_value = input(
            "Do you want to continue anyway (Enter), quit (q) or enter a new target_error"
            " for the current stage (n)?: ")
        printLog("User chose: " + str(new_value))
        if new_value == "q":
            printLog("Quitting application")
            sys.exit(0)
        if new_value == "n":
            target_error = float(input("Enter new target_error (Format: 0.3): "))
            printLog("User entered target_error_secondpart: " + str(target_error))

    # Show estimated sim time based on users chosen target_error
    if num_generated_profiles:
        result_data = get_analyzer_data(player_profile.class_spec)
        for i, (te, _iterations, elapsed_time_seconds) in enumerate(result_data):
            if target_error <= te:
                elapsed_time = datetime.timedelta(seconds=elapsed_time_seconds)
                estimated_time = chop_microseconds(elapsed_time * num_generated_profiles) if num_generated_profiles else None
                logging.info("Chosen Target Error: {:.3f}% <= {:.3f}%:  Time/Profile: {:5.2f} sec => Est. calc. time: {}".
                      format(target_error,
                             te,
                             elapsed_time.total_seconds(),
                             estimated_time)
                             )
                if not settings.skip_questions:
                    if estimated_time and estimated_time.total_seconds() > 43200:  # 12h
                        if input("Warning: This might take a *VERY* long time ({}) (q to quit, Enter to continue: )".
                                 format(estimated_time)) == "q":
                            printLog("Quitting application")
                            sys.exit(0)
                break
        else:
            logging.warning("Could not provide any estimated calculation time.")
    is_last_stage = (stage == num_stages)
    splitter.sim(get_subdir(stage), "target_error", target_error, player_profile,
                 stage, is_last_stage, num_generated_profiles)
    dynamic_stage(player_profile, num_generated_profiles, target_error, stage + 1)


def start_stage(player_profile, num_generated_profiles, stage):
    logging.info("Starting at stage {}".format(stage))
    logging.info("You selected grabbing method '{}'.".format(settings.default_grabbing_method))
    print("\nYou have to choose one of the following modes for calculation:")
    print("1) Static mode uses a fixed number of iterations, with varying error per profile ({})".
          format(settings.default_iterations))
    print("   It is however faster if simulating huge amounts of profiles")
    print(
        "2) Dynamic mode (preferred) lets you choose a specific 'correctness' of the calculation, but takes more time.")
    print(
        "   It uses the chosen target_error for the first part; in stage2 onwards, the following values are used: {}".format(settings.default_target_error))
    if settings.skip_questions:
        mode_choice = int(settings.auto_choose_static_or_dynamic)
    else:
        mode_choice = input("Please choose your mode (Enter to exit): ")
        if not len(mode_choice):
            logging.info("User exit.")
            sys.exit(0)
        mode_choice = int(mode_choice)
    valid_modes = (1, 2)
    if mode_choice not in valid_modes:
        raise RuntimeError("Invalid mode '{}' selected. Valid modes: {}.".format(mode_choice,
                                                                                 valid_modes))
    if mode_choice == 1:
        static_stage(player_profile, stage)
    elif mode_choice == 2:
        dynamic_stage(player_profile, num_generated_profiles, None, stage)
    else:
        assert(False)


def check_interpreter():
    """Check interpreter for minimum requirements."""
    # Does not really work in practice, since formatted string literals (3.6) lead to SyntaxError prior to execution of
    # the program with older interpreters.
    required_major, required_minor = (3, 4)
    major, minor, _micro, _releaselevel, _serial = sys.version_info
    if major > required_major:
        return
    elif major == required_major:
        if minor >= required_minor:
            return
    raise RuntimeError("Python-Version too old! You are running Python {}. Please install at least "
                       "Python-Version {}.{}.x".format(sys.version,
                                                       required_major,
                                                       required_minor))

########################
#     Program Start    #
########################


def main():
    global class_spec

    error_handler = logging.FileHandler(settings.errorFileName)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)s %(message)s"))

    # Handler to log messages to file
    log_handler = logging.FileHandler(settings.logFileName)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)s %(message)s"))

    # Handler for loging to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(level=logging.DEBUG, handlers=[error_handler,
                                                       log_handler,
                                                       stdout_handler])

    # check version of python-interpreter running the script
    check_interpreter()

    args = handleCommandLine()
    if args.debug:
        log_handler.setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.DEBUG)
    logging.debug("Parsed command line arguments: {}".format(args))

    if args.sim:
        autoDownloadSimc()
    validateSettings(args)

    player_profile = build_profile(args)

    print("Combinations in progress...")

    # can always be rerun since it is now deterministic
    outputGenerated = False
    num_generated_profiles = None
    if args.sim == "all" or args.sim is None:
        start = datetime.datetime.now()
        num_generated_profiles = permutate(args, player_profile)
        logging.info("Permutating took {}.".format(datetime.datetime.now() - start))
        outputGenerated = True
    elif args.sim == "stage1":
        if input("Do you want to generate {} again? Press y to regenerate: ".format(args.outputfile)) == "y":
            num_generated_profiles = permutate(args, player_profile)
            outputGenerated = True

    if outputGenerated:
        if num_generated_profiles == 0:
            raise ValueError("No valid profile combinations found."
                             " Please run again with --debug and check your input.txt and settings.py.")
        if args.sim:
            if not settings.skip_questions:
                if num_generated_profiles and num_generated_profiles > 50000:
                    if input(
                            "-----> Beware: Computation with Simcraft might take a VERY long time with this amount of profiles!"
                            " <----- (Press Enter to continue, q to quit)") == "q":
                        logging.info("Program exit by user")
                        sys.exit(0)

    if args.sim:
        if args.sim == "stage1" or args.sim == "all":
            start_stage(player_profile, num_generated_profiles, 1)
        if args.sim == "stage2":
            start_stage(player_profile, None, 2)
        if args.sim == "stage3":
            start_stage(player_profile, None, 3)

        if settings.clean_up:
            cleanup()
    print("Finished.")


if __name__ == "__main__":
    try:
        main()
        logging.shutdown()
    except Exception as e:
        logging.error("Error: {}".format(e), exc_info=True)
        sys.exit(1)
