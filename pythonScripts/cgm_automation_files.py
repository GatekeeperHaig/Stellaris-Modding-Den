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
#possible far away todo: Replace worst existing building with (empire) unique
eventNameSpace="cgm_auto.{!s}"
nameBase="cgm_auto_{!s}"
def main():

  debug=True
  os.chdir(os.path.dirname(__file__))
  
  # weightTypes=["energy", "minerals", "food", "unity", "society_research", "physics_research", "engineering_research"]
  weightTypes=["energy", "minerals", "food", "base_res_adjacency", "society_research", "physics_research", "engineering_research", "science_adjacency"]
  exampleBuildings=["building_power_plant_1","building_mining_network_1","building_hydroponics_farm_1","building_power_hub_1","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1"]
  varsToMove=["Weight","Tile","Type"]
  pseudoInf=99999

  name_empire_main_build_event=eventNameSpace.format(0)
  name_empire_standard_build_event=eventNameSpace.format(10)
  name_empire_special_build_event=eventNameSpace.format(11)
  name_planet_find_best=eventNameSpace.format(20)

  outTag=TagList("namespace", eventNameSpace.format("")[:-1])
  storedValsRange=range(1,4)

  outTag.addComment('there are 3*3 types of important variables used in these events:\n# "cur_" is always for the tile we are currently in,\n# "best_" is previously found best tiles.\n# "worst_" is previously found worst tiles -> to be used with special buildings who do not requre special tiles.\n#Each can be combined with\n# "Type", which is a number assigned to the different weight-type\n# "weight", which is the actual weight value\n# "Tile", which is the "id" of a tile')

#   direct_build_affects_autobuild_init = {
#     set_global_flag = display_low_tier_flag
# }

