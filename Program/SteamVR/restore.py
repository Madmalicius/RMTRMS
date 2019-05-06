#!/usr/bin/env python
"""

Restores the original SteamVR settings file and removes backup file.
See README for more info.

"""

import os
import shutil

steamVRPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings"
steamVRBakPath = "C:\Program Files (x86)\Steam\config\steamvr.vrsettings.bak"

def restore():
    try:
        shutil.copyfile(steamVRBakPath, steamVRPath)
        os.remove(steamVRBakPath)
    except OSError as e:
        print("ERROR: No backup found.")


if __name__ == "__main__":
    restore()
