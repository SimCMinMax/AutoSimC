#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil

_PYGETTEXT_ARGS = ['-d', 'AutoSimC', '*.py']
_PYGETTEXT_ENV = {
    # POT files contain a timestamp with timezone offset
    'TZ': 'UTC',
    # https://www.python.org/dev/peps/pep-0538/#explicitly-setting-lc-ctype-for-utf-8-locale-coercion
    'LANG': 'C.UTF-8',
    'LC_CTYPE': 'C.UTF-8',
    # https://docs.python.org/3/using/windows.html#utf-8-mode
    'PYTHONUTF8': '1',
}


def find_pygettext():
    # Windows: look for Tools/i18n/pygettext.py near the Python executable
    py_dir = os.path.join(os.path.dirname(sys.executable))
    if 'PythonSoftwareFoundation.Python' in py_dir:
        # pygettext isn't in the Microsoft Store Python.
        raise EnvironmentError(
            'This tool does not support Python from the Microsoft Store. '
            'Install Python for Windows from https://python.org/downloads/')
    else:
        # Python for Windows, eg: C:\Python39\Tools\i18n\pygettext.py
        pygettext = os.path.join(py_dir, 'Tools', 'i18n', 'pygettext.py')
    if os.path.exists(pygettext):
        return [sys.executable, pygettext]

    # Other platforms normally keep pygettext in the PATH.
    pygettext = shutil.which('pygettext3')
    if pygettext:
        return [pygettext]

    # Nothing!
    raise EnvironmentError('Cannot find pygettext3 in PATH')


def main():
    cmd = find_pygettext() + _PYGETTEXT_ARGS
    env = dict(os.environ)
    env.update(_PYGETTEXT_ENV)

    print(f'Running: {" ".join(map(repr, cmd))}')
    subprocess.run(cmd, cwd=os.path.dirname(__file__), env=env)


if __name__ == '__main__':
    main()
