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


#TODO: Prio List how to use this:
# 1. Core world important+medium important new building 2. Core world upgrades 3. Core world not so important building 4. Sector new buildings 5. Sector upgrades
# ET = "event_target:cgm_var_storage"
eventNameSpace="cgm_auto.{!s}"
nameBase="cgm_auto_{!s}"
def main():
  os.chdir(os.path.dirname(__file__))
  

  weightTypes=["energy", "minerals", "food", "unity", "society_research", "physics_research", "engineering_research"]
  exampleBuildings=["building_power_plant_1","building_mining_network_1","building_hydroponics_farm_1","building_heritage_site","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1"]
  varsToMove=["Weight","Tile","Type"]

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
  empireBuildEventImmediate.add("set_variable", TagList("which", "cgm_bestWeight_1").add("value", 0))
  findBestPlanet=TagList("limit",TagList("has_building_construction","no").add("free_building_tiles", "0", "", ">").add("or", TagList("and", TagList("sector_controlled","no").add("prev", TagList("has_country_flag", "cgm_core_world_auto"))).add("and", TagList("sector_controlled","yes").add("not", TagList("prev", TagList("has_country_flag", "cgm_core_world_auto"))))))
  empireBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
  findBestPlanet.add("if",TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value", "0","","="))).createEvent(name_planet_find_best, "planet_event"))
  findBestPlanetIf=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value", "prev","",">")))
  findBestPlanet.add("if", findBestPlanetIf)
  findBestPlanetIf.add("save_event_target_as", "cgm_best_planet")
  findBestPlanetIf.add("prev", TagList("set_variable", TagList("which", "cgm_bestWeight_1").add("value", "prev")))

  buildSomeThing=TagList("limit",TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value",0, "", ">")))
  empireBuildEventImmediate.add("if", buildSomeThing)
  planetBuildSomeThing=TagList()
  buildSomeThing.add("event_target:cgm_best_planet", planetBuildSomeThing)
  buildSomeThing.add("else", TagList("set_country_flag", "cgm_noAutobuildPlanetFound"))
  for i, weightType in enumerate(weightTypes):
    ifTypeBest=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestType_1").add("value", i+1))) #todo maybe do else -> when everything is done
    planetBuildSomeThing.add("if", ifTypeBest)
    ifTypeBest.variableOp("set", "cgm_curTile",0)
    everyTileBuild=ifTypeBest.addReturn("every_tile")
    everyTileBuild.addReturn("prev").variableOp("change", "cgm_curTile",1)
    everyTileBuild.createReturnIf(TagList("prev",variableOpNew("check", "cgm_curTile", "cgm_bestTile_1"))).add( "add_building_construction",exampleBuildings[i])
  curSubLevel=planetBuildSomeThing
  for j in reversed(storedValsRange[1:]):
    locSubIf=curSubLevel.createReturnIf(variableOpNew("check", "cgm_bestWeight_{!s}".format(j), 0, ">"))
    # if i==1 and curSubLevel==locIf:
    #   planetBuildSomeThing.add("if", locSubIf)
    # locPrev=locSubIf.addReturn("prev")
    for k in storedValsRange[1:j]:
      for varToMove in varsToMove:
        locSubIf.variableOp("set", "cgm_best"+varToMove+"_{!s}".format(k-1),"cgm_best"+varToMove+"_{!s}".format(k))
      # locSubIf.variableOp("set", "cgm_bestWeight_{!s}".format(k-1),"cgm_bestWeight_{!s}".format(k)).variableOp("set", "cgm_bestTile_{!s}".format(k-1),"cgm_bestTile_{!s}".format(k)) #todo: move other vars
    curSubLevel=TagList()
    locSubIf.add("else", curSubLevel)
    # ifTypeBest.add("Find correct tile and build")


  planetFindBestEvent=TagList("id", name_planet_find_best)
  outTag.add("planet_event", planetFindBestEvent)
  planetFindBestEvent.triggeredHidden()
  # triggeredHidden(planetFindBestEvent)
  planetFindBestEventImmediate=TagList()
  planetFindBestEvent.add("immediate", planetFindBestEventImmediate)
  planetFindBestEventImmediate.variableOp("set", "cgm_curTile", 0) 
  for i in storedValsRange:
    planetFindBestEventImmediate.variableOp("set", "cgm_bestWeight_{!s}".format(i), 0) 
  everyTileSearch=TagList()
  planetFindBestEventImmediate.add("every_tile", everyTileSearch)
  curPrev=everyTileSearch.addReturn("prev")
  curPrev.variableOp("change", "cgm_curTile", 1)
  # curPrev.variableOp("set", "cgm_curWeight", 0)
  # for weight in weightTypes:
  #   curPrev.variableOp("set", weight+"_weight", 0)

  everyTileSearch.addComment("doCALC! test:")
  testif=everyTileSearch.createReturnIf(TagList("prev", variableOp(TagList(), "check", "cgm_curTile", 5)))
  testif.add("prev", variableOp(TagList(),"set", "energy_weight", 25))
  testif.add("prev", variableOp(TagList(),"set", "minerals_weight", 21))
  testif=everyTileSearch.createReturnIf(TagList("prev", variableOp(TagList(), "check", "cgm_curTile", 9)))
  testif.add("prev", variableOp(TagList(),"set", "minerals_weight", 20))
  testif=everyTileSearch.createReturnIf(TagList("prev", variableOp(TagList(), "check", "cgm_curTile", 7)))
  testif.add("prev", variableOp(TagList(),"set", "food_weight", 5))
  everyTileSearch.addComment("END OF example")
  for i, weight in enumerate(weightTypes):
    ifWeightHigher=everyTileSearch.createReturnIf(TagList("prev",variableOp(TagList(), "check", weight+"_weight", "cgm_curWeight", ">")))
    ifWeightHigher.addReturn("prev").variableOp("set", "cgm_curWeight",weight+"_weight").variableOp("set", "cgm_curType",i+1)
  curLevel=everyTileSearch
  for i in storedValsRange:
    locIf=curLevel.createReturnIf(TagList("prev",variableOp(TagList(), "check", "cgm_curWeight", "cgm_bestWeight_{!s}".format(i), ">")))
    curSubLevel=locIf
    for j in reversed(storedValsRange[i:]):
      locSubIf=curSubLevel.createReturnIf(TagList("prev", variableOpNew("check", "cgm_bestWeight_{!s}".format(j-1), 0, ">")))
      # if i==1 and curSubLevel==locIf:
      #   planetBuildSomeThing.add("if", locSubIf)
      locPrev=locSubIf.addReturn("prev")
      for k in reversed(storedValsRange[i:j]):
        for varToMove in varsToMove:
          locPrev.variableOp("set", "cgm_best"+varToMove+"_{!s}".format(k),"cgm_best"+varToMove+"_{!s}".format(k-1))
        # locPrev.variableOp("set", "cgm_bestWeight_{!s}".format(k),"cgm_bestWeight_{!s}".format(k-1)).variableOp("set", "cgm_bestTile_{!s}".format(k),"cgm_bestTile_{!s}".format(k-1)).variableOp("set", "cgm_bestTile_{!s}".format(k),"cgm_bestTile_{!s}".format(k-1)) #todo: move other vars
      curSubLevel=TagList()
      locSubIf.add("else", curSubLevel)
    locPrev=locIf.addReturn("prev")
    for varToMove in varsToMove:
      locPrev.variableOp("set", "cgm_best{}_{!s}".format(varToMove,i),"cgm_cur{}".format(varToMove))

    # variableOp("set", "cgm_bestWeight_{!s}".format(i),"cgm_curWeight").variableOp("set", "cgm_bestTile_{!s}".format(i),"cgm_curTile").variableOp("set", "cgm_bestType_{!s}".format(i),"cgm_curType","=")
    curLevel=TagList()
    locIf.add("else", curLevel)
  curPrev=everyTileSearch.addReturn("prev")
  curPrev.variableOp("set", "cgm_curWeight", 0)
  for weight in weightTypes:
    curPrev.variableOp("set", weight+"_weight", 0)

  # outTag.deleteOnLowestLevel(checkEmpty)
  outTag.deleteOnLowestLevel(checkTotallyEmpty)


  outputToFolderAndFile(outTag, "events", "cgm_auto.txt",2, "../CGM/buildings_script_source")
  with open("test.txt", "w") as file:
    outTag.writeAll(file,args())


if __name__ == "__main__":
  main()