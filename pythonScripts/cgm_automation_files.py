#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList
from custom_difficulty_files import *
from functools import reduce

# ET = "event_target:cgm_var_storage"
eventNameSpace="cgm_auto.{!s}"
nameBase="cgm_auto_{!s}"
def main():
  os.chdir(os.path.dirname(__file__))
  

  weightTypes=["energy", "minerals", "food", "unity", "society_research", "physics_research", "engineering_research"]

  name_empire_build_event=eventNameSpace.format(0)

  outTag=TagList("namespace", eventNameSpace.format("")[:-1])

  empireBuildEvent=TagList("id",name_empire_build_event)
  outTag.add("country_event", empireBuildEvent)

  empireBuildEvent.add("is_triggered_only", "yes")
  empireBuildEvent.add("hide_window", "yes")
  empireBuildEventImmediate=TagList()
  empireBuildEvent.add("immediate", empireBuildEventImmediate)
  # empireBuildEventImmediate.add("set_variable", TagList("which", "cgm_currentEmpireMax").add("value", 0))
  empireBuildEventImmediate.add("set_variable", TagList("which", "cgm_bestWeight").add("value", 0))
  findBestPlanet=TagList("limit",TagList("has_building_construction","no").add("free_building_tiles", "0", "", ">"))
  empireBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
  findBestPlanet.add("if",TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight").add("value", "0","","="))).add("cgm_planet_checks", "yes"))#todo: right effect
  findBestPlanetIf=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight").add("value", "prev","",">")))
  findBestPlanet.add("if", findBestPlanetIf)
  findBestPlanetIf.add("save_event_target_as", "cgm_best_planet")
  findBestPlanetIf.add("prev", TagList("set_variable", TagList("which", "cgm_bestWeight").add("value", "prev")))

  buildSomeThing=TagList("limit",TagList("check_variable", TagList("which", "cgm_bestWeight").add("value",0, "", ">")))
  empireBuildEventImmediate.add("if", buildSomeThing)
  planetBuildSomeThing=TagList()
  buildSomeThing.add("event_target:cgm_best_planet", planetBuildSomeThing)
  for i, weightType in enumerate(weightTypes):
    ifTypeBest=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestType").add("value", i+1))) #todo maybe do else -> when everything is done
    planetBuildSomeThing.add("if", ifTypeBest)
    ifTypeBest.add("Find correct tile and build")


  with open("test.txt", "w") as file:
    outTag.writeAll(file,args())


if __name__ == "__main__":
  main()