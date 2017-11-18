# -*- coding: utf-8 -*-
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
from urllib.request import urlopen, urlretrieve
from re import search, match
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
c_profileid = 0
c_profilemaxid = 0
t19min = int(settings.default_equip_t19_min)
t19max = int(settings.default_equip_t19_max)
t20min = int(settings.default_equip_t20_min)
t20max = int(settings.default_equip_t20_max)
t21min = int(settings.default_equip_t21_min)
t21max = int(settings.default_equip_t21_max)

logFileName = settings.logFileName
errorFileName = settings.errorFileName

s_stage = ""

iterations_firstpart = settings.default_iterations_stage1
iterations_secondpart = settings.default_iterations_stage2
iterations_thirdpart = settings.default_iterations_stage3

target_error_secondpart = settings.default_target_error_stage2
target_error_thirdpart = settings.default_target_error_stage3

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

settings_subdir = {1: settings.subdir1,
                   2: settings.subdir2,
                   3: settings.subdir3
                   }
settings_iterations = {1: int(settings.default_iterations_stage1),
                       2: int(settings.default_iterations_stage2),
                       3: int(settings.default_iterations_stage3)
                       }
settings_n_stage = {2: settings.default_top_n_stage2,
                    3: settings.default_top_n_stage3
                    }

settings_target_error = {2: settings.default_target_error_stage2,
                         3: settings.default_target_error_stage3
                         }

# Global logger instance
logger = logging.getLogger()


#   Error handle
def printLog(stringToPrint):
    logging.info(stringToPrint)


# Add legendary to the right tab
def add_legendary(legendary_split, gear_list):
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


def build_gem_list(gems):
    splitted_gems = gems.split(",")
    for gem in splitted_gems:
        if gem not in gem_ids.keys():
            raise ValueError("Unknown gem '{}' to sim, please check your input. Valid gems: {}".
                             format(gem, gem_ids.keys()))
    # Convert parsed gems to list of gem ids
    gems = [gem_ids[gem] for gem in splitted_gems]

    # Unique by gem id, so that if user specifies eg. 200haste,haste there will only be 1 gem added.
    gems = list(set(gems))
    return gems


def cleanItem(item_string):
    if "--" in item_string:
        item_string = item_string.split("--")[1]

    return item_string


# Check if permutation is valid
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
                        choices=['permutation_only', 'all', 'stage1', 'stage2', 'stage3'],
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

    parser.add_argument('-quiet', '--quiet',
                        action='store_true',
                        default=settings.b_quiet,
                        help='Option for disabling Console-output. Generates the outputfile much faster for '
                        'large permuation-size')

    parser.add_argument('-gems', '--gems',
                        required=False,
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
                        'when enabling this.'.format(list(gem_ids.keys())))

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

    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))

    return parser.parse_args()


# Manage command line parameters
# todo: include logic to split into smaller/larger files (default 50)
def handleCommandLine():
    args = parse_command_line_args()

    # Sim stage is either None or ['stage1'], ['stage2'], ...
    args.sim = args.sim[0]
    if args.sim == "permutate_only":
        args.sim = None

    # For now, just write command line arguments into globals
    global outputFileName
    outputFileName = args.outputfile

    return args


# returns target_error, iterations, elapsed_time_seconds for a given class_spec
def get_analyzer_data(class_spec):
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
    filename = search(r'<a href="(simc.+win64.+7z)">', html).group(1)
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
    settings.simc_path = os.path.join(download_dir, filename[:filename.find("win64")+len("win64")], "simc.exe")
    splitter.simc_path = settings.simc_path
    if not os.path.exists(settings.simc_path):
        seven_zip_executables = ["7z.exe", "C:/Program Files/7-Zip/7z.exe"]
        for seven_zip_executable in seven_zip_executables:
            try:
                cmd = seven_zip_executable + ' x "'+filepath+'" -aoa -o"' + download_dir + '"'
                logging.debug("Running unpack command '{}'".format(cmd))
                subprocess.call(cmd)
                
                # keep the latest 7z to remember current version, but clean up any other ones
                files = glob.glob(download_dir + '/simc*win64*7z')
                for f in files:
                    if not os.path.basename(f)==filename:
                        print("Removing old simc:", os.path.basename(f))
                        os.remove(f)
                break
            except Exception as e:
                print("Exception when unpacking: {}".format(e))
        else:
            raise RuntimeError("Could not unpack SimC.")
    else:
        print("simc_path={}".format(repr(settings.simc_path)))


