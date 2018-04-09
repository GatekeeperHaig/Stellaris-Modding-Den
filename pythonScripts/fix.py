#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
from stellarisTxtRead import *
from custom_difficulty_files import *

# tagList=TagList().readFile("../cgm_buildings_script_source/common/buildings/cgm_new_building_content_tile_restricted_resource_buildings.txt",0)
# with open("test.txt",'w') as file:
#   tagList.writeAll(file, args())


# tagList=TagList().readFile("../cgm_buildings_script_source/common/buildings/cgm_new_building_content.txt")
# with open("test3.txt",'w') as file:
#   tagList.writeAll(file, args())

# contentInLine=""
# with open("../cgm_buildings_script_source/common/buildings/cgm_new_building_content.txt") as file:
#   for line in file:
#     if "#" in line:
#       continue
#     contentInLine+=line+"\t"
# tagList,i,j=TagList().readString(contentInLine,False)
# with open("test2.txt",'w') as file:
#   tagList.writeAll(file, args())


# tagList=readFile("../cgm_buildings_script_source/common/buildings/cgm_new_building_content.txt")
# with open("test4.txt",'w') as file:
#   tagList.writeAll(file, args())

# contentInLine=""
# with open("../cgm_buildings_script_source/common/buildings/cgm_new_building_content.txt") as file:
#   for line in file:
#     if "#" in line:
#       continue
#     contentInLine+=line+"\t"
# # print(contentInLine)
# tagList=readString(contentInLine,False)
# with open("test5.txt",'w') as file:
#   tagList.writeAll(file, args())


# contentInLine="test= { conditions_agricultural_processor_1 = yes new_building_content_enabled = yes }"
# tagList=readString(contentInLine)
contentInLine="{ conditions_agricultural_processor_1 = yes new_building_content_enabled = yes }"
tagList=readVal(contentInLine)
print(tagList)