#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.call('python ../pythonScripts/locList.py --create_main_file --output_folder "buildings/localisation/" buildings_script_source/localisation/english/cgm_building_l_english.yml', shell=True)
subprocess.call('python ../pythonScripts/locList.py --output_folder "buildings/localisation/" buildings_script_source/localisation/french/cgm_building_l_french.yml', shell=True)
subprocess.call('python buildings_rerun.py', shell=True)
subprocess.call('python buildings/localisation/cgm_building_main.py', shell=True)
subprocess.call('python ../pythonScripts/CGM/disable_non_restricted.py', shell=True)
input("Press Enter to continue...")