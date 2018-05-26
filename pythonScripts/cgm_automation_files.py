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
import createAIVarsFromModifiers
import createUpgradedBuildings


#TODO: Prio List how to use this:
# 1. Core world important+medium important new building 2. Core world upgrades 3. Core world not so important building 4. Sector new buildings 5. Sector upgrades
#possible far away todo: Replace worst existing building with (empire) unique
#todo:we need to add a special effect for AI, which optimizes capitals #remove them on placement and instant create them anew 
eventNameSpace="cgm_auto.{!s}"
nameBase="cgm_auto_{!s}"
resources=["energy", "minerals", "food","unity", "society_research", "physics_research", "engineering_research"]
# resourcesShort=["energy", "minerals", "food","unity", "society", "physics", "engineering"]
def main():

  debug=False
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  
  # weightTypes=["energy", "minerals", "food", "unity", "society_research", "physics_research", "engineering_research"]
  weightTypes=["energy", "minerals", "food", "society_research", "physics_research", "engineering_research"] #not same as resources, see below!
  for weight in deepcopy(weightTypes):
    weightTypes.append(weight+"_adjacency")
  inverseFactorComparedToMinerals=[4,1,8,4,4,4,4]
  inverseFactorComparedToMinerals25years=[4,1,8,3,3,3,3]
  inverseFactorComparedToMinerals50years=[4,1,8,2,2,2,2]
  exampleBuildings=["building_power_plant_1","building_mining_network_1","building_hydroponics_farm_1","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1","building_power_hub_1","building_power_hub_1","building_power_hub_1","building_basic_science_lab_1","building_basic_science_lab_1","building_basic_science_lab_1","blub"]
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

  miscAutoEffects=TagList()

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
  miscAutoEffects.addComment("this : country")
  planetPopAndSizeEffect=miscAutoEffects.addReturn("cgm_every_planet_free_pops_count_and_size_check")
  planetPopAndSizeEffect.variableOp("set", "cgm_free_pops", 0)
  planetPopAndSizeEffect.variableOp("set", "cgm_non_filled_planet_count", 0)
  countFreePops=planetPopAndSizeEffect.addReturn("every_owned_planet")
  countFreePops.add("limit", TagList("free_building_tiles", "0","",">"))
  countFreePops.addReturn("prev").variableOp("change", "cgm_non_filled_planet_count", 1)
  countFreePops.variableOp("set", "cgm_free_pops", 0)
  countFreePops.add("every_owned_pop", TagList("limit", TagList("OR", TagList("is_colony_pop", "yes").add("is_growing", "yes")).add("tile",TagList("NOR",TagList("has_building","yes").add("has_building_construction","yes"))).add("OR", TagList("is_being_purged", "no").add("has_purge_type", TagList("type", "purge_labor_camps")))).add("prev", variableOpNew("change", "cgm_free_pops", 1)))
  countFreeBuildings=countFreePops.createReturnIf(variableOpNew("check", "cgm_free_pops", 0, ">")).addReturn("every_tile")
  countFreeBuildings.add("limit", TagList("has_building", "yes").add("has_pop", "no"))
  countFreeBuildings.add("prev", variableOpNew("change", "cgm_free_pops", -1))
  countFreePops.addReturn("prev").variableOp("change", "cgm_free_pops", "prev")
  switchPlanetSize=countFreePops.addReturn("switch")
  switchPlanetSize.add("trigger", "planet_size")
  for planetSize in range(5,26):
    switchCommand=switchPlanetSize.addReturn(str(planetSize))
    differentSize=switchCommand.createReturnIf(TagList("NOT", variableOpNew("check", "cgm_planet_size", planetSize)))
    differentSize.add("set_planet_flag", "cgm_redo_planet_calc")
    differentSize.variableOp("set", "cgm_planet_size", planetSize)


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
  # findBestPlanetLimit.add("not",TagList("has_planet_flag", "purged_planet"))
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


  ifTypeBest=planetBuildSomeThing
  for i, weightType in enumerate(weightTypes+["special_resource"]):
    ifTypeBest=ifTypeBest.createReturnIf(TagList("check_variable", TagList("which", "cgm_bestType_1").add("value", i+1)))
    ifTypeBest.variableOp("set", "cgm_curTile",0)
    everyTileBuild=ifTypeBest.addReturn("every_tile")
    everyTileBuild.addReturn("prev").variableOp("change", "cgm_curTile",1)
    buildIt=everyTileBuild.createReturnIf(TagList("prev",variableOpNew("check", "cgm_curTile", "cgm_bestTile_1")))
    if debug:
      buildIt.add("log", '"trying to build on tile [planet.cgm_bestTile_1]"')
      buildIt.add("log", '"trying to build category {}"'.format(weightType))
    buildIt.add("add_"+weightType+"_building","yes" )
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
  chooseSpecialBuilding.add("save_event_target_as", "cgm_best_planet_for_special")
  effect.addComment("SPECIAL BUILDING NUMBER 2: FORTRESS")
  effect.variableOp("set", "cgm_special_bestWeight", 10)
  effect.addComment("cgm_special_bestWeight named like this for easier comparison! Local scope!")
  chooseSpecialBuilding=effect.createReturnIf(TagList("has_planet_flag","NEEDS_DEFENSE").variableOp("multiply", "cgm_special_bestWeight", 4))
  chooseSpecialBuilding=effect.createReturnIf(variableOpNew("check", "cgm_special_bestWeight", "prev", ">"))
  chooseSpecialBuilding.addReturn("prev").variableOp("set","cgm_special_bestWeight", "prev").variableOp("set","cgm_special_bestBuilding", 2)
  chooseSpecialBuilding.add("save_event_target_as", "cgm_best_planet_for_special")

  cgmCompEffect=TagList().readFile("../CGM/buildings_script_source/common/scripted_effects/00000_cgm_compatibility_effects.txt")
  miscAutoEffects.addComment("this : pop")
  miscAutoEffects.addComment("prev : planet")
  popTraits=miscAutoEffects.addReturn("check_pop_traits_rights_modifiers_vanilla_and_API")
  for name in cgmCompEffect.names:
    if "check_pop_traits" in name:
      if name=="check_pop_traits_additional_traits":
        popTraits.createReturnIf(TagList("additional_traits_enabled", "no")).add("check_vanilla_pop_traits", yes).add("else", TagList(name, yes))
      else:
        popTraits.add(name,"yes")
  popTraits.add("vanilla_pop_modifiers",yes)
  for name in cgmCompEffect.names:
    if "check_pop_modifiers" in name:
      popTraits.add(name,"yes")
  popTraits.add("check_pop_species_rights",yes)
  for name in cgmCompEffect.names:
    if "check_pop_species_rights_" in name:
      popTraits.add(name,"yes")
  miscAutoEffects.addComment("this : tile")
  miscAutoEffects.addComment("prev : planet")
  adjacencyAPI=miscAutoEffects.addReturn("check_neighboring_adj_bonus_buildings_APIs")
  for name in cgmCompEffect.names:
    if "check_neighboring_adj_bonus_buildings" in name:
      adjacencyAPI.add(name,"yes")
  miscAutoEffects.addComment("this : tile")
  miscAutoEffects.addComment("prev : planet")
  adjacencyBlockerAPI=miscAutoEffects.addReturn("check_neighboring_adj_bonus_blockers_APIs")
  for name in cgmCompEffect.names:
    if "check_adj_bonus_blockers" in name:
      adjacencyBlockerAPI.add(name,"yes")




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
  planetFindBestEventImmediate.add("remove_planet_flag", "purged_planet")
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
  # recheckModifiers.add("check_vanilla_planet_modifiers","yes")
  for name in cgmCompEffect.names:
    if "check_planet_modifiers" in name:
      if name=="check_planet_modifiers_gpm":
        recheckModifiers.createReturnIf(TagList("gpm_enabled", "no")).add("check_vanilla_planet_modifiers", yes).add("else", TagList(name, yes))
      else:
        recheckModifiers.add(name,"yes")
    # if "check_planet_modifiers" in name:
    #   recheckModifiers.add(name,"yes")

  redoLimit=TagList()
  redoOr=redoLimit.addReturn("NAND")
  for resource in resources:
    redoOr.variableOp("check", resource+"_mult_planet_base_old", resource+"_mult_planet_base")
  recheckModifiers.createReturnIf(redoLimit).add("set_planet_flag", "cgm_redo_planet_calc")
  modifierUpdateSingle.add("immediate", recheckModifiers)

  recheckBuildings=planetFindBestEventImmediate.createReturnIf(TagList("NOT", TagList("has_planet_flag", "cgm_bonus_building_calc_done")))
  for resource in resources:
    recheckBuildings.variableOp("set", resource+"_mult_planet_building", 0)
  recheckBuildings.add("check_planet_bonus_buildings","yes")
  for name in cgmCompEffect.names:
    if "check_planet_bonus_buildings" in name:
      recheckBuildings.add(name,"yes")
  # recheckBuildings.add("check_planet_bonus_buildings_pe","yes")
  # recheckBuildings.add("check_planet_bonus_buildings_am","yes")
  # recheckBuildings.add("check_planet_bonus_buildings_eutab","yes")
  # recheckBuildings.add("check_planet_bonus_buildings_ag","yes")
  recheckBuildings.add("set_planet_flag", "cgm_bonus_building_calc_done")

  recheckPops=planetFindBestEventImmediate.createReturnIf(TagList("NOT", TagList("has_planet_flag", "cgm_pop_calc_done")))
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
  everyTileSearchSub=everyTileSearch.createReturnIf(TagList("has_any_tile_strategic_resource", "yes"))
  specialResourcePossible=everyTileSearchSub.createReturnIf(TagList("special_resource_any_building_available",yes))
  specialResourcePossible=specialResourcePossible.addReturn("prev")
  specialResourcePossible.variableOp("set", "cgm_curWeight", 50)
  specialResourcePossible.variableOp("set", "cgm_curType", len(weightTypes)+1)

  everyTileSearchNoSpecial=everyTileSearch.addReturn("else")

  everyTileSearchNoSpecial.add("calculate_tile_weight","yes")
  everyTileSearchNoSpecial=everyTileSearchNoSpecial.addReturn("prev")
  for resource in resources:
    if resource!="unity":
      everyTileSearchNoSpecial.variableOp("subtract", resource+"_weight","unity_weight")
      everyTileSearchNoSpecial.variableOp("multiply", resource+"_weight",resource+"_mult_planet")
      everyTileSearchNoSpecial.variableOp("multiply", resource+"_adjacency_weight",resource+"_mult_planet")

  # everyTileSearchNoSpecial.addComment("doCALC! test:")
  # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 5))
  # testif.variableOp("set", "energy_weight", 25)
  # testif.variableOp("set", "minerals_weight", 21)
  # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 9))
  # testif.variableOp("set", "minerals_weight", 20)
  # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 7))
  # testif.variableOp("set", "food_weight", 5)
  # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 1))
  # testif.variableOp("set", "base_res_adjacency_weight", 27)
  # # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 2)) #removing the test of defining more of these. These lead to strange behavior (special building earlier than it should) in current version, but that would not be a problem in the final version: A new adjacency building would anyway trigger a recomp of weights!
  # # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 3))
  # # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # # testif=everyTileSearchNoSpecial.createReturnIf(variableOpNew("check", "cgm_curTile", 4))
  # # testif.variableOp("set", "base_res_adjacency_weight", 29)
  # everyTileSearchNoSpecial.addComment("END OF example")
  for i, weight in enumerate(weightTypes):
    ifWeightHigher=everyTileSearchNoSpecial.createReturnIf(variableOp(TagList(), "check", weight+"_weight", "cgm_curWeight", ">").add(weight+"_any_building_available", "yes"))
    # if "adjacency" in weight:
    if weight=="base_res_adjacency":
      outTriggers.add(weight+"_any_building_available", TagList("not",  TagList("has_building","building_power_hub_1")))
    else:
      outTriggers.add(weight+"_any_building_available", TagList())
    ifWeightHigher.variableOp("set", "cgm_curWeight",weight+"_weight").variableOp("set", "cgm_curType",i+1)
  everyTileSearch=everyTileSearch.addReturn("prev")
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
      curSubLevel=curSubLevel.addReturn("else") #fixed 2.1
    for varToMove in varsToMove:
      locIf.variableOp("set", "cgm_best{}_{!s}".format(varToMove,i),"cgm_cur{}".format(varToMove))

    curLevel=curLevel.addReturn("else") #fixed 2.1

  #finding the worst of the best: best over weightTypes, worst over tiles
  locIf=everyTileSearch.createReturnIf(variableOp(TagList(), "check", "cgm_curWeight", "cgm_worstWeight", "<").add("prev",TagList("has_any_tile_strategic_resource", "no")))
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
    resourceFocusIf=playerWeight.createReturnIf(TagList("has_country_flag","cgm_player_focus_"+resource))
    resourceFocusIf.variableOp("set", resource+"_country_weight", "cgm_focus_strength")
    playerWeight.add("else",variableOpNew("set", resource+"_country_weight", 1) ) #fixed 2.1
  playerWeight.variableOp("set", "food_country_weight_TILE", "food_country_weight")
  AIWeight=empireWeightsEventImmediate.addReturn("else") #fixed 2.1
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
    negativeResourceSubIf=negativeResourceSub.createReturnIf(variableOpNew("check", "cgm_months_to_starvation", 2, "<")).variableOp("change", resource+"_country_weight", starvationWeight)
    if resource=="food":
      negativeResourceSubIf.variableOp("set", resource+"_country_weight_TILE", resource+"_country_weight")
    negativeResourceSub=negativeResourceSub.addReturn("else") #fixed 2.1
    negativeResourceSub.variableOp("set", "cgm_tmp",  starvationWeight)
    negativeResourceSub.variableOp("divide", "cgm_tmp",  "cgm_months_to_starvation")
    negativeResourceSub.variableOp("change", resource+"_country_weight", "cgm_tmp")
    if resource=="food":
      negativeResourceSub.variableOp("set", resource+"_country_weight_TILE", resource+"_country_weight")



  empireWeightsEventAllPositive=AIWeight.createReturnIf(allPosLimit)
  empireWeightsEventAllPositive.addComment("All positive weightings:")
  for resource,factor,factor25,factor50 in zip(resources,inverseFactorComparedToMinerals, inverseFactorComparedToMinerals25years, inverseFactorComparedToMinerals50years):
    if resource!="minerals":
      empireWeightsEventAllPositive.addComment(resource.upper())
      empireWeightsEventAllPositive.variableOp("multiply",resource+"_country_weight", "minerals_log")
      empireWeightsEventAllPositive.variableOp("set","cgm_tmp", resource+"_log")
      if factor!=factor25 or factor!=factor50:
        factorEarlyGame=empireWeightsEventAllPositive.createReturnIf(TagList("years_passed", 25, "", "<"))
        factorEarlyGame.variableOp("change","cgm_tmp", math.log(factor,2))
        factorMidGame=empireWeightsEventAllPositive.addReturn("else") #fixed 2.1
        factorMidGameIf=factorMidGame.createReturnIf(TagList("years_passed", 50, "", "<"))
        factorMidGameIf.variableOp("change","cgm_tmp", math.log(factor25,2))
        factorLateGame=factorMidGame.addReturn("else") #fixed 2.1
        factorLateGame.variableOp("change","cgm_tmp", math.log(factor50,2))
      else:
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
        noFoodNeeded=empireWeightsEventAllPositive.createReturnIf(TagList("is_food_delimited", "yes"))
        noFoodNeeded.variableOp("set", "food_country_weight_TILE", "energy_country_weight")
        foodNeeded=empireWeightsEventAllPositive.addReturn("else") #fixed 2.1
        foodNeeded.variableOp("set", resource+"_country_weight_TILE", resource+"_country_weight")
        foodNeeded.variableOp("set", "cgm_max_useful_food", 0)
        searchGrowingPlanets=foodNeeded.addReturn("every_owned_planet")
        searchGrowingPlanets.add("limit", TagList("has_growing_pop", "yes"))
        searchGrowingPlanets.add("prev", variableOpNew("change", "cgm_max_useful_food", 100))
        reduceFoodWeightIf=foodNeeded.createReturnIf(variableOpNew("check", "food_income", "cgm_max_useful_food", ">"))
        reduceFoodWeightIf.variableOp("set", "food_country_weight", 0)
        reduceFoodWeight=foodNeeded.addReturn("else") #fixed 2.1
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
      curEffectIf=curEffect.createReturnIf(TagList("has_resource", TagList("type", resource).add("amount", i, "", "=")))
      # curEffect.add("prev", variableOpNew("change", resource+"_weight", round(i*math.sqrt(i),3)))
      curEffectIf.add("prev", variableOpNew("change", resource+"_weight", 2*i))
      curEffect=curEffect.addReturn("else") #fixed 2.1
  #adjacency:
  for resource in resources:
    if resource!="unity":
      tileWeightSummary.addReturn("prev").variableOp("set", resource+"_adjacency_weight", 0)
      tileWeightSummary.add("check_"+resource+"_adjacency","yes")
      curEffect=newTileCheckFile.addReturn("check_"+resource+"_adjacency")
      curEffect=curEffect.addReturn("every_neighboring_tile")
      buildingAndPopIf=curEffect.createReturnIf(TagList("has_building","yes").add("has_grown_pop","yes"))
      buildingAndPopIf.createReturnIf(TagList("pop", TagList("pop_produces_resource",TagList("type", resource).add("amount",0,"",">")))).add("prevprev",variableOpNew("change", resource+"_adjacency_weight", 3))
      noBuildingOrPop=curEffect.addReturn("else")   #fixed 2.1
      noBuildingOrPop.createReturnIf(TagList("has_resource", TagList("type", resource).add("amount", 0, "", ">"))).add("prevprev",variableOpNew("change", resource+"_adjacency_weight", 2.5))
  tileWeightSummary.add("check_neighboring_adj_bonus_buildings","yes")
  tileWeightSummary.add("check_adj_bonus_blockers","yes")

  newTileCheckFile.deleteOnLowestLevel(checkEmpty)

  if debug:
    locList=LocList(False)
  else:
    locList=LocList(2)
  locList.addLoc("FocusMenuTitle", "Choose Automation Focus")
  locList.addLoc("FocusMenuDesc", "Choose your preferred automation focus here, and choose the strength factor of the focus. '1' would mean no change. '3' should be used with caution as it most likely will use tiles that are much better for other things eventually.")
  locList.addLoc("focusStrength", "Focus Strength Factor")
  locList.addLoc("focus", "Focus")
  locList.addLoc("focusModifierDesc", "This income type will be placed at the given priority, ignoring empire focus settings. All other resources get the standard empire focus values.")
  locList.addLoc("country", "Empire")
  locList.addLoc("planet", "Planet Specific")
  locList.addLoc("asAI", "Same as AI")
  locList.addLoc("currently", "Currently")
  locList.addLoc("none", "None")
  
  locList.addLoc("FocusMenuTitle", "фокус автоматизации","ru")
  locList.addLoc("FocusMenuDesc", "Выберите предпочтительную категорию с определенным коэффициентом, который вы также можете выбрать здесь. «1» означало бы никаких изменений. «3» следует использовать с осторожностью, поскольку он, скорее всего, будет использовать плитки, которые в лучшем случае лучше подходят для других вещей.","ru")
  locList.addLoc("focusStrength", "Фокусный фактор веса","ru")
  locList.addLoc("focus", "Фокус","ru")
  locList.addLoc("focusModifierDesc", "Этот тип дохода будет размещаться по заданному приоритету, игнорируя настройки фокуса империи. Все остальные ресурсы получают стандартные значения фокуса империи.","ru")
  locList.addLoc("country", "Империя","ru")
  locList.addLoc("planet", "Планета","ru")
  locList.addLoc("asAI", "То же, что ИИ","ru")
  locList.addLoc("currently", "В данный момент","ru")
  locList.addLoc("none", "Ничего","ru")

  locList.append("as_ai", "@asAI")
  edictOut=TagList()
  playerWeightEvent=outTag.addReturn("country_event")
  playerWeightEventPlanet=outTag.addReturn("planet_event")
  playerWeightEvent.add("id", name_player_weights_country)
  playerWeightEventPlanet.add("id", name_player_weights_planet)
  for scope, e in zip(["country", "planet"],[playerWeightEvent,playerWeightEventPlanet]):
    e.add("is_triggered_only", "yes")
    e.add("custom_gui","cgm_buildings_advanced_configuration_more_options").add("diplomatic","yes").add("force_open", "no") 
    # e.add("custom_gui","cgm_buildings_advanced_configuration_more_options").add("diplomatic","yes").add("force_open", "no") 
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
    # e.add("picture_event_data", TagList("room","cgm_menu_room"))
    # e.add("picture_event_data", TagList("room","cgm_menu_room_small"))
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
      option.add("custom_gui","cgm_advanced_configuration_option_more_options")
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
      option.add("custom_gui","cgm_advanced_configuration_option_more_options")
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
      option.add("custom_gui","cgm_advanced_configuration_option_more_options")
      hiddenEffect=option.addReturn("hidden_effect")
      for res in resources:
        if res!="unity":
          hiddenEffect.add("remove_{}_flag".format(scope), "cgm_player_focus_{}".format(res))
          hiddenEffect.add("remove_modifier",res+"_focused_automation")



    option=e.addReturn("option")
    option.add("name", "cgm_main_menu.close.name").add("custom_gui","cgm_advanced_configuration_option_more_options")
    if scope=="country":
      option.add("hidden_effect", TagList("country_event", TagList("id",name_empire_weights)))


  upgradeEvent=outTag.addReturn("country_event")
  upgradeEvent.add("id", name_empire_upgrade_event)
  upgradeEvent.triggeredHidden()
  upgradeEvent=upgradeEvent.addReturn("immediate")
  upgradeEvent=upgradeEvent.addReturn("every_owned_planet")
  upgradeEvent.add("limit", TagList("has_building_construction", "no").add("sector_controlled","no"))
  everyPop=upgradeEvent.addReturn("every_owned_pop")
  everyPop.add("limit",  TagList("OR", TagList("is_colony_pop", "yes").add("is_growing", "yes")).add("OR", TagList("is_being_purged", "no").add("has_purge_type", TagList("type", "purge_labor_camps"))))
  tileSwitch=everyPop.addReturn("tile")

  buildingContent=TagList()
  for buildingFile in glob.glob("../CGM/buildings_script_source/common/buildings/*.txt"):
    buildingContent.readFile(buildingFile)

  createUpgradeSwitch(buildingContent, tileSwitch)
  tileSwitch.add("cgm_upgrade_building", yes)
  # tileSwitch.createReturnIf(TagList("OR", TagList("has_building_construction", yes).add("has_building", yes))).add("owner", TagList("set_country_flag", "cgm_auto_built"))

  everyPop.createReturnIf(TagList("tile", TagList("has_building_construction","yes"))).add("owner", TagList("set_country_flag", "cgm_auto_built")).add("break","yes")
  upgradeEvent.createReturnIf(TagList("has_building_construction","yes")).add("break","yes")


  #return automatedCreationAutobuildAPI(resources)
  # return automatedCreationAutobuildAPI(resources,"alphamod",["../NOTES/api files/cgm_api_files/alphamod/"]) #TODO!!!





  outputToFolderAndFile(edictOut, "common/edicts", "cgm_script_created_auto_edicts.txt",2, "../CGM/buildings_script_source")
  outputToFolderAndFile(newTileCheckFile, "common/scripted_effects", "cgm_new_tile_checks.txt",2, "../CGM/buildings_script_source")
  outputToFolderAndFile(miscAutoEffects, "common/scripted_effects", "cgm_misc_auto_effects.txt",2, "../CGM/buildings_script_source")
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
        curEffectIf=curEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",0 ,"", "<")))
        curNegEffect=curEffectIf
        for i in countToNeg:
          curNegEffectIf=curNegEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",funNeg(i) ,"", ">")))
          curNegEffectIf.variableOp("set", resource+"_log", -i)
          curNegEffectIf.variableOp("set", resource+"_income", round(funNeg(i-0.5),3))
          curNegEffect=curNegEffect.addReturn("else") #fixed 2.1
        curNegEffect.variableOp("set", resource+"_log", -i-1)
        curNegEffect.variableOp("set", resource+"_income", round(funNeg(i+0.5),3))
          # curEffect.variableOp("set", resource+"_income", -1)
        curEffect=curEffect.addReturn("else") #fixed 2.1
      for i in countToPos:
        curEffectIf=curEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",fun(i) ,"", "<")))
        curEffectIf.variableOp("set", resource+"_log", i) #possible todo: also output log for the more precise one!
        if i>3 and resource=="minerals":
          curSubEffect=curEffectIf
          for j in subCount:
            curSubEffectIf=curSubEffect.createReturnIf(TagList("has_monthly_income", TagList("resource", resource).add("value",round(fun(i-1+j/10),3) ,"", "<")))
            curSubEffectIf.variableOp("set", resource+"_income", round(fun(i-1+(j-0.5)/10),3))
            curSubEffect=curSubEffect.addReturn("else") #fixed 2.1
          curSubEffect.variableOp("set", resource+"_income", round(fun(i-1+(j+0.5)/10),3))
        else:
          curEffectIf.variableOp("set", resource+"_income", round(fun(i-0.5),3))
        curEffect=curEffect.addReturn("else") #fixed 2.1
      curEffect.variableOp("set", resource+"_log", i+1)
      curEffect.variableOp("set", resource+"_income", round(fun(i+0.5),3))
    outputToFolderAndFile(checkResourceEffect, "common/scripted_effects", "cgm_income_record_effects.txt",2, "../CGM/buildings_script_source")
    # outputToFolderAndFile(checkResourceEffect, "common/scripted_effects", "cgm_income_record_effects{}.txt".format(name),2, "../CGM/buildings_script_source")


  for language in locList.languages:
    outFolderLoc="../CGM/buildings_script_source/localisation/"+language
    if not os.path.exists(outFolderLoc):
      os.makedirs(outFolderLoc)
    locList.write(outFolderLoc+"/cgm_automization_l_"+language+".yml",language)
