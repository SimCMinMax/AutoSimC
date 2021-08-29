from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from item import SIMPLE_GEAR_SLOTS, Item
from specdata import getClassSpec, getRole

# Options which we don't permute
_GENERAL_OPTIONS = frozenset({
    'covenant',
    'flask',
    'food',
    'level',
    'position',
    'potion',
    'professions',
    'race',
    'region',
    'renown',
    'role',
    'server',
    'soulbind',
    'spec',
})

# All possbile options
ALL_OPTIONS = frozenset({
    'talents',
}) | _GENERAL_OPTIONS

@dataclass()
class SimcOptions:
    """Options to simulationcraft"""
    covenant: str = ''
    flask: str = ''
    food: str = ''
    level: str = ''
    position: str = ''
    potion: str = ''
    professions: str = ''
    race: str = ''
    region: str = ''
    renown: str = ''
    role: str = ''
    server: str = ''
    soulbind: str = ''
    spec: str = ''
    talents: str = ''

    gear: Dict[str, List[Item]] = field(default_factory=lambda: defaultdict(list))
    gear_in_bags: Dict[str, List[Item]] = field(default_factory=lambda: defaultdict(list))
    weekly_rewards: Dict[str, List[Item]] = field(default_factory=lambda: defaultdict(list))

    def all_gear(self) -> Dict[str, Sequence[Item]]:
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
    fightstyle: Optional[Dict[str, str]] = None

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
