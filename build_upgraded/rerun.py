#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "D:/Program Files (x86)/Steam/steamapps/common/Stellaris/common/buildings/*" "--tags" "Builings,Utilities,Fixes" "--picture_file" "thumb_direct_build.png" "-o" "build_upgraded" "--custom_mod_name" "Build Upgraded - Direct construction of high tier buildings"', shell=True)
import fnmatch
for root, dirnames, filenames in os.walk('.'):
	for filename in fnmatch.filter(filenames,'rerun_just_copy_and_check.py'):
		subprocess.call('python "'+os.path.join(root,filename)+'"', shell=True)
