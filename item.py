from enum import Enum
import json
import os.path
from typing import Dict, Iterator, List, Optional, Sequence, cast

SHADOWLANDS_LEGENDARY_IDS = frozenset({
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
})

# Fake enchants that we should ignore.
_FAKE_ENCHANTS = frozenset({
    # simc implements some of the Shards of Domination as gear enchants,
    # which gets added whenever it saves a profile. We should ignore them.
    #
    # Shard of Oth
    '30runspeed',
    '37runspeed',
    '45runspeed',
    '52runspeed',
    '60runspeed',
    # Shard of Rev
    '30leech',
    '37leech',
    '45leech',
    '52leech',
    '60leech',
})


class GearType(Enum):
    """Gear types, which match the naming used by SimulationCraft."""
    UNKNOWN = 0
    HEAD = 1
    NECK = 2
    SHOULDER = SHOULDERS = 3
    BACK = 4
    CHEST = 5
    SHIRT = 6
    TABARD = 7
    WRIST = WRISTS = 8
    HANDS = 9
    WAIST = 10
    LEGS = 11
    FEET = 12

    MAIN_HAND = 13
    OFF_HAND = 14

    # Finger and Trinket can each have two items equipped
    FINGER = FINGER1 = FINGER2 = 15
    TRINKET = TRINKET1 = TRINKET2 = 16

    @staticmethod
    def from_simc(name: str) -> 'Optional[GearType]':
        name = name.upper()
        o = cast(Optional[GearType], GearType.__members__.get(name))
        if o == GearType.UNKNOWN:
            o = None
        return o

    @staticmethod
    def all_names() -> Sequence[str]:
        return [n.lower() for n in GearType.__members__.keys()
                if n not in _GEARTYPE_SPECIAL_NAMES]

    @staticmethod
    def all_slots() -> 'Iterator[GearType]':
        return (cast(GearType, GearType.__members__[k])
                for k in GearType.__members__.keys()
                if k not in _GEARTYPE_SPECIAL_NAMES)

    def __str__(self):
        return self.name.lower()


_GEARTYPE_SPECIAL_NAMES = frozenset({
    'UNKNOWN',
    'FINGER1', 'FINGER2',
    'TRINKET1', 'TRINKET2',
    # Synonyms supported by simc
    'SHOULDERS', 'WRISTS',
})


class WeaponType(Enum):
    DUMMY = -1
    ONEHAND = 13
    SHIELD = 14
    BOW = 15
    TWOHAND = 17
    OFFHAND_WEAPON = 21
    OFFHAND_SPECIAL_WEAPON = 22
    OFFHAND = 23
    GUN = 26


