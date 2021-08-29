import logging
from enum import Enum, auto

from item import SIMPLE_GEAR_SLOTS, COMPLEX_GEAR_SLOTS, canonical_slot_name, Item
from profile import Profile, ALL_OPTIONS
from specdata import ALL_CLASSES


class Mode(Enum):
    DEFAULT = auto()
    GEAR_FROM_BAGS = auto()
    WEEKLY_REWARD = auto()


def build_profile_simc_addon(args) -> Profile:
    player_profile = Profile()

    # no sections available, so parse each line individually
    input_encoding = 'utf-8'
    try:
        with open(args.inputfile, "r", encoding=input_encoding) as f:
            player_profile.args = args
            # idea: in default-mode all #-lines are being ignored
            # once a ###-line is parsed, all following #-lines are assigned to the corresponding usage
            active_mode = Mode.DEFAULT

            for line in f:
                line = line.strip()
                if line == "":
                    continue

                if line.startswith("#"):
                    if line.startswith("### Gear from Bags"):
                        active_mode = Mode.GEAR_FROM_BAGS
                        continue
                    if line.startswith("### Weekly Reward Choices"):
                        active_mode = Mode.WEEKLY_REWARD
                        continue

                    # parse #-lines
                    if '=' in line[1:]:
                        key, value = line[1:].split('=', 1)
                        key = key.replace('\n', '').strip()
                        value = value.replace('\n', '').strip()

                        if key in SIMPLE_GEAR_SLOTS or key in COMPLEX_GEAR_SLOTS:
                            slot = canonical_slot_name(key)
                            item = Item(slot, active_mode == Mode.WEEKLY_REWARD, value)
                            if active_mode == Mode.GEAR_FROM_BAGS:
                                player_profile.simc_options.gear_in_bags[slot].append(item)
                            elif active_mode == Mode.WEEKLY_REWARD:
                                player_profile.simc_options.weekly_rewards[slot].append(item)
                else:
                    # parse active gear etc.
                    key, value = line.split('=', 1)
                    key = key.replace('\n', '').strip()
                    value = value.replace('\n', '').strip()

                    if key in ALL_CLASSES:
                        player_profile.wow_class = key
                        player_profile.profile_name = value
                    elif key in ALL_OPTIONS:
                        setattr(player_profile.simc_options, key, value)
                    elif key in SIMPLE_GEAR_SLOTS or key in COMPLEX_GEAR_SLOTS:
                        slot = canonical_slot_name(key)
                        for item_str in value.split('|'):
                            item = Item(slot, False, item_str)
                            player_profile.simc_options.gear[slot].append(item)
    except UnicodeDecodeError as e:
        raise RuntimeError("""AutoSimC could not decode your input file '{file}' with encoding '{enc}'.
        Please make sure that your text editor encodes the file as '{enc}',
        or as a quick fix remove any special characters from your character name.""".format(file=args.inputfile,
                                                                                            enc=input_encoding)) from e

    # Build 'general' profile options which do not permutate once into a simc-string
    logging.info(f'SimC options: {player_profile.simc_options}')
    logging.debug(f'Built simc general options string: {player_profile.general_options}')
    return player_profile
