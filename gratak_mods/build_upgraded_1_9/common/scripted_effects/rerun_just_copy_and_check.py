#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
os.chdir('..')
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "D:/Program Files (x86)/Steam/steamapps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt" "--just_copy_and_check" "--output_folder" "gratak_mods/build_upgraded_1_9/common/scripted_effects/" "--custom_mod_name" "Build Upgraded (1.9 locked) - Direct construction of high tier buildings" "--gameVersion" "1.9.*" "--t0_buildings" "building_colony_shelter,building_deployment_post,building_basic_power_plant,building_basic_farm,building_basic_mine" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0"', shell=True)