def cleanup_subdir(subdir):
    if os.path.exists(subdir):
        if not settings.delete_temp_default and not settings.skip_questions:
            if input("Do you want to remove subfolder: " + subdir + "? (Press y to confirm): ") != "y":
                return
        printLog("Removing: {}".format(subdir))
        shutil.rmtree(subdir)


def cleanup():
    printLog("Cleaning up")

    subdirs = [os.path.join(os.getcwd(), settings.subdir1),
               os.path.join(os.getcwd(), settings.subdir2),
               os.path.join(os.getcwd(), settings.subdir3)]
    result_folder = os.path.join(os.getcwd(), settings.result_subfolder)
    if not os.path.exists(result_folder):
        logging.info("Result-subfolder '{}' does not exist. Creating it.".format(result_folder))
        os.makedirs(result_folder)

    subdir3 = subdirs[2]
    if os.path.exists(subdir3):
        for _root, _dirs, files in os.walk(subdir3):
            for file in files:
                if file.endswith(".html"):
                    src = os.path.join(subdir3, file)
                    dst = os.path.join(result_folder, file)
                    printLog("Moving file: {} to {}".format(src, dst))
                    shutil.move(src, dst)

    for subdir in subdirs:
        cleanup_subdir(subdir)


def validateSettings(args):
    # Check simc executable availability. Maybe move to somewhere else.
    if args.sim:
        if not os.path.exists(settings.simc_path):
            raise ValueError("Error: Wrong path to simc executable: {}".format(settings.simc_path))
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


def file_checksum(filename):
    h = hashlib.sha3_256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def get_Possible_Gem_Combinations(gems_to_use, numberOfGems):
    if numberOfGems <= 0:
        return []
    printLog("Creating Gem Combinations")
    printLog("Number of Gems: " + str(numberOfGems))
    combinations = itertools.combinations_with_replacement(gems_to_use, r=numberOfGems)
    return list(combinations)


# gearlist contains a list of items, as in l_head
def permutate_gems_for_slot(splitted_gems, slot_name, slot_gearlist):
    logging.debug("Permutating Gems for slot {}".format(slot_name))
    for item in slot_gearlist.copy():
        logging.debug("Permutating slot_item: {}".format(item))
        num_gems = len(item.gem_ids)
        if num_gems == 0:
            logging.debug("No gems to permutate")
            continue

        new_gems = get_Possible_Gem_Combinations(splitted_gems, num_gems)
        logging.debug("New Gems: {}".format(new_gems))
        for gems in new_gems:
            new_item = copy.deepcopy(item)
            new_item.gem_ids = gems
            slot_gearlist.append(new_item)
    logging.debug("Final slot list: {}".format(slot_gearlist))


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


