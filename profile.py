from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import itertools
import logging
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple, cast

from item import Item, GearType, SHADOWLANDS_LEGENDARY_IDS, WeaponType, get_weapon_type
from specdata import ALL_CLASSES, getClassSpec, getRole
from utils import stable_unique

class _SimcReaderState(Enum):
    NONE = 0
    GEAR_FROM_BAGS = 1
    WEEKLY_REWARD = 2


# Options which we don't permute
_GENERAL_OPTIONS = frozenset({
    'augmentation',
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
    'temporary_enchant',
})

# All possbile options
ALL_OPTIONS = frozenset({
    'talents',
}) | _GENERAL_OPTIONS


# Slots which are part of EquipmentLayout.
_LOADOUT_SLOTS = (
    'head',
    'neck',
    'shoulder',
    'back',
    'chest',
    'shirt',
    'tabard',
    'wrist',
    'hands',
    'waist',
    'legs',
    'feet',
    'main_hand',
    'off_hand',
    'finger1',
    'finger2',
    'trinket1',
    'trinket2',
)

@dataclass
class EquipmentLoadout:
    head: Optional[Item] = None
    neck: Optional[Item] = None
    shoulder: Optional[Item] = None
    back: Optional[Item] = None
    chest: Optional[Item] = None
    shirt: Optional[Item] = None
    tabard: Optional[Item] = None
    wrist: Optional[Item] = None
    hands: Optional[Item] = None
    waist: Optional[Item] = None
    legs: Optional[Item] = None
    feet: Optional[Item] = None
    
    main_hand: Optional[Item] = None
    off_hand: Optional[Item] = None

    finger1: Optional[Item] = None
    finger2: Optional[Item] = None
    trinket1: Optional[Item] = None
    trinket2: Optional[Item] = None

    def equip(self, item: Item):
        """Add a an item to the character's equipment load-out."""
        # Finger and trinket are special. Always fill slot 1 first,
        # and if there is something there, make whichever is "greater"
        # occupy slot 1, and move the other to slot 2.
        #
        # This makes loadouts deterministic.
        if item.slot == GearType.UNKNOWN:
            raise ValueError(f'Cannot equip gear with no slot')
        elif item.slot == GearType.FINGER:
            if self.finger1 is None:
                self.finger1 = item
            elif self.finger2 is None:
                if self.finger1 < item:
                    self.finger2 = self.finger1
                    self.finger1 = item
                else:
                    self.finger2 = item
            else:
                raise ValueError(f'Cannot equip {item}, both finger slots have gear equipped')
        elif item.slot == GearType.TRINKET:
            if self.trinket1 is None:
                self.trinket1 = item
            elif self.trinket2 is None:
                if self.trinket1 < item:
                    self.trinket2 = self.trinket1
                    self.trinket1 = item
                else:
                    self.trinket2 = item
            else:
                raise ValueError(f'Cannot equip {item}, both trinket slots have gear equipped')
        else:
            # Other slots
            c = getattr(self, item.slot.name.lower())  # type: Optional[Item]
            if c is None:
                setattr(self, item.slot.name.lower(), item)
            else:
                raise ValueError(f'Cannot equip {item}, {item.slot.name} already has {c} equipped')

    def try_equip(self, item: Item):
        try:
            self.equip(item)
        except ValueError:
            pass

    def all_items_include_empty(self) -> Iterator[Tuple[str, Optional[Item]]]:
        """Returns a generator of all slots, and what item may be equipped."""
        for s in _LOADOUT_SLOTS:
            i = getattr(self, s)
            yield s, cast(Optional[Item], i)

    def all_items(self) -> Iterator[Tuple[str, Item]]:
        """Returns a generator of only slots with items equipped."""
        for s, i in self.all_items_include_empty():
            if i is not None:
                yield s, i 

    def weekly_rewards(self):
        """Returns all items which are part of the weekly rewards vault."""
        return [i for _s, i in self.all_items() if i.isWeeklyReward]

    def shadowlands_legendaries(self):
        """Returns all Shadowlands Legendaries (runecarver)."""
        return [i for _s, i in self.all_items() if i.item_id in SHADOWLANDS_LEGENDARY_IDS]

    def valid_weapons(self, c_class: str, c_spec: str) -> bool:
        # Apply weapon rules
        main_hand_type = get_weapon_type(self.main_hand)
        off_hand_type = get_weapon_type(self.off_hand)

        if main_hand_type in (WeaponType.SHIELD, WeaponType.OFFHAND, WeaponType.OFFHAND_SPECIAL_WEAPON, WeaponType.OFFHAND_WEAPON):
            # Off-hands can't be in main hand.
            return False
        elif main_hand_type in (WeaponType.BOW, WeaponType.GUN):
            # Only hunters, rogues and warriors can use bows and guns.
            if c_class not in ('hunter', 'rogue', 'warrior'):
                return False
            return off_hand_type is None
        elif main_hand_type == WeaponType.TWOHAND:
            if off_hand_type is None:
                # Nothing in off-hand slot is OK.
                return True
            elif c_class != 'warrior' or c_spec != 'fury':
                # Only Fury Warriors can equip something else OH for 2H
                return False
            elif off_hand_type in (WeaponType.OFFHAND, WeaponType.SHIELD, WeaponType.OFFHAND_SPECIAL_WEAPON, WeaponType.OFFHAND_WEAPON):
                # Can't equip a offhand or shield with 2H
                return False
            return True

        # No opinion on the loadout, probably fine?
        return True

    def valid_loadout(self) -> bool:
        if len(self.weekly_rewards()) > 1 or len(self.shadowlands_legendaries()) > 1:
            # Can't pick more than one thing from the Vault, or equip more than 1 SL legendary.
            return False
        if self.trinket1 is not None and self.trinket1 is self.trinket2:
            # Can't equip the same trinket twice
            return False
        if self.finger1 is not None and self.finger1 is self.finger2:
            # Can't equip the same ring twice
            return False

        return True

    @property
    def simc_input(self) -> str:
        return '\n'.join(
            f'{s}={i.output_str}' for s, i in self.all_items()
            if i.item_id > 0)

    def diff(self, other: 'EquipmentLoadout') -> 'Optional[Tuple[EquipmentLoadout, EquipmentLoadout]]':
        """Generate list of equipment that differs between each."""
        if not isinstance(other, EquipmentLoadout):
            raise TypeError(f'Cannot diff {type(other)} with EquipmentLoadout')
        a_only = EquipmentLoadout()
        b_only = EquipmentLoadout()
        any_diff = False
        for a, b in zip(self.all_items_include_empty(), other.all_items_include_empty()):
            a_slot, a_item = a
            b_slot, b_item = b
            if a_slot != b_slot:
                raise ValueError('Unexpected slot mismatch')
            if a_item != b_item:
                setattr(a_only, a_slot, a_item)
                setattr(b_only, b_slot, b_item)
                any_diff = True
        if any_diff:
            return a_only, b_only


