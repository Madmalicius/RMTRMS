#!/usr/bin/env python
"""

Restores the original SteamVR settings file and removes backup file.
See README for more info.

"""

import os
import shutil
import subprocess


class SteamVRRunningError(Exception):
    """ Raised when SteamVR is running while trying to modify conifg files"""

    pass


processes = subprocess.Popen(
    "tasklist", stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
).communicate()[
    0
]  # Get list of all running processes

steamVRPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings"
steamVRBakPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings.bak"


def restore():
    if b"vrmonitor.exe" in processes:
        raise SteamVRRunningError

    try:
        shutil.copyfile(steamVRBakPath, steamVRPath)
        os.remove(steamVRBakPath)
        print("Restored!")
        return 0
    except OSError as e:
        print("ERROR: No backup found.")


if __name__ == "__main__":
    restore()
