#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "C:/SteamLibrary/SteamApps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt" "--tags" "Builings,Utilities,Fixes" "--picture_file" "thumb_direct_build.png" "--custom_mod_name" "Build Upgraded - Direct construction of high tier buildings" "--just_copy_and_check"', shell=True)