def print_permutation_progress(current, maximum, start_time, max_profile_chars):
    # output status every 5000 permutations, user should get at least a minor progress shown; also does not slow down
    # computation very much
    if current % 50000 == 0 or current == maximum:
        pct = 100.0 * current / maximum
        elapsed = datetime.datetime.now() - start_time
        bandwith = current / 1000 / elapsed.total_seconds() if elapsed.total_seconds() else 0.0
        elapsed = chop_microseconds(elapsed)
        remaining_time = elapsed * (100.0 / pct - 1.0) if current else "nan"
        if type(remaining_time) is datetime.timedelta:
            remaining_time = chop_microseconds(remaining_time)
        logging.info("Processed {}/{} ({:5.2f}%) elapsed_time {} remaining {} bandwith {:.0f}k/s".
                     format(str(current).rjust(max_profile_chars),
                            maximum,
                            pct,
                            elapsed,
                            remaining_time,
                            bandwith))


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
    def __init__(self, permutations, slot_names, profile, max_profile_chars):
        self.profile = profile
        self.max_profile_chars = max_profile_chars
        permutations = list(itertools.chain(*permutations))

        # Build this dict to get correct slot names for finger1/2. Do not use item.slot in here
        self.items = {slot_names[i]: item for i, item in enumerate(permutations) if type(item) is Item}
        self.talents = permutations[slot_names.index("talents")]

        self.count_leg_and_tier()
        self.not_usable = self.check_usable()

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

    def check_usable(self):
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
        for slot, item in self.items.items():
            items.append(item.output_str(slot))
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
    with open(args.inputfile, encoding='utf-8-sig') as f:
        config.read_file(f)

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
        self.slot = slot
        self.name = ""
        self.item_id = 0
        self.bonus_ids = []
        self.enchant_ids = []
        self._gem_ids = []
        self.relic_ids = []
        self.tier_set = {}
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

    def _build_output_str(self):
        # Use external slot name because of permutation reasons with finger1/2
        self.output_str_tail = "={},id={}".\
            format(self.name,
                   self.item_id)
        if len(self.bonus_ids):
            self.output_str_tail += ",bonus_id=" + "/".join([str(v) for v in self.bonus_ids])
        if len(self.enchant_ids):
            self.output_str_tail += ",enchant_id=" + "/".join([str(v) for v in self.enchant_ids])
        if len(self.gem_ids):
            self.output_str_tail += ",gem_id=" + "/".join([str(v) for v in self.gem_ids])
        if len(self.relic_ids):
            self.output_str_tail += ",relic_id=" + "/".join([str(v) for v in self.relic_ids])

    def output_str(self, slotname):
        return str(slotname) + self.output_str_tail

    def __str__(self):
        return "Item({})".format(self.output_str(self.slot))

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
    Thanks to https://stackoverflow.com/questions/12093364/cartesian-product-of-large-iterators-itertools/12094519#12094519
    """
    if len(iterables) == 0:
        yield ()
    else:
        iterables = iterables
        it = iterables[0]
        for item in it() if callable(it) else iter(it):
            for items in product(*iterables[1:]):
                yield (item,) + items


def stable_unique(seq):
    """
    Filter sequence to only contain unique elements, in a stable order
    Credit to https://stackoverflow.com/a/480227
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# todo: add checks for missing headers, prio low
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
    normal_permutation_options["talents"] = permutate_talents(l_talents)

    # add gem-permutations to gear
    if args.gems:
        splitted_gems = build_gem_list(args.gems)
        for name, gear in parsed_gear.items():
            permutate_gems_for_slot(splitted_gems, name, gear)

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

    # Set up the combined permutation list with normal + special permutations
    all_permutation_options = [normal_permutations, *[opt for _name, _entries, opt in special_permutations.values()]]

    all_permutations = product(*all_permutation_options)
    special_names = [list(entries.keys()) for _name, entries, _opt in special_permutations.values()]
    all_permutation_names = list(itertools.chain(*[list(normal_permutation_options.keys()), *special_names]))

    # Calculate & Display number of permutations
    max_num_profiles = 1
    for name, perm in normal_permutation_options.items():
        max_num_profiles *= len(perm)
    permutations_product = {"normal gear&talents":  "{} ({})".format(max_num_profiles,
                                                                     {name: len(items) for name, items in
                                                                      normal_permutation_options.items()}
                                                                     )
                            }
    for name, _entries, opt in special_permutations.values():
        max_num_profiles *= len(opt)
        permutations_product[name] = len(opt)
    logging.info("Max number of profiles: {}".format(max_num_profiles))
    logging.info("Number of permutations: {}".format(permutations_product))
    max_profile_chars = len(str(max_num_profiles))  # String length of max_num_profiles

    # Start the permutation!
    processed = 0
    valid_profiles = 0
    start_time = datetime.datetime.now()
    unusable_histogram = {}  # Record not usable reasons
    with open(args.outputfile, 'w') as output_file:
        for perm in all_permutations:
            data = PermutationData(perm, all_permutation_names, player_profile, max_profile_chars)
            if not data.not_usable:
                data.write_to_file(output_file, valid_profiles)
                valid_profiles += 1
            elif args.debug:
                if data.not_usable not in unusable_histogram:
                    unusable_histogram[data.not_usable] = 0
                unusable_histogram[data.not_usable] += 1
            processed += 1
            print_permutation_progress(processed, max_num_profiles, start_time, max_profile_chars)

    result = "Finished permutations. Valid: {:n} of {:n} processed. ({:.2f}%)".\
        format(valid_profiles,
               processed,
               100.0 * valid_profiles / max_num_profiles if max_num_profiles else 0.0)
    print(result)
    logging.info(result)

    # Not usable histogram debug output
    if logger.isEnabledFor(logging.DEBUG):
        unusable_string = []
        for key, value in unusable_histogram.items():
            unusable_string.append("'{}': {} ({:.2f}%)".
                                   format(key, value, value * 100.0 / max_num_profiles if max_num_profiles else 0.0))
        logging.debug("Not usable histogram: {}".format(unusable_string))

    # Print checksum so we can check for equality when making changes in the code
    outfile_checksum = file_checksum(args.outputfile)
    logging.info("Output file checksum: {}".format(outfile_checksum))

    return valid_profiles