def addUniqueFirst(key, element, dictList,building):
  usedSubList=dictList.getOrCreate(key)
  if building.attemptGet("planet_unique")=="yes" or building.attemptGet("empire_unique")=="yes":
    if not hasattr(usedSubList, "countUnique"):
      usedSubList.countUnique=0
    usedSubList.insert(0,element) #0 is needed (unless I add another variable. don't add after countUnique!)
    usedSubList.countUnique+=1
    # insertToDictList(key, element, dictList)
  else:
    specialRequ=building.attemptGet("normal_resource_special_requirement").attemptGet("has_resource").attemptGet("type")
    # print(specialRequ)
    if len(specialRequ) and specialRequ in key:
      # print("blub")
      if not hasattr(usedSubList, "countUnique"):
        usedSubList.countUnique=0
      usedSubList.insert(usedSubList.countUnique,element)
      usedSubList.countUnique+=1 #+1 to keep the order
    else:
      usedSubList.add(element)
    # addToDictList(key, element, dictList)

def addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars, checkRun=False, buildingProductionTagName="produced_resources",subTag="{}", outName="{}" ):
  for resource in resources:
    buildingProductionTag=building.attemptGet(buildingProductionTagName)
    val=buildingProductionTag.attemptGet(subTag.format(resource))
    if hasattr(building, "bestVal"):
      compare=building.bestVal
    else:
      compare=0
    if len(val)>0: #string at this point!
      # print(subTag.format(resource))
      val=getVariableValueFromList(val, allVars)
      if "adjacency" in buildingProductionTagName:
        val*=4; #adjacency counts more
      if val>compare*0.5: #at least 50% of the best val to allow adding this to the category
        building.bestVal=max(val, compare)
        if checkRun==False: #only add after all have been processed once, or stuff might be added just because it was processed before a better type was found
          addUniqueFirst(outName.format(resource), buildingName, buildingLists,building)
          assigned=True
  return assigned
