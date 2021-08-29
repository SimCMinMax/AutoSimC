"""
SimulationCraft update manager.
"""
import glob
import logging
import platform
import os
import re
import subprocess
from typing import Optional, Tuple
from urllib.error import URLError
from urllib.request import urlopen, urlretrieve

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

from i18n import _


def get_simc_version() -> Optional[str]:
    """gets the version of our simc installation on disc"""
    try:
        p = subprocess.run([settings.simc_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        match = None
        for line in p.stdout.decode():
            # git build <branch> <git-ref>
            match = re.search(r'git build \S* (\S+)\)', line)
            if match:
                commit = match.group(1)
                logging.debug(_("Found program in {}: Git_Version: {}")
                                .format(settings.simc_path,
                                        commit))
                return commit

        if match is None:
            logging.info(_("Found no git-string in simc.exe, self-compiled?"))
    except FileNotFoundError:
        logging.info(_("Did not find program in '{}'.").format(settings.simc_path))


def get_latest_simc_version() -> Tuple[str, str]:
    """gets the version of the latest binaries available on the net"""
    try:
        html = urlopen('http://downloads.simulationcraft.org/nightly/?C=M;O=D').read().decode('utf-8')
    except URLError:
        logging.info("Could not access download directory on simulationcraft.org")
    # filename = re.search(r'<a href="(simc.+win64.+7z)">', html).group(1)
    filename = list(filter(None, re.findall(r'.+nonetwork.+|<a href="(simc.+win64.+7z)">', html)))[0]
    head, _tail = os.path.splitext(filename)
    latest_git_version = head.split("-")[-1]
    logging.debug(_("Latest version available: {}").format(latest_git_version))

    if not len(latest_git_version):
        logging.info(_("Found no git-string in filename, new or changed format?"))

    return (filename, latest_git_version)


def download_simc():
    if not settings.auto_download_simc:
        return
    try:
        if settings.auto_download_simc:
            if platform.system() != "Windows" or not platform.machine().endswith('64'):
                print(_("Sorry autodownloading only supported for 64bit windows"))
                return
    except AttributeError:
        return

    logging.info(_("Starting auto download check of SimulationCraft."))

    # Application root path, and destination path
    rootpath = os.path.dirname(os.path.realpath(__file__))
    download_dir = os.path.join(rootpath, "auto_download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Get filename of latest build of simc
    filename, _githash = get_latest_simc_version()
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