def resim(subdir, player_profile, stage):
    global user_targeterror

    print("Resimming empty files in " + str(subdir))
    if settings.skip_questions:
        mode = str(settings.auto_choose_static_or_dynamic)
    else:
        mode = input("Static (1) or dynamic mode (2)? (q to quit): ")
    if mode == "q":
        logging.info("User exit")
        sys.exit(0)
    elif mode == "1":
        if subdir == settings.subdir1:
            iterations = settings.default_iterations_stage1
        elif subdir == settings.subdir2:
            iterations = settings.default_iterations_stage2
        elif subdir == settings.subdir3:
            iterations = settings.default_iterations_stage3
        return splitter.sim(subdir, "iterations=" + str(iterations), player_profile, 1)
    elif mode == "2":
        if subdir == settings.subdir1:
            if settings.skip_questions:
                user_targeterror = settings.auto_dynamic_stage1_target_error_value
            else:
                user_targeterror = input("Which target_error?: ")
        elif subdir == settings.subdir2:
            if settings.skip_questions:
                user_targeterror = settings.default_target_error_stage2
            else:
                user_targeterror = input("Which target_error?: ")
        elif subdir == settings.subdir3:
            if settings.skip_questions:
                user_targeterror = settings.default_target_error_stage3
            else:
                user_targeterror = input("Which target_error?: ")
        return splitter.sim(subdir, "target_error=" + str(user_targeterror), player_profile, 1)
    return False


def launch_resims(subdir, player_profile, stage, count=2):

    if count > 0:
        if not settings.skip_questions:
            q = input("Do you want to resim the empty files? Warning: May not succeed! (Press q to quit): ")
            if q == "q":
                printLog("User exit")
                sys.exit(0)

        printLog(F"Resimming files: Count: {count}")
        print("Starting resim with {} tries left.".format(count-1))
        if not resim(subdir, player_profile, stage):
            return launch_resims(subdir, player_profile, stage, count - 1)
        print("resim success")
        return True
    else:
        printLog("Maximum number of retries reached, sth. is wrong; exiting")
        return False


def checkResultFiles(subdir, player_profile, count=2):
    subdir = os.path.join(os.getcwd(), subdir)
    printLog("Checking Files in subdirectory: {}".format(subdir))
    if os.path.exists(subdir):
        empty = 0
        checkedFiles = 0
        for _root, _dirs, files in os.walk(subdir):
            for file in files:
                checkedFiles += 1
                if file.endswith(".result"):
                    filename = os.path.join(subdir, file)
                    if os.stat(filename).st_size <= 0:
                        printLog("File is empty: {}".format(file))
                        empty += 1
    else:
        printLog("Error: Subdir does not exist: {}".format(subdir))
        return False

    if checkedFiles == 0:
        printLog("No files in: " + str(subdir))
        print("No files in: " + str(subdir) + ", exiting")
        return False

    if empty > 0:
        printLog("Found empty files")
        return False
    else:
        printLog("Checked all files in " + str(subdir) + " : Everything seems to be alright.")
        print("Checked all files in " + str(subdir) + " : Everything seems to be alright.")
        return True