def getVariableValueFromList(name, allVars):
  if name[0]=="@":
    try:
      name=float(allVars.get(name))
    except:
      print("Warning: income variable {} not found. Assuming to be >=1".format(name))
      name=1
  else:
    name=float(name)
  return name

def uniquenessList(buildingContentOrig, type="planet_unique"):
  planetUniqueLists=dict()
  for buildingName, building in buildingContentOrig.getNameVal():
    if isinstance(building, TagList) and not building.attemptGet("is_listed")=="no" and  building.attemptGet(type)=="yes" and not buildingName in planetUniqueLists:
      upgrades=building.attemptGet("upgrades")
      toParseList=[]
      parsedList=[buildingName]
      tagListOfMembers=TagList()
      tagListOfMembers.add(buildingName)
      planetUniqueLists[buildingName]=tagListOfMembers
      for upgradeName in upgrades.names:
        if upgradeName!="" and upgradeName!=buildingName:
          toParseList.append(upgradeName)
      while len(toParseList)>0:
        nextToParse=toParseList.pop(0)
        # print(nextToParse)
        if nextToParse in planetUniqueLists: #"exception" need to join branches. We write everything into the old one!
          planetUniqueLists[nextToParse].addTagList(tagListOfMembers)
          tagListOfMembers=planetUniqueLists[nextToParse]
          for e in parsedList:
            planetUniqueLists[e]=tagListOfMembers
        else:
          upgrade=buildingContentOrig.get(nextToParse)
          # print(nextToParse)
          try:
            if upgrade.attemptGet("planet_unique")=="yes" or upgrade.attemptGet("empire_unique")=="yes":
              tagListOfMembers.add(nextToParse)
              upgrades=upgrade.attemptGet("upgrades")
              for upgradeName in upgrades.names:
                if upgradeName!="" and not upgradeName in parsedList:
                  # print("up"+upgradeName)
                  toParseList.append(upgradeName)
          except:
            print(upgrade)
            print(buildingName)
            raise
        parsedList.append(nextToParse)
  # for key, val in planetUniqueLists.items():
    # print("KEY:"+key)
    # print(val)
  return planetUniqueLists

