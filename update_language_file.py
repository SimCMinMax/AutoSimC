import subprocess
import sys
import os

python_dir, _python_exe = os.path.split(sys.executable)
i18n_dir = "Tools\i18n"
pygettext = "pygettext.py"

path = os.path.join(python_dir, i18n_dir, pygettext)
print("pygettext path: {}".format(path))

cmd = [sys.executable, path, "-d", "AutoSimC", "main.py", "splitter.py"]
print("cmd: {}".format(cmd))
subprocess.Popen(cmd)
print("done")
