from datetime import date
import unittest

from simc import SimcVersion


class SimcTest(unittest.TestCase):
    def test_shadowlands(self):
        self.assertEqual(
            SimcVersion(
                version='910-01',
                wow_version='9.1.0.39653',
                hotfix_date=date(2021, 8, 5),
                hotfix_version=39653,
                expansion='shadowlands',
                git_commit='bb7091c',
            ),
            SimcVersion.parse(
                'SimulationCraft 910-01 for World of Warcraft 9.1.0.39653 '
                'Live (hotfix 2021-08-05/39653, git build shadowlands '
                'bb7091c)'))

        self.assertEqual(
            SimcVersion(
                version='905-01',
                wow_version='9.0.5.38134',
                hotfix_date=date(2021, 3, 31),
                hotfix_version=38134,
                expansion='shadowlands',
                git_commit='e55e8d3',
            ),
            SimcVersion.parse(
                'SimulationCraft 905-01 for World of Warcraft 9.0.5.38134 '
                'Live (hotfix 2021-03-31/38134, git build shadowlands '
                'e55e8d3)'))

    def test_bfa(self):
        self.assertEqual(
            SimcVersion(
                version='830-02',
                wow_version='8.3.0.34769',
                hotfix_date=date(2020, 6, 27),
                hotfix_version=34769,
            ),
            SimcVersion.parse(
                'SimulationCraft 830-02 for World of Warcraft 8.3.0.34769 '
                'Live (hotfix 2020-06-27/34769)'))
