#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
os.chdir('..')
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "D:/Program Files (x86)/Steam/steamapps/workshop/content/281990/1202444327/AlphaMod1p8b/common/policies/ethictekpx_policies.txt" "--just_copy_and_check" "--output_folder" "compatibility-patches-exoverhaul/BUAlphaMod/common/policies/" "--custom_mod_name" "Build Upgraded - AlphaMod Comp. Patch" "--gameVersion" "1.9.*" "--t0_buildings" "building_colony_shelter,building_deployment_post,building_basic_power_plant,building_basic_farm,building_basic_mine" "--languages" "braz_por,english,french,german,polish,russian,spanish" "--time_discount" "0.25" "--cost_discount" "0.0" "--load_order_priority" "--load_order_priority"', shell=True)
