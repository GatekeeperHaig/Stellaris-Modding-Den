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
  name_planet_find_best=eventNameSpace.format(10)

  outTag=TagList("namespace", eventNameSpace.format("")[:-1])
  storedValsRange=range(1,4)

  empireBuildEvent=TagList("id",name_empire_build_event)
  outTag.add("country_event", empireBuildEvent)

  empireBuildEvent.add("is_triggered_only", "yes")
  empireBuildEvent.add("hide_window", "yes")
  empireBuildEventImmediate=TagList()
  empireBuildEvent.add("immediate", empireBuildEventImmediate)
  # empireBuildEventImmediate.add("set_variable", TagList("which", "cgm_currentEmpireMax").add("value", 0))
  empireBuildEventImmediate.add("set_country_flag", "cgm_core_world_auto", " #TODO: remove. just for testing the event")
  empireBuildEventImmediate.add("set_variable", TagList("which", "cgm_bestVal_1").add("value", 0))
  findBestPlanet=TagList("limit",TagList("has_building_construction","no").add("free_building_tiles", "0", "", ">").add("or", TagList("and", TagList("sector_controlled","no").add("has_country_flag", "cgm_core_world_auto")).add("and", TagList("sector_controlled","yes").add("not", TagList("has_country_flag", "cgm_core_world_auto")))))
  empireBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
  findBestPlanet.add("if",TagList("limit", TagList("check_variable", TagList("which", "cgm_bestVal_1").add("value", "0","","="))).createEvent(name_planet_find_best, "planet_event"))
  findBestPlanetIf=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestVal_1").add("value", "prev","",">")))
  findBestPlanet.add("if", findBestPlanetIf)
  findBestPlanetIf.add("save_event_target_as", "cgm_best_planet")
  findBestPlanetIf.add("prev", TagList("set_variable", TagList("which", "cgm_bestVal_1").add("value", "prev")))

  buildSomeThing=TagList("limit",TagList("check_variable", TagList("which", "cgm_bestVal_1").add("value",0, "", ">")))
  empireBuildEventImmediate.add("if", buildSomeThing)
  planetBuildSomeThing=TagList()
  buildSomeThing.add("event_target:cgm_best_planet", planetBuildSomeThing)
  for i, weightType in enumerate(weightTypes):
    ifTypeBest=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestType").add("value", i+1))) #todo maybe do else -> when everything is done
    planetBuildSomeThing.add("if", ifTypeBest)
    ifTypeBest.variableOp("set", "cgm_tileCount",0)
    everyTileBuild=ifTypeBest.addReturn("every_tile")
    everyTileBuild.addReturn("prev").variableOp("change", "cgm_tileCount",1)
    everyTileBuild.createReturnIf(TagList("prev",variableOpNew("check", "cgm_tileCount", "cgm_bestTile_1"))).add( "add_building_construction","building_power_plant_1")
  curSubLevel=planetBuildSomeThing
  for j in reversed(storedValsRange[1:]):
    locSubIf=curSubLevel.createReturnIf(variableOpNew("check", "cgm_bestVal_{!s}".format(j), 0, ">"))
    # if i==1 and curSubLevel==locIf:
    #   planetBuildSomeThing.add("if", locSubIf)
    # locPrev=locSubIf.addReturn("prev")
    for k in storedValsRange[1:j]:
      locSubIf.variableOp("set", "cgm_bestVal_{!s}".format(k-1),"cgm_bestVal_{!s}".format(k)).variableOp("set", "cgm_bestTile_{!s}".format(k-1),"cgm_bestTile_{!s}".format(k)) #todo: move other vars
    curSubLevel=TagList()
    locSubIf.add("else", curSubLevel)
    # ifTypeBest.add("Find correct tile and build")


  planetFindBestEvent=TagList("id", name_planet_find_best)
  outTag.add("planet_event", planetFindBestEvent)
  planetFindBestEvent.triggeredHidden()
  # triggeredHidden(planetFindBestEvent)
  planetFindBestEventImmediate=TagList()
  planetFindBestEvent.add("immediate", planetFindBestEventImmediate)
  planetFindBestEventImmediate.variableOp("set", "cgm_tileCount", 0) 
  for i in storedValsRange:
    planetFindBestEventImmediate.variableOp("set", "cgm_bestVal_{!s}".format(i), 0) 
  everyTileSearch=TagList()
  planetFindBestEventImmediate.add("every_tile", everyTileSearch)
  everyTileSearch.add("prev", variableOp(TagList(),"change", "cgm_tileCount", 1))
  everyTileSearch.addComment("doCALC! test:")
  everyTileSearch.add("prev", variableOp(TagList(),"set", "cgm_curVar", 0))
  testif=everyTileSearch.createReturnIf(TagList("prev", variableOp(TagList(), "check", "cgm_tileCount", 5)))
  testif.add("prev", variableOp(TagList(),"set", "cgm_curVar", 25))
  testif=everyTileSearch.createReturnIf(TagList("prev", variableOp(TagList(), "check", "cgm_tileCount", 9)))
  testif.add("prev", variableOp(TagList(),"set", "cgm_curVar", 20))
  testif=everyTileSearch.createReturnIf(TagList("prev", variableOp(TagList(), "check", "cgm_tileCount", 7)))
  testif.add("prev", variableOp(TagList(),"set", "cgm_curVar", 5))
  curLevel=everyTileSearch
  for i in storedValsRange:
    locIf=curLevel.createReturnIf(TagList("prev",variableOp(TagList(), "check", "cgm_curVar", "cgm_bestVal_{!s}".format(i), ">")))
    curSubLevel=locIf
    for j in reversed(storedValsRange[i:]):
      locSubIf=curSubLevel.createReturnIf(TagList("prev", variableOpNew("check", "cgm_bestVal_{!s}".format(j-1), 0, ">")))
      # if i==1 and curSubLevel==locIf:
      #   planetBuildSomeThing.add("if", locSubIf)
      locPrev=locSubIf.addReturn("prev")
      for k in reversed(storedValsRange[i:j]):
        locPrev.variableOp("set", "cgm_bestVal_{!s}".format(k),"cgm_bestVal_{!s}".format(k-1)).variableOp("set", "cgm_bestTile_{!s}".format(k),"cgm_bestTile_{!s}".format(k-1)) #todo: move other vars
      curSubLevel=TagList()
      locSubIf.add("else", curSubLevel)
    locIf.addReturn("prev").variableOp("set", "cgm_bestVal_{!s}".format(i),"cgm_curVar").variableOp("set", "cgm_bestTile_{!s}".format(i),"cgm_tileCount").variableOp("set", "cgm_bestType".format(i),1,"=").addComment("TODO")
    curLevel=TagList()
    locIf.add("else", curLevel)

  # outTag.deleteOnLowestLevel(checkEmpty)
  outTag.deleteOnLowestLevel(checkTotallyEmpty)


  outputToFolderAndFile(outTag, "events", "cgm_auto.txt",2, "../CGM/buildings_script_source")
  with open("test.txt", "w") as file:
    outTag.writeAll(file,args())


if __name__ == "__main__":
  main()