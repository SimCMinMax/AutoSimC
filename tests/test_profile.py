"""
Tests for profile module
"""

from collections import defaultdict
from item import GearType, WeaponType
import os.path
from parameterized import parameterized
import unittest

import permutation
from profile import Profile, load_multiple_profiles

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
T27_PROFILE_PATH = os.path.join(TEST_DATA_PATH, 't27')

# Simple profiles, which contain only one character definition.
T27_SIMPLE_PROFILES = [
    'T27_Death_Knight_Blood.simc',
    'T27_Death_Knight_Frost.simc',
    'T27_Death_Knight_Frost_2H.simc',
    'T27_Death_Knight_Frost_Breath.simc',
    'T27_Death_Knight_Frost_Icecap.simc',
    'T27_Death_Knight_Unholy.simc',
    'T27_Demon_Hunter_Havoc.simc',
    'T27_Demon_Hunter_Havoc_Momentum.simc',
    'T27_Demon_Hunter_Vengeance.simc',
    'T27_Druid_Balance.simc',
    'T27_Druid_Feral.simc',
    'T27_Druid_Feral_Owlweave.simc',
    'T27_Druid_Guardian.simc',
    'T27_Druid_Guardian_Venthyr.simc',
    'T27_Hunter_Beast_Mastery.simc',
    'T27_Hunter_Marksmanship.simc',
    'T27_Hunter_Survival.simc',
    'T27_Mage_Arcane.simc',
    'T27_Mage_Arcane_Kyrian.simc',
    'T27_Mage_Fire.simc',
    'T27_Mage_Frost.simc',
    'T27_Monk_Brewmaster.simc',
    'T27_Monk_Windwalker.simc',
    'T27_Monk_Windwalker_Necrolord.simc',
    'T27_Monk_Windwalker_Night_Fae.simc',
    'T27_Paladin_Holy.simc',
    'T27_Paladin_Protection.simc',
    'T27_Paladin_Retribution.simc',
    'T27_Priest_Discipline.simc',
    'T27_Priest_Shadow.simc',
    'T27_Priest_Shadow_Kyrian.simc',
    'T27_Priest_Shadow_Necrolord.simc',
    'T27_Priest_Shadow_Venthyr.simc',
    'T27_Rogue_Assassination.simc',
    'T27_Rogue_Outlaw.simc',
    'T27_Rogue_Subtlety.simc',
    'T27_Shaman_Elemental.simc',
    'T27_Shaman_Elemental_Kyrian.simc',
    'T27_Shaman_Elemental_Necrolord.simc',
    'T27_Shaman_Elemental_Venthyr.simc',
    'T27_Shaman_Enhancement.simc',
    'T27_Shaman_Enhancement_SORG.simc',
    'T27_Shaman_Enhancement_VDW.simc',
    'T27_Shaman_Restoration.simc',
    'T27_Warlock_Affliction.simc',
    'T27_Warlock_Demonology.simc',
    'T27_Warlock_Destruction.simc',
    'T27_Warrior_Arms.simc',
    'T27_Warrior_Fury.simc',
    'T27_Warrior_Protection.simc',
]

# Complex profiles, which contain more than one character definition.
T27_GENERATE_PROFILES = [
    'T27_Generate_Death_Knight.simc',
    'T27_Generate_Demon_Hunter.simc',
    'T27_Generate_Druid.simc',
    'T27_Generate_Hunter.simc',
    'T27_Generate_Mage.simc',
    'T27_Generate_Monk.simc',
    'T27_Generate_Paladin.simc',
    'T27_Generate_Priest.simc',
    'T27_Generate_Rogue.simc',
    'T27_Generate_Shaman.simc',
    'T27_Generate_Warlock.simc',
    'T27_Generate_Warrior.simc',
]


def _open_data(fn: str):
    return open(os.path.join(TEST_DATA_PATH, fn), 'r')


def _open_t27(fn: str):
    return open(os.path.join(T27_PROFILE_PATH, fn), 'r')


def _get_gear(gear_list, item_id, is_weekly_reward):
    for i in gear_list:
        if i.item_id == item_id and i.isWeeklyReward == is_weekly_reward:
            return i

