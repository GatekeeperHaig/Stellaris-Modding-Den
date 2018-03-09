#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "C:/Users/David/Downloads/Autobuild-master/events/autobuild_events.txt" "--just_copy_and_check" "--output_folder" "../gratak_mods/autobuild_comp/events" "--custom_mod_name" "Build Upgraded - Autobuild Comp. Patch" "--gameVersion" "2.0.*" "--t0_buildings" "building_colony_shelter,building_deployment_post,building_basic_power_plant,building_basic_farm,building_basic_mine" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0" "--load_order_priority" "--load_order_priority" "--one_line_level" "1"', shell=True)
