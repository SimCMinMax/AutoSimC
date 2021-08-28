from enum import Enum
import json
import os.path
from typing import Dict

# Items to parse. First entry is the "correct" name
GEAR_SLOTS = [("head",),
              ("neck",),
              ("shoulder", "shoulders"),
              ("back",),
              ("chest",),
              ("wrist", "wrists"),
              ("hands",),
              ("waist",),
              ("legs",),
              ("feet",),
              ("finger", "finger1", "finger2"),
              ("trinket", "trinket1", "trinket2",),
              ("main_hand",),
              ("off_hand",)]


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
    tiers = [27]

    def __init__(self, slot, is_weekly_reward, input_string=""):
        self._slot = slot
        self.name = ""
        self.item_id = 0
        self.bonus_ids = []
        self.enchant_ids = []
        self._gem_ids = []
        self.drop_level = 0
        self.tier_set = {}
        self.extra_options = {}
        self._isWeeklyReward = is_weekly_reward

        for tier in self.tiers:
            n = "T{}".format(tier)
            if self.name.startswith(n):
                setattr(self, "tier_{}".format(tier), True)
                self.name = self.name[len(n):]
            else:
                setattr(self, "tier_{}".format(tier), False)
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
            elif name == "drop_level":
                self.drop_level = int(value)
            else:
                if name not in self.extra_options:
                    self.extra_options[name] = []
                self.extra_options[name].append(value)

    def _build_output_str(self):
        self.output_str = "{}={},id={}". \
            format(self.slot,
                   self.name,
                   self.item_id)
        if len(self.bonus_ids):
            self.output_str += ",bonus_id=" + "/".join([str(v) for v in self.bonus_ids])
        if len(self.enchant_ids):
            self.output_str += ",enchant_id=" + "/".join([str(v) for v in self.enchant_ids])
        if len(self.gem_ids):
            self.output_str += ",gem_id=" + "/".join([str(v) for v in self.gem_ids])
        if self.drop_level > 0:
            self.output_str += ",drop_level=" + str(self.drop_level)
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


def isValidWeaponPermutation(permutation, player_profile):
    mh_type = _WEAPONDATA[permutation[10].item_id]
    oh_type = _WEAPONDATA[permutation[11].item_id]

    # only gun or bow is equippable
    if (mh_type is WeaponType.BOW or mh_type is WeaponType.GUN) and oh_type is None:
        return True
    if player_profile.wow_class != "hunter" and (mh_type is WeaponType.BOW or mh_type is WeaponType.GUN):
        return False
    # only warriors can wield twohanders in offhand
    if player_profile.wow_class != "warrior" and oh_type is WeaponType.TWOHAND:
        return False
    # no true offhand in mainhand possible
    if mh_type is WeaponType.SHIELD or mh_type is WeaponType.OFFHAND:
        return False
    if player_profile.wow_class != "warrior" and mh_type is WeaponType.TWOHAND and (
            oh_type is WeaponType.OFFHAND or oh_type is WeaponType.SHIELD):
        return False

    return True

