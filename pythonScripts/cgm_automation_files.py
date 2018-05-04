#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io,math
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList
from custom_difficulty_files import *
from functools import reduce
import glob


#TODO: Prio List how to use this:
# 1. Core world important+medium important new building 2. Core world upgrades 3. Core world not so important building 4. Sector new buildings 5. Sector upgrades
#possible far away todo: Replace worst existing building with (empire) unique
#TODO: event target: global -> local
#todo:we need to add a special effect for AI, which optimizes capitals #remove them on placement and instant create them anew 
eventNameSpace="cgm_auto.{!s}"
nameBase="cgm_auto_{!s}"
def main():

  debug=False
  os.chdir(os.path.dirname(__file__))
  
  # weightTypes=["energy", "minerals", "food", "unity", "society_research", "physics_research", "engineering_research"]
  weightTypes=["energy", "minerals", "food", "society_research", "physics_research", "engineering_research"]
  for weight in deepcopy(weightTypes):
    weightTypes.append(weight+"_adjacency")
  resources=["energy", "minerals", "food","unity", "society_research", "physics_research", "engineering_research"]
  inverseFactorComparedToMinerals=[4,1,4,4,2,2,2]
  exampleBuildings=["building_power_plant_1","building_mining_network_1","building_hydroponics_farm_1","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1","building_power_hub_1","building_power_hub_1","building_power_hub_1","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1"]
  varsToMove=["Weight","Tile","Type"]
  pseudoInf=99999
  countToNeg=range(8)
  countToPos=range(15)
  subCount=range(1,10)
  starvationWeight=100

  name_empire_main_build_event=eventNameSpace.format(0)
  name_empire_standard_build_event=eventNameSpace.format(10)
  name_empire_special_build_event=eventNameSpace.format(11)
  name_empire_upgrade_event=eventNameSpace.format(12)
  name_planet_find_best=eventNameSpace.format(20)
  name_update_modifiers_on_all_planets=eventNameSpace.format(21)
  name_update_modifiers_on_planet=eventNameSpace.format(22)
  name_empire_weights=eventNameSpace.format(30)
  name_player_weights_country=eventNameSpace.format(40)
  name_player_weights_planet=eventNameSpace.format(41)

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
  resetAll=empireMainBuildEventImmediate.createReturnIf(TagList("has_country_flag","cgm_redo_all_planet_calcs"))
  resetAll.add("remove_country_flag", "cgm_redo_all_planet_calcs")
  resetAll=resetAll.addReturn("every_owned_planet")
  resetAll.variableOp("set", "cgm_worstWeight", pseudoInf)
  for i in storedValsRange:
    resetAll.variableOp("set", "cgm_bestWeight_{!s}".format(i), 0)
  

  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("tile",TagList("NOR",TagList("has_building","yes").add("has_building_construction","yes"))))

  #added to different file. DO NOT DELETE!
  # everyHalfYear=empireMainBuildEventImmediate.createReturnIf(TagList("NOT", TagList("has_country_flag", "cgm_empire_weights_computed_timed")))
  # everyHalfYear.createEvent(name_empire_weights)

  #added to different file. DO NOT DELETE!
  # empireMainBuildEventImmediate.variableOp("set", "cgm_free_pops", 0)
  # empireMainBuildEventImmediate.variableOp("set", "cgm_non_filled_planet_count", 0)
  # countFreePops=empireMainBuildEventImmediate.addReturn("every_owned_planet")
  # countFreePops.add("limit", TagList("free_building_tiles", "0","",">"))
  # countFreePops.addReturn("prev").variableOp("change", "cgm_non_filled_planet_count", 1)
  # countFreePops.variableOp("set", "cgm_free_pops", 0)
  # countFreePops.add("every_pop", TagList("limit", TagList("OR", TagList("is_colony_pop", "yes").add("is_growing", "yes")).add("tile",TagList("NOR",TagList("has_building","yes").add("has_building_construction","yes"))).add("OR", TagList("is_being_purged", "no").add("has_purge_type", TagList("type", "purge_labor_camps")))).add("prev", variableOpNew("change", "cgm_free_pops", 1)))
  # countFreePops.addReturn("prev").variableOp("change", "cgm_free_pops", "prev")


  empireMainBuildEventImmediate.add("set_country_flag", "display_low_tier_flag", "#The buildings we create are otherwise probably unavaiable due to direct build. Later removed again.")
  standard_build=empireMainBuildEventImmediate.createReturnIf(TagList("not", TagList("has_country_flag", "cgm_sector_autobuild")))
  standard_build.add("set_country_flag", "cgm_core_world_auto", "#searching core worlds for standard buildings")
  standard_build.addComment("Search for possible Special buildings:")
  standard_build.createEvent(name_empire_special_build_event)
  standard_build.addComment("Search for possible Standard buildings. Build best out of standard/special:")
  standard_build.createEvent(name_empire_standard_build_event)
  upgrade_build=standard_build.createReturnIf(TagList("is_ai", "no").add("not", TagList("has_country_flag", "cgm_auto_built")))
  upgrade_build.addComment("Try to upgrade something. Player only!")
  upgrade_build.createEvent(name_empire_upgrade_event)
  #disabl for better testing(no deletion of variables):
  sectorBuild=empireMainBuildEventImmediate.createReturnIf(TagList("not", TagList("has_country_flag", "cgm_auto_built")))
  sectorBuild.add("remove_country_flag", "cgm_core_world_auto", "#searching sector worlds for standard buildings")
  sectorBuild.addComment("Search for possible Special buildings:")
  sectorBuild.createEvent(name_empire_special_build_event)
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
  findBestPlanetLimit.variableOp("check", "cgm_free_pops", 0, ">")
  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("tile",TagList("NOR",TagList("has_building","yes").add("has_building_construction","yes"))))
  # findBestPlanetLimit.
  empireStandardBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
  if debug:
    findBestPlanet.add("log", '"searching on planet [this.GetName]"')
  findBestPlanet.add("if",TagList("limit", TagList("OR", TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value", "0","","=")).add("has_planet_flag", "cgm_redo_planet_calc"))).createEvent(name_planet_find_best, "planet_event"))
  findBestPlanetIf=TagList("limit", TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value", "prev","",">")))
  findBestPlanet.add("if", findBestPlanetIf)
  findBestPlanetIf.add("save_event_target_as", "cgm_best_planet")
  findBestPlanetIf.add("prev", TagList("set_variable", TagList("which", "cgm_bestWeight_1").add("value", "prev")))

  # empireStandardBuildEventImmediate.add("remove_country_flag", "cgm_redo_all_planet_calcs")
  if debug:
    empireStandardBuildEventImmediate.add("log",'"bestStandard:[this.cgm_bestWeight_1]"')
    empireStandardBuildEventImmediate.add("log",'"bestSpecial:[this.cgm_special_bestWeight]"')
  buildSomeThing=TagList("limit",TagList("check_variable", TagList("which", "cgm_bestWeight_1").add("value","cgm_special_bestWeight", "", ">")))
  empireStandardBuildEventImmediate.add("if", buildSomeThing)
  planetBuildSomeThing=TagList()
  buildSomeThing.createReturnIf(variableOpNew("check","cgm_bestWeight_1", 0 ,">")).add("event_target:cgm_best_planet", planetBuildSomeThing)
  buildSpecial=buildSomeThing.addReturn("else")
  buildSpecial=buildSpecial.createReturnIf(variableOpNew("check","cgm_special_bestWeight", 0 ,">"))
  buildSpecial=buildSpecial.addReturn("event_target:cgm_best_planet_for_special")
  redoCalcForWorstTile=buildSpecial.createReturnIf(variableOpNew("check","cgm_worstWeight",pseudoInf))
  redoCalcForWorstTile.createEvent(name_planet_find_best,"planet_event")
  if debug:
    buildSpecial.add("log",'"worst tile::[this.cgm_worstTile]"')
    buildSpecial.add("log",'"worst weight::[this.cgm_worstWeight]"')
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
  ifTypeBest=planetBuildSomeThing
  for i, weightType in enumerate(weightTypes):
    ifTypeBest=ifTypeBest.createReturnIf(TagList("check_variable", TagList("which", "cgm_bestType_1").add("value", i+1)))
    # ifTypeBest= 
    # planetBuildSomeThing.add("if", ifTypeBest)
    ifTypeBest.variableOp("set", "cgm_curTile",0)
    everyTileBuild=ifTypeBest.addReturn("every_tile")
    everyTileBuild.addReturn("prev").variableOp("change", "cgm_curTile",1)
    everyTileBuild.createReturnIf(TagList("prev",variableOpNew("check", "cgm_curTile", "cgm_bestTile_1"))).add("add_"+weightType+"_building","yes" )
    ifTypeBest=ifTypeBest.addReturn("else")
    
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
  findBestPlanetLimit.variableOp("check", "cgm_free_pops", 0, ">")
  # findBestPlanetLimit.add("any_pop", TagList("is_colony_pop", "yes").add("tile",TagList("NOR",TagList("has_building","yes").add("has_building_construction","yes"))))
  # findBestPlanetLimit.
  empireSpecialBuildEventImmediate.add("every_owned_planet",  findBestPlanet)
    
  findBestPlanet.add("cgm_search_for_special_building", "yes")
  outEffects.addComment("Special SEARCH effect:\n# this = planet\n#  prev/owner = country")
  effect=outEffects.addReturn("cgm_search_for_special_building")
  effect.addComment("Search for special building!")
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

  cgmCompTrigger=TagList().readFile("../CGM/buildings_script_source/common/scripted_effects/z_cgm_compatibility_effects.txt")


  planetFindBestEvent=TagList("id", name_planet_find_best)
  outTag.add("planet_event", planetFindBestEvent)
  planetFindBestEvent.triggeredHidden()
  # triggeredHidden(planetFindBestEvent)
  planetFindBestEventImmediate=TagList()
  planetFindBestEvent.add("immediate", planetFindBestEventImmediate)
  planetFindBestEventImmediate.add("remove_planet_flag","cgm_redo_planet_calc")
  planetFindBestEventImmediate.variableOp("set", "cgm_curTile", 0) 
  for i in storedValsRange:
    planetFindBestEventImmediate.variableOp("set", "cgm_bestWeight_{!s}".format(i), 0) 
  planetFindBestEventImmediate.addComment("set worst value to very large number, such that any found tile is initially worse")
  planetFindBestEventImmediate.variableOp("set", "cgm_worstWeight".format(varToMove),pseudoInf)


  planetFindBestEventImmediate=planetFindBestEventImmediate.createReturnIf(TagList("NOT", TagList("any_owned_pop", TagList("is_being_purged", "no")))).add("set_planet_flag", "purged_planet")
  planetFindBestEventImmediate=planetFindBestEventImmediate.addReturn("else")
  planetFindBestEventImmediate.addComment("modifiers are updated yearly!")

  modifierUpdate=TagList("id", name_update_modifiers_on_all_planets)
  outTag.add("event", modifierUpdate)
  modifierUpdate.triggeredHidden()
  modifierUpdateSingle=TagList("id", name_update_modifiers_on_planet)
  outTag.add("planet_event", modifierUpdateSingle)
  modifierUpdateSingle.triggeredHidden()
  recheckModifiers=modifierUpdate.addReturn("immediate")
  recheckModifiers=recheckModifiers.addReturn("every_country")
  recheckModifiers=recheckModifiers.addReturn("every_owned_planet")
  # recheckModifiers=planetFindBestEventImmediate.createReturnIf(TagList("has_planet_flag", "cgm_modifier_calc_done"))
  for resource in resources:
    recheckModifiers.variableOp("set", resource+"_mult_planet_base_old", resource+"_mult_planet_base")
    recheckModifiers.variableOp("set", resource+"_mult_planet_base", 0)
  recheckModifiers.add("check_vanilla_planet_modifiers","yes")
  for name in cgmCompTrigger.names:
    if "check_planet_modifiers" in name:
      recheckModifiers.add(name,"yes")
  # recheckModifiers.add("check_planet_modifiers_pe","yes")
  # recheckModifiers.add("check_planet_modifiers_gpm","yes")
  # recheckModifiers.add("check_planet_modifiers_pd","yes")
  # recheckModifiers.add("check_planet_modifiers_am","yes")
  # recheckModifiers.add("check_planet_modifiers_se","yes")
  # recheckModifiers.add("check_planet_modifiers_gse","yes")
  redoLimit=TagList()
  redoOr=redoLimit.addReturn("NAND")
  for resource in resources:
    redoOr.variableOp("check", resource+"_mult_planet_base_old", resource+"_mult_planet_base")
  recheckModifiers.createReturnIf(redoLimit).add("set_planet_flag", "cgm_redo_planet_calc")
  modifierUpdateSingle.add("immediate", recheckModifiers)

  recheckBuildings=planetFindBestEventImmediate.createReturnIf(TagList("has_planet_flag", "cgm_bonus_building_calc_done"))
  for resource in resources:
    recheckBuildings.variableOp("set", resource+"_mult_planet_building", 0)
  recheckBuildings.add("check_planet_bonus_buildings","yes")
  for name in cgmCompTrigger.names:
    if "check_planet_bonus_buildings" in name:
      recheckBuildings.add(name,"yes")
  # recheckBuildings.add("check_planet_bonus_buildings_pe","yes")
  # recheckBuildings.add("check_planet_bonus_buildings_am","yes")
  # recheckBuildings.add("check_planet_bonus_buildings_eutab","yes")
  # recheckBuildings.add("check_planet_bonus_buildings_ag","yes")
  recheckBuildings.add("set_planet_flag", "cgm_bonus_building_calc_done")

  recheckPops=planetFindBestEventImmediate.createReturnIf(TagList("has_planet_flag", "cgm_pop_calc_done"))
  for resource in resources:
    recheckPops.variableOp("set", resource+"_mult_planet_pop", 0)
  recheckPops.add("calculate_average_pop_multipliers","yes")
  recheckPops.add("set_planet_flag", "cgm_pop_calc_done")

  for resource in resources:
    planetFindBestEventImmediate.variableOp("set", resource+"_mult_planet", 1)
    planetFindBestEventImmediate.variableOp("change", resource+"_mult_planet", resource+"_mult_planet_base")
    planetFindBestEventImmediate.variableOp("change", resource+"_mult_planet", resource+"_mult_planet_building")
    planetFindBestEventImmediate.variableOp("change", resource+"_mult_planet", resource+"_mult_planet_pop")
    planetSpecificWeight=planetFindBestEventImmediate.createReturnIf(TagList("has_planet_flag", "cgm_player_focus_"+resource))
    nonSpecific=TagList()
    if resource=="food":
      planetSpecificWeight.variableOp("set", resource+"_country_weight_TILE", "cgm_focus_strength")
      nonSpecific.variableOp("set", resource+"_country_weight_TILE", "owner")
      planetFindBestEventImmediate.variableOp("multiply", resource+"_mult_planet", resource+"_country_weight_TILE")
    else:
      planetSpecificWeight.variableOp("set", resource+"_country_weight", "cgm_focus_strength")
      nonSpecific.variableOp("set", resource+"_country_weight", "owner")
      planetFindBestEventImmediate.variableOp("multiply", resource+"_mult_planet", resource+"_country_weight")
    planetSpecificWeight.add("else", nonSpecific)

  everyTileSearch=TagList()
  planetFindBestEventImmediate.add("every_tile", everyTileSearch)
  curPrev=everyTileSearch.addReturn("prev")
  curPrev.variableOp("change", "cgm_curTile", 1)
  everyTileSearch=everyTileSearch.createReturnIf(TagList("has_building","no").add("has_blocker", "no"))
  # curPrev.variableOp("set", "cgm_curWeight", 0)
  # for weight in weightTypes:
  #   curPrev.variableOp("set", weight+"_weight", 0)

  everyTileSearch.add("calculate_tile_weight","yes")
  everyTileSearch=everyTileSearch.addReturn("prev")
  for resource in resources:
    if resource!="unity":
      everyTileSearch.variableOp("multiply", resource+"_weight",resource+"_mult_planet")
      everyTileSearch.variableOp("multiply", resource+"_adjacency_weight",resource+"_mult_planet")

  # everyTileSearch.addComment("doCALC! test:")
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 5))
  # testif.variableOp("set", "energy_weight", 25)
  # testif.variableOp("set", "minerals_weight", 21)
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 9))
  # testif.variableOp("set", "minerals_weight", 20)
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 7))
  # testif.variableOp("set", "food_weight", 5)
  # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 1))
  # testif.variableOp("set", "base_res_adjacency_weight", 27)
  # # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 2)) #removing the test of defining more of these. These lead to strange behavior (special building earlier than it should) in current version, but that would not be a problem in the final version: A new adjacency building would anyway trigger a recomp of weights!
  # # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 3))
  # # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # # testif=everyTileSearch.createReturnIf(variableOpNew("check", "cgm_curTile", 4))
  # # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # everyTileSearch.addComment("END OF example")
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

  empireWeightsEvent=TagList("id",name_empire_weights)
  outTag.add("country_event", empireWeightsEvent)
  empireWeightsEvent.triggeredHidden()
  empireWeightsEventImmediate=empireWeightsEvent.addReturn("immediate")
  empireWeightsEventImmediate.add("set_timed_country_flag", TagList( "flag", "cgm_empire_weights_computed_timed").add("days", 180))
  playerWeight=empireWeightsEventImmediate.createReturnIf(TagList("AND", TagList("is_ai", "no").add("NOT", TagList("has_country_flag","cgm_player_focus_as_ai"))))
  for resource in resources:
    resourceFocus=playerWeight.createReturnIf(TagList("has_country_flag","cgm_player_focus_"+resource))
    resourceFocus.variableOp("set", resource+"_country_weight", "cgm_focus_strength")
    resourceFocus.add("else",variableOpNew("set", resource+"_country_weight", 1) )
  playerWeight.variableOp("set", "food_country_weight_TILE", "food_country_weight")
  AIWeight=playerWeight.addReturn("else")
  # for resource in resources:
  #   empireWeightsEventImmediate.add("determine_surplus_"+resource,"yes")
  for resource in resources:
    AIWeight.variableOp("set",resource+"_country_weight",1)
  AIWeight.variableOp("set","food_country_weight_TILE",1)
  AIWeight.addComment("First negative part test:")
  allPosLimit=TagList()
  allPosNor=allPosLimit.addReturn("NOR")
  for resource in ["minerals", "energy", "food"]:
    negativeResourceSub=AIWeight
    negativeResourceSub.addComment(resource.upper()+" CHECK NEGATIVE")
    negCond=variableOpNew("check", resource+"_income", 0, "<")
    negativeResourceSub=negativeResourceSub.createReturnIf(negCond)
    allPosNor.addTagList(negCond)
    negativeResourceSub.variableOp("set", "cgm_tmp",  resource+"_income")
    negativeResourceSub.variableOp("multiply", "cgm_tmp",  -1)
    negativeResourceSub.variableOp("set", "cgm_months_to_starvation",  resource+"_reserve")
    negativeResourceSub.variableOp("divide", "cgm_months_to_starvation",  resource+"_income")
    negativeResourceSub=negativeResourceSub.createReturnIf(variableOpNew("check", "cgm_months_to_starvation", 2, "<")).variableOp("change", resource+"_country_weight", starvationWeight)
    negativeResourceSub=negativeResourceSub.addReturn("else")
    negativeResourceSub.variableOp("set", "cgm_tmp",  starvationWeight)
    negativeResourceSub.variableOp("divide", "cgm_tmp",  "cgm_months_to_starvation")
    negativeResourceSub.variableOp("change", resource+"_country_weight", "cgm_tmp")
    if resource=="food":
      negativeResourceSub.variableOp("set", resource+"_country_weight_TILE", resource+"_country_weight")
    # food_reserve


    # empireWeightsEventImmediate=empireWeightsEventImmediate.createReturnIf(variableOpNew("check", resource+"_log", 0, "<"))
    # empireWeightsEventImmediate.addComment("Give a factor of 2-4 depending on how negative we are.")
    # empireWeightsEventImmediate.variableOp("set", "cgm_tmp",  resource+"_log")
    # empireWeightsEventImmediate.variableOp("divide", "cgm_tmp",  (-countToNeg[-1]-1)/2)
    # empireWeightsEventImmediate.variableOp("change", "cgm_tmp",  1)
    # empireWeightsEventImmediate.variableOp("change", resource+"_country_weight", "cgm_tmp")
    # empireWeightsEventImmediate=empireWeightsEventImmediate.addReturn("else")


  empireWeightsEventAllPositive=AIWeight.createReturnIf(allPosLimit)
  empireWeightsEventAllPositive.addComment("All positive weightings:")
  for resource,factor in zip(resources,inverseFactorComparedToMinerals):
    if resource!="minerals":
      empireWeightsEventAllPositive.addComment(resource.upper())
      empireWeightsEventAllPositive.variableOp("multiply",resource+"_country_weight", "minerals_log")
      empireWeightsEventAllPositive.variableOp("set","cgm_tmp", resource+"_log")
      empireWeightsEventAllPositive.variableOp("change","cgm_tmp", math.log(factor,2))
      if "research" in resource:
        empireWeightsEventAllPositive.addComment("Subtract extra bonuses that hary AIs are getting from minerals to prevent them going science crazy. Actually treated as an addition to science output as that is less prone to problems")
        empireWeightsEventAllPositive.variableOp("change","cgm_tmp", "cgm_difficutly_imbalance_log")
      if resource == "energy":
        empireWeightsEventAllPositive.addComment("Reduce energy surplus wanted during war. Minerals are more important and energy surplus is harder to reach due to active fleets")
        empireWeightsEventAllPositive.createReturnIf(TagList("is_at_war", "yes")).variableOp("change","cgm_tmp", 4)
      empireWeightsEventAllPositive.variableOp("divide",resource+"_country_weight", "cgm_tmp")
      empireWeightsEventAllPositive.createReturnIf(variableOpNew("check",resource+"_country_weight", 2,">")).variableOp("set",resource+"_country_weight", 2)
      if resource=="food":
        empireWeightsEventAllPositive.addComment("check if the food is really needed: If there are few growing planets, we reduce the amount! _TILE remains unchanged as food on tile can be used for energy")
        empireWeightsEventAllPositive.variableOp("set", resource+"_country_weight_TILE", resource+"_country_weight")
        empireWeightsEventAllPositive.variableOp("set", "cgm_max_useful_food", 0)
        searchGrowingPlanets=empireWeightsEventAllPositive.addReturn("every_owned_planet")
        searchGrowingPlanets.add("limit", TagList("has_growing_pop", "yes"))
        searchGrowingPlanets.add("prev", variableOpNew("change", "cgm_max_useful_food", 100))
        reduceFoodWeight=empireWeightsEventAllPositive.createReturnIf(variableOpNew("check", "food_income", "cgm_max_useful_food", ">"))
        reduceFoodWeight.variableOp("set", "food_country_weight", 0)
        reduceFoodWeight=reduceFoodWeight.addReturn("else")
        reduceFoodWeight.variableOp("divide", "cgm_max_useful_food", 2)
        reduceFoodWeight=reduceFoodWeight.createReturnIf(variableOpNew("check", "food_income", "cgm_max_useful_food", ">"))
        reduceFoodWeight.addComment("Reduction as soon as we have more than half the limit: *1 for half the limit. *0.5 for 3/4 the limit. *0 for limit. Linear interpolation in between. 2*(1-x) Where x is income/max_required. '*-1' instead of '*-2' as we divided the nominator by 2 already")
        reduceFoodWeight.variableOp("set", "cgm_tmp", "food_income")
        reduceFoodWeight.variableOp("divide", "cgm_tmp","cgm_max_useful_food")
        reduceFoodWeight.variableOp("multiply", "cgm_tmp",-1)
        reduceFoodWeight.variableOp("change", "cgm_tmp",2)
        reduceFoodWeight.variableOp("multiply", "food_country_weight", "cgm_tmp")
        if debug:
          empireWeightsEventAllPositive.add("log", '"tile food weight: [this.food_country_weight_TILE]"')
          empireWeightsEventAllPositive.add("log", '"country food weight: [this.food_country_weight]"')

  # empireWeightsEventImmediate.add("check_income","yes")
  noChangeYet=empireWeightsEventImmediate
  for resource in resources:
    noChangeYet=noChangeYet.createReturnIf(TagList("NOT", TagList("has_country_flag", "cgm_redo_all_planet_calcs")))
    atLeastOneZero=noChangeYet.createReturnIf(TagList("OR", variableOpNew("check", resource+"_country_weight_old",0).variableOp("check", resource+"_country_weight",0)))
    atLeastOneDecentlyLarge=atLeastOneZero.createReturnIf(TagList("OR", variableOpNew("check", resource+"_country_weight_old",0.5,">").variableOp("check", resource+"_country_weight",0.5,">")))
    atLeastOneDecentlyLarge.add("set_country_flag", "cgm_redo_all_planet_calcs")

    noChangeYet=noChangeYet.createReturnIf(TagList("NOT", TagList("has_country_flag", "cgm_redo_all_planet_calcs")))
    noChangeYet.variableOp("set", "cgm_tmp", resource+"_country_weight_old")
    noChangeYet.variableOp("divide", "cgm_tmp", resource+"_country_weight")
    noChangeYet.createReturnIf(TagList("OR", variableOpNew("check", "cgm_tmp",1.5,">").variableOp("check", "cgm_tmp",0.666,"<"))).add("set_country_flag", "cgm_redo_all_planet_calcs")


  storeWeightsAfterChange=empireWeightsEventImmediate.createReturnIf(TagList("has_country_flag", "cgm_redo_all_planet_calcs"))
  for resource in resources:
    storeWeightsAfterChange.variableOp("set",resource+"_country_weight_old",resource+"_country_weight")
  if debug:
    for resource in resources:
      empireWeightsEventImmediate.add("log", '"'+resource+"_country_weight:[this."+resource+'_country_weight]"')

  newTileCheckFile=TagList()
  tileWeightSummary=newTileCheckFile.addReturn("calculate_tile_weight")
  # tileWeightSummary.createReturnIf(TagList("OR", TagList("has_deposit", "yes").add("any_neighboring_tile"))) #more efford than gain!
  for resource in resources:
    if resource=="unity":
      tileWeightSummary.addReturn("prev").variableOp("set", resource+"_weight", 0)
      tileWeightSummary.addComment("Unity is layer subtracted from other weights on this tile as we build unity on the 'worst' tile. Thus it must not have a base value")
    else:
      tileWeightSummary.addReturn("prev").variableOp("set", resource+"_weight", 3)
    tileWeightSummary.createReturnIf(TagList("has_resource", TagList("type", resource).add("amount", 0, "", ">"))).add("check_"+resource+"_deposit","yes")
    curEffect=newTileCheckFile.addReturn("check_"+resource+"_deposit")
    for i in range(1,10):
      curEffect=curEffect.createReturnIf(TagList("has_resource", TagList("type", resource).add("amount", i, "", "=")))
      # curEffect.add("prev", variableOpNew("change", resource+"_weight", round(i*math.sqrt(i),3)))
      curEffect.add("prev", variableOpNew("change", resource+"_weight", 2*i))
      curEffect=curEffect.addReturn("else")
  #adjacency:
  for resource in resources:
    if resource!="unity":
      tileWeightSummary.addReturn("prev").variableOp("set", resource+"_adjacency_weight", 0)
      tileWeightSummary.add("check_"+resource+"_adjacency","yes")
      curEffect=newTileCheckFile.addReturn("check_"+resource+"_adjacency")
      curEffect=curEffect.addReturn("every_neighboring_tile")
      buildingAndPop=curEffect.createReturnIf(TagList("has_building","yes").add("has_grown_pop","yes"))
      buildingAndPop.createReturnIf(TagList("pop", TagList("pop_produces_resource",TagList("type", resource).add("amount",0,"",">")))).add("prevprev",variableOpNew("change", resource+"_adjacency_weight", 4))
      noBuildingOrPop=buildingAndPop.addReturn("else")
      noBuildingOrPop.createReturnIf(TagList("has_resource", TagList("type", resource).add("amount", 0, "", ">"))).add("prevprev",variableOpNew("change", resource+"_adjacency_weight", 3))
        # curEffect=curEffect.createReturnIf(TagList("has_resource", TagList("type", resource).add("amount", i, "", "=")))
        # # curEffect.add("prev", variableOpNew("change", resource+"_weight", round(i*math.sqrt(i),3)))
        # curEffect.add("prev", variableOpNew("change", resource+"_weight", 2*i))
        # curEffect=curEffect.addReturn("else")

  newTileCheckFile.deleteOnLowestLevel(checkEmpty)

  if debug:
    locList=LocList(False)
  else:
    locList=LocList(2)
  locList.addLoc("FocusMenuTitle", "Choose Automation Focus")
  locList.addLoc("FocusMenuDesc", "Choose a category that should be prefered with a certain factor you can also choose here. '1' would mean no change. '3' should be used with caution as it most likely will use tiles that are way better for other things eventually.")
  locList.addLoc("focusStrength", "Focus Strength Factor")
  locList.addLoc("focus", "Focus")
  locList.addLoc("focusModifierDesc", "This income type will be placed at the given priority, ignoring empire focus settings. All other resources get the standard empire focus values.")
  locList.addLoc("country", "Empire")
  locList.addLoc("planet", "Planet Specific")
  locList.addLoc("asAI", "Same as AI")
  locList.addLoc("currently", "Currently")
  locList.append("as_ai", "@asAI")
  locList.addLoc("none", "None")

  edictOut=TagList()
  playerWeightEvent=outTag.addReturn("country_event")
  playerWeightEventPlanet=outTag.addReturn("planet_event")
  playerWeightEvent.add("id", name_player_weights_country)
  playerWeightEventPlanet.add("id", name_player_weights_planet)
  for scope, e in zip(["country", "planet"],[playerWeightEvent,playerWeightEventPlanet]):
    e.add("is_triggered_only", "yes")
    e.add("custom_gui","cgm_buildings_advanced_configuration_more_options").add("diplomatic","yes").add("force_open", "no") 
    e.add("title", locList.append(nameBase.format(scope+"_focus_event.name"), "@"+scope+": @FocusMenuTitle"))
    descTrigger=TagList("text", locList.append(nameBase.format(scope+"_focus_event.desc"), "@FocusMenuDesc @currently:"))
    customTooltips=TagList()
    for resource in resources:
      triggerText=TagList("text", locList.append(nameBase.format(resource+"_focus_event.desc"), "${}$: @focusStrength [this.cgm_focus_strength]".format(resource))).add("has_{}_flag".format(scope), "cgm_player_focus_{}".format(resource))
      descTrigger.add("success_text", triggerText)
      customTooltips.add("custom_tooltip", deepcopy(triggerText))

    resource="as_ai"
    triggerText=TagList("text", locList.append(nameBase.format(resource+"_focus_event.desc"), "${}$".format(resource))).add("has_{}_flag".format(scope), "cgm_player_focus_{}".format(resource))
    descTrigger.add("success_text", triggerText)
    customTooltips.add("custom_tooltip", deepcopy(triggerText))

    e.add("desc", TagList("trigger", descTrigger))
    e.add("picture_event_data", TagList("room","cgm_menu_room"))
    edict=edictOut.addReturn(scope+"_edict")
    edict.add("name", locList.append("edict_"+nameBase.format(scope+"_focus_event"), "@FocusMenuTitle").replace("edict_",""))
    locList.append("edict_"+nameBase.format(scope+"_focus_event_desc"), "@FocusMenuDesc")
    edict.add("length", 0)
    edict.add("cost", TagList())
    if scope=="country":
      edict.add("potential", TagList("is_ai", "no").add("NOT", TagList("has_country_flag", "cgm_disable_autobuild")))
    else:
      edict.add("potential", TagList("owner", TagList("is_ai", "no").add("NOT", TagList("has_country_flag", "cgm_disable_autobuild"))))
    # edict.add("effect", TagList("hidden_effect", createEvent(TagList(), e.get("id"), scope+"_event").add("custom_tooltip", TagList("trigger", deepcopy(descTrigger)))))
    edict.add("effect", TagList("hidden_effect", createEvent(TagList(), e.get("id"), scope+"_event")))#.addTagList(customTooltips))
  # playerWeightEvent.add("is_triggered_only", "yes")
  # playerWeightEvent.add("custom_gui","cgm_buildings_advanced_configuration").add("diplomatic","yes").add("force_open", "no") 
  # playerWeightEvent.add("title", locList.append(nameBase.format("main_event.name"), "@mainTitle"))
  # playerWeightEvent.add("desc", locList.append(nameBase.format("main_event.desc"), "@mainDesc"))
  # playerWeightEvent.add("picture_event_data", TagList("room","cgm_menu_room"))
  # playerWeightEventPlanet.add("is_triggered_only", "yes")
  # playerWeightEventPlanet.add("custom_gui","cgm_buildings_advanced_configuration").add("diplomatic","yes").add("force_open", "no") 
  # playerWeightEventPlanet.add("title", locList.append(nameBase.format("main_event.name"), "@mainTitle"))
  # playerWeightEventPlanet.add("desc", locList.append(nameBase.format("main_event.desc"), "@mainDesc"))
  # playerWeightEventPlanet.add("picture_event_data", TagList("room","cgm_menu_room"))
    for bonusStrength in [1,1.5,2,3]:
      option=e.addReturn("option")
      option.add("name", locList.append(nameBase.format("focus_strength_{!s}".format(bonusStrength).replace(".","_")+".name"), "@focusStrength: {!s}".format(bonusStrength)))
      option.add("custom_gui","cgm_option")
      option.add("hidden_effect", variableOpNew("set", "cgm_focus_strength", bonusStrength).add(scope+"_event", TagList("id",e.get("id"))))
    for resource in resources+["as_ai"]:
      if resource=="unity":
        continue
      if scope=="planet" and resource=="as_ai":
        continue
      if scope=="planet":
        locList.append(resource+"_focused_automation", "@focus: ${}$".format(resource))
        locList.append(resource+"_focused_automation_desc", "@focusModifierDesc")
      option=e.addReturn("option")
      # if resource=="as_ai":
      #   option.add("name", locList.append(nameBase.format(resource+"_focus.name"),"@{}".format(resource)))
      # else:
      option.add("name", locList.append(nameBase.format(resource+"_focus.name"),"${}$".format(resource)))
      option.add("custom_gui","cgm_option")
      hiddenEffect=option.addReturn("hidden_effect")
      hiddenEffect.add("set_{}_flag".format(scope), "cgm_player_focus_{}".format(resource))
      for res in resources+["as_ai"]:
        if res!=resource and res!="unity":
          hiddenEffect.add("remove_{}_flag".format(scope), "cgm_player_focus_{}".format(res))
      if resource!="as_ai":
        hiddenEffect.createReturnIf(variableOpNew("check", "cgm_focus_strength", 1.001, "<")).variableOp("set", "cgm_focus_strength", 1.5)
      if scope=="planet":
        hiddenEffect.add("add_modifier", TagList("modifier", resource+"_focused_automation").add("days", -1))
        for res in resources:
          if res!=resource and res!="unity":
            hiddenEffect.add("remove_modifier",res+"_focused_automation")
      hiddenEffect.add(scope+"_event", TagList("id",e.get("id")))
    
    #ALLOW FOCUS REMOVAL ON PLANET:
    if scope=="planet":
      option=e.addReturn("option")
      option.add("name", locList.append(nameBase.format("none_focus.name"),"@none"))
      option.add("custom_gui","cgm_option")
      hiddenEffect=option.addReturn("hidden_effect")
      for res in resources:
        if res!="unity":
          hiddenEffect.add("remove_{}_flag".format(scope), "cgm_player_focus_{}".format(res))
          hiddenEffect.add("remove_modifier",res+"_focused_automation")



    option=e.addReturn("option")
    option.add("name", "cgm_main_menu.close.name").add("custom_gui","cgm_option")
    if scope=="country":
      option.add("hidden_effect", TagList("country_event", TagList("id",name_empire_weights)))


  upgradeEvent=outTag.addReturn("country_event")
  upgradeEvent.add("id", name_empire_upgrade_event)
  upgradeEvent.triggeredHidden()
  upgradeEvent=upgradeEvent.addReturn("immediate")
  upgradeEvent=upgradeEvent.addReturn("every_owned_planet")
  upgradeEvent.add("limit", TagList("has_building_construction", "no").add("sector_controlled","no"))
  everyPop=upgradeEvent.addReturn("every_pop")
  everyPop.add("limit",  TagList("OR", TagList("is_colony_pop", "yes").add("is_growing", "yes")).add("OR", TagList("is_being_purged", "no").add("has_purge_type", TagList("type", "purge_labor_camps"))))
  tileSwitch=everyPop.addReturn("tile")
  tileSwitch=tileSwitch.addReturn("switch")
  tileSwitch.add("trigger", "has_building")



  # everyTile.add(name)


  # every_tile = {
  #     limit = { autobuild_trigger_tile_has_pop = yes }
  #     switch = {
  #       trigger = has_building

  for buildingFile in glob.glob("../CGM/buildings_script_source/common/buildings/*.txt"):
    buildingContent=TagList().readFile(buildingFile)
    for buildingName, building in buildingContent.getNameVal():
      if isinstance(building, TagList):
        upgrades=building.attemptGet("upgrades")
        if len(upgrades)>0:
          tileSwitch.add(buildingName, TagList("add_building_construction", upgrades.names[0]))
  everyPop.createReturnIf(TagList("tile", TagList("has_building_construction","yes"))).add("owner", TagList("set_country_flag", "cgm_auto_built")).add("break","yes")
  upgradeEvent.createReturnIf(TagList("has_building_construction","yes")).add("break","yes")


  outputToFolderAndFile(edictOut, "common/edicts", "cgm_script_created_auto_edicts.txt",2, "../CGM/buildings_script_source")
  outputToFolderAndFile(newTileCheckFile, "common/scripted_effects", "cgm_new_tile_checks.txt",2, "../CGM/buildings_script_source")
  outputToFolderAndFile(outTag, "events", "cgm_auto.txt",2, "../CGM/buildings_script_source")
  if debug:
    outputToFolderAndFile(outTriggers, "common/scripted_triggers/WIP/", "cgm_auto_trigger_template.txt",2, "../CGM/buildings_script_source")
    outputToFolderAndFile(outEffects, "common/scripted_effects/WIP/", "cgm_auto_effects_template.txt",2, "../CGM/buildings_script_source")
  # with open("test.txt", "w") as file:
  #   outTag.writeAll(file,args())





  # for fun,name in zip([lambda i:pow(2,i)  ,lambda i:i*i*i+1], ["","_cubic"]):
  for fun,name in zip([lambda i:pow(2,i)], [""]):
    checkResourceEffect=TagList()
    funNeg= lambda i:-pow(2,i)
    for resource in resources:
      curEffect=checkResourceEffect.addReturn("determine_surplus_"+resource)
      if resource in ["energy", "minerals", "food"]:
        curEffect=curEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",0 ,"", "<")))
        curNegEffect=curEffect
        for i in countToNeg:
          curNegEffect=curNegEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",funNeg(i) ,"", ">")))
          curNegEffect.variableOp("set", resource+"_log", -i)
          curNegEffect.variableOp("set", resource+"_income", round(funNeg(i-0.5),3))
          curNegEffect=curNegEffect.addReturn("else")
          curNegEffect.variableOp("set", resource+"_log", -i-1)
        curNegEffect.variableOp("set", resource+"_income", round(funNeg(i+0.5),3))
          # curEffect.variableOp("set", resource+"_income", -1)
        curEffect=curEffect.addReturn("else")
      for i in countToPos:
        curEffect=curEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",fun(i) ,"", "<")))
        curEffect.variableOp("set", resource+"_log", i)
        if i>3 and resource=="minerals":
          curSubEffect=curEffect
          for j in subCount:
            curSubEffect=curSubEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",round(fun(i-1+j/10),3) ,"", "<")))
            curSubEffect.variableOp("set", resource+"_income", round(fun(i-1+(j-0.5)/10),3))
            curSubEffect=curSubEffect.addReturn("else")
          curSubEffect.variableOp("set", resource+"_income", round(fun(i-1+(j+0.5)/10),3))
        else:
          curEffect.variableOp("set", resource+"_income", round(fun(i-0.5),3))
        curEffect=curEffect.addReturn("else")
      curEffect.variableOp("set", resource+"_log", i+1)
      curEffect.variableOp("set", resource+"_income", round(fun(i+0.5),3))
    outputToFolderAndFile(checkResourceEffect, "common/scripted_effects", "cgm_income_record_effects.txt",2, "../CGM/buildings_script_source")
    # outputToFolderAndFile(checkResourceEffect, "common/scripted_effects", "cgm_income_record_effects{}.txt".format(name),2, "../CGM/buildings_script_source")


  for language in locList.languages:
    outFolderLoc="../CGM/buildings_script_source/localisation/"+language
    if not os.path.exists(outFolderLoc):
      os.makedirs(outFolderLoc)
    locList.write(outFolderLoc+"/cgm_automization_l_"+language+".yml",language)


if __name__ == "__main__":
  main()