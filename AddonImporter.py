import logging
from enum import Enum, auto

class Mode(Enum):
    DEFAULT = auto()
    GEAR_FROM_BAGS = auto()
    WEEKLY_REWARD = auto()

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
# Parse general profile options
simc_profile_options = ["race",
                        "level",
                        "server",
                        "region",
                        "professions",
                        "spec",
                        "role",
                        "talents",
                        "position",
                        "covenant",
                        "soulbind",
                        "renown",
                        "potion",
                        "flask",
                        "food"]

def build_profile_simc_addon(args, gear_slots, profile, specdata, weapondata):
    # will contain any gear in file for each slot, divided by |
    gear = {}
    for slot in gear_slots:
        gear[slot[0]] = []
    gearInBags = {}
    for slot in gear_slots:
        gearInBags[slot[0]] = []
    weeklyRewards = {}
    for reward in weeklyRewards:
        weeklyRewards[slot[0]] = []

    # no sections available, so parse each line individually
    input_encoding = 'utf-8'
    c_class = ""
    try:
        with open(args.inputfile, "r", encoding=input_encoding) as f:
            player_profile = profile
            player_profile.args = args
            player_profile.simc_options = {}
            # idea: in default-mode all #-lines are being ignored
            # once a ###-line is parsed, all following #-lines are assigned to the corresponding usage
            active_mode = Mode.DEFAULT

            for line in f:
                if line == "\n":
                    continue
                # Shadowlands
                if line.startswith("renown"):
                    splitted = line.split("=", 1)[1].rstrip().lstrip()
                    player_profile.simc_options["renown"] = splitted
                if line.startswith("covenant"):
                    splitted = line.split("=", 1)[1].rstrip().lstrip()
                    player_profile.simc_options["covenant"] = splitted
                if line.startswith("soulbind"):
                    splitted = line.split("=", 1)[1].rstrip().lstrip()
                    player_profile.simc_options["soulbind"] = splitted

                if line.startswith("#"):
                    if line.startswith("### Gear from Bags"):
                        # gear-in-bag handling
                        active_mode = Mode.GEAR_FROM_BAGS
                        continue
                    if line.startswith("### Weekly Reward Choices"):
                        active_mode = Mode.WEEKLY_REWARD
                        continue

                    # parse #-lines
                    splittedLine = line.replace("#", "").replace("\n", "").lstrip().rstrip().split("=", 1)
                    for gearslot in gear_slots:
                        if splittedLine[0].replace("\n", "") == gearslot[0]:
                            if active_mode is Mode.GEAR_FROM_BAGS:
                                gearInBags[splittedLine[0].replace("\n", "")].append(
                                    splittedLine[1].replace("\n", "").lstrip().rstrip())
                            if active_mode is Mode.WEEKLY_REWARD:
                                weeklyRewards[splittedLine[0].replace("\n", "")].append(
                                    splittedLine[1].replace("\n", "").lstrip().rstrip())
                        # trinket and finger-handling
                        trinketOrRing = splittedLine[0].replace("\n", "").replace("1", "").replace("2", "")
                        if (trinketOrRing == "finger" or trinketOrRing == "trinket") and trinketOrRing == gearslot[
                            0]:
                            if active_mode is Mode.GEAR_FROM_BAGS:
                                gearInBags[splittedLine[0].replace("\n", "").replace("1", "").replace("2", "")].append(
                                    splittedLine[1].lstrip().rstrip())
                            if active_mode is Mode.WEEKLY_REWARD:
                                weeklyRewards[splittedLine[0].replace("\n", "").replace("1", "").replace("2", "")].append(
                                    splittedLine[1].lstrip().rstrip())
                else:
                    # parse active gear etc.
                    splittedLine = line.split("=", 1)
                    if splittedLine[0].replace("\n", "") in valid_classes:
                        c_class = splittedLine[0].replace("\n", "").lstrip().rstrip()
                        player_profile.wow_class = c_class
                        player_profile.profile_name = splittedLine[1].replace("\n", "").lstrip().rstrip()
                    if splittedLine[0].replace("\n", "") in simc_profile_options:
                        player_profile.simc_options[splittedLine[0].replace("\n", "")] = splittedLine[1].replace("\n",
                                                                                                                 "").lstrip().rstrip()
                    for gearslot in gear_slots:
                        if splittedLine[0].replace("\n", "") == gearslot[0]:
                            gear[splittedLine[0].replace("\n", "")].append(
                                splittedLine[1].replace("\n", "").lstrip().rstrip())
                        # trinket and finger-handling
                        trinketOrRing = splittedLine[0].replace("\n", "").replace("1", "").replace("2", "")
                        if (trinketOrRing == "finger" or trinketOrRing == "trinket") and trinketOrRing == gearslot[0]:
                            gear[splittedLine[0].replace("\n", "").replace("1", "").replace("2", "")].append(
                                splittedLine[1].lstrip().rstrip())

    except UnicodeDecodeError as e:
        raise RuntimeError("""AutoSimC could not decode your input file '{file}' with encoding '{enc}'.
        Please make sure that your text editor encodes the file as '{enc}',
        or as a quick fix remove any special characters from your character name.""".format(file=args.inputfile,
                                                                                            enc=input_encoding)) from e
    if c_class != "":
        player_profile.class_spec = specdata.getClassSpec(c_class, player_profile.simc_options["spec"])
        player_profile.class_role = specdata.getRole(c_class, player_profile.simc_options["spec"])

    # Build 'general' profile options which do not permutate once into a simc-string
    logging.info("SimC options: {}".format(player_profile.simc_options))
    player_profile.general_options = "\n".join(["{}={}".format(key, value) for key, value in
                                                player_profile.simc_options.items()])
    logging.debug("Built simc general options string: {}".format(player_profile.general_options))

    # Parse gear
    player_profile.simc_options["gear"] = gear
    player_profile.simc_options["gearInBag"] = gearInBags
    player_profile.simc_options["weeklyRewards"] = weeklyRewards

    return player_profile