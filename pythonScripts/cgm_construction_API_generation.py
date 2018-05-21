#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io,math
from cgm_automation_files import *
import cgm_planet_auto_API

def main():

  os.chdir(os.path.dirname(os.path.abspath(__file__)))

  # createEffectDecisionStuff()
  automatedCreationAutobuildAPI()
  #return
  with open("../NOTES/other mod files used for API files/list of abbrevations used in API files.csv", 'r') as file:
    for line in file:
      lineSplit=list(map(lambda x:x.strip(),line.split(",")))
      modFolder, modAbbr, modName=lineSplit[:3]
      modFolder="../NOTES/other mod files used for API files/"+modFolder
      lowPri=[]
      highPri=[]
      if modName<"!Core Game Mechanics: Buildings":
        highPri.append(modFolder)
      if modName>"!Core Game Mechanics: Buildings":
        lowPri.append(modFolder)
      # print(modFolder)
      # print(lowPri)
      # if "gwen" in modFolder:
      print("automatedCreationAutobuildAPI({},{},{})".format(modAbbr,lowPri,highPri))
      automatedCreationAutobuildAPI(modAbbr,lowPri,highPri)
  cgm_planet_auto_API.main()
      


if __name__ == "__main__":
  main()
