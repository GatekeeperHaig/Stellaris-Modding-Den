#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import re

work_dir = "test"

# auto upgrade links for autobuild
target_dir = "../gratak_mods/build_upgraded/common/buildings"
		      # ../gratak_mods/build_upgraded/common/buildings/

def make_upgrade(files):
    for file in files:
        with open(file, 'r') as f:
            text = f.read()
        text = re.sub('#+.*\n', '\n', text)
        text = re.sub('\t*\n', '\n', text)
        text = re.sub(' *\n', '\n', text)
        buildings = re.findall(r'\n\w*? = {.*?\n}', text, re.DOTALL)
        for building in buildings:
            if 'upgrades = {' in building:
                name = re.match(r'\n\w* = {', building).group(0).replace(' = {', '')
                print(name)
                upgrade = re.search(r'upgrades = {.*?}', building, re.DOTALL).group(0).replace('upgrades = {', '').replace('}', '').replace('\t', '')
                upgrade = upgrade.split()
                print(upgrade)
                if len(upgrade) == 1:
                    with open(os.path.join(work_dir, 'update_code'), 'a') as f2:
                        f2.write('{0} = {{ add_building_construction = {1} }}'.format(name, upgrade[0]))

make_upgrade(glob.glob(target_dir + '\\*.txt'))
print('done')