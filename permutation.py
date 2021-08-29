import copy
from dataclasses import dataclass
import itertools
import logging 
from profile import Profile
from typing import Dict, Sequence

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

from item import Item
from utils import stable_unique

SHADOWLANDS_LEGENDARY_IDS = [
    # Plate
    171412,
    171413,
    171414,
    171415,
    171416,
    171417,
    171418,
    171419,
    # Leather
    172314,
    172315,
    172316,
    172317,
    172318,
    172319,
    172320,
    172321,
    # Mail
    172322,
    172323,
    172324,
    172325,
    172326,
    172327,
    172328,
    172329,
    # Cloth
    173241,
    173242,
    173243,
    173244,
    173245,
    173246,
    173247,
    173248,
    173249,
    # Ring, neck
    178926,
    178927,
]

T27_MIN = int(settings.default_equip_t27_min)
T27_MAX = int(settings.default_equip_t27_max)


def get_gem_combinations(gems_to_use, num_gem_slots):
    if num_gem_slots <= 0:
        return []
    combinations = itertools.combinations_with_replacement(gems_to_use, r=num_gem_slots)
    return list(combinations)


@dataclass
class PermutationData:
    """Data for each permutation"""
    items: Dict[str, Item]
    profile: Profile
    max_profile_chars: int
    talents: str = ''

    def permute_gems(self, gem_list) -> Sequence[Dict[str, Item]]:
        gems_on_gear = []
        gear_with_gems = {}
        for slot, gear in self.items.items():
            gems_on_gear += gear.gem_ids
            gear_with_gems[slot] = len(gear.gem_ids)

        # logging.debug("gems on gear: {}".format(gems_on_gear))
        if len(gems_on_gear) == 0:
            return (self.items,)

        # Combine existing gems of the item with the gems supplied by --gems
        combined_gem_list = gems_on_gear
        combined_gem_list += gem_list
        combined_gem_list = stable_unique(combined_gem_list)
        # logging.debug("Combined gem list: {}".format(combined_gem_list))
        new_gems = get_gem_combinations(combined_gem_list, len(gems_on_gear))
        # logging.debug("New Gems: {}".format(new_gems))
        new_combinations = []
        for gems in new_gems:
            new_items = copy.deepcopy(self.items)
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

    @property
    def weekly_rewards(self) -> Sequence[Item]:
        return [i for i in self.items.values() if i.isWeeklyReward]

    @property
    def t27_items(self) -> Sequence[Item]:
        return [i for i in self.items.values() if i.tier_27]

    @property
    def legendaries(self) -> Sequence[Item]:
        return [i for i in self.items.values() if i.item_id in SHADOWLANDS_LEGENDARY_IDS]

    @property
    def is_usable_before_talents(self) -> bool:
        return (
            len(self.legendaries) <= 1 and
            len(self.weekly_rewards) <= 1 and
            len(self.t27_items) >= T27_MIN and
            len(self.t27_items) <= T27_MAX
        )

    def get_profile_id(self, profile_number: int) -> str:
        return str(profile_number).rjust(self.max_profile_chars, "0")

    @property
    def equipped_items(self) -> str:
        return "\n".join(i.output_str for i in self.items.values()
                         if i.item_id > 0)

    def simc_input(self, profile_number: int, additional_options: str) -> str:
        profile_id = self.get_profile_id(profile_number)
        char_name = self.profile.profile_name.replace('"', '')
        return f'''\
{self.profile.wow_class}={char_name}_{profile_id}
{self.profile.general_options}
talents={self.talents}
{self.equipped_items}
{additional_options}\n\n'''


def permute_talents(talents_list: str) -> Sequence[str]:
    """Given a list of talent configurations, expand to all possible options."""
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