def createUpgradeSwitch(buildingContent, tagList):
  tileSwitch=tagList.addReturn("switch")
  tileSwitch.add("trigger", "has_building")

  for buildingName, building in buildingContent.getNameVal():
    if isinstance(building, TagList) and not hasattr(building, "helper"):
      # if hasattr(building, "helper"):
        # print(building.helper)
      upgrades=building.attemptGet("upgrades")
      if len(upgrades)>0:
        buildingFound=tileSwitch.addReturn(buildingName)
        if len(upgrades)==1:
          buildingFound.add("add_building_construction", upgrades.names[0])
        else:
          # for resource in resourcesShort:
          #   for upgrade in upgrades:
          #     if resource in upgrade:
          #       print(resource)
          #       print(upgrade)
          buildingFound.addComment("First a random list, then all possible ones -> fail safe if the one chosen in the random list is invalid")
          randomList=buildingFound.addReturn("random_list")
          for upgrade in upgrades.names:
            randomList.add(str(round(100/len(upgrades))), TagList("add_building_construction", upgrade))
            buildingFound.add("add_building_construction", upgrade)

def makeUnique(seq, idfun=None): 
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def priorityFileCheck(fileLists,reverse=False): #earlier -> higher prio
  fileLists=list(map(lambda x: makeUnique(x, os.path.basename),fileLists))
  allLists=list(reduce(lambda x,y:x+y,fileLists))
  allLists=makeUnique(allLists, os.path.basename)
  fileLists=list(map(lambda x: list(filter(lambda y: y in allLists,x)),fileLists)) #remove stuff that has been removed from allLists when making it unique
  fileLists=list(map(lambda x: sorted(x),fileLists))
  # print(fileLists)
  if reverse:
    fileLists=list(map(lambda x: list(reversed(x)),fileLists))
    allLists=list(reversed(allLists))

  return fileLists,allLists