def static_stage(player_profile, stage):
    if stage > 3:
        return

    printLog("\nEntering static mode, STAGE {}.\n".format(stage))

    if stage > 1:
        if not checkResultFiles(settings_subdir[stage - 1], player_profile):
            if not launch_resims(settings_subdir[stage - 1], player_profile, stage - 1):
                raise RuntimeError("Error, some result-files are empty in {}".format(settings_subdir[stage - 1]))
            else:
                logging.info("Resimming succeeded.")
        splitter.grab_best("count", settings_n_stage[stage], settings_subdir[stage - 1],
                           settings_subdir[stage], outputFileName)
    else:
        # Stage1 splitting
        splitter.split(outputFileName, settings.splitting_size, player_profile.wow_class)
    # sim these with few iterations, can still take hours with huge permutation-sets; fewer than 100 is not advised
    splitter.sim(settings_subdir[stage], "iterations={}".format(settings_iterations[stage]), player_profile, stage - 1)
    static_stage(player_profile, stage + 1)


def dynamic_stage1(player_profile, num_generated_profiles, stage=1):
    printLog("Entering dynamic mode, STAGE {}".format(stage))
    result_data = get_analyzer_data(player_profile.class_spec)
    print("Listing options:")
    print("Estimated calculation times based on your data:")
    print("Class/Spec: " + str(player_profile.class_spec))
    print("Number of permutations to simulate: " + str(num_generated_profiles))
    for i, (target_error, _iterations, elapsed_time_seconds) in enumerate(result_data):
        elapsed_time = datetime.timedelta(seconds=elapsed_time_seconds)
        estimated_time = chop_microseconds(elapsed_time * num_generated_profiles) if num_generated_profiles else None

        print("({:2n}): Target Error: {:.3f}%:  Time/Profile: {:5.2f} sec => Est. calc. time: {}".
              format(i,
                     target_error,
                     elapsed_time.total_seconds(),
                     estimated_time)
              )

    if settings.skip_questions:
        calc_choice = settings.auto_dynamic_stage1_target_error_table
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

    target_error, _iterations, elapsed_time_seconds = result_data[calc_choice]
    elapsed_time = datetime.timedelta(seconds=elapsed_time_seconds)
    estimated_time = chop_microseconds(elapsed_time * num_generated_profiles) if num_generated_profiles else None

    logger.info("Selected: ({:2n}): Target Error: {:.3f}%: Time/Profile: {:5.2f} sec => Est. calc. time: {}".
                format(i,
                       target_error,
                       elapsed_time.total_seconds(),
                       estimated_time))
    if not settings.skip_questions:
        if estimated_time and estimated_time.total_seconds() > 43200:  # 12h
            if input("Warning: This might take a *VERY* long time ({}) (q to quit, Enter to continue: )".format(estimated_time)) == "q":
                printLog("Quitting application")
                sys.exit(0)

    # split into chunks of n (max 100) to not destroy the hdd
    # todo: calculate dynamic amount of n
    splitter.split(outputFileName, settings.splitting_size, player_profile.wow_class)
    splitter.sim(settings.subdir1, "target_error=" + str(target_error), player_profile, 1)

    # if the user chose a target_error which is lower than the default_one for the next step
    # he is given an option to either skip stage 2 or adjust the target_error
    stage_next_target_error = float(settings.default_target_error_stage2)
    if target_error <= stage_next_target_error:
        print("Warning Target_Error chosen in stage {}: {} <= Default_Target_Error for stage {}: {}".
              format(stage, target_error, stage+1, stage_next_target_error))
        new_value = input(
            "Do you want to continue anyway (y), quit (q), skip to stage3 (s) or enter a new target_error"
            " for stage2 (n)?: ")
        printLog("User chose: " + str(new_value))
        if new_value == "q":
            printLog("Quitting application")
            sys.exit(0)
        if new_value == "n":
            stage_next_target_error = float(input("Enter new target_error (Format: 0.3): "))
            printLog("User entered target_error_secondpart: " + str(stage_next_target_error))
        if new_value == "s":
            dynamic_stage3(True, settings.default_target_error_stage3, target_error, player_profile)
            return
    dynamic_stage2(stage_next_target_error, target_error, player_profile)


