#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.call('python ../pythonScripts/createUpgradedBuildings.py "cgm_buildings_script_source.mod" "-m" "--output_folder" "buildings" "--one_line_level" "2" "--custom_mod_name" "!Core Game Mechanics: Buildings" "--make_optional" "--scripted_variables" "buildings_script_source/common/scripted_variables/cgm_variables.txt"', shell=True)