def automatedCreationAutobuildAPI(modName="cgm_buildings", addedFolders=[], addedFoldersPriority=[], specialBuildingWeight=10, apiOutFolder="", buildingsIgnoredByBU=[]): #if multiple are added  in one category, earlier is higher priority
#AUTOMATED CREATION OF EFFECTS AND TRIGGERS USED FOR AUTOBUILD API
  additionString=""
  if modName!="cgm_buildings":
    additionString="_"+modName
  buildingFilesCGM=glob.glob("../CGM/buildings_script_source/common/buildings/*.txt")
  buildingFilesAdded=[]
  for folder in addedFolders:
    buildingFilesAdded+=glob.glob(folder+"/buildings/*txt")
    # print(folder+"/buildings/*txt")
  buildingFilesPriority=[]
  for folder in addedFoldersPriority:
    buildingFilesPriority+=glob.glob(folder+"/buildings/*txt")
  # print(buildingFilesAdded)
  # return

  triggerFilesCGM=glob.glob("../CGM/buildings_script_source/common/scripted_triggers/*.txt")
  triggerFilesAdded=[]
  for folder in addedFolders:
    triggerFilesAdded+=glob.glob(folder+"/scripted_triggers/*txt")
  triggerFilesPriority=[]
  for folder in addedFoldersPriority:
    triggerFilesPriority+=glob.glob(folder+"/scripted_triggers/*txt")

  effectFilesCGM=glob.glob("../CGM/buildings_script_source/common/scripted_effects/*.txt")
  effectFilesAdded=[]
  for folder in addedFolders:
    effectFilesAdded+=glob.glob(folder+"/scripted_effects/*txt")
  effectFilesPriority=[]
  for folder in addedFoldersPriority:
    effectFilesPriority+=glob.glob(folder+"/scripted_effects/*txt")

  variableFilesCGM=glob.glob("../CGM/buildings_script_source/common/scripted_variables/*.txt")
  variableFilesAdded=[]
  for folder in addedFolders:
    variableFilesAdded+=glob.glob(folder+"/scripted_variables/*txt")
  variableFilesPriority=[]
  for folder in addedFoldersPriority:
    variableFilesPriority+=glob.glob(folder+"/scripted_variables/*txt")

  (buildingFilesPriority,buildingFilesCGM,buildingFilesAdded),buildingAllFiles=priorityFileCheck([buildingFilesPriority,buildingFilesCGM,buildingFilesAdded],True)
  (triggerFilesPriority,triggerFilesCGM,triggerFilesAdded),triggerAllFiles=priorityFileCheck([triggerFilesPriority,triggerFilesCGM,triggerFilesAdded],True)
  (effectFilesPriority,effectFilesCGM,effectFilesAdded),effectAllFiles=priorityFileCheck([effectFilesPriority,effectFilesCGM,effectFilesAdded],True)
  (variableFilesPriority,variableFilesCGM,variableFilesAdded),variableAllFiles=priorityFileCheck([variableFilesPriority,variableFilesCGM,variableFilesAdded],True) #no idea of reversed is correct...

  # buildingFilesAdded=makeUnique(buildingFilesAdded, os.path.basename)
  # buildingFilesPriority=makeUnique(buildingFilesPriority, os.path.basename)
  # allBuildingsFiles=buildingFilesPriority+buildingFilesCGM+buildingFilesAdded
  # allBuildingsFiles=makeUnique(allBuildingsFiles, os.path.basename)
  # buildingFilesCGM=list(filter(lambda x: x in allBuildingsFiles,buildingFilesCGM))
  # buildingFilesAdded=list(filter(lambda x: x in allBuildingsFiles,buildingFilesAdded))

  # with open("test.txt", "w") as file:
  #   file.write(str(buildingFilesAdded))
  #   file.write("\n")
  #   # file.write(str(allBuildingsFiles))
  #   file.write("\n")
  #   file.write(str(buildingFilesCGM))
    # buildingFilesAdded=makeUnique(buildingFilesAdded, os.path.basename)
    # buildingFilesPriority=makeUnique(buildingFilesAdded, os.path.basename)
    # print(buildingFilesAdded)
    # file.write(str(buildingFilesAdded))

  buildingContent=TagList()
  allVars=TagList()
  for buildingFile in buildingAllFiles:
    prevLen=len(buildingContent.vals)
    buildingContent.readFile(buildingFile,0,allVars)
    if modName!="cgm_buildings" and buildingFile in buildingFilesCGM:
      for b in buildingContent[prevLen:]:
        if isinstance(b,TagList):
          b.helper=True
  buildingContent.removeDuplicateNames()


  # buildingContent=TagList()
  # allVars=TagList()
  # for buildingFile in buildingFilesPriority:
  #   buildingContent.readFile(buildingFile,0,allVars)

  # #mark cgm_buildings stuff as helper unless we are parsing only cgm_buildings
  # prevLen=len(buildingContent.vals)
  # for buildingFile in buildingFilesCGM:
  #   buildingContent.readFile(buildingFile,0,allVars)
  # if modName!="cgm_buildings":
  #   for b in buildingContent[prevLen:]:
  #     if isinstance(b,TagList):
  #       b.helper=True

  # for buildingFile in buildingFilesAdded:
  #   buildingContent.readFile(buildingFile,0,allVars)

  # buildingContent.removeDuplicateNames()


  for varFile in variableAllFiles:
  # for varFile in glob.glob("../CGM/buildings_script_source/common/scripted_variables/*.txt"):
    allVars.readFile(varFile)


  upgradeEffect=TagList()
  upgradeActualEffect=upgradeEffect.addReturn("cgm_upgrade_building"+additionString)
  createUpgradeSwitch(buildingContent, upgradeActualEffect)
  

  allTriggers=TagList()
  # triggersFiles=glob.glob("../CGM/buildings_script_source/common/scripted_triggers/*.txt")#+glob.glob(...)
  # effectFiles=glob.glob("../CGM/buildings_script_source/common/scripted_effects/*.txt")#+glob.glob(...)
  # triggersFiles=list(reversed(sorted(triggersFiles, key=os.path.basename))) #earlier files in our list are prefered -> need to reverse order here
  # effectFiles=sorted(effectFiles, key=os.path.basename)

  for file in triggerAllFiles:
    allTriggers.readFile(file)
  buildingContentOrig=deepcopy(buildingContent)
  buildingContent.resolveStellarisLinks(allTriggers)
  buildingContent.removeDuplicatesRec()
  # outputToFolderAndFile(allTriggers, "", "test.txt",2, ".")
  # return

  # buildingContent=TagList()
  # allVars=TagList()
  # for buildingFile in glob.glob("../NOTES/api files/cgm_api_files/alphamod/buildings/*.txt"):
  #   buildingContent.readFile(buildingFile,0,allVars)


  planetUniqueDict=uniquenessList(buildingContentOrig)
  # print("EMPIRE UNIQUE")
  empireUniqueDict=uniquenessList(buildingContentOrig,"empire_unique")






  # buildingLists=dict()
  buildingLists=TagList()
  specialResourceTrigger=TagList()
  for i,(buildingName, building) in enumerate(buildingContent.getNameVal()):
    if isinstance(building, TagList) and building.attemptGet("is_listed")!="no" and not hasattr(building, "helper"):
      assigned=False
      for potAllowName in ["potential","allow"]:
        hasResourceTag=building.attemptGet(potAllowName).getAnywhereRequired("has_resource")
        if hasResourceTag:
          if not hasResourceTag.get("type") in resources:
            triggerAND=specialResourceTrigger.addReturn("AND")
            triggerAND.add("has_resource", hasResourceTag)
            for tech in building.attemptGet("prerequisites").names:
              triggerAND.add("owner", TagList("has_technology", tech))
            triggerAND.addTagList(buildingContentOrig[i].attemptGet("potential"))
            triggerAND.addTagList(buildingContentOrig[i].attemptGet("allow"))
            addUniqueFirst("special_resource", buildingName, buildingLists, building)
            assigned=True
            break
          else:
            building.getOrCreate("normal_resource_special_requirement").add("has_resource", hasResourceTag)
            # print(building)
      if not assigned:
        # if building.attemptGet("potential").getAnywhereRequired("has_resource") or building.attemptGet("allow").getAnywhereRequired("has_resource"):
        assigned=addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars,True)
        assigned=addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars,True,"adjacency_bonus", "tile_building_resource_{}_add", "{}_adjacency")
        assigned=addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars,True,"planet_modifier", "static_planet_resource_{}_add")
        assigned=addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars)
        assigned=addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars,False,"adjacency_bonus", "tile_building_resource_{}_add", "{}_adjacency")
        assigned=addToBuildingListsIf(assigned, buildingName,building, buildingLists,resources,allVars,False,"planet_modifier", "static_planet_resource_{}_add")
        if not assigned:
          print("Building {} not assigned to any list".format(buildingName))
  buildingLists.removeDuplicatesRec()
  specialResourceTrigger.removeLayer("custom_tooltip",["fail_text", "success_text", "text"])
  specialResourceTrigger.removeLayer("tile")
  def condParent(tagList, i):
    if tagList.names[i]=="OR":
      return True
    else:
      return False
  def condChild(tagList, i):
    if tagList.names[i]=="always" and tagList.vals[i]=="no":
      return True
    else:
      return False
  specialResourceTrigger.twoConditionRemove(condParent,condChild)


  specialResourceTrigger.removeDuplicatesRec()
  specialResourceTrigger=TagList("special_resource_any_building_available"+additionString, TagList("OR", specialResourceTrigger))
  # print(buildingLists)

  automationEffects=TagList()
  adjacencyTriggers=TagList()
  specialBuildingNumber=0
  for typeName, typeContent in buildingLists.getNameVal():
    if "unity" in typeName:
      unity=True
    else:
      unity=False
    automationEffects.addComment("this = tile")
    automationEffects.addComment("prev = planet")
    if unity:
      typeEffect=automationEffects.getOrCreate("cgm_add_special_building"+additionString)
    else:
      typeEffect=automationEffects.addReturn("add_"+typeName+"_building"+additionString)
    if "adjacency" in typeName or unity:
      if unity:
        automationEffects.addComment("this = planet")
        automationEffects.addComment("prev = OWNER")
        adjacencyTrigger2=automationEffects.getOrCreate("cgm_search_for_special_building"+additionString)
        adjacencyTrigger=TagList()
      else:
        adjacencyTriggers.addComment("this = planet")
        adjacencyTriggers.addComment("prev = tile")
        adjacencyTrigger=adjacencyTriggers.addReturn(typeName+"_any_building_available"+additionString).addReturn("OR")
    for buildingName in typeContent.names:
      if unity==True:
        tileStuff=False
        for potAllow in ["potential","allow"]:
          potResolved=building.attemptGet(potAllow)
          if potResolved.getAnywhere("tile")!=None:
            otherUsage=buildingLists.getAnywhere(buildingName, ["unity", "unity_adjacency"])
            if otherUsage==None:
              print("Not taking {} as special building. It has tile specific conditions. As if is in no other category, this building will be missing from autobuild!".format(buildingName))
            #   print("but also in other category")
            # else:
            #   print("not in other category!")
            #   print(buildingLists)
            tileStuff=True
            break
        if tileStuff:
          continue
        hashFixedNumber=getSpecialBuildingNumberHash(modName, buildingName, specialBuildingNumber)
        specialBuildingNumber+=1
        # hashFixedNumber=round((hash(buildingName+additionString)%math.pow(2,32)-math.pow(2,31))/1000,3)
      building=buildingContent.get(buildingName)
      neededPlanetFlag=building.attemptGet("ai_allow").getAnywhereRequired("has_planet_flag")
      if unity==True:
        buildIt=typeEffect.createReturnIf(TagList("owner",variableOpNew("check","cgm_special_bestBuilding", hashFixedNumber)))
        buildIt.add("add_building_construction", buildingName)
        if neededPlanetFlag!=None:
          buildIt.add("planet", TagList("remove_planet_flag", neededPlanetFlag))
      elif neededPlanetFlag!=None and not unity:
        typeEffect.createReturnIf(TagList("has_planet_flag", neededPlanetFlag), "addFront").add("add_building_construction", buildingName).add("planet", TagList("remove_planet_flag", neededPlanetFlag))
      else:
        typeEffect.add("add_building_construction", buildingName)
      if "adjacency" in typeName or unity:
        localTrigger=adjacencyTrigger.addReturn("AND")
        for tech in building.attemptGet("prerequisites").names:
          localTrigger.add("owner", TagList("has_technology", tech))
        for potAllow in ["potential","allow"]:
          pot=buildingContentOrig[buildingContentOrig.names.index(buildingName)].attemptGet(potAllow)
          if len(pot):
            if unity:
              localTrigger.addTagList(deepcopy(pot).removeLayer("planet"))
            else:
              localTrigger.add("prev",pot )
        # pot=buildingContentOrig[buildingContentOrig.names.index(buildingName)].attemptGet("allow")
        # if len(pot):
        #   localTrigger.add("prev",pot )
        if building.attemptGet("planet_unique")=="yes":
          locNor=localTrigger.addReturn("NOR")
          for b in planetUniqueDict[buildingName].names:
            locNor.add("has_building", b)
        if building.attemptGet("empire_unique")=="yes":
          locOr=localTrigger.addReturn("NOT").addReturn("owner").addReturn("any_owned_planet").addReturn("OR")
          for b in empireUniqueDict[buildingName].names:
            locOr.add("has_building", b)
        if unity==True:
          localTrigger.add("owner",variableOpNew("check", "cgm_special_bestWeight", specialBuildingWeight, "<"))
          if neededPlanetFlag!=None:
            localTrigger.insert(0, "has_planet_flag", neededPlanetFlag)
          takeThis=adjacencyTrigger2.createReturnIf(localTrigger)
          takeThis.addReturn("prev").variableOp("set", "cgm_special_bestWeight", specialBuildingWeight).variableOp("set", "cgm_special_bestBuilding", hashFixedNumber)
          takeThis.add("save_event_target_as","cgm_best_planet_for_special")
    # typeEffect.createReturnIf(TagList("OR", TagList("has_building_construction", yes).add("has_building",yes))).add("owner", TagList("set_country_flag", "cgm_auto_built"))

  adjacencyTriggers.deleteOnLowestLevel(checkTotallyEmpty)
  automationEffects.deleteOnLowestLevel(checkTotallyEmpty)
  specialResourceTrigger.deleteOnLowestLevel(checkTotallyEmpty)
  for name,val in automationEffects.getNameVal():
    if "add" in name and val.getAnywhere("add_building_construction")==None:
      automationEffects.remove(name)
  for name,val in upgradeEffect.getNameVal():
    if val.getAnywhere("add_building_construction")==None:
      upgradeEffect.remove(name)

  mainTriggerFileContent=TagList()
  autobuildCompTrigger=TagList()
  # if modName!="cgm_buildings":
  autobuildCompTrigger.readFile("../CGM/buildings_script_source/common/scripted_triggers/00000_cgm_auto_compatibilty_triggers.txt")
  mainTriggerFileContent.readFile("../CGM/buildings_script_source/common/scripted_triggers/cgm_automations_triggers.txt")
  for resource in resources:
    if resource!="unity":
      trigger=mainTriggerFileContent.get(resource+"_any_building_available")

      if modName=="cgm_buildings":
        if resource+"_any_building_available_API" not in trigger.names:
          trigger.add(resource+"_any_building_available_API",yes)
        autobuildCompTrigger.addUnique(resource+"_any_building_available_API", TagList())

      #ADJACENCY
      trigger=mainTriggerFileContent.get(resource+"_adjacency_any_building_available")
      if modName=="cgm_buildings":  
        if not "or" in trigger.names and not "OR" in trigger.names:
          trigger.add("OR", TagList("always", "no"))
      else:
        adjName=resource+"_adjacency_any_building_available_"+modName
        if adjName in adjacencyTriggers.names:
          triggerOR=trigger.get("OR")
          if "always" in triggerOR.names:
            triggerOR.remove("always")
          if not adjName in triggerOR.names:
            triggerOR.add(adjName, yes)
          # if not adjName in autobuildCompTrigger.names:
          autobuildCompTrigger.addUnique(adjName,TagList("always", "no"))

  if modName!="cgm_buildings":
    mainEffectFileContent=TagList()
    mainEffectFileContent.readFile("../CGM/buildings_script_source/common/scripted_effects/cgm_automation_effects.txt")
    autobuildCompEffects=TagList()
    autobuildCompEffects.readFile("../CGM/buildings_script_source/common/scripted_effects/00000_cgm_auto_compatibility_effects.txt")
    for effectName in automationEffects.names:
      if effectName=="":
        continue
      # if not isinstance(effectName, TagList):
      #   continue
      # if "unity" in typeName:
      #   # effect=mainEffectFileContent.get("add_"+resource+"_building")
      # else:
      effect=mainEffectFileContent.get(effectName.replace(additionString,""))
      if not effectName in effect.names:
        if "cgm_search_for_special_building" in effectName:
          effect.add(effectName, "yes")#must not be first as it would be before set variable that is first neeeded!
        else:
          effect.insert(0, effectName, "yes")
      autobuildCompEffects.addUnique(effectName,TagList())
    if len(specialResourceTrigger)>0:
      mainTriggerFileContent.get("special_resource_any_building_available").get("OR").addUnique(specialResourceTrigger.names[0],yes)
      autobuildCompTrigger.addUnique(specialResourceTrigger.names[0],TagList("always","no"))
    if len(upgradeEffect)>0:
      mainEffectFileContent.get("cgm_upgrade_building").addUnique(upgradeEffect.names[0],yes)
      autobuildCompEffects.addUnique(upgradeEffect.names[0],TagList())

  outputToFolderAndFile(mainTriggerFileContent, "common/scripted_triggers/", "cgm_automations_triggers.txt",2, "../CGM/buildings_script_source",False)
  if modName!="cgm_buildings":
    outputToFolderAndFile(mainEffectFileContent, "common/scripted_effects/", "cgm_automation_effects.txt",2, "../CGM/buildings_script_source",False)
    outputToFolderAndFile(autobuildCompEffects, "common/scripted_effects/", "00000_cgm_auto_compatibility_effects.txt",2, "../CGM/buildings_script_source",False)
  outputToFolderAndFile(autobuildCompTrigger, "common/scripted_triggers/", "00000_cgm_auto_compatibilty_triggers.txt",2, "../CGM/buildings_script_source", False)

  if apiOutFolder=="":
    apiOutFolder="../NOTES/api files/cgm_auto/"+modName
    # apiOutFolder="../../mod/cgm_auto_"+modName
  if len(specialResourceTrigger):
    outputToFolderAndFile(specialResourceTrigger, "/common/scripted_triggers/", "zz_cgm_special_resource_trigger{}.txt".format(additionString),2,apiOutFolder )
  if len(automationEffects):
    automationEffects=addCheckBeforeAnyBuildingConstruction(automationEffects)
    outputToFolderAndFile(automationEffects, "/common/scripted_effects/", "zz_cgm_automation_effects{}.txt".format(additionString),2, apiOutFolder)
  if len(adjacencyTriggers):
    outputToFolderAndFile(adjacencyTriggers, "/common/scripted_triggers/", "zz_cgm_adjacency_triggers{}.txt".format(additionString),2, apiOutFolder)
  if len(upgradeEffect):
    outputToFolderAndFile(upgradeEffect, "/common/scripted_effects/", "zz_cgm_upgrade_effects{}.txt".format(additionString),2, apiOutFolder)
  for modFolder in addedFolders+addedFoldersPriority:
    if modName!="cgm_planets": #those are written separately. this would mess things up!
      createAIVarsFromModifiers.main(createAIVarsFromModifiers.parse([modFolder+"/buildings/*",modFolder+"/static_modifiers/*",modFolder+"/tile_blockers/*",modFolder+"/traits/*", "--effect_name", modName, "--output_folder", apiOutFolder]))
      for dirpath, dirnames, files in os.walk(modFolder+"/buildings"):
        for file in files:
          buildingFileContent=readFile(os.path.join(dirpath, file))
          buildingOut=TagList()
          for name, val, comment, seperator in buildingFileContent.getAll():
            if isinstance(val, TagList):
              val.getOrCreate("ai_allow").add("NOT",TagList("owner" , TagList("has_country_flag","cgm_disable_vanilla_building_AI")))
              val.removeDuplicatesRec()
            buildingOut.add(name, val, comment, seperator)
          outputToFolderAndFile(buildingOut, "/common/buildings/", file,2, apiOutFolder)
      BUArgV=[apiOutFolder+"/common/buildings/*","../CGM/buildings_script_source/common/buildings/*","--output_folder","../NOTES/api files/cgm_auto_BU/"+modName, "--custom_mod_name", "CGM - {}: Comp Patch".format(modName), "--load_order_priority", "--make_optional", "--scripted_variables",",".join(variableAllFiles),"--copy_folder_first", apiOutFolder,"--helper_file_list","01", "--skip_building", ",".join(buildingsIgnoredByBU) ]
      createUpgradedBuildings.main(createUpgradedBuildings.parse(BUArgV),BUArgV)

  #priority sorted output for potential autobuild. Joined into one file!
  # buildingOut=TagList()
  # for name, val, comment, seperator in buildingContentOrig.getAll():
  #   if isinstance(val, TagList):
  #     if hasattr(val, "helper") and val.helper==True:
  #       continue
  #     val.getOrCreate("ai_allow").add("NOT",TagList("owner" , TagList("has_country_flag","cgm_disable_vanilla_building_AI")))
  #     val.removeDuplicatesRec()
  #   buildingOut.add(name, val, comment, seperator)
  # outputToFolderAndFile(buildingOut, "", "actuallyActiveBuildings.txt",2, apiOutFolder)


  aiWeightTriggerFileName=apiOutFolder+"/common/scripted_triggers/cgm_{}_ai_weight_scripted_trigger.txt".format(modName)
  if os.path.exists(aiWeightTriggerFileName):
    hasBuildingTrigger=readFile(aiWeightTriggerFileName)
    mainEngineTriggerFileContent=readFile("../CGM/buildings_script_source/common/scripted_triggers/cgm_engine_triggers.txt")
    cgmCompTrigger=TagList().readFile("../CGM/buildings_script_source/common/scripted_triggers/00000_cgm_compatibility_triggers.txt")
    for triggerName in ["has_{}planet_bonus", "had_{}planet_bonus", "has_{}adj_bonus", "had_{}adj_bonus"]:
      if triggerName.format(modName+"_")+"_building" in hasBuildingTrigger.names:
        mainEngineTriggerFileContent.get("cgm_"+triggerName.format("")+"_building").get("OR").addUnique(triggerName.format(modName+"_")+"_building",yes)#
        cgmCompTrigger.addUnique(triggerName.format(modName+"_")+"_building", TagList("always","no"))
    outputToFolderAndFile(mainEngineTriggerFileContent, "common/scripted_triggers/", "cgm_engine_triggers.txt",2, "../CGM/buildings_script_source",False)
    outputToFolderAndFile(cgmCompTrigger, "common/scripted_triggers/", "00000_cgm_compatibility_triggers.txt",2, "../CGM/buildings_script_source",False)

  aiWeightEffectFileName=apiOutFolder+"/common/scripted_effects/cgm_{}_ai_weight_API.txt".format(modName)
  if os.path.exists(aiWeightEffectFileName):
    aiWeightEffectFile=readFile(aiWeightEffectFileName)
    cgmCompEffect=TagList().readFile("../CGM/buildings_script_source/common/scripted_effects/00000_cgm_compatibility_effects.txt")
    for triggerName in aiWeightEffectFile.names:
      cgmCompEffect.addUnique(triggerName, TagList())
    outputToFolderAndFile(cgmCompEffect, "common/scripted_effects/", "00000_cgm_compatibility_effects.txt",2, "../CGM/buildings_script_source",False)

    

  modFile=TagList()
  modFile.add("name", '"!cgm_comp_{}"'.format(modName))
  modFile.add("path", '"mod/cgm_auto_{}"'.format(modName))
  modFile.add("tags", TagList('"BLUB"',""))
  modFile.add("supported_version", '"2.0.*"')
  outputToFolderAndFile(modFile, "", "cgm_auto_"+modName+".mod",2, "../../mod/")

  # for key, item in buildingLists.items():
  #   print(key)
  #   print(item)
  # return

  #END OF AUTOMATED CREATION OF EFFECTS AND TRIGGERS USED FOR AUTOBUILD API (might be moved elsewhere later)
