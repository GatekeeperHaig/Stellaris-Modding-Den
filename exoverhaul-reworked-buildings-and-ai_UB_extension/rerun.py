#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "-o" "./exoverhaul-reworked-buildings-and-ai_UB_extension/" "./exoverhaul-reworked-buildings-and-ai/common/buildings/*" "-j" "-r" "--replacement_file" "./NOTES/replaceFile.txt" "--create_tier5_enhanced"', shell=True)
