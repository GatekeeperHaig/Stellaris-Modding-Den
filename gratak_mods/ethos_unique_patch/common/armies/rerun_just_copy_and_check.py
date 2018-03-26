#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
os.chdir('..')
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "C:/SteamLibrary/SteamApps/workshop/content/281990/804732593/eutab/common/armies/eutab_armies.txt" "--just_copy_and_check" "--output_folder" "gratak_mods/ethos_unique_patch/common/armies/" "--custom_mod_name" "Build Upgraded - Ethos Unique Techs and Buildings Comp Patch" "--game_version" "2.0.*" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0" "--load_order_priority" "--load_order_priority" "--one_line_level" "1"', shell=True)
