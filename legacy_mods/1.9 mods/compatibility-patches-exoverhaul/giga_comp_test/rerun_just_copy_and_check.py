#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "--just_copy_and_check" "--output_folder" "giga_comp_test" "exoverhaul/ai_suite/common/buildings/ex_capital_buildings.txt" "exoverhaul/ai_suite/common/buildings/ex_empire_unique_buildings.txt" "exoverhaul/ai_suite/common/buildings/ex_event_buildings.txt" "exoverhaul/ai_suite/common/buildings/ex_planet_unique_buildings.txt" "exoverhaul/ai_suite/common/buildings/ex_resource_buildings.txt" "exoverhaul/ai_suite/common/buildings/ex_sr_buildings.txt" "--replacement_file" "addVirtual.txt"', shell=True)
