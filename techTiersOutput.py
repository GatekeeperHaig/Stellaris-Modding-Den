#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
# os.chdir('..')
subprocess.call("python convertCSV_TXT.py -j 'combat-overhaul-beta/common/technology/*.txt' --manual_filter combat-overhaul-beta/common/technology/costTierWeight.filter", shell=True)
