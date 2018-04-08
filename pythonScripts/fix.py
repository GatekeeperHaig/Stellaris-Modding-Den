#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
from stellarisTxtRead import *

tagList=TagList().readFile("../cgm_buildings_script_source/common/buildings/cgm_new_building_content_tile_restricted_resource_buildings.txt",0)
with open("test.txt",'w') as file:
  tagList.writeAll(file)