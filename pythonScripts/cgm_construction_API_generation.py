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
  with open("../NOTES/api_files/sources/modList.csv", 'r') as file:
    for i,line in enumerate(file):
      if i==0:
        continue #header
      lineSplit=list(map(lambda x:x.strip(),line.split(";")))
      modFolder, modAbbr, modName=lineSplit[:3]
      buildingsIgnoredByBU=[]
      if len(lineSplit)>4:
        buildingsIgnoredByBU=lineSplit[4]
        print(buildingsIgnoredByBU)
      priority=False
      if len(lineSplit)>5 and lineSplit[5].lower()=="yes":
        priority=True
      modFolder="../NOTES/api_files/sources/"+modFolder
      lowPri=[]
      highPri=[]
      if modName<"!Core Game Mechanics: Buildings":
        highPri.append(modFolder)
      if modName>"!Core Game Mechanics: Buildings":
        lowPri.append(modFolder)
      # print(modFolder)
      # print(lowPri)
      # if "gwen" in modFolder:
      # print("automatedCreationAutobuildAPI({},{},{})".format(modAbbr,lowPri,highPri))
      # if modAbbr!="gwen":
        # continue
      automatedCreationAutobuildAPI(modAbbr,lowPri,highPri, 10,"",buildingsIgnoredByBU, modName, priority)
  cgm_planet_auto_API.main()
      


if __name__ == "__main__":
  main()
