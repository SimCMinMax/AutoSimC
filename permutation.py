import copy
from dataclasses import dataclass
import functools
import itertools
import logging
import math
import operator
from profile import Profile, EquipmentLoadout
from typing import Iterator

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

from i18n import _
from item import GearType
from utils import stable_unique

T27_MIN = int(settings.default_equip_t27_min)
T27_MAX = int(settings.default_equip_t27_max)


def get_gem_combinations(gems_to_use, num_gem_slots):
    if num_gem_slots <= 0:
        return []
    combinations = itertools.combinations_with_replacement(gems_to_use, r=num_gem_slots)
    return list(combinations)


@dataclass
class PermutedCharacter:
    loadout: EquipmentLoadout
    talents: str

    @property
    def simc_input(self) -> str:
        return f'''\
talents={self.talents}
{self.loadout.simc_input}
'''


def max_permutation_count(profile: Profile) -> int:
    """
    The maximum number of profiles that generate_permutations can built.
    
    This does not exclude infeasible configurations.
    """
    # Get number of combinations of simple gear
    o = functools.reduce(operator.mul,
                         (max(1, len(v)) for k, v in profile.all_gear().items()
                          if k not in (GearType.FINGER, GearType.TRINKET)), 1)

    # calculate others
    rings = len(profile.gear[GearType.FINGER])
    trinkets = len(profile.gear[GearType.TRINKET])
    
    # Number of results for itertools.combinations.
    # math.factorial(2) = 2; so it is inlined here.
    if rings > 2:
        o *= int(math.factorial(rings) / 2 / math.factorial(rings - 2))
    if trinkets > 2:
        o *= int(math.factorial(trinkets) / 2 / math.factorial(trinkets - 2))

    o *= max(1, len(profile.talents))
    return o


def generate_permutations(profile: Profile) -> Iterator[PermutedCharacter]:
    """Generate PermutedLoadouts for a profile."""
    parsed_gear = profile.all_gear()
    logging.debug(_("Parsed gear: {}").format(parsed_gear))
    # TODO: handle gems, handle Shards of Domination

    # Filter each slot to only have unique items, before doing any gem permutation.
    for key, value in parsed_gear.items():
        parsed_gear[key] = stable_unique(value)

    simple_permutation_gear = {
        k: v for k, v in parsed_gear.items()
        if k not in (GearType.FINGER, GearType.TRINKET)}
    simple_permutations = itertools.product(*simple_permutation_gear.values())

    # Get every ring pairing.
    if len(parsed_gear[GearType.FINGER]) > 2:
        rings = list(itertools.combinations(parsed_gear[GearType.FINGER], 2))
    else:
        rings = (parsed_gear[GearType.FINGER],)
    logging.debug(f'Rings: {rings}')

    # Get every trinket pairing.
    if len(parsed_gear[GearType.TRINKET]) > 2:
        trinkets = list(itertools.combinations(parsed_gear[GearType.TRINKET], 2))
    else:
        trinkets = (parsed_gear[GearType.TRINKET],)
    logging.debug(f'Trinkets: {trinkets}')

    for permutation in simple_permutations:
        # Build a base EquipmentLoadout
        base_loadout = EquipmentLoadout()
        for item in permutation:
            base_loadout.equip(item)

        # Check if the base loadout is a valid loadout
        # (this will let us skip a bunch of processing later!)
        if not base_loadout.valid_loadout() or not base_loadout.valid_weapons(profile.player_class, profile.spec):
            continue

        for ring_permutation in rings:
            ring_loadout = copy.copy(base_loadout)
            for ring in ring_permutation:
                ring_loadout.equip(ring)
            if not ring_loadout.valid_loadout():
                continue

            for trinket_permutation in trinkets:
                # Build a Loadout
                loadout = copy.copy(ring_loadout)
                for trinket in trinket_permutation:
                    loadout.equip(trinket)

                # Check if this is a valid loadout
                if not base_loadout.valid_loadout():
                    continue

                for talent in profile.talents:
                    yield PermutedCharacter(loadout, talent)