def dynamic_stage2(targeterror, targeterrorstage1, player_profile):
    printLog("Entering dynamic mode, stage2")
    checkResultFiles(settings.subdir1, player_profile)
    if settings.default_use_alternate_grabbing_method:
        splitter.grab_best("target_error", targeterrorstage1, settings.subdir1, settings.subdir2, outputFileName)
    else:
        # grabbing top 100 files
        splitter.grab_best("count", settings.default_top_n_stage2, settings.subdir1, settings.subdir2, outputFileName)
    # where they are simmed again, now with higher quality
    splitter.sim(settings.subdir2, "target_error=" + str(targeterror), player_profile, 1)
    # if the user chose a target_error which is lower than the default_one for the next step
    # he is given an option to either skip stage 2 or adjust the target_error
    if float(target_error_secondpart) <= float(settings.default_target_error_stage3):
        printLog("Target_Error chosen in stage 2: " + str(
            targeterror) + " <= Default_Target_Error stage 3: " + str(
            settings.default_target_error_stage3))
        print("Warning!\n")
        printLog("Target_Error chosen in stage 2: " + str(
            targeterror) + " <= Default_Target_Error stage 3: " + str(
            settings.default_target_error_stage3))
        new_value = input(
            "Do you want to continue (y), quit (q) or enter a new target_error for stage3 (n)?: ")
        printLog("User chose: " + str(new_value))
        if new_value == "q":
            sys.exit(0)
        if new_value == "n":
            target_error_thirdpart = input("Enter new target_error (Format: 0.3): ")
            printLog("User entered target_error_thirdpart: " + str(target_error_thirdpart))
            dynamic_stage3(False, target_error_thirdpart, targeterror, player_profile)
        if new_value == "y":
            dynamic_stage3(False, settings.default_target_error_stage3, targeterror, player_profile)
    else:
        dynamic_stage3(False, settings.default_target_error_stage3, targeterror, player_profile)


def dynamic_stage3(skipped, targeterror, targeterrorstage2, player_profile):
    printLog("Entering dynamic mode, stage3")
    ok = False
    if skipped:
        ok = checkResultFiles(settings.subdir1, player_profile)
    else:
        ok = checkResultFiles(settings.subdir2, player_profile)
    if ok:
        printLog(".result-files ok, proceeding")
        # again, for a third time, get top 3 profiles and put them into subdir3
        if skipped:
            if settings.default_use_alternate_grabbing_method:
                splitter.grab_best("target_error", targeterrorstage2, settings.subdir1, settings.subdir3, outputFileName)
            else:
                splitter.grab_best("count", settings.default_top_n_stage3, settings.subdir1, settings.subdir3, outputFileName)
        else:
            if settings.default_use_alternate_grabbing_method:
                splitter.grab_best("target_error", targeterrorstage2, settings.subdir2, settings.subdir3, outputFileName)
            else:
                splitter.grab_best("count", settings.default_top_n_stage3, settings.subdir2, settings.subdir3, outputFileName)
        # sim them finally with all options enabled; html-output remains in subdir3, check cleanup for moving to results
        splitter.sim(settings.subdir3, "target_error=" + str(targeterror), player_profile, 2)
    else:
        printLog("No valid .result-files found for stage3!")


def stage1(player_profile, num_generated_profiles):
    printLog("Entering Stage1")
    print("You have to choose one of the following modes for calculation:")
    print("1) Static mode uses a fixed amount, but less accurate calculations per profile (" + str(
        iterations_firstpart) + "," + str(iterations_secondpart) + "," + str(iterations_thirdpart) + ")")
    print("   It is however faster if simulating huge amounts of profiles")
    print(
        "2) Dynamic mode (preferred) lets you choose a specific 'correctness' of the calculation, but takes more time.")
    print(
        "   It uses the chosen target_error for the first part; in stage2 error lowers to " + str(
            target_error_secondpart) + " and " + str(
            target_error_thirdpart) + " for the final top " + str(settings.default_top_n_stage3))
    if settings.skip_questions:
        sim_mode = str(settings.auto_choose_static_or_dynamic)
    else:
        sim_mode = input("Please choose your mode (Enter to exit): ")
    if sim_mode == "1":
        static_stage(player_profile, 1)
    elif sim_mode == "2":
        dynamic_stage1(player_profile, num_generated_profiles)
    else:
        print("Error, wrong mode: Stage1")
        printLog("Error, wrong mode: Stage1")
        sys.exit(0)


