#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
os.chdir('..')
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "D:/Program Files (x86)/Steam/steamapps/workshop/content/281990/1147051128/novus_orbis_new/common/armies/99_novus_defense_armies.txt" "--just_copy_and_check" "--output_folder" "../gratak_mods/novus_orbis_BU/common/armies/" "--custom_mod_name" "Build Upgraded - Norvus Orbis Comp. Patch" "--game_version" "2.0.*" "--t0_buildings" "building_colony_shelter,building_deployment_post,building_basic_power_plant,building_basic_farm,building_basic_mine" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0" "--load_order_priority" "--load_order_priority" "--one_line_level" "1"', shell=True)