@dataclass
class Profile:
    """Profile of options to simulationcraft"""
    player_class: str = ''
    profile_name: str = ''
    fightstyle: Optional[Dict[str, str]] = None

    augmentation: str = ''
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
    talents: List[str] = field(default_factory=list)
    temporary_enchant: str = ''

    baseline: EquipmentLoadout = field(default_factory=EquipmentLoadout)

    gear: Dict[GearType, List[Item]] = field(default_factory=lambda: defaultdict(list))

    def all_gear(self) -> Dict[GearType, Sequence[Item]]:
        """Get a list of all possible gear, regardless of feasibility."""
        o = {}
        for k in GearType.all_slots():
            o[k] = self.gear[k]

        # create a dummy-item so no_offhand-combinations are not being dismissed later in the product-function
        o[GearType.OFF_HAND].append(Item(GearType.OFF_HAND, False, ',id=-1'))

        for k in GearType.all_slots():
            if not o[k]:
                # We havent found any items for that slot, add empty dummy item
                o[k] = [Item(k, False, '')]
        return o

    def load_simc(self, f: Iterable[str]):
        """Loads input from simc addon."""
        reader_state = _SimcReaderState.NONE

        for line in f:
            line = line.strip()
            commented = False
            if not line:
                continue

            if line.startswith('##'):
                # Special comments
                line = line.lower()
                if 'gear from bags' in line:
                    reader_state = _SimcReaderState.GEAR_FROM_BAGS
                elif 'weekly reward choices' in line:
                    reader_state = _SimcReaderState.WEEKLY_REWARD
                continue
            
            if line.startswith('#'):
                if reader_state == _SimcReaderState.NONE:
                    continue
                # Commented line, but triggered special state
                line = line[1:].strip()
                commented = True
            if '=' not in line:
                continue

            key, value = (t.strip() for t in line.split('=', 1))
            slot = GearType.from_simc(key)

            if slot:
                for item_str in value.split('|'):
                    item = Item(slot, reader_state == _SimcReaderState.WEEKLY_REWARD, item_str)
                    self.gear[slot].append(item)
                    if not commented:
                        # Try to equip the first uncommented item in each slot as the "baseline".
                        self.baseline.try_equip(item)
            elif not commented:
                if key in ALL_CLASSES:
                    self.player_class = key
                    self.profile_name = value.strip('"')
                elif key in _GENERAL_OPTIONS:
                    setattr(self, key, value)
                elif key == 'talents':
                    self.talents = _permute_talents(value)

    @property
    def class_spec(self) -> str:
        return getClassSpec(self.player_class, self.spec)

    @property
    def class_role(self) -> str:
        return getRole(self.player_class, self.spec)

    @property
    def general_options(self) -> str:
        o = []
        for k in _GENERAL_OPTIONS:
            v = getattr(self, k)
            if v != '':
                o.append(f'{k}={v}')
        return '\n'.join(o)


def _permute_talents(talents_list: str) -> List[str]:
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


def load_multiple_profiles(f: Iterable[str]) -> Iterator[Profile]:
    """Try to load a simc file that contains many profiles."""
    current_actor = []
    for l in f:
        t = l.split('=')
        if t[0].strip() in ALL_CLASSES:
            # start a new character
            if current_actor:
                p = Profile()
                p.load_simc(current_actor)

                # Check if that actually loaded something
                if p.player_class:
                    current_actor = []
                    yield p
        current_actor.append(l)

    # Yield any remainder.
    p = Profile()
    p.load_simc(current_actor)
    yield p