class Item:
    """WoW Item"""

    def __init__(self, slot: GearType, is_weekly_reward: bool, input_string: str = ""):
        self._slot = slot
        self.name = ""
        self.item_id = 0
        self.bonus_ids = []  # type: List[int]
        self.enchant_ids = []  # type: List[int]
        self.enchants = []  # type: List[str]
        self._gem_ids = []  # type: List[int]
        self.drop_level = 0
        self.extra_options = {}
        self._isWeeklyReward = is_weekly_reward

        if len(input_string):
            self.parse_input(input_string.strip("\""))

        self._build_output_str()  # Pre-Build output string as good as possible

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, value):
        self._slot = value
        self._build_output_str()

    @property
    def isWeeklyReward(self):
        return self._isWeeklyReward

    @isWeeklyReward.setter
    def isWeeklyReward(self, value):
        self._isWeeklyReward = value
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

        for s in parts[1:]:
            name, value = s.split("=")
            name = name.lower()
            if name == "id":
                self.item_id = int(value)
            elif name == "bonus_id":
                self.bonus_ids = [int(v) for v in value.split("/")]
            elif name == 'enchant':
                self.enchants = [v for v in value.split('/') if v not in _FAKE_ENCHANTS]
            elif name == "enchant_id":
                self.enchant_ids = [int(v) for v in value.split("/")]
            elif name == "gem_id":
                self.gem_ids = [int(v) for v in value.split("/")]
            elif name == "drop_level":
                self.drop_level = int(value)
            else:
                if name not in self.extra_options:
                    self.extra_options[name] = []
                self.extra_options[name].append(value)

    def _build_output_str(self):
        self.output_str = f'{self.name},id={self.item_id}'
        if self.bonus_ids:
            self.output_str += ",bonus_id=" + "/".join([str(v) for v in self.bonus_ids])
        if self.enchants:
            self.output_str += ',enchant=' + '/'.join(self.enchants)
        if self.enchant_ids:
            self.output_str += ",enchant_id=" + "/".join([str(v) for v in self.enchant_ids])
        if self.gem_ids:
            self.output_str += ",gem_id=" + "/".join([str(v) for v in self.gem_ids])
        if self.drop_level > 0:
            self.output_str += ",drop_level=" + str(self.drop_level)
        for name, values in self.extra_options.items():
            for value in values:
                self.output_str += ",{}={}".format(name, value)

    def __str__(self):
        return f'Item({self.slot}; {self.output_str})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        if self.name and self.item_id == 0:
            # We have only an item name, no ID.
            if self.name != other.name:
                return False

            # Don't check the item_id, our name matched.
        elif self.item_id != other.item_id:
            return False

        return (
            self.slot == other.slot and
            self.bonus_ids == other.bonus_ids and
            self.enchants == other.enchants and
            self.enchant_ids == other.enchant_ids and
            self.gem_ids == other.gem_ids and
            self.drop_level == other.drop_level and
            self.extra_options == other.extra_options
        )

    def __hash__(self):
        # We are just lazy and use __str__ to avoid all the complexity about having mutable members, etc.
        return hash(str(self.__dict__))

    def __lt__(self, other: 'Item'):
        if not isinstance(other, Item):
            raise TypeError(f'Cannot compare {type(other)} with Item')
        return self.item_id < other.item_id

    @property
    def weapon_type(self) -> Optional[WeaponType]:
        if self.slot in (GearType.MAIN_HAND, GearType.OFF_HAND):
            return get_weapon_type(self)


# generate map of id->type pairs
def _read_weapon_data() -> Dict[int, WeaponType]:
    # weapondata is directly derived from blizzard-datatables
    # Thanks to Theunderminejournal.com for providing the database:
    # http://newswire.theunderminejournal.com/phpMyAdmin
    # SELECT id, type
    # FROM `tblDBCItem`
    # WHERE type = 13 or type = 14 or type = 15 or type = 17
    # or type = 21 or type = 22 or type = 23 or type = 26
    #
    # type is important:
    # 13: onehand                                                   -mh, oh
    # 14: shield                                                    -oh
    # 15: bow                                                       -mh
    # 17: twohand (two twohanders are allowed for fury-warriors)    -mh, oh
    # 21: offhand-weapon                                            -oh
    # 22: offhand special stuff                                     -oh
    # 23: offhand                                                   -oh
    # 26: gun                                                       -mh
    #
    # WE REALLY DONT CARE if you can equip it or not, if it has str or int
    # we only use it to distinguish whether to put it into main_hand or off_hand slot
    #
    # therefore, if a warrior tries to sim a polearm, it would be assigned to the main_Hand (possibly two, if fury), but
    # the stats etc. would not be taken into account by simulationcraft
    # similar to weird combinations like bow and offhand or onehand and shield for druids
    # => disable those items or sell them, or implement a validation-check, no hunter needs a shield...
    weapondata_fn = os.path.join(os.path.dirname(__file__), 'weapondata.json')

    weapondata = {}
    with open(weapondata_fn, 'r', encoding='utf-8') as data_file:
        weapondata_json = json.load(data_file)

        for weapon in weapondata_json:
            weapondata[int(weapon['id'])] = WeaponType(int(weapon['type']))
    # always create one offhand-item which is used as dummy for twohand-permutations
    weapondata[-1] = WeaponType.DUMMY

    return weapondata


_WEAPONDATA = _read_weapon_data()

def get_weapon_type(item: Optional[Item]) -> Optional[WeaponType]:
    if item is None:
        return
    return _WEAPONDATA.get(item.item_id)
