from datetime import date
from io import BytesIO
import os.path
import unittest
from unittest.mock import patch

import simc
from simc import SimcVersion

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(_DATA_DIR, 'downloads.html'), 'rb') as f:
    _DOWNLOADS_PAGE = f.read()
with open(os.path.join(_DATA_DIR, 'downloads_qt5.html'), 'rb') as f:
    _DOWNLOADS_QT5_PAGE = f.read()


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

    def test_parse_invalid(self):
        self.assertIsNone(
            SimcVersion.parse('Microsoft Windows [Version 10.0.19043.1165]'))

    def test_get_version(self):
        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_PAGE)) as m:
            self.assertEqual(simc.latest_simc_version(platform='win64'),
                             ('simc-910-01-win64-5a43e33.7z', '5a43e33'))
        m.assert_called_once_with(
            'http://downloads.simulationcraft.org/nightly/?C=M;O=D')

        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_PAGE)):
            self.assertEqual(simc.latest_simc_version(platform='win32'),
                             ('simc-910-01-win32-5a43e33.7z', '5a43e33'))

        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_PAGE)):
            self.assertEqual(simc.latest_simc_version(platform='macos'),
                             ('simc-910-01-macos-5a43e33.dmg', '5a43e33'))

        # Platform auto-detection
        with (patch.object(simc, 'simc_platform', return_value='macos'),
              patch.object(simc,
                           'urlopen',
                           return_value=BytesIO(_DOWNLOADS_PAGE))):
            self.assertEqual(simc.latest_simc_version(),
                             ('simc-910-01-macos-5a43e33.dmg', '5a43e33'))

        # Platform auto-detection failure
        with (patch.object(simc, 'simc_platform', return_value=None),
              patch.object(simc,
                           'urlopen',
                           return_value=BytesIO(_DOWNLOADS_PAGE))):
            self.assertIsNone(simc.latest_simc_version())

        # Other versions
        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_PAGE)):
            self.assertEqual(
                simc.latest_simc_version(major_ver='830-02', platform='win64'),
                ('simc-830-02-win64-8790a08.7z', '8790a08'))

        # No match
        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_PAGE)):
            self.assertIsNone(
                simc.latest_simc_version(major_ver='810-01', platform='win64'))

    def test_get_version_qt5(self):
        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)) as m:
            self.assertEqual(simc.latest_simc_version(platform='win64'),
                             ('simc-910-01-win64-ff51bf3.7z', 'ff51bf3'))
        m.assert_called_once_with(
            'http://downloads.simulationcraft.org/nightly/?C=M;O=D')

        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)):
            self.assertEqual(simc.latest_simc_version(platform='winarm64'),
                             ('simc-910-01-winarm64-ff51bf3.7z', 'ff51bf3'))

        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)):
            self.assertEqual(simc.latest_simc_version(platform='win32_qt5'),
                             ('simc-910-01-win32_qt5-ff51bf3.7z', 'ff51bf3'))

        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)):
            self.assertEqual(simc.latest_simc_version(platform='win64_qt5'),
                             ('simc-910-01-win64_qt5-ff51bf3.7z', 'ff51bf3'))

        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)):
            self.assertEqual(simc.latest_simc_version(platform='macos'),
                             ('simc-910-01-macos-ff51bf3.dmg', 'ff51bf3'))

        # Platform auto-detection
        with (patch.object(simc, 'simc_platform', return_value='macos'),
              patch.object(simc,
                           'urlopen',
                           return_value=BytesIO(_DOWNLOADS_QT5_PAGE))):
            self.assertEqual(simc.latest_simc_version(),
                             ('simc-910-01-macos-ff51bf3.dmg', 'ff51bf3'))

        # Platform auto-detection failure
        with (patch.object(simc, 'simc_platform', return_value=None),
              patch.object(simc,
                           'urlopen',
                           return_value=BytesIO(_DOWNLOADS_QT5_PAGE))):
            self.assertIsNone(simc.latest_simc_version())

        # Other versions
        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)):
            self.assertEqual(
                simc.latest_simc_version(major_ver='830-02', platform='win64'),
                ('simc-830-02-win64-8790a08.7z', '8790a08'))

        # No match
        with patch.object(simc,
                          'urlopen',
                          return_value=BytesIO(_DOWNLOADS_QT5_PAGE)):
            self.assertIsNone(
                simc.latest_simc_version(major_ver='810-01', platform='win64'))
