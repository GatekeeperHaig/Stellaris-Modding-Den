#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io,math
from cgm_automation_files import *

def main():

  os.chdir(os.path.dirname(__file__))

  modFolder="../CGM/cgm_planets_enhanced/common"
  lowPri=[]
  highPri=[]
      # if modName<"!Core Game Mechanics: Buildings":
  highPri.append(modFolder)
      # if modName>"!Core Game Mechanics: Buildings":
        # lowPri.append(modFolder)
      # print(modFolder)
      # print(lowPri)
      # if "gwen" in modFolder:
  modAbbr="cgm_planets"
  print("automatedCreationAutobuildAPI({},{},{},10,../CGM/cgm_planets_enhanced)".format(modAbbr,lowPri,highPri))
  automatedCreationAutobuildAPI(modAbbr,lowPri,highPri,10,"../CGM/cgm_planets_enhanced")


if __name__ == "__main__":
  main()
