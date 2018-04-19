#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.call('python pythonScripts/createUpgradedBuildings.py "cgm_buildings.mod" "-m" "--output_folder" "exo_mod_rework/CGM_full" "--one_line_level" "2" "--custom_mod_name" "!!Core Game Mechanics: Buildings" "--make_optional"', shell=True)
