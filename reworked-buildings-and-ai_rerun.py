#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.call('python ./createUpgradedBuildings.py "--simplify_upgrade_AI_allow" "-o" "./exoverhaul/reworked-buildings-and-ai/" "./exoverhaul-reworked-buildings-and-ai.mod" "-m" "-j" "-r" "--replacement_file" "./NOTES/replaceFile.txt" "-t" "0.5" "--create_tier5_enhanced" "--custom_mod_name" "((((--ExOverhaul: Reworked Buildings and AI--))))"', shell=True)