def getSpecialBuildingNumberHash(modName, buildingName, i):
  j=0
  number=0
  for c in modName:
    n=ord(c.lower())
    n-=ord("a")
    if n<0 or n>25:
      continue #not a normal letter
    n+=1 #1-26, zero would not work
    number+=n*math.pow(2, 5*j) #need 5 bits per letter
    j+=1
    if j>4: #5*5 bits for this part
      break
  j=5
  number+=(i+1)*math.pow(2, 5*j) #25 bits where reserved for the letters. 7 bits remain (->128 special buildings max per mod)
  number-=math.pow(2,31) #use the negative parts as well!
  number/=1000 #use the 3 digits
  number=round(number,3)
  if number in [1,2,3,4,5]:
    print("DAMN! You hit one of the five defined by hand! You should play the lottery! 1 in a billion chance. EXITING!")
    sys.exit(1)
  return number

def addCheckBeforeAnyBuildingConstruction(tagList):
  outTag=TagList()
  for nameTop,valTop in tagList.getNameVal():
    if isinstance(valTop, TagList):
      cur=outTag.addReturn(nameTop)
      for name,val in valTop.getNameVal():
        cur.createReturnIf(TagList("OR", TagList("has_building_construction", yes).add("has_building",yes))).add("owner", TagList("set_country_flag", "cgm_auto_built"))
        cur=cur.addReturn("else")  #fixed 2.1
        cur.add(name, val)
  return outTag

  # round((hash(buildingName+additionString)%math.pow(2,32))/1000,3)
  # number+=hash(modName+buildingName)%



