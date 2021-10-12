"""
SimulationCraft update manager.
"""
import datetime
from dataclasses import dataclass
import glob
import html.parser
import logging
import platform
import os
import re
import subprocess
from typing import List, Optional, Tuple
from urllib.request import urlopen, urlretrieve

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

from i18n import _


_CURRENT_SIMC_VERSION = '910-01'
_VERSION_RE = re.compile(
    r'SimulationCraft (?P<version>\d+-\d+) for World of Warcraft '
    r'(?P<wow_version>\d+\.\d+\.\d+\.\d+) .+'
    r'hotfix (?P<hotfix_date>\d{4}-\d{2}-\d{2})/(?P<hotfix_version>\d+)(?:, '
    r'git build (?P<expansion>\S+) (?P<git_commit>[a-f0-9]{1,7}))?')
_PACKAGE_RE = re.compile(
    r'(?P<filename>simc-(?P<version>\d+-\d+)-'
    r'(?P<platform>[^-]+)-(?P<git_commit>[a-f0-9]{1,7})\.(?:dmg|7z))')


@dataclass(frozen=True)
class SimcVersion:
    version: str
    wow_version: str
    hotfix_date: datetime.date
    hotfix_version: int
    expansion: Optional[str] = None
    git_commit: Optional[str] = None

    @staticmethod
    def parse(input: str) -> 'Optional[SimcVersion]':
        match = _VERSION_RE.search(input)
        if not match:
            return
        
        match = match.groupdict()
        match['hotfix_version'] = int(match['hotfix_version'])
        match['hotfix_date'] = datetime.date.fromisoformat(match['hotfix_date'])
        return SimcVersion(**match)


class LinkParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links = []  # type: List[str]

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attrs = dict(attrs)
        href = attrs.get('href')
        if href and '/' not in href:
            self.links.append(href)


def get_simc_version(simc_path: str) -> Optional[SimcVersion]:
    """Gets simc version information."""
    p = subprocess.run([simc_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return SimcVersion.parse(p.stdout.decode())


def simc_platform() -> Optional[str]:
    """SimC platform name for binary builds."""
    if platform.system() == 'Windows':
        return {
            'AMD64': 'win64',
            'x86': 'win32',
        }.get(platform.machine())
    elif platform.system() == 'Darwin':
        return 'macos'


def latest_simc_version(major_ver: str = _CURRENT_SIMC_VERSION, platform: Optional[str] = None) -> Optional[Tuple[str, str]]:
    """
    Checks the SimulationCraft nightly builds for the latest binary build.
    
    Args:
        major_ver: A major version of simc, eg: '910-01'.
        platform: Platform to check, eg: 'win64', 'macos', or None to auto-detect.

    Returns:
        tuple of (filename, git_commit) with the latest version.
    """
    if not platform:
        platform = simc_platform()
        if not platform:
            # Unsupported platform, cannot answer.
            return

    listing = urlopen('http://downloads.simulationcraft.org/nightly/?C=M;O=D').read().decode('utf-8')
    parser = LinkParser()
    parser.feed(listing)

    # Parse the filenames
    for link in parser.links:
        v = _PACKAGE_RE.match(link)
        if not v:
            continue
        if major_ver == v.group('version') and platform == v.group('platform'):
            return (v.group('filename'), v.group('git_commit'))


def download_simc():
    if platform.system() != "Windows" or not platform.machine().endswith('64'):
        print(_("Sorry autodownloading only supported for 64bit windows"))
        return

    logging.info(_("Starting auto download check of SimulationCraft."))

    # Application root path, and destination path
    rootpath = os.path.dirname(os.path.realpath(__file__))
    download_dir = os.path.join(rootpath, "auto_download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Get filename of latest build of simc
    latest = latest_simc_version()
    if not latest:
        raise ValueError('Could not find latest version')
    filename = latest[0]
    print(_("Latest simc: {filename}").format(filename=filename))

    # Download latest build of simc
    filepath = os.path.join(download_dir, filename)
    if not os.path.exists(filepath):
        url = 'http://downloads.simulationcraft.org/nightly/' + filename
        logging.info(_("Retrieving simc from url {} to {}.").format(url,
                                                                    filepath))
        urlretrieve(url, filepath)
    else:
        logging.debug(_("Latest simc version already downloaded at {}.").format(filename))

    # Unpack downloaded build and set simc_path
    settings.simc_path = os.path.join(download_dir, filename[:filename.find(".7z")][:-8], "simc.exe")
    if not os.path.exists(settings.simc_path):
        seven_zip_executables = ["7z.exe", "C:/Program Files/7-Zip/7z.exe"]
        for seven_zip_executable in seven_zip_executables:
            try:
                if not os.path.exists(seven_zip_executable):
                    logging.info(_("7Zip executable at '{}' does not exist.").format(seven_zip_executable))
                    continue
                cmd = [seven_zip_executable, 'x', filepath, '-aoa', '-o' + download_dir]
                logging.debug(_("Running unpack command '{}'").format(cmd))
                subprocess.run(cmd)

                # keep the latest 7z to remember current version, but clean up any other ones
                files = glob.glob(download_dir + '/simc*win64*7z')
                for f in files:
                    if not os.path.basename(f) == filename:
                        print(_("Removing old simc from '{}'.").format(os.path.basename(f)))
                        os.remove(f)
                break
            except Exception as e:
                print(_("Exception when unpacking: {}").format(e))
        else:
            raise RuntimeError(_("Could not unpack the auto downloaded SimulationCraft executable."
                                 "Please note that you need 7Zip installed at one of the following locations: {}.").
                               format(seven_zip_executables))
    else:
        print(_("Simc already exists at '{}'.").format(repr(settings.simc_path)))