# direct_build_affects_autobuild_finish = {
#     if = {
#       limit = { NOT = { has_global_flag = do_no_remove_low_tier_flag } }
#             remove_global_flag = display_low_tier_flag
#     }
# }

  empireMainBuildEvent=TagList("id",name_empire_main_build_event)
  outTag.add("country_event", empireMainBuildEvent)
  empireMainBuildEvent.triggeredHidden()
  empireMainBuildEventImmediate=empireMainBuildEvent.addReturn("immediate")
  empireMainBuildEventImmediate.add("remove_country_flag", "cgm_auto_built")
  empireMainBuildEventImmediate.add("set_country_flag", "display_low_tier_flag", "#The buildings we create are otherwise probably unavaiable due to direct build. Later removed again.")
  empireMainBuildEventImmediate.add("set_country_flag", "cgm_core_world_auto", "#searching core worlds for standard buildings")
  empireMainBuildEventImmediate.addComment("Search for possible Special buildings:")
  empireMainBuildEventImmediate.createEvent(name_empire_special_build_event)
  empireMainBuildEventImmediate.addComment("Search for possible Standard buildings. Build best out of standard/special:")
  empireMainBuildEventImmediate.createEvent(name_empire_standard_build_event)
  #disabl for better testing(no deletion of variables):
  sectorBuild=empireMainBuildEventImmediate.createReturnIf(TagList("not", TagList("has_country_flag", "cgm_auto_built")))
  sectorBuild.add("remove_country_flag", "cgm_core_world_auto", "#searching sector worlds for standard buildings")
  sectorBuild.addComment("Search for possible Special buildings:")
  sectorBuild.createEvent(name_empire_standard_build_event)
  sectorBuild.addComment("Search for possible Standard buildings. Build best out of standard/special:")
  sectorBuild.createEvent(name_empire_standard_build_event)
  empireMainBuildEventImmediate.createReturnIf(TagList("NOT", TagList("has_country_flag", "do_no_remove_low_tier_flag"))).add("remove_country_flag", "display_low_tier_flag")


  outTriggers=TagList()
  outTriggers.addComment("this = planet")
  outTriggers.addComment("prev = tile")
  outTriggers.addComment("prevprev = planet. Don't use this!")
  outTriggers.addComment("owner = country.")
  outTriggers.addComment("Check if any building of the type is available, including tech requ check. Can be left empty if there are non-unique buildings without tech requ in the category. ")
  outEffects=TagList()
  outEffects.addComment("this = tile")
  outEffects.addComment("prev = planet")
  outEffects.addComment("prevprev = country")
  outEffects.addComment("Build the building that fits the category defined in the name of each trigger.")
  outEffects.addComment("Check if unique buildings of that category can be build first and do so if possible")
  outEffects.addComment("Leave the 'succesful ->set flag' at the end as it is")

  empireStandardBuildEvent=TagList("id",name_empire_standard_build_event)
  outTag.add("country_event", empireStandardBuildEvent)
  empireStandardBuildEvent.triggeredHidden()
  empireStandardBuildEventImmediate=TagList()
  empireStandardBuildEvent.add("immediate", empireStandardBuildEventImmediate)

  empireStandardBuildEventImmediate.variableOp("set","cgm_bestWeight_1", 0) #TODO move to buttom of event to leave less trash
  findBestPlanet=TagList()
  findBestPlanetLimit=findBestPlanet.addReturn("limit")
  findBestPlanetLimit.add("has_building_construction","no")
  findBestPlanetLimit.add("free_building_tiles", "0", "", ">")
  findBestPlanetLimit.add("not",TagList("has_planet_flag", "purged_planet"))
  findBestPlanetLimit.add("or", TagList("and", TagList("sector_controlled","no").add("prev", TagList("has_country_flag", "cgm_core_world_auto"))).add("and", TagList("sector_controlled","yes").add("not", TagList("prev", TagList("has_country_flag", "cgm_core_world_auto")))))
  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("or", TagList("is_growing", "yes").add("is_unemployed","yes")))
  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("is_unemployed","yes")) #seems not to work
  findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("NOR",TagList("tile",TagList("has_building","yes").add("has_building_construction","yes"))))
  # findBestPlanetLimit.
  empireStandardBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
  if debug:
    findBestPlanet.add("log", '"searching on planet [this.GetName]"')
  findBestPlanet.add("if",TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value", "0","","="))).createEvent(name_planet_find_best, "planet_event"))
  findBestPlanetIf=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value", "prev","",">")))
  findBestPlanet.add("if", findBestPlanetIf)
  findBestPlanetIf.add("save_event_target_as", "cgm_best_planet")
  findBestPlanetIf.add("prev", TagList("set_variable", TagList("which", "cgm_bestWeight_1").add("value", "prev")))

  if debug:
    empireStandardBuildEventImmediate.add("log",'"bestStandard:[this.cgm_bestWeight_1]"')
    empireStandardBuildEventImmediate.add("log",'"bestSpecial:[this.cgm_special_bestWeight]"')
  buildSomeThing=TagList("limit",TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value","cgm_special_bestWeight", "", ">")))
  empireStandardBuildEventImmediate.add("if", buildSomeThing)
  planetBuildSomeThing=TagList()
  buildSomeThing.add("event_target:cgm_best_planet", planetBuildSomeThing)
  buildSpecial=buildSomeThing.addReturn("else")
  buildSpecial=buildSpecial.addReturn("event_target:cgm_best_planet_for_special")
  redoCalcForWorstTile=buildSpecial.createReturnIf(variableOpNew("check","cgm_worstWeight",pseudoInf))
  redoCalcForWorstTile.createEvent(name_planet_find_best,"planet_event")
  if debug:
    buildSpecial.add("log",'"worst tile::[this.cgm_worstTile]"')
  buildSpecial.variableOp("set", "cgm_curTile",0)
  buildSpecialTile=buildSpecial.addReturn("every_tile")
  buildSpecialTile.addReturn("prev").variableOp("change", "cgm_curTile",1)
  buildSpecialTile=buildSpecialTile.createReturnIf(TagList("prev",variableOpNew("check", "cgm_curTile", "cgm_worstTile")))

  buildSpecialTile.add("cgm_add_special_building","yes")
  effect=outEffects.addReturn("cgm_add_special_building")
  if debug:
    effect.add("log", '"trying to build special on tile [prev.cgm_curTile]"')
  effect.addComment("SPECIAL BUILDING NUMBER 1:")
  effect.createReturnIf(TagList("prev.owner", variableOpNew("check", "cgm_special_bestBuilding", 1))).add("add_building_construction", "building_autochthon_monument")
  effect.addComment("SPECIAL BUILDING NUMBER 2:")
  effect.createReturnIf(TagList("prev.owner", variableOpNew("check", "cgm_special_bestBuilding", 2))).add("add_building_construction", "building_fortress")
  effect.createReturnIf(TagList("or", TagList("has_building","yes").add("has_building_construction", "yes"))).add("prevprev",TagList("set_country_flag", "cgm_auto_built"))
  buildSpecial.variableOp("set", "cgm_worstWeight", pseudoInf)


  # buildSomeThing.add("else", TagList("set_country_flag", "cgm_noAutobuildPlanetFound"))
  for i, weightType in enumerate(weightTypes):
    ifTypeBest=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestType_1").add("value", i+1))) #todo maybe do else -> when everything is done
    planetBuildSomeThing.add("if", ifTypeBest)
    ifTypeBest.variableOp("set", "cgm_curTile",0)
    everyTileBuild=ifTypeBest.addReturn("every_tile")
    everyTileBuild.addReturn("prev").variableOp("change", "cgm_curTile",1)
    everyTileBuild.createReturnIf(TagList("prev",variableOpNew("check", "cgm_curTile", "cgm_bestTile_1"))).add("add_"+weightType+"_building","yes" )
    
    effect=TagList()
    outEffects.insert(0,"add_"+weightType+"_building",effect)
    if debug:
      effect.add("log", '"trying to build standard on tile [prev.cgm_curTile]"')
    effect.add("add_building_construction",exampleBuildings[i])
    effect.createReturnIf(TagList("or", TagList("has_building","yes").add("has_building_construction", "yes"))).add("prevprev",TagList("set_country_flag", "cgm_auto_built"))
  curSubLevel=planetBuildSomeThing
  for j in reversed(storedValsRange[1:]):
    locSubIf=curSubLevel.createReturnIf(variableOpNew("check", "cgm_bestWeight_{!s}".format(j), 0, ">"))
    # if i==1 and curSubLevel==locIf:
    #   planetBuildSomeThing.add("if", locSubIf)
    # locPrev=locSubIf.addReturn("prev")
    for k in storedValsRange[1:j]:
      for varToMove in varsToMove:
        locSubIf.variableOp("set", "cgm_best"+varToMove+"_{!s}".format(k-1),"cgm_best"+varToMove+"_{!s}".format(k))
    locSubIf.variableOp("set", "cgm_bestWeight_{!s}".format(j), 0)
    curSubLevel=TagList()
    locSubIf.add("else", curSubLevel)
  curSubLevel.variableOp("set", "cgm_bestWeight_1".format(j), 0)
    # ifTypeBest.add("Find correct tile and build")


  empireSpecialBuildEvent=TagList("id",name_empire_special_build_event)
  outTag.add("country_event", empireSpecialBuildEvent)
  empireSpecialBuildEvent.triggeredHidden()
  empireSpecialBuildEventImmediate=TagList()
  empireSpecialBuildEvent.add("immediate", empireSpecialBuildEventImmediate)

  empireSpecialBuildEventImmediate.variableOp("set","cgm_special_bestWeight", 0) #don't move to button as this is later used!
  findBestPlanet=TagList()
  findBestPlanetLimit=findBestPlanet.addReturn("limit")
  findBestPlanetLimit.add("has_building_construction","no")
  findBestPlanetLimit.add("free_building_tiles", "0", "", ">")
  findBestPlanetLimit.add("not",TagList("has_planet_flag", "purged_planet"))
  findBestPlanetLimit.add("or", TagList("and", TagList("sector_controlled","no").add("prev", TagList("has_country_flag", "cgm_core_world_auto"))).add("and", TagList("sector_controlled","yes").add("not", TagList("prev", TagList("has_country_flag", "cgm_core_world_auto")))))
  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("or", TagList("is_growing", "yes").add("is_unemployed","yes")))
  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("is_unemployed","yes")) #seems not to work
  findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("NOR",TagList("tile",TagList("has_building","yes").add("has_building_construction","yes"))))
  # findBestPlanetLimit.
  empireSpecialBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
    
  findBestPlanet.add("cgm_search_for_special_building", "yes")
  outEffects.addComment("Special SEARCH effect:\n# this = planet\n#  prev/owner = country")
  effect=outEffects.addReturn("cgm_search_for_special_building")
  effect.addComment("TODO search for special building!")
  effect.addComment("define tmp global event target to the planet we want to build on and a tile specification on that scope. We can later use those to build when this weight is better than the general one")
  if debug:
    effect.add("log", '"searching for special buildings on planet [this.GetName]"')
  effect.addComment("SPECIAL BUILDING NUMBER 1:")
  chooseSpecialBuilding=effect.createReturnIf(TagList("NOT", TagList("has_building","building_autochthon_monument")).add("prev",variableOpNew("check", "cgm_special_bestWeight", 20, "<")))
  chooseSpecialBuilding.addReturn("prev").variableOp("set","cgm_special_bestWeight", 20).variableOp("set","cgm_special_bestBuilding", 1)
  chooseSpecialBuilding.add("save_global_event_target_as", "cgm_best_planet_for_special")
  effect.addComment("SPECIAL BUILDING NUMBER 2: FORTRESS")
  effect.variableOp("set", "cgm_special_bestWeight", 10)
  effect.addComment("cgm_special_bestWeight named like this for easier comparison! Local scope!")
  chooseSpecialBuilding=effect.createReturnIf(TagList("has_planet_flag","NEEDS_DEFENSE").variableOp("multiply", "cgm_special_bestWeight", 4))
  chooseSpecialBuilding=effect.createReturnIf(variableOpNew("check", "cgm_special_bestWeight", "prev", ">"))
  chooseSpecialBuilding.addReturn("prev").variableOp("set","cgm_special_bestWeight", "prev").variableOp("set","cgm_special_bestBuilding", 2)
  chooseSpecialBuilding.add("save_global_event_target_as", "cgm_best_planet_for_special")
    # (findBestPlanet.addReturn("prev")).variableOp("set","cgm_special_bestWeight", 20, "=", " #TODO just a test!")
    # findBestPlanet.add("save_global_event_target_as", "cgm_best_planet_for_special"," #TODO just a test!")





  planetFindBestEvent=TagList("id", name_planet_find_best)
  outTag.add("planet_event", planetFindBestEvent)
  planetFindBestEvent.triggeredHidden()
  # triggeredHidden(planetFindBestEvent)
  planetFindBestEventImmediate=TagList()
  planetFindBestEvent.add("immediate", planetFindBestEventImmediate)
  planetFindBestEventImmediate.variableOp("set", "cgm_curTile", 0) 
  for i in storedValsRange:
    planetFindBestEventImmediate.variableOp("set", "cgm_bestWeight_{!s}".format(i), 0) 
  planetFindBestEventImmediate.addComment("set worst value to very large number, such that any found tile is initially worse")
  planetFindBestEventImmediate.variableOp("set", "cgm_worstWeight".format(varToMove),pseudoInf)
  everyTileSearch=TagList()
  planetFindBestEventImmediate.add("every_tile", everyTileSearch)
  curPrev=everyTileSearch.addReturn("prev")
  curPrev.variableOp("change", "cgm_curTile", 1)
  everyTileSearch=everyTileSearch.createReturnIf(TagList("has_building","no"))
  # curPrev.variableOp("set", "cgm_curWeight", 0)
  # for weight in weightTypes:
  #   curPrev.variableOp("set", weight+"_weight", 0)

  everyTileSearch.addComment("doCALC! test:")
  everyTileSearch=everyTileSearch.addReturn("prev")
  testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 5))
  testif.variableOp("set", "energy_weight", 25)
  testif.variableOp("set", "minerals_weight", 21)
  testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 9))
  testif.variableOp("set", "minerals_weight", 20)
  testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 7))
  testif.variableOp("set", "food_weight", 5)
  testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 1))
  testif.variableOp("set", "base_res_adjacency_weight", 27)
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 2)) #removing the test of defining more of these. These lead to strange behavior (special building earlier than it should) in current version, but that would not be a problem in the final version: A new adjacency building would anyway trigger a recomp of weights!
  # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 3))
  # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 4))
  # testif.variableOp("set", "base_res_adjacency_weight", 29)
  everyTileSearch.addComment("END OF example")
  for i, weight in enumerate(weightTypes):
    ifWeightHigher=everyTileSearch.createReturnIf(variableOp(TagList(), "check", weight+"_weight", "cgm_curWeight", ">").add(weight+"_any_building_available", "yes"))
    # if "adjacency" in weight:
    if weight=="base_res_adjacency":
      outTriggers.add(weight+"_any_building_available", TagList("not",  TagList("has_building","building_power_hub_1")))
    else:
      outTriggers.add(weight+"_any_building_available", TagList())
    ifWeightHigher.variableOp("set", "cgm_curWeight",weight+"_weight").variableOp("set", "cgm_curType",i+1)
  curLevel=everyTileSearch
  for i in storedValsRange:
    locIf=curLevel.createReturnIf(variableOp(TagList(), "check", "cgm_curWeight", "cgm_bestWeight_{!s}".format(i), ">"))
    curSubLevel=locIf
    for j in reversed(storedValsRange[i:]):
      locSubIf=curSubLevel.createReturnIf(variableOpNew("check", "cgm_bestWeight_{!s}".format(j-1), 0, ">"))
      # if i==1 and curSubLevel==locIf:
      #   planetBuildSomeThing.add("if", locSubIf)
      # locPrev=locSubIf.addReturn("prev")
      for k in reversed(storedValsRange[i:j]):
        for varToMove in varsToMove:
          locSubIf.variableOp("set", "cgm_best"+varToMove+"_{!s}".format(k),"cgm_best"+varToMove+"_{!s}".format(k-1))
      curSubLevel=TagList()
      locSubIf.add("else", curSubLevel)
    # locPrev=locIf.addReturn("prev")
    for varToMove in varsToMove:
      locIf.variableOp("set", "cgm_best{}_{!s}".format(varToMove,i),"cgm_cur{}".format(varToMove))

    curLevel=TagList()
    locIf.add("else", curLevel)

  #finding the worst of the best: best over weightTypes, worst over tiles
  locIf=everyTileSearch.createReturnIf(variableOp(TagList(), "check", "cgm_curWeight", "cgm_worstWeight", "<"))
  for varToMove in varsToMove[:-1]: #:-1 as type is not needed. Don't care about type here
    locIf.variableOp("set", "cgm_worst{}".format(varToMove),"cgm_cur{}".format(varToMove))

  # curPrev=everyTileSearch.addReturn("prev")
  everyTileSearch.variableOp("set", "cgm_curWeight", 0)
  for weight in weightTypes:
    everyTileSearch.variableOp("set", weight+"_weight", 0)

  # outTag.deleteOnLowestLevel(checkEmpty)
  outTag.deleteOnLowestLevel(checkTotallyEmpty)


  outputToFolderAndFile(outTag, "events", "cgm_auto.txt",2, "../CGM/buildings_script_source")
  if debug:
    outputToFolderAndFile(outTriggers, "common/scripted_triggers", "cgm_auto_trigger_template.txt",2, "../CGM/buildings_script_source")
    outputToFolderAndFile(outEffects, "common/scripted_effects", "cgm_auto_effects_template.txt",2, "../CGM/buildings_script_source")
  # with open("test.txt", "w") as file:
  #   outTag.writeAll(file,args())





if __name__ == "__main__":
  main()