def createEffectDecisionStuff(modName="cgm_buildings"):
  outTag=TagList()
  curTag=outTag
  buildingsDict=dict()
  buildingsDict["energy"]="building_energy_conduit_1_"
  buildingsDict["minerals"]="building_energy_matter_converter_1_"
  buildingsDict["food"]="building_food_replicator_1_"
  buildingsDict["society_research"]="building_computational_array_1_"
  buildingsDict["physics_research"]="building_computational_array_1_"
  buildingsDict["engineering_research"]="building_computational_array_1_"
  for i,resource in enumerate(resources):
    if resource=="unity":
      continue
    cond=TagList()
    prev=cond.addReturn("prev")
    for resource2 in resources[i+1:]:
      if resource2=="unity":
        continue
      prev.variableOp("check", resource+"_adjacency_weight", resource2+"_adjacency_weight", ">")
    if len(prev)<2:
      break
    if len(prev)>2:
      curTagIf=curTag.createReturnIf(cond)
    for j in range(1,4):
      curTagIf.add("add_building_construction", buildingsDict[resource]+str(j))
    curTag=curTag.addReturn("else") #fixed 2.1 POSSIBLE TODO: This probably need to be manually added to the right place! Possible write a script to do that automatically
  outputToFolderAndFile(outTag, modName, "megastructure_node_stuff.txt",2, ".")


if __name__ == "__main__":
  main()