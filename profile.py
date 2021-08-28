from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from item import SIMPLE_GEAR_SLOTS, Item
from specdata import getClassSpec, getRole


_GENERAL_OPTIONS = [
    'renown',
    'covenant',
    'soulbind',
    'race',
    'level',
    'server',
    'region',
    'professions',
    'spec',
    'role',
    'talents',
    'position',
    'flask',
    'food',
]

@dataclass()
class SimcOptions:
    """Options to simulationcraft"""
    renown: str = ''
    covenant: str = ''
    soulbind: str = ''
    race: str = ''
    level: str = ''
    server: str = ''
    region: str = ''
    professions: str = ''
    spec: str = ''
    role: str = ''
    talents: str = ''
    position: str = ''
    flask: str = ''
    food: str = ''

    gear: Dict[str, List[Item]] = field(default_factory=lambda: defaultdict(list))
    gear_in_bags: Dict[str, List[Item]] = field(default_factory=lambda: defaultdict(list))
    weekly_rewards: Dict[str, List[Item]] = field(default_factory=lambda: defaultdict(list))

    def all_gear(self) -> Dict[str, List[Item]]:
        """Get a list of all possible gear, regardless of feasibility."""
        o = {}
        for k in SIMPLE_GEAR_SLOTS:
            o[k] = self.gear[k] + self.gear_in_bags[k] + self.weekly_rewards[k]

        # create a dummy-item so no_offhand-combinations are not being dismissed later in the product-function
        o['off_hand'].append(Item('off-hand', False, ',id=-1'))

        for k in SIMPLE_GEAR_SLOTS:
            if not o[k]:
                # We havent found any items for that slot, add empty dummy item
                o[k] = [Item(k, False, '')]
        return o


@dataclass()
class Profile:
    """Represent global profile data"""
    simc_options: SimcOptions = field(default_factory=SimcOptions)
    wow_class: str = ''
    profile_name: str = ''

    @property
    def class_spec(self) -> str:
        return getClassSpec(self.wow_class, self.simc_options.spec)

    @property
    def class_role(self) -> str:
        return getRole(self.wow_class, self.simc_options.spec)

    @property
    def general_options(self) -> str:
        o = []
        for k in _GENERAL_OPTIONS:
            v = getattr(self.simc_options, k)
            if v != '':
                o.append(f'{k}={v}')
        return '\n'.join(o)