def stage_restart(player_profile, stage):
    if stage > 3 or stage < 1:
        raise ValueError("No stage {} available to restart.".format(stage))
    logging.info("\nRestarting STAGE{}".format(stage))
    if not checkResultFiles(settings_subdir[stage - 1], player_profile):
        raise RuntimeError("Error restarting stage {}. Some result-files are empty in {}".
                           format(stage, settings_subdir[stage - 1]))
    if settings.skip_questions:
        mode_choice = str(settings.auto_choose_static_or_dynamic)
    else:
        mode_choice = input("What mode did you use: Static (1) or dynamic (2): ")
        mode_choice = int(mode_choice)
    valid_modes = [1, 2]
    if mode_choice not in valid_modes:
        raise RuntimeError("Invalid mode '{}' selected. Valid modes: {}.".format(mode_choice,
                                                                                 valid_modes))
    if mode_choice == 1:
        static_stage(player_profile, stage)
    elif mode_choice == 2:
        if stage == 3:
            if input("Did you skip stage 2? (y,n)") == "y":
                skip = True
            else:
                skip = False
        new_te = settings_target_error[stage]
        if not settings.skip_questions:
            user_te = input("Specify target error for stage{}: (Press enter for default: {}):".format(stage,
                                                                                                      new_te))
            if len(user_te):
                new_te = float(user_te)
            logging.info("User selected target_error={} for stage{}.".format(new_te, stage))
        if stage == 2:
            dynamic_stage2(new_te, splitter.user_targeterror, player_profile)
        elif stage == 3:
            dynamic_stage3(skip, new_te, splitter.user_targeterror, player_profile)


def check_interpreter():
    """Check interpreter for minimum requirements."""
    # Does not really work in practice, since formatted string literals (3.6) lead to SyntaxError prior to execution of
    # the program with older interpreters.
    required_major, required_minor = (3, 6)
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

    error_handler = logging.FileHandler(errorFileName)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)s %(message)s"))

    # Handler to log messages to file
    log_handler = logging.FileHandler(logFileName)
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
    if args.quiet:
        stdout_handler.setLevel(logging.WARNING)
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
    if args.sim == "all" or args.sim is None:
        start = datetime.datetime.now()
        num_generated_profiles = permutate(args, player_profile)
        logging.info("Permutating took {}.".format(datetime.datetime.now() - start))
        outputGenerated = True
    else:
        if input("Do you want to generate {} again? Press y to regenerate: ".format(args.outputfile)) == "y":
            num_generated_profiles = permutate(args, player_profile)
            outputGenerated = True
        else:
            outputGenerated = False
            num_generated_profiles = None

    if outputGenerated:
        if num_generated_profiles == 0:
            raise ValueError("No valid combinations found. Please check settings.py and your simpermut-export.")

    if args.sim:
        if not settings.skip_questions:
            if num_generated_profiles and num_generated_profiles > 50000:
                if input(
                        "-----> Beware: Computation with Simcraft might take a VERY long time with this amount of profiles!"
                        " <----- (Press Enter to continue, q to quit)") == "q":
                    logging.info("Program exit by user")
                    sys.exit(0)

        print("Simulation in progress...")

        if args.sim == "stage1" or args.sim == "all":
            stage1(player_profile, num_generated_profiles)
        if args.sim == "stage2":
            stage_restart(player_profile, 2)
        if args.sim == "stage3":
            stage_restart(player_profile, 3)

    if settings.clean_up_after_step3:
        cleanup()
    print("Finished.")


if __name__ == "__main__":
    try:
        main()
        logging.shutdown()
    except Exception as e:
        logging.error("Error: {}".format(e), exc_info=True)
        sys.exit(1)
