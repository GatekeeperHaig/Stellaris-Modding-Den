#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io,inspect
from copy import deepcopy
from googletrans import Translator
import re
from functools import reduce
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from stellarisTxtRead import *
from custom_difficulty_files import *

def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  buildingsFile=readFile("../../CGM/buildings/common/buildings/cgm_new_building_content.txt")
  nonRestricted=False
  for name,val,comment,seperator in buildingsFile.getAll():
    if nonRestricted:
      if "### Tile Restricted Resource Buildings" in comment:
        break
      if name!="" and val.attemptGet("is_listed").lower()!="no":
        prodRes=val.get("produced_resources").names[0]
        val.get("potential").add("OR", TagList("tile", TagList("NOT", TagList("has_resource", TagList("type", prodRes).add("amount", 0, "", ">")))).add("planet_is_artificial", "yes"))
    else:
      if "### Non-restricted Resource Buildings" in comment:
        nonRestricted=True
  outputToFolderAndFile(buildingsFile, "common/buildings", "cgm_new_building_content.txt",2, "../../CGM/buildings", False)





if __name__ == "__main__":
  main()