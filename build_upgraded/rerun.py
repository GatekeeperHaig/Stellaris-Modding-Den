#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')
subprocess.call('python ./createUpgradedBuildings.py "D:/Program Files (x86)/Steam/steamapps/common/Stellaris/common/buildings/*"', shell=True)
