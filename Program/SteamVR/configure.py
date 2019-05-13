#!/usr/bin/env python
"""

Configures the necessary files in Steam and SteamVR for running
HMD-less tracking. See README for more info.

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

steamVRSettings = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "steamvr.vrsettings"
)

steamVRPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings"
steamVRBakPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings.bak"


def configure():

    if b"vrmonitor.exe" in processes:
        raise SteamVRRunningError

    try:
        if not os.path.isfile(steamVRBakPath):
            shutil.copyfile(steamVRPath, steamVRBakPath)
            print("Back-up created.\n")
        shutil.copyfile(steamVRSettings, steamVRPath)
        print("Configured!\n")
    except shutil.Error as e:
        print(e)


if __name__ == "__main__":
    configure()
