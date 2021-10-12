import unittest

import fights


class FightsTest(unittest.TestCase):
    def test_fights_available(self):
        self.assertGreaterEqual(len(fights.all_fights()), 5)

    def test_get_fight(self):
        self.assertEqual(fights.get_fight('Patchwerk').name, 'Patchwerk')

        # Case-insensitive match
        self.assertEqual(fights.get_fight('paTCHweRk').name, 'Patchwerk')

        # Unknown fights return None
        self.assertIsNone(fights.get_fight('abcdef'))

    def test_simc_options(self):
        self.assertEqual(
            fights.get_fight('Patchwerk').simc_options,
            ('fight_style=Patchwerk',))
        self.assertEqual(
            fights.get_fight('Two Patchwerks, stacked').simc_options,
            ('enemy=Patchwerk', 'enemy=Patchwerk2'))

    def test_validate_fight(self):
        fight_count = len(fights.all_fights())
        with self.assertRaises(ValueError):
            fights.Fight(
                name='Incomplete fight',
                description='No style or custom param',
            )

        # This fight should not appear in all_fights
        self.assertEqual(len(fights.all_fights()), fight_count)

        with self.assertRaises(ValueError):
            fights.Fight(
                name='Invalid fight',
                description='Both style and custom param set',
                style='Invalid',
                custom=['enemy=Custom'],
            )

        # This fight should not appear in all_fights
        self.assertEqual(len(fights.all_fights()), fight_count)
    
    def test_auto_register(self):
        self.assertIsNone(fights.get_fight('test_auto_register'))

        fight_count = len(fights.all_fights())
        fights.Fight(
            name='test_auto_register',
            description='A new fight should be in global state automatically',
            custom=('enemy=Custom',),
        )

        self.assertEqual(len(fights.all_fights()), fight_count + 1)
        self.assertEqual(fights.get_fight('test_auto_register').simc_options, ('enemy=Custom',))

        # Unregister the fight
        del fights._FIGHTS['test_auto_register']
