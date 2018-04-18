#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
os.chdir('..')
os.chdir('..')
subprocess.call('python C:/Users/David/Documents/Paradox Interactive/Stellaris/modModding/pythonScripts/createUpgradedBuildings.py "C:/SteamLibrary/SteamApps/common/Stellaris/common/scripted_effects/00_scripted_effects.txt" "--just_copy_and_check" "--output_folder" "gratak_mods/build_upgraded/common/scripted_effects/" "--game_version" "2.0.*" "--t0_buildings" "building_colony_shelter,building_deployment_post,building_basic_power_plant,building_basic_farm,building_basic_mine" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0" "--one_line_level" "1"', shell=True)