class TestProfile(unittest.TestCase):
    @parameterized.expand(T27_SIMPLE_PROFILES)
    def test_loading_simple_profiles(self, fn):
        p = Profile()
        with _open_t27(fn) as fd:
            p.load_simc(fd)

        self.assertNotEqual(p.player_class, '')
        self.assertTrue(p.baseline.valid_weapons(p.player_class, p.spec))
        self.assertTrue(p.baseline.valid_loadout())

    @parameterized.expand(T27_GENERATE_PROFILES)
    def test_loading_multiple_profiles(self, fn):
        with _open_t27(fn) as fd:
            profiles = list(load_multiple_profiles(fd))

        # Every class has at least three profiles
        self.assertGreaterEqual(len(profiles), 3)

        for p in profiles:
            # Every profile should have a name set.
            self.assertTrue(p.profile_name)

            # Look for a similarly named .simc file
            p2 = Profile()
            p2.load_simc_file(
                os.path.join(T27_PROFILE_PATH, f'{p.profile_name}.simc'))

            # Check that the profile has the same loadout
            diff = p.baseline.diff(p2.baseline)
            self.assertIsNone(diff, p.profile_name)
            self.assertEqual(p.baseline, p2.baseline, p.profile_name)

    def test_t27_dk_unholy(self):
        p = Profile()
        with _open_t27('T27_Death_Knight_Unholy.simc') as fd:
            p.load_simc(fd)

        self.assertEqual(p.player_class, 'deathknight')
        self.assertEqual(p.profile_name, 'T27_Death_Knight_Unholy')
        self.assertEqual(p.spec, 'unholy')
        self.assertEqual(p.level, '60')
        self.assertEqual(p.race, 'troll')
        self.assertEqual(p.role, 'attack')
        self.assertEqual(p.position, 'back')
        self.assertEqual(p.covenant, 'necrolord')
        self.assertEqual(
            p.soulbind, 'plague_deviser_marileth,'
            'volatile_solvent/eternal_hunger:9:1/convocation_of_the_dead:9:1/'
            'adaptive_armor_fragment:9:1/kevins_oozeling')
        self.assertEqual(p.renown, '80')

        self.assertEqual(p.potion, 'potion_of_spectral_strength')
        self.assertEqual(p.flask, 'spectral_flask_of_power')
        self.assertEqual(p.augmentation, 'veiled')
        self.assertEqual(p.temporary_enchant,
                         'main_hand:shaded_sharpening_stone')

        self.assertEqual(p.baseline.head.item_id, 186350)
        self.assertEqual(p.baseline.neck.item_id, 186379)
        self.assertEqual(p.baseline.shoulder.item_id, 186349)
        self.assertEqual(p.baseline.back.item_id, 173242)
        self.assertEqual(p.baseline.chest.item_id, 186347)
        self.assertIsNone(p.baseline.shirt)
        self.assertIsNone(p.baseline.tabard)
        self.assertEqual(p.baseline.wrist.item_id, 186351)
        self.assertEqual(p.baseline.hands.item_id, 186311)
        self.assertEqual(p.baseline.waist.item_id, 178734)
        self.assertEqual(p.baseline.legs.item_id, 178701)
        self.assertEqual(p.baseline.feet.item_id, 186353)
        self.assertEqual(p.baseline.main_hand.item_id, 186410)
        self.assertIsNone(p.baseline.off_hand)

        # Our ring/trinket assignment always puts the higher item ID first.
        # This is the reverse of what appears in the source data.
        self.assertEqual(p.baseline.finger1.item_id, 186377)
        self.assertEqual(p.baseline.finger2.item_id, 178869)
        self.assertEqual(p.baseline.trinket1.item_id, 186438)
        self.assertEqual(p.baseline.trinket2.item_id, 179350)

        self.assertTrue(p.baseline.valid_weapons(p.player_class, p.spec))
        self.assertTrue(p.baseline.valid_loadout())

        legendaries = p.baseline.shadowlands_legendaries()
        self.assertEqual(len(legendaries), 1)
        self.assertEqual(legendaries[0].item_id, 173242)

        self.assertEqual(len(p.baseline.weekly_rewards()), 0)
        self.assertEqual(p.class_spec, 'Unholy Death Knight')
        self.assertEqual(p.class_role, 'strattack')

    def test_2h_warrior(self):
        p = Profile()
        with _open_t27('T27_Warrior_Fury.simc') as fd:
            p.load_simc(fd)

        # Expect two 2H weapons
        self.assertEqual(p.baseline.main_hand.weapon_type, WeaponType.TWOHAND)
        self.assertEqual(p.baseline.off_hand.weapon_type, WeaponType.TWOHAND)
        self.assertTrue(p.baseline.valid_weapons(p.player_class, p.spec))

        # Other specs should fail
        self.assertFalse(p.baseline.valid_weapons('warrior', 'arms'))
        self.assertFalse(p.baseline.valid_weapons('warrior', 'protection'))
        self.assertFalse(p.baseline.valid_weapons('warlock', 'affliction'))

    def test_vault_choices(self):
        p = Profile()
        with _open_data('vault_choices.simc') as fd:
            p.load_simc(fd)

        self.assertEqual(p.profile_name, 'Mage_Vault_Choice')

        # Expect that baseline contains currently equipped gear
        # Only check the slots that may get other gear
        self.assertEqual(p.baseline.neck.item_id, 186379)
        self.assertEqual(p.baseline.trinket1.item_id, 178809)
        self.assertIsNone(p.baseline.trinket2)
        self.assertEqual(p.baseline.main_hand.item_id, 186406)

        # Check the gear in bags (1 neck, 1 trinket, 1 MH) and vault (2 trinkets, 1 OH, 1 ring)
        self.assertEqual(2, len(p.gear[GearType.NECK]))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.NECK],
                      item_id=185954,
                      is_weekly_reward=False))

        self.assertEqual(4, len(p.gear[GearType.TRINKET]))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.TRINKET],
                      item_id=187447,
                      is_weekly_reward=False))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.TRINKET],
                      item_id=178708,
                      is_weekly_reward=True))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.TRINKET],
                      item_id=186431,
                      is_weekly_reward=True))

        self.assertEqual(2, len(p.gear[GearType.MAIN_HAND]))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.MAIN_HAND],
                      item_id=178753,
                      is_weekly_reward=False))

        self.assertEqual(3, len(p.gear[GearType.FINGER]))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.FINGER],
                      item_id=186375,
                      is_weekly_reward=True))

        self.assertEqual(1, len(p.gear[GearType.OFF_HAND]))
        self.assertIsNotNone(
            _get_gear(p.gear[GearType.OFF_HAND],
                      item_id=178868,
                      is_weekly_reward=True))


        # Permute gear
        # 6 trinket combos * 3 ring combos * 2 necks * 2 MH * 2 OH
        # (ignoring vault limits, and always picking 2 trinkets, 1 dummy OH)
        self.assertEqual(144, permutation.max_permutation_count(p))

        # Get a list of valid combos
        combos = list(permutation.generate_permutations(p))
        # Bags: 2 necks, 2 MH; Vault: 2 trinkets, 1 ring, 1 off-hand
        # 2  = 2 neck combos
        # 8  = 2 * 4 vault trinket combos (AC, AD, BC, BD)
        # 4  = 2 * 2 vault ring combos (AC, BC)
        # 2  = 2 * 1 one hand + vault off
        # 10 = 2 * 5 one hand + no off + vault trinket combos
        # 4  = 2 * 2 one hand + no off + vault ring combos
        self.assertEqual(2 + 8 + 4 + 2 + 10 + 4, len(combos))

        gv_ids = frozenset({178708, 186431, 186375, 178868})
        seen_items = defaultdict(lambda: 0)

        for combo in combos:
            # We should always have 2 trinkets and main hand equipped
            self.assertIsNotNone(combo.loadout.trinket1)
            self.assertIsNotNone(combo.loadout.trinket2)
            self.assertIsNotNone(combo.loadout.main_hand)

            # Get all equipped gear IDs for rule checks
            equipped_gear_ids = [
                i.item_id for _slot, i in combo.loadout.all_items()
            ]
            for i in equipped_gear_ids:
                seen_items[i] += 1

            # Great vault rewards appear at most once in any loadout.
            self.assertLessEqual(len(gv_ids & set(equipped_gear_ids)), 1)

            if combo.loadout.main_hand.item_id == 178753:
                # Main-hand 178753 must appear with off-hand 178868 or -1
                self.assertIn(combo.loadout.off_hand.item_id, (178868, -1))
            elif combo.loadout.main_hand.item_id == 186406:
                # Main hand 186406 must appear with only dummy OH
                self.assertEqual(combo.loadout.off_hand.item_id, -1)
            else:
                # Other things must not appear here
                self.fail(
                    f'Unexpected item {combo.loadout.main_hand} in main hand')

        self.assertDictEqual(
            seen_items,
            # New dictionary based on seen_items, updated with expected values.
            {
                **seen_items,
                # Items that should always be there
                186325: 30,
                186324: 30,
                179349: 30,
                186320: 30,
                186321: 30,
                173244: 30,
                186322: 30,
                186285: 30,
                186354: 30,

                # Necks
                186379: 15,
                185954: 15,

                # Main-hand
                186406: 14,
                178753: 16,
                # Off-hand (vault)
                178868: 2,

                # Trinkets
                178809: 30 - 8,
                187447: 30 - 8,
                # Trinkets (vault)
                178708: 8,
                186431: 8,

                # Rings
                186377: 30 - 4,
                186376: 30 - 4,
                # Rings (vault)
                186375: 8,
            })


if __name__ == '__main__':
    unittest.main()
