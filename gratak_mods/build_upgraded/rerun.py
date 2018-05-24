#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
subprocess.call('python C:/Users/David/Documents/Paradox Interactive/Stellaris/modModding/pythonScripts/createUpgradedBuildings.py "C:/SteamLibrary/SteamApps/common/Stellaris/common/buildings/00_buildings.txt" "C:/SteamLibrary/SteamApps/common/Stellaris/common/buildings/00_event_buildings.txt" "C:/SteamLibrary/SteamApps/common/Stellaris/common/buildings/00_habitat_buildings.txt" "C:/SteamLibrary/SteamApps/common/Stellaris/common/buildings/00_horizonsignal_buildings.txt" "C:/SteamLibrary/SteamApps/common/Stellaris/common/buildings/00_syntheticdawn_buildings.txt" "C:/SteamLibrary/SteamApps/common/Stellaris/common/buildings/00_leviathans_buildings.txt" "--output_folder" "../gratak_mods/build_upgraded" "--custom_mod_name" "Build Upgraded - Direct construction of high tier buildings" "--game_version" "2.1.*" "--t0_buildings" "building_colony_shelter,building_deployment_post" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0" "--one_line_level" "2" "--helper_file_list" "000000"', shell=True)
import fnmatch
for root, dirnames, filenames in os.walk('.'):
	for filename in fnmatch.filter(filenames,'rerun_just_copy_and_check.py'):
		subprocess.call('python "'+os.path.join(root,filename)+'"', shell=True)
