#!/usr/bin/env python
"""

Configures the necessary files in Steam and SteamVR for running
HMD-less tracking. See README for more info.

"""

import os
import shutil

steamVRSettings = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "steamvr.vrsettings"
)

steamVRPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings"
steamVRBakPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings.bak"

def configure():
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