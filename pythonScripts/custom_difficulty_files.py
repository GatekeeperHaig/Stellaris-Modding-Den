#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
# from googletrans import Translator
import re
from locList import LocList
import math
import custom_difficulty_more_modifiers as cdmm


ETOld = "event_target:custom_difficulty_var_storage"
ETNew = "event_target:global_event_country"
ET = ETNew

yes="yes"


eventNameSpace="custom_difficulty.{!s}"

name_mainMenuEvent="custom_difficulty.0"
name_defaultMenuEvent="custom_difficulty.1"
name_customMenuEvent="custom_difficulty.2"
name_optionsEvent="custom_difficulty.3"
name_gameStartFireOnlyOnce="custom_difficulty.10"
name_gameStartFireOnlyOnceWithDialog="custom_difficulty.12"
name_randomDiffFireOnlyOnce="custom_difficulty.11"
name_dmm_new_init="custom_difficulty.13"
name_dmm_new_start="custom_difficulty.14"
name_resetEvent="custom_difficulty.20" # same as above with triggered_only instead of fire_only_once
name_resetConfirmationEvent="custom_difficulty.21" # same as above with triggered_only instead of fire_only_once
name_resetFlagsEvent="custom_difficulty.22"
name_resetAIFlagsEvent="custom_difficulty.23"
name_resetYearlyFlagsEvent="custom_difficulty.24"
name_resetPlayerFlagsEvent="custom_difficulty.25"
# name_resetConfEventMM="custom_difficulty.27"
# name_removeConfEventMM="custom_difficulty.28"
name_removeEvent="custom_difficulty.29"
name_rootYearlyEvent="custom_difficulty.30"
name_rootUpdateEvent="custom_difficulty.40"
name_countryRootUpdateEvent="custom_difficulty.41"
# name_rootUpdateEventSimple="custom_difficulty.41"
name_countryUpdateEvent="custom_difficulty.50"
name_countryUpdateEventSimple="custom_difficulty.51"
name_countryUpdateOneDayDelayEvent="custom_difficulty.52" #used for crisis/emerging countries immediate modifier application
name_lockEvent="custom_difficulty.60"
id_removeModifiers=70  #reserved range up to 72
id_removeGroupModifiers=73  #reserved range up to 75
name_removeAllModifiers=eventNameSpace.format(id_removeModifiers+9)
name_removeEventTarget=eventNameSpace.format(id_removeModifiers+8)
name_removeOLDModifiers="custom_difficulty_old.{}".format(id_removeModifiers+9)
id_addModifiers=80  #reserved range up to 82
id_addGroupModifiers=83  #reserved range up to 85
id_defaultEvents=100 #reserved range up to 119
id_updateEventCountryEvents=120 #reserved range up to 119
id_ChangeEvents=1000 #reserved range up to 9999
id_subChangeEvents=10

dmmId=4
dmmType="utilities"

# t_notLockedTrigger=TagList("not", TagList("has_global_flag", "custom_difficulty_locked"))
t_notLockedTrigger=TagList("custom_difficulty_allow_changes", "yes")
t_mainMenuEvent=TagList("id",name_mainMenuEvent)
t_rootUpdateEvent=TagList("id",name_countryRootUpdateEvent)
t_backMainOption=TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name_mainMenuEvent)))
t_closeOption=TagList("name", "custom_difficulty_close.name").add("hidden_effect", TagList("country_event", t_rootUpdateEvent).add("if", TagList("limit", TagList("has_global_flag", "custom_difficultyMM_active")).add("country_event", TagList("id","custom_difficulty_mm.2"))))


playerFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_player")
scalingFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_scaling")
otherFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_other")

aiFlag="custom_difficulty_ai_flag"
feFlag="custom_difficulty_fe_ae_flag"
leviathanFlag="custom_difficulty_leviathan_flag"
playerFlag="custom_difficulty_player_flag"
crisisFlag="custom_difficulty_crisis_flag"
marauderFlag="custom_difficulty_marauder_flag"
noBonusFlag="custom_difficulty_no_bonuses_flag"


def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  debugMode=False

  changeStepYears=[5,4,3,2,1]
  changeSteps = [50, 25, 10, 5, 1]
  for s in reversed(changeSteps):
    changeSteps.append(-s)
  for s in reversed(changeStepYears):
    changeStepYears.append(-s)
  possibleBoniNames=["station", "jobs",  "cap",   "upkeep", "ship_cost","stability", "diplo_upkeep", "damage","hull","armor","shield","fire_rate", "trade_value"] #, "growth"
  npcBoni=[           False,      False,   False,   False,    False,    False       ,False          ,True,   True,     True, True,True,              False]
  # boniFactor= [         1,          1,      1,    -1,           -1,         0.2,        -1,             1,      1,      1,      1]
  boniUnit=dict()
  for bonus in possibleBoniNames:
    boniUnit[bonus]="%"
  boniUnit["stability"]="" #continued for groups below
  boniFactor=dict()
  for bonus in possibleBoniNames:
    boniFactor[bonus]=1
  boniFactor["stability"]=0.2
  boniFactor["upkeep"]=-0.25
  boniFactor["ship_cost"]=-0.25
  boniFactor["diplo_upkeep"]=-1

  possibleBoniPictures=[
  "GFX_evt_mining_station",
  "GFX_evt_metropolis",
  "GFX_evt_busy_spaceport", 
  "GFX_evt_cargoship_caravan", 
  "GFX_evt_hangar_bay",
  "GFX_evt_alien_propaganda", 
  "GFX_evt_arguing_senate",
  "GFX_evt_debris", 
  "GFX_evt_sabotaged_ship",
  "GFX_evt_pirate_armada",
  "GFX_evt_fleet_neutral",
  "GFX_evt_debris",
  "GFX_evt_tradedeal"
  ]
  possibleBoniModifier=[
  "stations_produces_mult", 
  "planet_jobs_produces_mult", 
  "country_naval_cap_mult", 
  "ships_upkeep_mult", 
  "starbase_shipyard_build_cost_mult",
  "planet_stability_add",
  "pop_resettlement_cost_mult",
  ["weapon_type_strike_craft_weapon_fire_rate_mult","ship_weapon_damage"],
  "ship_hull_mult",
  "ship_armor_mult",
  "ship_shield_mult",
  "ship_fire_rate_mult",
  "trade_value_mult"
  # ["ship_upkeep_mult","planet_building_upkeep_mult","country_starbase_upkeep_mult","army_upkeep_mult","pop_robot_upkeep_mult"]#,
  # ["pop_growth_speed","pop_robot_build_speed_mult"]
  ]
  possibleBoniIcons=["£systems","£job", "£navy_size", "£ship_stats_maintenance","£ship_stats_build_cost", "£stability", "£influence","£military_power","£ship_stats_hitpoints","£ship_stats_armor","£ship_stats_shield","£military_power","£trade_value"
  # ,"£ship_stats_maintenance","£pops"
  ]
  possibleBoniColor=["E","B","G","P","Y","H","M","R","G","H","B","R","G"
  # ,"T","G"
  ]
  defaultEmpireBonusMultList=[25,25,15,-10,-10,5,-25,0,0,0,0,0,25]
  defaultEmpireBonusMult=dict()
  for i,bonus in enumerate(possibleBoniNames):
    defaultEmpireBonusMult[bonus]=defaultEmpireBonusMultList[i]
    # print(defaultEmpireBonusMult[bonus])
    # print(bonus)
  npcBonusAdd=5
  npcBonusBase=30



  # stations_produces_mult = 1 GFX_evt_mining_station £systems "T"
  # planet_jobs_produces_mult = 1 GFX_evt_metropolis £job "M"
  # country_naval_cap_mult = 0.6 busy_spaceport £navy_size "G"
  # ships_upkeep_mult = -0.4 cargoship_caravan £ship_stats_maintenance "Y"
  # starbase_shipyard_build_cost_mult = -0.4 GFX_evt_hangar_bay £ship_stats_build_cost "W"
  # planet_stability_add = 20 alien_propaganda £stability "P"

  #UNCHANGED
  # ship_weapon_damage = 0.50
  # ship_hull_mult = 0.50
  # ship_armor_mult = 0.50
  # ship_shield_mult = 0.50


  #SEE gfx/interface/icons/text_icons/ or interface/texticons.gfx
  #mod_planet_jobs_produces_mult:0 "Resources from £job£ Jobs"
  # 5131:  SHIP_STAT_COST_INLINE:0 "£ship_stats_build_cost£ $SHIP_STAT_COST$:"
 # 5132:  SHIP_STAT_BUILD_TIME_INLINE:0 "£ship_stats_build_time£ $SHIP_STAT_BUILD_TIME$:"
 # 5133:  SHIP_STAT_MINERAL_MAINTENENCE_INLINE:0 "£ship_stats_maintenance£ $SHIP_STAT_MINERAL_MAINTENENCE$:"
 # 5134:  SHIP_STAT_ENERGY_MAINTENENCE_INLINE:0 "£ship_stats_maintenance£ SHIP_STAT_ENERGY_MAINTENENCE:"
 # 5135:  SHIP_STAT_POWER_USAGE_INLINE:0 "£ship_stats_power£ $SHIP_STAT_POWER_USAGE$:"
 # 5136:  SHIP_STAT_HITPOINTS_INLINE:0 "£ship_stats_hitpoints£ $SHIP_STAT_HITPOINTS$:"
 # 5137:  SHIP_STAT_ARMOR_INLINE:0 "£ship_stats_armor£ $SHIP_STAT_ARMOR$:"
 # 5138:  SHIP_STAT_SHIELDS_INLINE:0 "£ship_stats_shield£ $SHIP_STAT_SHIELDS$:"
 # 5139:  SHIP_STAT_COMBAT_SPEED_INLINE:0 "£ship_stats_speed£ $SHIP_STAT_COMBAT_SPEED$:"
 # 5140:  SHIP_STAT_EVASION_INLINE:0 "£ship_stats_evasion£ $SHIP_STAT_EVASION$:"
 # 5141:  SHIP_STAT_DAMAGE_INLINE:0 "£ship_stats_damage£ $SHIP_STAT_DAMAGE$:"
 # 5142:  SHIP_STAT_SPECIAL_INLINE:0 "£ship_stats_special£ $SHIP_STAT_SPECIAL$:"
 # 5143:  SHIP_STAT_SPEED_INLINE:0 "£ship_stats_speed£ $SHIP_STAT_SPEED$:"
 # 5144:  SHIP_STAT_RANK_INLINE:0 "£ship_stats_special£ Rank:"
 # 5145:  SHIP_STAT_HULL_REGENERATION_INLINE:0 "£ship_stats_hitpoints£ $SHIP_STAT_HULL_REGENERATION$:"
 # 5146   SHIP_STAT_HULL_REGENERATION_STATIC_INLINE:0 "$SHIP_STAT_HULL_REGENERATION_INLINE$"
 # 5147:  SHIP_STAT_ARMOR_REGENERATION_INLINE:0 "£ship_stats_armor£ $SHIP_STAT_ARMOR_REGENERATION$:"
 # 5148   SHIP_STAT_ARMOR_REGENERATION_STATIC_INLINE:0 "$SHIP_STAT_ARMOR_REGENERATION_INLINE$"
 # 5149:  SHIP_STAT_SHIELD_REGENERATION_INLINE:0 "£ship_stats_shield£ $SHIP_STAT_SHIELD_RECHARGE$:"
 # 5150   SHIP_STAT_SHIELD_REGENERATION_STATIC_INLINE:0 "$SHIP_STAT_SHIELD_REGENERATION_INLINE$"
 # 5151  


  bonusesListNames=["all","planets","systems", "allShip"]
  for bonus in bonusesListNames:
    boniUnit[bonus]="@steps"
    boniFactor[bonus]=1
  representGroup=dict()
  representGroup["jobs"]="planets"
  representGroup["station"]="systems"
  representGroup["damage"]="allShip"
  bonusListNPC=[    False,   False, False,  True]
  bonusesListEntries=[[i for i in range(len(possibleBoniNames))], [1,5,6],[0,2,3,4,12], [7,8,9,10,11]]
  bonusesListPictures=["GFX_evt_alien_city", "GFX_evt_galactic_market", "GFX_evt_satellite_in_orbit","GFX_evt_federation_fleet"]
  # bonusesListNames=["all","default", "allShip"]
  # bonusListNPC=[    True,   False,    False]
  # bonusesListEntries=[[0,1,2,3,4,5,6,7,8,9,10,11,12], [0,1,2,3,4,6], [7,8,9,10]]
  # bonusesListPictures=["GFX_evt_towel", "GFX_evt_alien_city","GFX_evt_federation_fleet"]



  cats=["ai","ai_yearly","fe","leviathan","player","crisis","marauders", "other"]
  catToModifierType=dict()
  catToModifierType["ai"]="ai"
  catToModifierType["ai_yearly"]="none"
  catToModifierType["fe"]="ai"
  catToModifierType["leviathan"]="crisis"
  catToModifierType["player"]="player"
  catToModifierType["crisis"]="crisis"
  catToModifierType["marauders"]="crisis"
  catToModifierType["other"]="ai"
  catToModifierType["no_bonuses"]=""
  catCountryType=[
  ["default"], 
  ["default"],
  ["fallen_empire", "awakened_fallen_empire","ascended_empire","eternal_empire"],
  ["guardian", "guardian_dragon", "guardian_stellarite","guardian_wraith","guardian_hiver","guardian_horror","guardian_fortress","guardian_dreadnought", "guardian_sphere","guardian_scavenger_bot","guardian_elderly_tiyanki","ldragon_country","guardian_hatchling"],
  [],
  ["swarm", "extradimensional", "extradimensional_2", "extradimensional_3", "ai_empire","cybrex_empire","sentinels", "portal_holders", "feral_prethoryn","feral_prethoryn_infighting"],
  ["dormant_marauders","ruined_marauders", "awakened_marauders","marauder_raiders"],
  []]
  catNotCountryType=[[], [],[],[],[],[],[],catCountryType+[["global_event"]]]
  catPictures=["GFX_evt_throne_room","GFX_evt_organic_oppression","GFX_evt_fallen_empire_awakes","GFX_evt_wraith","GFX_evt_towel","GFX_evt_ai_planet","GFX_evt_khan_throne_room","GFX_evt_unknown_ships"]
  catColors="BHBBGRBB"

  allFlags=[aiFlag, feFlag, leviathanFlag, playerFlag, crisisFlag, marauderFlag, noBonusFlag]
  specificFlags=[aiFlag, aiFlag, feFlag, leviathanFlag, playerFlag, crisisFlag, marauderFlag, None, noBonusFlag]

  # difficulties=["easy", "no_player_bonus", "ensign","captain","commodore","admiral", "grand_admiral", "scaling", "no_scaling"]
  difficulties=[#"easy", "no_player_bonus",
  "cadet", "ensign","captain","commodore","admiral", "grand_admiral", "scaling", "no_scaling"]
  ai_non_scaling_DifficultyNames=difficulties[0:-2]

  vanillaDefaultDifficulty=[]
  # possibleBoniNames=["Minerals", "Energy","Food", "Research", "Unity", "Influence", "Naval capacity", "Weapon Damage", "Hull","Armor","Shield","Upkeep", "Any Pop growth speed"]
  # aiDefault=[True, True, True, True, True, False, True, False, False, False, False, False, False]
  # aiDefaultPrecise=[2, 2, 2, 1, 1, 0, 1, 0,0,0,0,0,0]
  catsWithnpcBoniBoni=["crisis","fe","leviathan","marauders", "other"]



  doTranslation=False
  # doTranslation=False
  locClass=LocList(doTranslation)
  locClassReplace=LocList(doTranslation, useReplaceFolder=True)
  
  globalAddLocs(locClass)







  # locClass.addEntry(, [])
  # locClass.addEntry(, [])










  difficultyChangeWindows = []
  mainIndex=0
  for cat in cats:
    mainIndex+=1 #starting with event 1000
    tagList=TagList()
    difficultyChangeWindows.append(tagList)
    tagList.add("namespace", "custom_difficulty")
    tagList.add("","","#Event ID starting at {0:d}000, blocked up to {0:d}999".format(mainIndex))
    choiceEvent=TagList()
    tagList.add("country_event", choiceEvent)
    choiceEvent.add("id",eventNameSpace.format(mainIndex*id_ChangeEvents))
    choiceEvent.add("is_triggered_only", yes)
    choiceEvent.add("title","custom_difficulty_{}.name".format(cat))
    choiceEvent.add("picture",'"'+catPictures[mainIndex-1]+'"')
    trigger=TagList()
    locClass.addEntry("custom_difficulty_{}.name".format(cat), "@change @{} @bonuses".format(cat))
    choiceEvent.add("desc", TagList().add("trigger",trigger))
    successText=TagList().add("text","custom_difficulty_locked.name").add("custom_difficulty_allow_changes", "no")
    trigger.add("success_text",successText)
    if cat=="ai_yearly":
      immediate=TagList()
      choiceEvent.add("immediate",immediate)
    if cat=="crisis":
      trigger.add("text", "custom_difficulty_crisis_strength_desc")
      locClass.append("custom_difficulty_crisis_strength_desc", "@vanilla @example @values: @grandAdmiral + x5 @crisis @strength: 750%. @ensign + x5 @crisis @strength: 450%. @ensign + x0.25 @crisis @strength: 22.5%.")
    if cat=="ai_yearly":
      trigger.add("text", "custom_difficulty_current_yearly_desc") #loc global
    else:
      trigger.add("text", "custom_difficulty_current_bonuses") #loc global

    #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before)
    optionIndex=0
    for bonusesListName in bonusesListNames:
      optionIndex+=1
      if bonusesListName=="all":
        icons=""
        locClass.addEntry("custom_difficulty_{}_change_{}_name".format(cat,bonusesListName), "@change @{} @bonuses".format(bonusesListName))
      else:
        icons=" ".join([possibleBoniIcons[i] for i in bonusesListEntries[optionIndex-1]])
        locClass.addEntry("custom_difficulty_{}_change_{}_name".format(cat,bonusesListName), "@change @{} ({} ) @bonuses".format(bonusesListName,icons))
      firstVarName=possibleBoniNames[bonusesListEntries[optionIndex-1][0]]
      option=TagList().add("name", "custom_difficulty_{}_change_{}_name".format(cat,bonusesListName))
      option.add("custom_tooltip", "custom_difficulty_{}_change_{}_desc".format(cat,bonusesListName))
      option.add("trigger", TagList("custom_difficulty_allow_changes", "yes"))
      locClass.addEntry("custom_difficulty_{}_change_{}_desc".format(cat,bonusesListName), "@{}Desc".format(bonusesListName))
      option.add("hidden_effect", TagList().add("country_event",TagList().add("id", eventNameSpace.format(mainIndex*id_ChangeEvents+optionIndex*id_subChangeEvents))))
      if bonusesListName!="all":
        if cat!="ai_yearly":
          localVarName="custom_difficulty_{}_{}_value".format(cat,firstVarName)
          localDescName="custom_difficulty_{}_{}_desc".format(cat,bonusesListName)
          checkVar=TagList().add("which", localVarName).add("value","0")
          trigger.add("success_text",TagList()
              .add("text",localDescName).add(ET,TagList()
                .add("not", TagList("check_variable", checkVar))).add("has_global_flag", "custom_difficulty_activate_simple_mode"))
          locClass.addEntry(localDescName, "{} @{}: [{}.custom_difficulty_{}_{}_value]%".format(icons, bonusesListName,ET,cat,firstVarName))
        else:
          localVarName="custom_difficulty_{}_{}_value".format(cat,firstVarName)
          localDescIncName="custom_difficulty_{}_{}_inc_desc".format(cat,bonusesListName)
          localDescDecName="custom_difficulty_{}_{}_dec_desc".format(cat,bonusesListName)
          checkVar=TagList().add("which", localVarName).add("value","0","",">")
          trigger.add("success_text",TagList().add("text",localDescIncName).add(ET,TagList().add("check_variable", checkVar)).add("has_global_flag", "custom_difficulty_activate_simple_mode"))
          checkVar=TagList().add("which", localVarName).add("value","0","","<")
          trigger.add("success_text",TagList().add("text",localDescDecName).add(ET,TagList().add("check_variable", checkVar)).add("has_global_flag", "custom_difficulty_activate_simple_mode"))
          locClass.addEntry("custom_difficulty_{}_{}_inc_desc".format(cat,bonusesListName),"{0} @{1} : 1 @step @increase @every [this.custom_difficulty_{2}_{3}_value] @years".format(icons, bonusesListName, cat,firstVarName)) #local tmp var
          locClass.addEntry("custom_difficulty_{}_{}_dec_desc".format(cat,bonusesListName),"{0} @{1} : 1 @step @decrease @every [this.custom_difficulty_{2}_{3}_value] @years".format(icons, bonusesListName, cat,firstVarName)) #local tmp var
          #create a local variable and make sure it is positive!
          immediate.variableOp("set",localVarName, ET)
          immediateIf=TagList().add("limit",TagList().add("check_variable",checkVar)) #<0
          immediateIf.add("multiply_variable", TagList().add("which", localVarName).add("value","-1"))
          immediate.add("if",immediateIf)
      if not catToModifierType[cat]=="crisis" or bonusListNPC[optionIndex-1]:
        choiceEvent.add("option",option)

    for bonusI, bonus in enumerate(possibleBoniNames):
      optionIndex+=1
      localVarName="custom_difficulty_{}_{}_value".format(cat,bonus)
      if cat=="ai_yearly":
        checkVar=TagList().add("which", localVarName).add("value","0","",">")
        trigger.add("success_text",TagList().add("text","custom_difficulty_{}_{}_inc_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)).add("has_global_flag", "custom_difficulty_activate_custom_mode"))
        checkVar=TagList().add("which", localVarName).add("value","0","","<")
        trigger.add("success_text",TagList().add("text","custom_difficulty_{}_{}_dec_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)).add("has_global_flag", "custom_difficulty_activate_custom_mode"))
        locClass.addEntry("custom_difficulty_{}_{}_inc_desc".format(cat,bonus),"{} §{}@{} : 1 @step @increase @every [this.custom_difficulty_{}_{}_value] @years".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonus)) #local tmp var
        locClass.addEntry("custom_difficulty_{}_{}_dec_desc".format(cat,bonus),"{} §{}@{} : 1 @step @decrease @every [this.custom_difficulty_{}_{}_value] @years".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonus)) #local tmp var
        #create a local variable and make sure it is positive!
        immediate.variableOp("set",localVarName, ET)
        immediateIf=TagList().add("limit",TagList().add("check_variable",checkVar)) #<0
        immediateIf.add("multiply_variable", TagList().add("which", localVarName).add("value","-1"))
        immediate.add("if",immediateIf)
      else:
        checkVar=TagList().add("which", localVarName).add("value","0")
        # trigger.add("fail_text",TagList().add("text","custom_difficulty_{}_{}_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)))
        trigger.add("success_text",TagList()
          .add("text","custom_difficulty_{}_{}_desc".format(cat,bonus)).add(ET,TagList()
            .add("not", TagList("check_variable", checkVar))).add("has_global_flag", "custom_difficulty_activate_custom_mode"))
        locClass.append("custom_difficulty_{}_{}_desc".format(cat,bonus),"{} §{}@{} : [{}.custom_difficulty_{}_{}_value] {}".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, ET, cat,bonus, boniUnit[bonus]))

      #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before the loop)
      option=TagList().add("name", "custom_difficulty_{}_change_{}_button.name".format(cat,bonus))
      option.add("trigger", TagList().add("NOR", TagList().add("custom_difficulty_allow_changes", "no").add("has_global_flag", "custom_difficulty_activate_simple_mode")))
      locClass.append("custom_difficulty_{}_change_{}_button.name".format(cat,bonus), "§{}@change @{} ({} ) @bonuses§!".format(possibleBoniColor[bonusI],bonus,possibleBoniIcons[bonusI]))
      option.add("hidden_effect", TagList().add("country_event",TagList().add("id", eventNameSpace.format(mainIndex*id_ChangeEvents+optionIndex*id_subChangeEvents))))
      if not catToModifierType[cat]=="crisis" or npcBoni[bonusI]:
        choiceEvent.add("option",option) 

    option=TagList().add("name","custom_difficulty_back") #loc global
    if cat=="crisis":
      option2=deepcopy(option)
      option2.add("trigger", TagList("not", TagList("has_global_flag","custom_difficulty_menu_crisis_from_custom")))
      option2.add("hidden_effect", TagList().add("country_event",TagList().add("id", name_mainMenuEvent)))
      choiceEvent.add("option",option2)
      option.add("trigger", TagList("has_global_flag","custom_difficulty_menu_crisis_from_custom"))
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", name_customMenuEvent)))
    choiceEvent.add("option",option)
    option=TagList().add("name","custom_difficulty_close.name") #loc global
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", name_countryRootUpdateEvent)))
    choiceEvent.add("option",option)

    

    bonusIndex=0
    for bonus in bonusesListNames+possibleBoniNames:
      bonusIndex+=1
      changeEvent=TagList()
      if not catToModifierType[cat]=="crisis" or (bonusListNPC+npcBoni)[bonusIndex-1]:
        tagList.add("country_event", changeEvent)
        changeEvent.add("id",eventNameSpace.format(mainIndex*id_ChangeEvents+bonusIndex*id_subChangeEvents))
        changeEvent.add("is_triggered_only", yes)
        changeEvent.add("title","custom_difficulty_{}_change_{}.name".format(cat,bonus))
        locClass.append("custom_difficulty_{}_change_{}.name".format(cat,bonus), "@change @{} @bonuses (@{})".format(bonus,cat))
        changeEvent.add("desc", TagList().add("trigger",trigger)) #same desc trigger as above?
        changeEvent.add("picture",'"'+(bonusesListPictures+possibleBoniPictures)[bonusIndex-1]+'"')
        if cat=="ai_yearly":
          changeEvent.add("immediate",immediate)

        if cat=="ai_yearly":
          changeStepListUsed=changeStepYears
        else:
          changeStepListUsed=changeSteps
        for changeStep in changeStepListUsed:
          if catToModifierType[cat]=="crisis":
            changeStep*=5
          if cat=="player" and (abs(changeStep)==1 or abs(changeStep)==5 or abs(changeStep)==25):
            continue
          if changeStep>0:
            option=TagList().add("name","custom_difficulty_{}_{}_increase_{!s}".format(cat,bonus, changeStep))
            if cat=="ai_yearly":
              locClass.append("custom_difficulty_{}_{}_increase_{!s}".format(cat,bonus, changeStep), 
                "§G@increase @{} @years by {}".format(bonus, changeStep))
            else:
              locClass.append("custom_difficulty_{}_{}_increase_{!s}".format(cat,bonus, changeStep), 
                "§G@increase @{} @bonuses by {} {}".format(bonus, changeStep*boniFactor[bonus], boniUnit[bonus]))
          else:
            option=TagList().add("name","custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonus, -changeStep))
            if cat=="ai_yearly":
              locClass.append("custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonus, -changeStep), 
                "§R@decrease @{} @years by {}".format(bonus, -changeStep))
            else:
              locClass.append("custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonus, -changeStep), 
                "§R@decrease @{} @bonuses by {} {}".format(bonus, -changeStep*boniFactor[bonus], boniUnit[bonus]))

          hidden_effect=TagList()
          if bonusIndex>len(bonusesListNames):
            valueToBeChanged=changeStep*boniFactor[bonus]
            if cat=="ai_yearly":
              valueToBeChanged=changeStep*(1 if boniFactor[bonus] > 0 else -1)
            hidden_effect.add(ET,TagList().add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value",str(valueToBeChanged))))
          else:
            et=TagList()
            hidden_effect.add(ET,et)
            for bonusListIndex in bonusesListEntries[bonusIndex-1]:
              if not catToModifierType[cat]=="crisis" or npcBoni[bonusListIndex]:
                bonusListValue=possibleBoniNames[bonusListIndex]
                et.add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusListValue)).add("value",str(changeStep*boniFactor[possibleBoniNames[bonusListIndex]])))
          hidden_effect.add("country_event", TagList().add("id",eventNameSpace.format(mainIndex*id_ChangeEvents+bonusIndex*id_subChangeEvents)))
          if cat=="player":
            hidden_effect.add("country_event", TagList().add("id",name_resetPlayerFlagsEvent)) #remove flags
            hidden_effect.add("set_global_flag", "custom_difficulty_advanced_configuration_player")
          elif cat=="ai_yearly":
            hidden_effect.add("country_event", TagList().add("id",name_resetYearlyFlagsEvent)) #remove flags
            hidden_effect.add("set_global_flag", "custom_difficulty_advanced_configuration_scaling")
          elif cat!="crisis":
            hidden_effect.add("country_event", TagList().add("id",name_resetAIFlagsEvent)) #remove flags
            hidden_effect.add("set_global_flag", "custom_difficulty_advanced_configuration")
          option.add("hidden_effect",hidden_effect)
          changeEvent.add("option",option)


        option=TagList().add("name","custom_difficulty_back")
        option.add("hidden_effect", TagList().add("country_event",TagList().add("id", eventNameSpace.format(mainIndex*id_ChangeEvents))))
        changeEvent.add("option",option)
        option=TagList().add("name","custom_difficulty_close.name")
        option.add("hidden_effect", TagList().add("country_event",TagList().add("id", name_countryRootUpdateEvent)))
        changeEvent.add("option",option)

    # difficultyChangeWindows[-1].printAll()
    # break




  outFolder="../gratak_mods/custom_difficulty/events"
  if not os.path.exists(outFolder):
    os.mkdir(outFolder)
  for cat, eventFileCont in zip(cats, difficultyChangeWindows):
    with open(outFolder+"/"+"custom_difficulty_"+cat+".txt",'w') as file:
      eventFileCont.writeAll(file,args())



  defaultEvents=TagList()
  defaultEvents.add("namespace", "custom_difficulty")
  # eventIndex=id_defaultEvents
  defaultEvents.add("","","#Events from {} blocked up to {}".format(id_defaultEvents,id_defaultEvents+99))


  condVal = lambda x,y: x if y else 0
  condValSign = lambda x,y: x//y if y else 0
  # condValPrec = lambda x1,x2,y: x1 if y==1 else (x2 if y==2  else 0)
  difficultiesPresetProperties=dict()
  for difficulty in difficulties:
    difficultiesPresetProperties[difficulty]=dict()
  # difficultiesPresetProperties["easy"]["player"]=[20 for b in possibleBoniNames]
  # difficultiesPresetProperties["no_player_bonus"]["player"]=[0 for b in possibleBoniNames]
  difficultiesPresetProperties["scaling"]["ai_yearly"]=[condValSign(100,defaultEmpireBonusMult[bonus]) for bonus in possibleBoniNames]
  difficultiesPresetProperties["no_scaling"]["ai_yearly"]=[0 for b in possibleBoniNames]

  for i, diff in enumerate(difficulties[ difficulties.index("ensign") : difficulties.index("grand_admiral")+1 ]):
    difficultiesPresetProperties[diff]["ai"]=[defaultEmpireBonusMult[bonus]*i for bonus in possibleBoniNames]
    difficultiesPresetProperties[diff]["player"]=[0 for _ in possibleBoniNames]
    for cat in catsWithnpcBoniBoni:
      difficultiesPresetProperties[diff][cat]=[condVal(1,s)*(npcBonusBase+i*npcBonusAdd) for s in npcBoni[:-1]]
      if cat != "crisis":
        difficultiesPresetProperties[diff][cat]=[f/2 for f in difficultiesPresetProperties[diff][cat]]
  difficultiesPresetProperties["cadet"]=deepcopy(difficultiesPresetProperties["ensign"])
  difficultiesPresetProperties["cadet"]["player"]=difficultiesPresetProperties["commodore"]["ai"]

  # print(difficultiesPresetProperties)


  ## TODO!!
  # diffLevels=dict() 
  # diffLevels["ensign"]=[30, 0,0 ] # crisis, high ai and npc, low ai
  # diffLevels["captain"]=[35, 25,15 ]
  # diffLevels["commodore"]=[40, 50,30 ]
  # diffLevels["admiral"]=[45, 75,45 ]
  # diffLevels["grand_admiral"]=[50, 100,60 ]
  # diffLevels["ensign"]=[0, 0,0 ] # npc, high ai, low ai
  # diffLevels["captain"]=[25, 25,15 ]
  # diffLevels["commodore"]=[50, 50,30 ]
  # diffLevels["admiral"]=[75, 75,45 ]
  # diffLevels["grand_admiral"]=[100, 100,60 ]
  # for diff, level in diffLevels.items():
  #   difficultiesPresetProperties[diff]["ai"]=[condValPrec(level[2], level[1],b) for b in aiDefaultPrecise]
  #   difficultiesPresetProperties[diff]["crisis"]=[condVal(level[0],b) for b in npcBoni]
  #   for cat in catsWithnpcBoniBoni:
  #     difficultiesPresetProperties[diff][cat]=[condVal(level[1],b) for b in npcBoni]

  #CRISIS DEFAULTS scheint nicht zu klappen!
  #get_galaxy_setup_value = { 
  # setting = crises
  # which = localVar
  #scale_by = 3
  #}


  defaultEvents.addComment("variable transfer: old event country to new")
  defaultDifficultyEvent=TagList("id", eventNameSpace.format(id_updateEventCountryEvents))
  defaultEvents.add("country_event",defaultDifficultyEvent)
  defaultDifficultyEvent.add("fire_only_once",yes)
  defaultDifficultyEvent.add("hide_window",yes)
  t=defaultDifficultyEvent.addReturn("trigger")
  t.addReturn("NOT").add("has_global_flag", "custom_difficulty_variables_transfered")
  immediate=defaultDifficultyEvent.addReturn("immediate")
  immediate.add("set_global_flag", "custom_difficulty_variables_transfered")
  et=immediate.addReturn(ETNew)
  for cat in cats:
    for val in possibleBoniNames:
      et.variableOpNew("set","custom_difficulty_{}_{}_value".format(cat,val), ETOld)
  et.variableOpNew("set","custom_difficulty_crisis_strength".format(cat,val), ETOld)
  et.variableOpNew("set","custom_difficulty_random_handicap_perc".format(cat,val), ETOld,"=","",True)
  et.variableOpNew("set","custom_difficulty_random_handicap".format(cat,val), ETOld,"=","",True)
  et.variableOpNew("set","custom_difficulty_randomness_factor".format(cat,val), ETOld,"=","",True)
      # et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,val)).add("value", str(value)))


  for difficultyIndex, difficulty in enumerate(difficulties):
    defaultDifficultyEvent=TagList("id", eventNameSpace.format(id_defaultEvents+difficultyIndex))
    defaultEvents.add("country_event",defaultDifficultyEvent)
    defaultDifficultyEvent.add("is_triggered_only",yes)
    defaultDifficultyEvent.add("hide_window",yes)
    immediate=TagList()
    defaultDifficultyEvent.add("immediate",immediate)
    if "scaling" in difficulty:
      immediate.add("country_event",TagList().add("id",name_resetYearlyFlagsEvent))
      scalingFlags.add("remove_global_flag","custom_difficulty_"+difficulty)
    # elif "player" in difficulty or "easy" in difficulty:
    #   immediate.add("country_event",TagList().add("id",name_resetPlayerFlagsEvent))
    #   playerFlags.add("remove_global_flag","custom_difficulty_"+difficulty)
    else:
      immediate.add("country_event",TagList().add("id",name_resetAIFlagsEvent))
      otherFlags.add("remove_global_flag","custom_difficulty_"+difficulty)
    immediate.add("set_global_flag","custom_difficulty_"+difficulty)
    et=TagList()
    immediate.add(ET,et)
    for cat, values in difficultiesPresetProperties[difficulty].items():
      if cat=="crisis":
        continue
      for i, value in enumerate(values):
        et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,possibleBoniNames[i])).add("value", str(value)))
    

    cat="crisis"
    if cat in difficultiesPresetProperties[difficulty]:
      et.addComment("Crisis strength multiply")
      values=difficultiesPresetProperties[difficulty][cat]
      for i, value in enumerate(values):
        if value:
          crisisVar="custom_difficulty_{}_{}_value".format(cat,possibleBoniNames[i])
          ifCrisisNotSet=TagList("limit", TagList("check_variable", TagList("which",crisisVar).add("value",0)))
          et.add("if", ifCrisisNotSet)
          ifCrisisNotSet.add("set_variable", TagList().add("which", crisisVar).add("value", str(value)))
          ifCrisisNotSet.add("multiply_variable", TagList("which", crisisVar).add("value", "custom_difficulty_crisis_strength"))
          ifCrisisNotSet.add("multiply_variable", TagList("which", crisisVar).add("value", 3))

  with open(outFolder+"/"+"custom_difficulty_defaults.txt",'w') as file:
    defaultEvents.writeAll(file, args())


  staticModifiers=TagList()

  modifierCats=["ai", "player", "crisis"] #three different types of modifiers. Those cats are "randomly" chosen to represent those

  removeModifierImmediates=dict()
  name_removeModifiers=dict()
  removeModifierImmediates["player"]=TagList()
  removeModifierImmediates["ai"]=TagList()
  removeModifierImmediates["crisis"]=TagList()
  addModifierImmediates=dict()
  name_addModifiers=dict()
  addModifierImmediates["player"]=TagList()
  addModifierImmediates["ai"]=TagList()
  addModifierImmediates["crisis"]=TagList()

  removeGroupModifierImmediates=dict()
  name_removeGroupModifiers=dict()
  removeGroupModifierImmediates["player"]=TagList()
  removeGroupModifierImmediates["ai"]=TagList()
  removeGroupModifierImmediates["crisis"]=TagList()
  addGroupModifierImmediates=dict()
  name_addGroupModifiers=dict()
  addGroupModifierImmediates["player"]=TagList()
  addGroupModifierImmediates["ai"]=TagList()
  addGroupModifierImmediates["crisis"]=TagList()


  removeEvents=TagList("namespace", "custom_difficulty")
  addEvents=TagList("namespace", "custom_difficulty")




  createModifierEvents(removeModifierImmediates,name_removeModifiers,removeEvents,id_removeModifiers,False) 
  createModifierEvents(addModifierImmediates,name_addModifiers,addEvents, id_addModifiers,True) 
  createModifierEvents(removeGroupModifierImmediates,name_removeGroupModifiers,removeEvents,id_removeGroupModifiers,False) 
  createModifierEvents(addGroupModifierImmediates,name_addGroupModifiers,addEvents, id_addGroupModifiers,True)


  modifierFuns=dict()
  modifierFuns["player"]=lambda i: 10*i
  modifierFuns["ai"]=lambda i: pow(2,i) 
  modifierFuns["crisis"]=lambda i: pow(2,i)*5

  modifierRange=dict()
  modifierRange["player"]=[-10, 20] #[0]*10 to [1]*10
  modifierRange["ai"]=[-8, 11] #2^([0]-1)-1 to 2^([1]-1)-1
  modifierRange["crisis"]=[-5, 20] #10*(2^([0]-1)-1) to 10*(2^([1]-1)-1)

  updateFile=TagList()
  updateFile.add("namespace","custom_difficulty")

  for groupUpdate in [False,True]:
    updateEvent=TagList()
    updateFile.add("country_event",updateEvent)

    if groupUpdate:
      updateEvent.add("id", name_countryUpdateEventSimple)
      updateEvent.add("trigger", TagList("has_global_flag", "custom_difficulty_activate_simple_mode"))
    else:
      updateEvent.add("id", name_countryUpdateEvent)
      updateEvent.add("trigger", TagList("has_global_flag", "custom_difficulty_activate_custom_mode"))
    updateEvent.add("is_triggered_only",yes)
    updateEvent.add("hide_window",yes)
    immediate=TagList()
    updateEvent.add("immediate",immediate)
    after=TagList()
    # updateEvent.add("after",after)
    for catI,cat in enumerate(cats+["no_bonuses"]):
      if catToModifierType[cat]=="none":
        continue
      applyBonuses=cat!="no_bonuses"
        
      immediate.addComment(cat)
        
      ifTagList=TagList()
      immediate.add("if",ifTagList)
      limit=TagList()
      ifTagList.add("limit",limit)
      # topLimit=limit
      if applyBonuses:
        limit=limit.addReturn("or")
      if not specificFlags[catI] is None:
        limit.add("has_country_flag", specificFlags[catI])
      if applyBonuses:
        limit=limit.addReturn("and")
        for f in allFlags:
          if f!=specificFlags[catI]:
            limit.add("not", TagList("has_country_flag", f))

        if cat=="ai":
          tmp=TagList(ET, TagList("is_variable_set", "custom_difficulty_random_handicap_perc"))
          t2=tmp.addReturn("OR")
          t2.addReturn("NOT").add("is_variable_set", "custom_difficulty_random_handicap_perc")
          t2.add("NOT",variableOpNew("check", "custom_difficulty_random_handicap_perc", ET))
          handicapChangedTest=ifTagList.createReturnIf(tmp)
          for bonus in possibleBoniNames:
            if not groupUpdate or bonus in representGroup:
              handicapChangedTest.add("set_country_flag", "custom_difficulty_{}_changed".format(bonus))
          handicapChangedTest.variableOp("set", "custom_difficulty_random_handicap_perc", ET)


        et=TagList()
        ifTagList.add(ET,et)
        if cat=="ai":
          et2=ifTagList.createReturnIf(TagList("exists","overlord").add("overlord",TagList("is_ai","no")).add("has_global_flag", "custom_difficulty_deactivate_player_vassal_ai_boni"))
          et2=et2.addReturn(ET)
        if len(catCountryType[catI])>1:
          limitOr=TagList()
          limit.add("or",limitOr)
          for countryType in catCountryType[catI]:
            limitOr.add("is_country_type", countryType)
        elif len(catCountryType[catI])==1:
          limit.add("is_country_type", catCountryType[catI][0])


        if catNotCountryType[catI]:
          norSet=set()
          toParseList=deepcopy(catNotCountryType[catI])
          while toParseList:
            # print(toParseList)
            entry=toParseList.pop(0)
            if isinstance(entry, list):
              toParseList+=entry
            else:
              norSet.add(entry)
          norTagList=TagList()
          limit.add("NOR", norTagList)
          for entry in sorted(norSet):
            norTagList.add("is_country_type", entry)
        if "player"==cat or "ai" in cat:
          # orTagList=TagList()
          if cat=="player":
            limit.add("is_ai", "no")
            # orTagList.add("and", TagList().add("has_global_flag", "custom_difficulty_deactivate_player_vassal_ai_boni").add("exists","overlord").add("overlord",TagList().add("is_ai","no")))
          else:
            limit.add("is_ai", yes)
            # orTagList.add("has_global_flag", "custom_difficulty_activate_player_vassal_ai_boni")
            # orTagList.add("not", TagList().add("exists","overlord"))
            # orTagList.add("and", TagList().add("exists","overlord").add("overlord",TagList().add("is_ai","yes")))
          # limit.add("or",orTagList)
        else:
          limit.add("is_ai", "yes")
        # afterIfTaglist=deepcopy(ifTagList)
        # after.add("if",afterIfTaglist)
        shortened=False

        for bonus, bonusModifier, val in zip(possibleBoniNames,possibleBoniModifier,defaultEmpireBonusMultList):
          if groupUpdate and not bonus in representGroup:
            continue
          et.add("set_variable", TagList().add("which", "custom_difficulty_{}_value".format(bonus)).add("value", "custom_difficulty_{}_{}_value".format(cat,bonus)))
          if cat=="ai":
            if val!=0:
              t=et2.createReturnIf(variableOpNew("check", "custom_difficulty_{}_value".format(bonus), val*9//10, ">" if val>0 else "<"))
              t.variableOpNew("change", "custom_difficulty_{}_value".format(bonus), -val)
              # et2.add("set_variable", TagList().add("which", "custom_difficulty_{}_value".format(bonus)).add("value", "custom_difficulty_{}_{}_value".format(cat,bonus)))



          ifChanged=TagList("limit", TagList("not", 
            variableOpNew("check","custom_difficulty_{}_value".format(bonus), ET)))
          # ifChanged=TagList("limit", TagList("not", 
          #   TagList("check_variable", 
          #     TagList("which","custom_difficulty_{}_value".format(bonus))
          #     .add("value", ET+":custom_difficulty_{}_value".format(bonus)))))
          ifTagList.add("if",ifChanged)
          ifChanged.add("set_country_flag", "custom_difficulty_{}_changed".format(bonus))
          if debugMode:
            ifChanged.add("log",'"setting flag {}"'.format("custom_difficulty_{}_changed".format(bonus)))
          ifChanged.variableOp("set","custom_difficulty_{}_value".format(bonus), ET)
          if bonus=="minerals":
            ifChanged.createReturnIf(TagList("has_global_flag","core_game_mechanics_and_ai")).add("check_country_imbalanced_difficulty_bonuses","yes")
          if cat in modifierCats: #only create the modifier for these cats. Rest use the same as one of those!
            removeIFChanged=TagList("limit", TagList("has_country_flag", "custom_difficulty_{}_changed".format(bonus)))
            addIFChanged=deepcopy(removeIFChanged)
            if groupUpdate:
              removeGroupModifierImmediates[cat].add("if",removeIFChanged)
              addGroupModifierImmediates[cat].add("if",addIFChanged)
            else:
              removeModifierImmediates[cat].add("if",removeIFChanged)
              addModifierImmediates[cat].add("if",addIFChanged)
            addIFChanged.add("remove_country_flag","custom_difficulty_{}_changed".format(bonus) )
            addIFChanged=addIFChanged.createReturnIf(TagList("is_variable_set", "custom_difficulty_{}_value".format(bonus)))
            addIFChanged.add("set_variable",TagList("which", "custom_difficulty_tmp").add("value","custom_difficulty_{}_value".format(bonus)))
            if cat == "ai":
              addIFChanged.variableOp("multiply", "custom_difficulty_tmp", "custom_difficulty_randomness_factor")
            for i in range(modifierRange[cat][0],modifierRange[cat][1]+1):
              #compare signs and stop for i==0
              if i<0:
                compSign="<"
                sign=-1
                signName="neg"
              elif i>0:
                compSign=">"
                sign=1
                signName="pos"
              else:
                continue
              i=abs(i)
              if cat!="player":
                i-=1
              changeValOrig=modifierFuns[cat](i)
              changeVal=sign*abs(boniFactor[bonus])*changeValOrig
              changeValModifier=changeVal
              if boniUnit[bonus]=="%":
                changeValModifier/=100
              ifModifierApplied=TagList()
              if sign>0:
                addIFChanged.insert(addIFChanged.names.index("if"),"if", ifModifierApplied)
              else:
                addIFChanged.add("if", ifModifierApplied)
              ifModifierApplied.add("limit",TagList().add("check_variable",
                TagList().add("which","custom_difficulty_tmp")
                .add("value", "{:.3f}".format(changeVal-sign*0.01),"",compSign)))
              if groupUpdate:
                modifierName="custom_difficulty_{:02d}_{}_{}_{}_value".format(i,representGroup[bonus],signName,cat)
              else:
                modifierName="custom_difficulty_{:02d}_{}_{}_{}_value".format(i,bonus,signName,cat)
              modifier=TagList()
              if groupUpdate:
                for i in bonusesListEntries[bonusesListNames.index(representGroup[bonus])]:
                  bonusModifier=[]
                  localModifier=possibleBoniModifier[i]
                  localBonus=possibleBoniNames[i]
                  if isinstance(localModifier,list):
                    bonusModifier+=localModifier
                  else:
                    bonusModifier.append(localModifier)
                  changeValLoc=sign*boniFactor[localBonus]*changeValOrig #NO ABS HERE. WE ACTUALLY NEED NEGATIVE
                  if boniUnit[localBonus]=="%":
                    changeValLoc/=100
                  for modifierEntry in bonusModifier:
                    modifier.add(modifierEntry,str(changeValLoc))
              else:
                if not isinstance(bonusModifier,list):
                  bonusModifier=[bonusModifier]
                for modifierEntry in bonusModifier:
                  modifier.add(modifierEntry,str(changeValModifier))
                # if bonus=="upkeep":
                  # modifier.add(modifierEntry,str(-sign*changeVal/100))
                # else:
                  # modifier.add(modifierEntry,str(sign*changeVal/100))
              locClass.append(modifierName,"@difficulty")
              staticModifiers.add(modifierName,modifier)
              ifModifierApplied.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
              if debugMode:
                ifModifierApplied.add("log",'"adding modifier {}"'.format(modifierName))
              removeIFChanged.add("remove_modifier", modifierName)
              if debugMode and i==1:
                removeIFChanged.add("log",'"removing modifiers (all of them, not only 1) {}"'.format(modifierName))
              ifModifierApplied.add("change_variable",TagList().add("which","custom_difficulty_tmp").add("value", str(-1*changeVal)))
      for modifierCat in modifierCats:
        ifModifierCat=TagList("limit", TagList("has_country_flag","custom_difficulty_{}_modifier_active".format(modifierCat)))
        if groupUpdate:
          ifModifierCat.add("country_event", TagList("id", name_removeGroupModifiers[modifierCat]))
        else:
          ifModifierCat.add("country_event", TagList("id", name_removeModifiers[modifierCat]))
        if not applyBonuses:
          ifModifierCat.add("country_event", TagList("id", name_removeAllModifiers))
        ifTagList.addComment("removing {} bonuses if they exist".format(modifierCat))
        ifTagList.add("if", ifModifierCat)
      if applyBonuses:
        ifTagList.addComment("adding {} bonuses".format(catToModifierType[cat]))
        if groupUpdate:
          ifTagList.add("country_event", TagList("id", name_addGroupModifiers[catToModifierType[cat]]))
        else:
          ifTagList.add("country_event", TagList("id", name_addModifiers[catToModifierType[cat]]))
    # immediate.addTagList(after)




  removeALLmodifiersEvent=TagList("id", name_removeAllModifiers)
  removeEvents.addComment("remove ALL modifier no matter what. Slow but sure. Not called on yearly stuff.")
  removeEvents.add("country_event", removeALLmodifiersEvent)
  removeALLmodifiersEvent.add("is_triggered_only",yes)
  removeALLmodifiersEvent.add("hide_window",yes)
  everyCountry=TagList()
  removeALLmodifiersEvent.add("immediate",TagList("every_country",everyCountry))
  for name in staticModifiers.names:
    if name!="":
      everyCountry.add("remove_modifier",name)
  for bonus in possibleBoniNames:
    everyCountry.add("set_variable", TagList("which","custom_difficulty_{}_value".format(bonus)).add("value",0))

  removeEventTargetEvent=TagList("id", name_removeEventTarget)
  removeEvents.addComment("remove everything on event target. Slow but sure. Not called on yearly stuff.")
  removeEvents.add("country_event", removeEventTargetEvent)
  removeEventTargetEvent.add("is_triggered_only",yes)
  removeEventTargetEvent.add("hide_window",yes)
  et=TagList()
  removeEventTargetEvent.add("immediate",TagList(ET,et))
  for cat in cats:
    for bonus in possibleBoniNames:
      et.add("set_variable", TagList("which","custom_difficulty_{}_{}_value".format(cat,bonus)).add("value",0))


  with open(outFolder+"/"+"custom_difficulty_remove_modifiers.txt",'w') as file:
    removeEvents.writeAll(file, args(1))
  with open(outFolder+"/"+"custom_difficulty_add_modifiers.txt",'w') as file:
    addEvents.writeAll(file, args(1))

  with open(outFolder+"/"+"custom_difficulty_update.txt",'w') as file:
    updateFile.writeAll(file, args())


  outputFolderStaticModifiers="../gratak_mods/custom_difficulty/common/static_modifiers"
  if not os.path.exists(outputFolderStaticModifiers):
    os.makedirs(outputFolderStaticModifiers)
  with open(outputFolderStaticModifiers+"/"+"custom_difficulty_static_modifiers.txt",'w') as file:
    staticModifiers.writeAll(file, args())


  yearlyFile=TagList()
  yearlyFile.add("namespace","custom_difficulty")
  yearlyEvent=TagList()
  yearlyFile.add("event", yearlyEvent)
  yearlyEvent.add("id", name_rootYearlyEvent)
  yearlyEvent.add("is_triggered_only",yes)
  yearlyEvent.add("hide_window",yes)
  trigger=TagList()
  yearlyEvent.add("trigger",trigger)
  immediate=TagList()
  yearlyEvent.add("immediate",immediate)
  et=TagList()
  immediate.add(ET, et)
  cat="ai"
  for bonus in possibleBoniNames:
    yearCountVar="custom_difficulty_{}_year_counter".format(bonus)
    yearLimitVar="custom_difficulty_{}_{}_value".format(cat+"_yearly",bonus)
    bonusVar="custom_difficulty_{}_{}_value".format(cat,bonus)
    ifPos=TagList().add("limit",TagList().add("check_variable", TagList().add("which", yearLimitVar).add("value","0","",">")))
    et.add("if", ifPos)
    ifNeg=TagList().add("limit",TagList().add("check_variable", TagList().add("which", yearLimitVar).add("value","0","","<")))
    et.add("if", ifNeg)
    ifPos.add("change_variable", TagList().add("which", yearCountVar).add("value", "1"))
    ifNeg.add("change_variable", TagList().add("which", yearCountVar).add("value", "1"))

    ifTagList=TagList()
    ifPos.add("if",ifTagList)
    ifTagList.add("limit", TagList().add("not",TagList().add("check_variable", TagList().add("which", yearCountVar).add("value",yearLimitVar,"","<"))))
    ifTagList.add("set_variable", TagList().add("which", yearCountVar).add("value", "0"))
    ifTagList.add("change_variable", TagList().add("which", bonusVar).add("value", f"{abs(boniFactor[bonus])}"))

    ifTagList=TagList()
    ifNeg.add("multiply_variable", TagList().add("which", yearLimitVar).add("value","-1"))
    ifNeg.add("if",ifTagList)
    ifNeg.add("multiply_variable", TagList().add("which", yearLimitVar).add("value","-1"))
    ifTagList.add("limit", TagList().add("not",TagList().add("check_variable", TagList().add("which", yearCountVar).add("value",yearLimitVar,"","<"))))
    ifTagList.add("set_variable", TagList().add("which", yearCountVar).add("value", "0"))
    ifTagList.add("change_variable", TagList().add("which", bonusVar).add("value", f"-{abs(boniFactor[bonus])}"))

  with open(outFolder+"/"+"custom_difficulty_yealy_event.txt",'w') as file:
    yearlyFile.writeAll(file, args())




  createEdictFile()

  onActions=TagList()
  onActions.add("on_yearly_pulse", TagList("events",TagList().add(name_rootYearlyEvent,""," #rootYearly").add(name_rootUpdateEvent,""," #rootUpdate")))
  onActions.add("on_game_start_country", TagList("events",TagList().add(name_gameStartFireOnlyOnce),"#set flag,set event target, start default events, start updates for all countries"))
  # onActions.add("on_single_player_save_game_load", TagList("events",TagList().add(eventNameSpace.format(id_updateEventCountryEvents))))


  # onActions.add("on_single_player_save_game_load", TagList("events",TagList().add(name_dmm_new_init)))
  # onActions.add("dmm_mod_selected", TagList("events",TagList().add(name_dmm_new_start)))
  onActions.add("on_ruler_set", TagList("events",TagList().add(name_countryUpdateOneDayDelayEvent), "#new country update"))
  outputToFolderAndFile(onActions, "common/on_actions", "custom_difficulty_on_action.txt")
  onActionsDMM=TagList("on_single_player_save_game_load", TagList("events",TagList().add(name_dmm_new_init)))
  onActionsDMM.add("on_game_start", TagList("events",TagList().add(name_dmm_new_init)))
  onActionsDMM.add("dmm_mod_selected", TagList("events",TagList().add(name_dmm_new_start)))
  outputToFolderAndFile(onActionsDMM, "common/on_actions", "custom_difficulty_dmm_on_action.txt",2)

  scriptedEffects=TagList("guardian_difficulty",TagList()," #I commented out the effect of the stuff applied here, but it was not up to date. Once they update it, that will be active again. Thus I kill this function as well to make sure it won't become active!")
  outputToFolderAndFile(scriptedEffects,"common/scripted_effects","!_custom_difficulty_00_scripted_effects.txt")

  scriptedModifiers=TagList("","","########################################################################")
  scriptedModifiers.add("","","# Difficulty Modifiers - empty. Everything is applied via the mod to make it customizable. Defaults are basically the same!")
  scriptedModifiers.add("","","##########################################################################")
  scriptedModifiers.add("","","# For playable empires")
  scriptedModifiers.add("difficulty_scaling",TagList())
  scriptedModifiers.add("difficulty_grand_admiral",TagList())
  scriptedModifiers.add("difficulty_admiral",TagList())
  scriptedModifiers.add("difficulty_commodore",TagList())
  scriptedModifiers.add("difficulty_captain",TagList())
  scriptedModifiers.add("difficulty_ensign",TagList())
  scriptedModifiers.add("difficulty_cadet_player",TagList())
  scriptedModifiers.add("","","# For non-playable empires, scales to setting in country type")
  scriptedModifiers.add("difficulty_scaling_npc",TagList())
  scriptedModifiers.add("difficulty_grand_admiral_npc",TagList())
  scriptedModifiers.add("difficulty_admiral_npc",TagList())
  scriptedModifiers.add("difficulty_commodore_npc",TagList())
  scriptedModifiers.add("difficulty_captain_npc",TagList())
  scriptedModifiers.add("difficulty_ensign_npc",TagList())
  scriptedModifiers.add("guardian_hard",TagList())
  scriptedModifiers.add("guardian_insane",TagList())
  scriptedModifiers.add("difficulty_insane_ai",TagList())
  scriptedModifiers.add("difficulty_very_hard_ai",TagList())
  scriptedModifiers.add("difficulty_hard_ai",TagList())
  scriptedModifiers.add("difficulty_normal_ai",TagList())
  scriptedModifiers.add("difficulty_scaled_insane",TagList())
  scriptedModifiers.add("difficulty_scaled_very_hard",TagList())
  scriptedModifiers.add("difficulty_scaled_hard",TagList())
  scriptedModifiers.add("difficulty_scaled_normal",TagList())
  # scriptedModifiers.add("playable_ai_empire",TagList())
  outputToFolderAndFile(scriptedModifiers, "common/static_modifiers","!_custom_difficulty_00_static_modifier.txt")

  createMenuFile(locClass, cats, catColors,difficulties,debugMode)

  createTriggerFile()

  locClass.writeToMod("../gratak_mods/custom_difficulty","custom_difficulty")
  locClassReplace.addLoc("modName", "Dynamic Difficulty", "all")
  locClassReplace.addLoc("menuDesc", "Triggers an event to let you customize the difficulty of your current game")
  locClassReplace.addEntry(f"dmm_mod_{dmmType}_{dmmId}", "@modName")
  locClassReplace.addEntry(f"dmm_mod_{dmmType}_{dmmId}.title", "@modName")
  locClassReplace.addEntry(f"dmm_mod_{dmmType}_{dmmId}.desc", "@menuDesc")
  locClassReplace.writeToMod("../gratak_mods/custom_difficulty","custom_difficulty_dmm")

  # locClassCopy=deepcopy(locClass)
  # for language in locClass.languages:
  #   outFolderLoc="../gratak_mods/custom_difficulty/localisation/"+language
  #   if not os.path.exists(outFolderLoc):
  #     os.makedirs(outFolderLoc)
  #   locClass.write(outFolderLoc+"/custom_difficulty_l_"+language+".yml",language)

def createMenuFile(locClass, cats, catColors, difficulties, debugMode=False, modFolder="../gratak_mods/custom_difficulty", reducedMenu=False, gameStartAfter=None):

  locClass.addEntry("custom_difficulty_current_bonuses","@curBon:")
  locClass.addEntry("custom_difficulty_current_yearly_desc", "@yearlyDesc. @cur:")
  locClass.addEntry("custom_difficulty_back", "@back")
  locClass.addEntry("custom_difficulty_cancel", "@cancel")
  locClass.addEntry("custom_difficulty_close.name", "@close @modName @menu")
  locClass.addEntry("custom_difficulty_lock.name", "§R@lock§!")
  locClass.addEntry("custom_difficulty_lock.desc", "@lockDesc @care")
  locClass.addEntry("custom_difficulty_locked.name", "@lockActive")
  locClass.addEntry("custom_difficulty_locked.desc", "§R@lockActive @lockActiveDesc§!")
  # locClass.addEntry("custom_difficulty_lockActive.desc", "@lockActive @lockActiveDesc")
  locClass.addEntry("custom_difficulty_unlock.name", "@unlock")
  locClass.addEntry("edict_custom_difficulty", "@modName - @main @menu") #also used for menu title. Has to be named edict for the edict
  locClass.addEntry("edict_custom_difficulty_desc", "@menuDesc")
  locClass.addEntry("custom_difficulty_init", "@modName - @init") #also used for menu title. Has to be named edict for the edict
  locClass.addEntry("custom_difficulty_init_desc", "@initDesc")
  locClass.addEntry("custom_difficulty_options.name", "@options")
  locClass.addEntry("custom_difficulty_choose_desc", "@choose")
  locClass.addEntry("custom_difficulty_choose", "@choosePreDef.§R @delWarn§! @combineText")
  # locClass.addEntry("custom_difficulty_easy.name", "§G@easy - 20% @bonus @allCat @forPlayer§!")
  locClass.addEntry("custom_difficulty_reset.name", "@reset")
  locClass.addEntry("custom_difficulty_reset_conf.name", "@reset - @confirmation")
  locClass.addEntry("custom_difficulty_reset.desc", "@resetDesc")
  if not reducedMenu:
    locClass.addEntry("custom_difficulty_init_crisis_desc", "@crisisInit")
    locClass.addEntry("custom_difficulty_init_no_crisis_desc", "@noCrisisInit")
    locClass.addEntry("custom_difficulty_predef_head.name", "@modName - @preDef")
    locClass.addEntry("custom_difficulty_predefined_colored.name", "§G@preDef")
    locClass.append("custom_difficulty_crisis_colored.name","§R@crisis @strength")
    locClass.append("custom_difficulty_customize_colored.name","§Y@difficulty @customization")
    locClass.append("custom_difficulty_customize.name","§Y@difficulty @customization")
    locClass.addEntry("custom_difficulty_no_player_bonus.name", "§G@no @bonus @forPlayer§!")
    locClass.addEntry("custom_difficulty_cadet.name", "§B@cadet - 30-50% @bonus @forPlayer. @no @bonus @forAI. 15% @forNPCs§!")
    locClass.addEntry("custom_difficulty_ensign.name", "§B@ensign - @no @bonus @forAI. 15% @bonus @forNPCs§!")
    locClass.addEntry("custom_difficulty_captain.name", "§B@captain - 15-25% @bonus @forAI. 17.5% @forNPCs§!")
    locClass.addEntry("custom_difficulty_commodore.name", "§B@commodore - 30-50% @bonus @forAI. 20% @forNPCs§!")
    locClass.addEntry("custom_difficulty_admiral.name", "§B@admiral - 45-75% @bonus @forAI. 22.5% @forNPCs§!")
    locClass.addEntry("custom_difficulty_grand_admiral.name", "§B@grandAdmiral - 60-100% @bonus @forAI. 25% @forNPCs§!")
    locClass.addEntry("custom_difficulty_scaling.name", "§H@scaling - @increase @bonus @forAI @every 4 @years§!")
    locClass.addEntry("custom_difficulty_no_scaling.name", "§H@no @scaling§!")
    locClass.addEntry("custom_difficulty_advanced_configuration.name", "§B@advCust @nonPlayer§!")
    locClass.addEntry("custom_difficulty_advanced_configuration_player.name", "§G@advCust @player§!")
    locClass.addEntry("custom_difficulty_advanced_configuration_scaling.name", "§H@advCust @yearly§!")

  mainFileContent=TagList("namespace","custom_difficulty")
  mainFileContent.add("","","#main menu")
  # main Menu (including unlock output)
  mainMenu=TagList()
  mainFileContent.add("country_event",mainMenu)
  for allowUnlock in [False]:#[False,True]:
    mainMenu.add("id", name_mainMenuEvent)
    mainMenu.add("is_triggered_only", yes)
    mainMenu.add("title", "edict_custom_difficulty")
    if reducedMenu:
      mainMenu.add("picture", "GFX_evt_synth_sabotage")
    else:
      mainMenu.add("picture", "GFX_evt_custom_difficulty_pyra")
    immediate=mainMenu.addReturn("immediate")
    if not reducedMenu:
      immediate.addReturn("country_event").add("id", eventNameSpace.format(id_updateEventCountryEvents)) #call transfer event. Only happens if player opens menu the day the new version is first loaded
      immediate=immediate.createReturnIf(TagList("has_global_flag","custom_difficultyMM_active"))
    immediate.addReturn("country_event").add("id", cdmm.name_updateEventCountryEvents_mm) #call transfer event. Only happens if player opens menu the day the new version is first loaded
    trigger=TagList()
    mainMenu.add("desc", TagList("trigger", trigger))
    trigger.add("fail_text", TagList().add("text", "custom_difficulty_choose_desc").add("custom_difficulty_allow_changes", "no"))
    trigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("custom_difficulty_allow_changes", "no"))
    if not reducedMenu:
      mainMenu.add("option", TagList("name","custom_difficulty_predefined_colored.name").add("hidden_effect", TagList("country_event", TagList("id", name_defaultMenuEvent))))
      mainMenu.add("option", TagList("name","custom_difficulty_crisis_colored.name").add("trigger", TagList("is_crises_allowed", yes)).add("hidden_effect", TagList("country_event", TagList("id", eventNameSpace.format(id_ChangeEvents+cats.index("crisis")*id_ChangeEvents))).add("remove_global_flag","custom_difficulty_menu_crisis_from_custom")))
      mainMenu.add("option", TagList("name","custom_difficulty_customize_colored.name").add("hidden_effect", TagList("country_event", TagList("id", name_customMenuEvent))))
    mainMenu.add("option", TagList("name","custom_difficulty_options.name").add("hidden_effect", TagList("country_event", TagList("id", name_optionsEvent))))
    mainMenu.add("option", TagList("name","custom_difficulty_mainMenuMM.name").add("trigger", TagList("has_global_flag", "custom_difficultyMM_active")).add("hidden_effect", TagList("country_event", TagList("id", "custom_difficulty_mm.{!s}".format(1)))))
    locClass.append("custom_difficulty_mainMenuMM.name", "§BMore Modifiers§!")

    mainMenu.add("option", t_closeOption)


  if not reducedMenu:
    customMenu=TagList()
    mainFileContent.addComment("custom Menu")
    mainFileContent.add("country_event",customMenu)
    customMenu.add("id", name_customMenuEvent)
    customMenu.add("is_triggered_only", yes)
    customMenu.add("title", "custom_difficulty_customize.name")
    customMenu.add("picture", "GFX_evt_custom_difficulty")
    trigger=TagList()
    customMenu.add("desc", TagList("trigger", trigger))
    trigger.add("fail_text", TagList().add("text", "custom_difficulty_choose_desc").add("custom_difficulty_allow_changes", "no"))
    trigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("custom_difficulty_allow_changes", "no"))
    for i,cat in enumerate(cats):
      hidden_effect=TagList("country_event", TagList("id", eventNameSpace.format(id_ChangeEvents+i*id_ChangeEvents)))
      option=TagList("name","custom_difficulty_{}_colored.name".format(cat))
      customMenu.add("option",option)
      if cat=="crisis":
        hidden_effect.add("set_global_flag","custom_difficulty_menu_crisis_from_custom")
        option.add("trigger", TagList("is_crises_allowed", yes))
      option.add("hidden_effect", hidden_effect)
      locClass.addEntry("custom_difficulty_{}_colored.name".format(cat), "§{}@change @{} @bonuses§!".format(catColors[i],cat))
    customMenu.add("option", t_backMainOption)
    customMenu.add("option", t_closeOption)

    mainFileContent.add("","","#default menu")
    defaultMenuEvent=TagList("id", name_defaultMenuEvent)
    mainFileContent.add("country_event", defaultMenuEvent)
    defaultMenuEvent.add("is_triggered_only", yes)
    defaultMenuEvent.add("title", "custom_difficulty_predef_head.name")
    defaultMenuEvent.add("picture", "GFX_evt_towel")
    trigger=TagList()
    defaultMenuEvent.add("desc", TagList("trigger", trigger))
    trigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("custom_difficulty_allow_changes", "no"))
    trigger.add("text", "custom_difficulty_current_bonuses")
    for difficulty in difficulties:
      trigger.add("success_text", TagList("text", "custom_difficulty_{}.name".format(difficulty)).add("has_global_flag", "custom_difficulty_{}".format(difficulty)))
    trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_player.name").add("has_global_flag", "custom_difficulty_advanced_configuration_player"))
    trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration.name").add("has_global_flag", "custom_difficulty_advanced_configuration"))
    trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_scaling.name").add("has_global_flag", "custom_difficulty_advanced_configuration_scaling"))
    # trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_crisis.name").add("has_global_flag", "custom_difficulty_advanced_configuration_crisis"))
    trigger.add("fail_text", TagList("text", "custom_difficulty_choose").add("custom_difficulty_allow_changes", "no"))
    for i,difficulty in enumerate(difficulties):
      option=TagList("name","custom_difficulty_{}.name".format(difficulty))
      defaultMenuEvent.add("option", option)
      option.add("trigger", deepcopy(t_notLockedTrigger).add("not",TagList("has_global_flag", "custom_difficulty_{}".format(difficulty))))
      option.add("hidden_effect", TagList("country_event", TagList("id", eventNameSpace.format(id_defaultEvents+i))).add("country_event", TagList("id", name_defaultMenuEvent)))
    defaultMenuEvent.add("option", TagList("name", "custom_difficulty_reset.name").add("trigger", t_notLockedTrigger).add("hidden_effect", TagList("country_event", TagList("id", name_resetConfirmationEvent))))
    defaultMenuEvent.add("option", t_backMainOption)
    defaultMenuEvent.add("option", t_closeOption)

  optionsEvent=TagList()
  mainFileContent.addComment("options Event")
  mainFileContent.add("country_event", optionsEvent)

  rootUpdateMenu=TagList("id",name_rootUpdateEvent)
  mainFileContent.addComment("root update event")
  mainFileContent.add("event", rootUpdateMenu)
  rootUpdateMenu.add("is_triggered_only", yes)
  rootUpdateMenu.add("hide_window", yes)
  if not reducedMenu:
    immediate=TagList()
    rootUpdateMenu.add("immediate",immediate)
    ifSimple=TagList("limit",TagList("has_global_flag", "custom_difficulty_activate_simple_mode"))
    ifSimple.add("if", ifDelay(name_countryUpdateEventSimple))
    ifSimple.add("else", TagList("every_country", TagList("country_event", TagList("id", name_countryUpdateEventSimple)))) #fixed 2.1
    immediate.add("if", ifSimple)
    immediate.add("else", TagList("if",ifDelay(name_countryUpdateEvent)).add("else", TagList("every_country", TagList("country_event", TagList("id", name_countryUpdateEvent))))) #fixed 2.1

  countryRootUpdateMenu=deepcopy(rootUpdateMenu)
  countryRootUpdateMenu.replace("id",name_countryRootUpdateEvent)
  mainFileContent.addComment("root update event")
  mainFileContent.add("country_event", countryRootUpdateMenu)

  newCountryUpdateEvent=TagList("id",name_countryUpdateOneDayDelayEvent)
  mainFileContent.addComment("newCountryUpdateEvent")
  mainFileContent.add("country_event", newCountryUpdateEvent)
  newCountryUpdateEvent.add("is_triggered_only", yes)
  newCountryUpdateEvent.add("hide_window", yes)
  immediate=TagList()
  newCountryUpdateEvent.add("immediate",immediate)
  ifSimple=TagList("limit",TagList("has_global_flag", "custom_difficulty_activate_simple_mode"))
  ifSimple.add("country_event", TagList("id", name_countryUpdateEventSimple).add("days","1"))
  immediate.add("if", ifSimple)
  immediate.add("else", TagList("country_event", TagList("id", name_countryUpdateEvent).add("days","1")))


  dmmNewInit=TagList("id",name_dmm_new_init)
  mainFileContent.addComment("new dmm init event")
  mainFileContent.add("event", dmmNewInit)
  dmmNewInit.triggeredHidden()
  dmmNewInit.add("immediate", TagList("dmm_register_mod", TagList("DMM_NAME","custom_difficulty_dmm_loc").add("DMM_FLAG", "custom_difficuly_new_dmm_menu_flag")))
  locClass.addEntry("custom_difficulty_dmm_loc", "@modNameFull")

  dmmNewMenu=TagList("id",name_dmm_new_start)
  mainFileContent.addComment("dmm new menu starter")
  mainFileContent.add("country_event", dmmNewMenu)
  dmmNewMenu.triggeredHidden()
  dmmNewMenu.add("trigger", TagList("from", TagList("has_leader_flag", "custom_difficuly_new_dmm_menu_flag")))
  dmmNewMenu.add("immediate", TagList("country_event", TagList("id", name_mainMenuEvent)))

  gameStartInitEventWithDialog=TagList("id", name_gameStartFireOnlyOnceWithDialog) #still required for older versions
  gameStartInitEventWithDialog.add("title","custom_difficulty_init" )
  gameStartInitEventWithDialog.add("picture","GFX_evt_custom_difficulty")
  gameStartInitEventWithDialog.add("is_triggered_only", yes)
  gameStartInitEvent=TagList("id", name_gameStartFireOnlyOnce)
  gameStartInitEvent.add("hide_window", yes)
  trigger=TagList()
  gameStartInitEventWithDialog.add("desc", TagList("trigger", trigger)) #"" )
  trigger.add("text","custom_difficulty_init_desc")
  trigger.add("success_text", TagList("text","custom_difficulty_init_crisis_desc").add("is_crises_allowed", "yes"))
  trigger.add("success_text", TagList("text", "custom_difficulty_init_no_crisis_desc").add("is_crises_allowed", "no"))
  mainFileContent.add("","","#game start init")
  mainFileContent.add("country_event", gameStartInitEvent)
  mainFileContent.add("","","#legacy game start init")
  mainFileContent.add("country_event", gameStartInitEventWithDialog)
  gameStartInitEvent.add("fire_only_once", yes)
  # gameStartInitEvent.add("hide_window", yes)
  t_anyOption=TagList()
  gameStartInitEvent.add("trigger", TagList("is_ai","no").add("or", TagList("NOR", t_anyOption).add("not", TagList("has_global_flag", "custom_difficulty_active")).add("has_global_flag", "MM_was_active_before_custom_difficulty")))
  immediate=TagList()
  gameStartInitEvent.add("immediate",immediate)
  immediate.createEvent(name_randomDiffFireOnlyOnce)
  immediate.add("set_country_flag", "custom_difficulty_game_host")
  immediate.add("set_global_flag", "custom_difficulty_variables_transfered")
  immediate.add("if", TagList("limit", TagList("NOR", t_anyOption).add("has_global_flag", "custom_difficulty_active"))
    .add("country_event", TagList("id", name_resetFlagsEvent)," #resetFlagsEvent")
    .add("country_event", TagList("id", name_removeEventTarget)," #removeEventTarget"))
  # .add("every_country",TagList("country_event", TagList("id", name_removeOLDModifiers)," #removeOldModifiers")))

  # resetEvent.get("immediate").insert(0, "country_event", TagList("id", name_resetFlagsEvent)," #resetFlagsEvent").insert(0, "country_event", TagList("id", name_removeEventTarget)," #removeEventTarget")
  createEventTarget=immediate.createReturnIf(TagList("has_global_flag","MM_was_active_before_custom_difficulty"))
  createEventTarget.add("remove_global_flag","MM_was_active_before_custom_difficulty")
  # createEventTarget=immediate.addReturn("else")
  # createEventTarget.add("random_galaxy_planet", TagList("save_global_event_target_as", "custom_difficulty_var_storage"))
  # createEventTarget.add("random_planet", TagList("save_global_event_target_as", "custom_difficulty_var_storage"))

  immediate.add(ET,TagList("get_galaxy_setup_value", TagList("which", "custom_difficulty_crisis_strength").add("setting", "crisis_strength_scale")).variableOp("set", "custom_difficulty_random_handicap_perc", 0).variableOp("set", "custom_difficulty_random_handicap", 0))#.add("scale_by", "3"))
  # gameStartInitEvent.add("option", TagList("name", "OK").add("trigger", TagList(ET,TagList("check_variable",TagList("which", "custom_difficulty_crisis_strength").add("value","0","",">")))))
  for strength in [0.25, 0.5, 1, 2,3,4,5,10,15,20,25]:
    gameStartInitEventWithDialog.add("option", TagList("name", "custom_difficulty_{!s}_crisis.name".format(strength))
      .add("trigger", TagList("is_crises_allowed", yes))
      .add("hidden_effect", TagList(ET,TagList("set_variable", TagList("which","custom_difficulty_crisis_strength").add("value",str(strength))))))
    locClass.addEntry("custom_difficulty_{!s}_crisis.name".format(strength), "§R{}x @crisisStrength§!".format(strength))
  gameStartInitEventWithDialog.add("option", TagList("name", "OK").add("trigger", TagList("is_crises_allowed", "no")))
  for s in [gameStartInitEventWithDialog,gameStartInitEvent]:
    gameStartAfter=TagList()
    s.add("after",TagList("hidden_effect", gameStartAfter))
    gameStartAfter2=gameStartAfter
    if s==gameStartInitEvent:
      gameStartAfter=gameStartAfter.createReturnIf(TagList(ET,TagList("OR", TagList("check_variable",TagList("which", "custom_difficulty_crisis_strength").add("value","0","",">")).add("is_crises_allowed", "no"))))
    # gameStartInitEvent.add("option", TagList("name", "OK").add("trigger", TagList(ET,TagList("check_variable",TagList("which", "custom_difficulty_crisis_strength").add("value","0","",">")))))
    gameStartAfter.add("set_global_flag", "custom_difficulty_active")
    gameStartAfter.add("set_global_flag", f"dmm_mod_{dmmType}_{dmmId}")
    gameStartAfter.add("set_global_flag","custom_difficulty_no_player_bonus")
    gameStartAfter.add("set_global_flag","custom_difficulty_no_scaling")

    if not reducedMenu:
      vanillaDefaultDifficultyNames=difficulties[0:]
      for i, difficulty in enumerate(difficulties):
        if difficulty=="scaling":
          continue
        elif difficulty in vanillaDefaultDifficultyNames:
          k=vanillaDefaultDifficultyNames.index(difficulty)
        else:
          continue #those cannot be preset in game creation
        gameStartAfter.add("","","#"+difficulty)
        gameStartAfter.add("if", TagList("limit", TagList("is_difficulty", str(k))).add("country_event",TagList("id", eventNameSpace.format(id_defaultEvents+i))))
      gameStartAfter.add("country_event", TagList("id", name_countryRootUpdateEvent))
      if s==gameStartInitEvent:
        gameStartAfter2.add("else",TagList("country_event",TagList("id",name_gameStartFireOnlyOnceWithDialog)))

  mainFileContent.addComment("Assign a variable to each default country that will decide how much their difficulty modifiers are decreased by randomness")
  randomInitEvent=mainFileContent.addReturn("country_event")
  randomInitEvent.add("id", name_randomDiffFireOnlyOnce)
  randomInitEvent.add("hide_window",yes)
  randomInitEvent.add("trigger", TagList("NOT", TagList("has_global_flag", "custom_difficulty_random_difficulty_given")))
  immediate=randomInitEvent.addReturn("immediate")
  immediate.add("set_global_flag", "custom_difficulty_random_difficulty_given")
  immediateEachCountry=immediate.addReturn("every_country")
  immediateEachCountry.add("limit", TagList("is_country_type","default").add("is_ai", "yes"))
  randomList=immediateEachCountry.addReturn("random_list")
  maxRandVal=20 #if you change this, you need to also change the 20 in createModifierEvents (where I was to lazy to add this as input!)
  for i in range(maxRandVal+1): #nbr of random steps
    e=randomList.addReturn("1") #uniform chance
    e.variableOp("set", "custom_difficulty_random_handicap",i)
  if debugMode:
    immediateEachCountry.add("log",'"[this.GetName]:[this.custom_difficulty_random_handicap]"')







  optionsEvent.add("id", name_optionsEvent)
  optionsEvent.add("is_triggered_only", yes)
  optionsEvent.add("title", "custom_difficulty_options.name")
  # optionsEvent.add("desc", "custom_difficulty_options.desc")
  optionsEvent.add("picture", "GFX_evt_towel")
  # optionsEvent.add("picture","GFX_evt_custom_difficulty_pyra")


  descTrigger=TagList()
  optionsEvent.add("desc", TagList("trigger", descTrigger))
  descTrigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("custom_difficulty_allow_changes", "no"))
  descTrigger.add("text", "custom_difficulty_current_options")
  locClass.append("custom_difficulty_current_options", "@current_options")


  optionWithInverse=dict()
  # flag is going to be "custom_difficulty_"+key
  # name "custom_difficulty_"+key
  # desc "custom_difficulty_"+key+".desc"
  if not reducedMenu:
    optionWithInverse["activate_custom_mode"]=["activate_simple_mode"]
    optionWithInverse["activate_simple_mode"]=["activate_custom_mode"]
    optionWithInverse["deactivate_player_vassal_ai_boni"]=["activate_player_vassal_ai_boni"]
    optionWithInverse["activate_player_vassal_ai_boni"]=["deactivate_player_vassal_ai_boni"]
    optionWithInverse["deactivate_delay_mode"]=["activate_delay_mode"]
    optionWithInverse["activate_delay_mode"]=["deactivate_delay_mode"]
  optionWithInverse["activate_edict"]=["deactivate_edict"]
  optionWithInverse["deactivate_edict"]=["activate_edict"]
  optionWithInverse["activate_host_only"]=["deactivate_host_only"]
  optionWithInverse["deactivate_host_only"]=["activate_host_only"]
  # optionWithInverse[]=[]

  optionExtraEvents=dict()
  optionExtraEvents["activate_simple_mode"]=["name_removeAllModifiers"]
  optionExtraEvents["activate_custom_mode"]=["name_removeAllModifiers"]

  optionColors="GGBBYYEERR"
  defaultOptions=[]


  optionI=-1
  for key, inverses in optionWithInverse.items():
    optionI+=1
    seperateDesc=False
    locClass.append("custom_difficulty_"+key+".desc", "§{}@{}Desc§!".format(optionColors[optionI],key))
    locClass.append("custom_difficulty_"+key+".name", "§{}@{}§!".format(optionColors[optionI],key))

    successText=descTrigger.addReturn("success_text")
    successText.add("text", "custom_difficulty_"+key+".desc").add("has_global_flag", "custom_difficulty_"+key)
    if "host_only" in key:
      successText.add("is_multiplayer", "yes")
    option=TagList("name","custom_difficulty_{}.name".format(key))
    optionsEvent.add("option", option)
    option.add("custom_tooltip", "custom_difficulty_{}.desc".format(key))
    trigger=deepcopy(t_notLockedTrigger)
    option.add("trigger", trigger)
    trigger.add("not", TagList("has_global_flag", "custom_difficulty_"+key))
    if "host_only" in key:
      trigger.add("is_multiplayer","yes") 
      # immediate.add("set_country_flag", "custom_difficulty_game_host")
      trigger.add("has_country_flag", "custom_difficulty_game_host") 
    if not reducedMenu:
      t_anyOption.add("has_global_flag", "custom_difficulty_"+key)
    effect=TagList("set_global_flag", "custom_difficulty_"+key)
    inverseIsDefault=False
    for inverse in inverses:
      effect.add("remove_global_flag", "custom_difficulty_"+inverse)
      if inverse in defaultOptions:
        inverseIsDefault=True
    if not inverseIsDefault:
      for name, val in effect.getNameVal():
        gameStartAfter2.insert(0, name, deepcopy(val))
      # gameStartAfter.addTagList(deepcopy(effect))
      defaultOptions.append(key)
    if key in optionExtraEvents:
      for e in optionExtraEvents[key]:
        add_event(effect,e)
    add_event(effect,"name_optionsEvent")
    # effect.add("country_event", TagList("id", name_optionsEvent))
    option.add("hidden_effect", effect)
  optionsEvent.add("option", TagList("name","custom_difficulty_lock.name").add("trigger", t_notLockedTrigger).add("hidden_effect", TagList("country_event", TagList("id",name_lockEvent))))
  hostOrNotMP=TagList("OR", TagList("is_multiplayer", "no").add("has_country_flag", "custom_difficulty_game_host"))
  increaseRandomOpt=optionsEvent.addReturn("option")
  decreaseRandomOpt=optionsEvent.addReturn("option")
  if not reducedMenu:
    optionsEvent.add("option", TagList("name","custom_difficulty_remove.name").add("trigger", hostOrNotMP).add("custom_tooltip","custom_difficulty_remove.desc").add("hidden_effect", TagList("country_event", TagList("id",name_removeEvent))))
  resetMM=optionsEvent.addReturn("option")
  removeMM=optionsEvent.addReturn("option")
  trigger=TagList("trigger", TagList("has_global_flag", "custom_difficultyMM_active"))
  resetMM.addTagList(trigger)
  removeMM.addTagList(trigger)
  resetMM.add("name", "custom_difficultyMM_reset.name")
  removeMM.add("name", "custom_difficultyMM_remove.name")
  resetMM.add("custom_tooltip", "custom_difficultyMM_reset.desc")
  removeMM.add("custom_tooltip", "custom_difficultyMM_remove.desc")
  resetMM.addReturn("hidden_effect").createEvent(cdmm.name_resetConfirmationEvent)
  removeMM.addReturn("hidden_effect").createEvent(cdmm.name_removeConfirmationEvent)

  locClass.addEntry("custom_difficultyMM_remove.name", "@uninstall @modName : More Modifiers")
  locClass.addEntry("custom_difficultyMM_remove.desc", "@uninstallDescMM")
  locClass.addEntry("custom_difficultyMM_reset.name", "@reset @for @modName : More Modifiers")
  locClass.addEntry("custom_difficultyMM_reset.desc", "@resetDescMM")

  optionsEvent.add("option", t_backMainOption )
  optionsEvent.add("option", t_closeOption)


  # enableUpdateEffect=TagList("every_country",TagList("limit",TagList("is_country_type","default").add("is_ai","yes")).add("set_country_flag", "custom_difficulty_{}_changed".format(bonus)))


  successText=descTrigger.addReturn("success_text")
  successText.add("text", "custom_difficulty_random_handicap.desc")
  successText.addReturn(ET).addReturn("not").variableOp("check","custom_difficulty_random_handicap_perc",0) #.addReturn("trigger")
  locClass.append("custom_difficulty_random_handicap.desc","§P@randomHandicap: @max [{}.custom_difficulty_random_handicap_perc] %§!".format(ET))
  decreaseRandomOpt.addReturn("trigger").add("custom_difficulty_allow_changes","yes").addReturn(ET).variableOp("check", "custom_difficulty_random_handicap_perc",0,">")
  decreaseRandomOpt.add("name", "custom_difficulty_random_handicap_dec.desc")
  decreaseRandomOpt.addReturn("hidden_effect").add_event("name_optionsEvent").addReturn(ET).variableOp("change","custom_difficulty_random_handicap_perc",-10)
  # decreaseRandomOpt.addReturn("hidden_effect").add_event("name_optionsEvent").addTagList(enableUpdateEffect).addReturn(ET).variableOp("change","custom_difficulty_random_handicap_perc",-5)
  locClass.append("custom_difficulty_random_handicap_dec.desc","§P@decrease @randomHandicap @by 10%§!")
  increaseRandomOpt.addReturn("trigger").add("custom_difficulty_allow_changes","yes")
  increaseRandomOpt.add("name", "custom_difficulty_random_handicap_inc.desc")
  increaseRandomOpt.addReturn("hidden_effect").add_event("name_optionsEvent").addReturn(ET).variableOp("change","custom_difficulty_random_handicap_perc",10)
  # increaseRandomOpt.addReturn("hidden_effect").add_event("name_optionsEvent").addTagList(enableUpdateEffect).addReturn(ET).variableOp("change","custom_difficulty_random_handicap_perc",5)
  locClass.append("custom_difficulty_random_handicap_inc.desc","§P@increase @randomHandicap @by 10%§!")

  if not reducedMenu:
    optionEventUnlock=deepcopy(optionsEvent)
    optionEventUnlock.insert(-2,"option",TagList("name","custom_difficulty_unlock.name").add("trigger", TagList("has_global_flag","custom_difficulty_locked")).add("hidden_effect",TagList("remove_global_flag", "custom_difficulty_locked").add("country_event", t_mainMenuEvent)))
    mainFileUnlock=TagList("namespace", "custom_difficulty")
    mainFileUnlock.add("country_event", optionEventUnlock)
    outputToFolderAndFile(mainFileUnlock, "events", "!_custom_difficulty_unlock.txt", 1, "../gratak_mods/custom_difficulty_unlock_new/")

  if not reducedMenu: #todo: might need some of this!
    mainFileContent.add("","","#reset event")
    resetEvent=deepcopy(gameStartInitEvent)
    resetEvent.replace("id", name_resetEvent)
    resetEvent.remove("fire_only_once")
    resetEvent.remove("trigger")
    resetEvent.add("is_triggered_only",yes)
    resetEvent.get("immediate").remove("if")
    resetEvent.get("immediate").insert(0, "country_event", TagList("id", name_resetFlagsEvent)," #resetFlagsEvent").insert(0, "country_event", TagList("id", name_removeEventTarget)," #removeEventTarget")
    mainFileContent.add("country_event", resetEvent)

    mainFileContent.add("","","#reset confirmation")
    resetConfirmation=TagList("id", name_resetConfirmationEvent)
    mainFileContent.add("country_event", resetConfirmation)
    resetConfirmation.add("is_triggered_only",yes)
    resetConfirmation.add("title","custom_difficulty_reset_conf.name")
    resetConfirmation.add("desc","custom_difficulty_reset.desc")
    resetConfirmation.add("picture", "GFX_evt_towel")
    effect=TagList()
    add_event(effect, "name_resetFlagsEvent")
    add_event(effect, "name_resetEvent")
    resetConfirmation.add("option", TagList("name", "OK").add("hidden_effect", effect))
    resetConfirmation.add("option", TagList("name", "custom_difficulty_cancel").add("hidden_effect", TagList("country_event", TagList("id", name_defaultMenuEvent))))

    mainFileContent.add("","","#remove confirmation")
    removeConfirmation=TagList("id", name_removeEvent)
    mainFileContent.add("country_event", removeConfirmation)
    removeConfirmation.add("is_triggered_only",yes)
    removeConfirmation.add("title","custom_difficulty_remove.name")
    locClass.addEntry("custom_difficulty_remove.name", "@uninstall @modName")
    locClass.addEntry("custom_difficulty_remove.desc", "@uninstallDesc")
    removeConfirmation.add("desc","custom_difficulty_remove.desc")
    removeConfirmation.add("picture", "GFX_evt_towel")
    effect=TagList()
    add_event(effect, "name_resetFlagsEvent")
    # add_event(effect, "name_resetEvent")
    add_event(effect, "name_removeAllModifiers")
    effect.add("remove_global_flag", "custom_difficulty_active")
    effect.add("remove_global_flag", f"dmm_mod_{dmmType}_{dmmId}")
    removeConfirmation.add("option", TagList("name", "OK").add("hidden_effect", effect))
    removeConfirmation.add("option", TagList("name", "custom_difficulty_cancel").add("hidden_effect", TagList("country_event", TagList("id", name_optionsEvent))))


  mainFileContent.add("","","#lock confirmation")
  lockEvent=TagList("id", name_lockEvent)
  mainFileContent.add("country_event", lockEvent)
  lockEvent.add("is_triggered_only", yes)
  lockEvent.add("title", "custom_difficulty_lock.name")
  lockEvent.add("desc", "custom_difficulty_lock.desc")
  lockEvent.add("picture", "GFX_evt_towel")
  lockEvent.add("option", TagList("name","OK").add("hidden_effect", TagList("set_global_flag", "custom_difficulty_locked").add("country_event", t_rootUpdateEvent)))
  lockEvent.add("option", TagList("name","custom_difficulty_cancel").add("hidden_effect", TagList("country_event", TagList("id", name_optionsEvent))))

  flagResetEvent=TagList("id", name_resetFlagsEvent)
  flagResetEvent.add("is_triggered_only",yes)
  flagResetEvent.add("hide_window",yes)

  # playerFlags=TagList("remove_global_flag", "custom_difficulty_easy").add("remove_global_flag", "custom_difficulty_advanced_configuration_player")
  # scalingFlags=TagList("remove_global_flag", "custom_difficulty_scaling").add("remove_global_flag", "custom_difficulty_advanced_configuration_scaling")
  # otherFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_other")
  # for difficulty in ai_non_scaling_DifficultyNames:
  #   otherFlags.add("remove_global_flag", "custom_difficulty_{}".format(difficulty))

  playerFlagResetEvent=deepcopy(flagResetEvent)
  scalingFlagResetEvent=deepcopy(flagResetEvent)
  otherFlagResetEvent=deepcopy(flagResetEvent)
  playerFlagResetEvent.replace("id", name_resetPlayerFlagsEvent).add("immediate", playerFlags)
  scalingFlagResetEvent.replace("id", name_resetYearlyFlagsEvent).add("immediate", scalingFlags)
  otherFlagResetEvent.replace("id", name_resetAIFlagsEvent).add("immediate", otherFlags)
  flagResetEvent.add("immediate", deepcopy(playerFlags).addTagList(scalingFlags).addTagList(otherFlags))

  mainFileContent.addComment("all flags")
  mainFileContent.add("country_event", flagResetEvent)
  mainFileContent.addComment("player flags")
  mainFileContent.add("country_event", playerFlagResetEvent)
  mainFileContent.addComment("scaling flags")
  mainFileContent.add("country_event", scalingFlagResetEvent)
  mainFileContent.addComment("other flags")
  mainFileContent.add("country_event", otherFlagResetEvent)



  outputToFolderAndFile(mainFileContent , "events", "custom_difficulty_main.txt",1, modFolder )

  dmmFileContent= TagList()
  dmmFileContent.add("namespace",f"dmm_mod_{dmmType}")
  dmmEvent=dmmFileContent.addReturn("country_event")
  dmmEvent.add("id",f"dmm_mod_{dmmType}.{dmmId}")
  triggeredHidden(dmmEvent)
  dmmImm=dmmEvent.addReturn("immediate")
  add_event(dmmImm, "name_mainMenuEvent")
  dmmImm.add("remove_global_flag",f"dmm_mod_{dmmType}_{dmmId}_opened")
  outputToFolderAndFile(dmmFileContent , "events", "000_custom_difficulty_dmm.txt",1, modFolder )

def createTriggerFile(modFolder="../gratak_mods/custom_difficulty"):
  scriptedTriggers=TagList()
  allowChangesTrigger=scriptedTriggers.addReturn("custom_difficulty_allow_changes")
  allowChangesTrigger.add("NOT", TagList("has_global_flag", "custom_difficulty_locked"))
  allowChangesTrigger.add("OR", TagList("is_multiplayer", "no").add("has_country_flag","custom_difficulty_game_host").add("not", TagList("has_global_flag","custom_difficulty_activate_host_only")))

  outputToFolderAndFile(scriptedTriggers , "common/scripted_triggers", "custom_difficulty_triggers.txt",2,modFolder )

def createEdictFile(modFolder="../gratak_mods/custom_difficulty"):

  edict=TagList().add("length","0")
  edict.add("resources", TagList("category", "edicts").add("cost",TagList()))
  edict.add("effect", TagList("hidden_effect",TagList("country_event",TagList("id",name_mainMenuEvent))))
  edict.add("potential", TagList("is_ai","no").add("not",TagList("has_global_flag", "custom_difficulty_deactivate_edict")).add("NOT",TagList("has_global_flag","dmm_installed")))
  edictFile=TagList().add("custom_difficulty", edict)
  outputToFolderAndFile(edictFile, "common/edicts", "custom_difficulty_edict.txt",2, modFolder)


def outputToFolderAndFile(tagList, folder, fileName, level=2, modFolder="../gratak_mods/custom_difficulty", warningText=True,encoding=None):
  tagList=deepcopy(tagList)
  if warningText:
    tagList.insert(0, "","","# This file was created by script!\n # Instead of editing it, you should change the python script.\n # Changes to the file will be overwritten the next time the script is run.")
  folder=modFolder+"/"+folder
  if not os.path.exists(folder):
    os.makedirs(folder)
  with open(folder+"/"+fileName,'w',encoding=encoding) as file:
    tagList.writeAll(file, args(level))
  return folder+"/"+fileName



def t_back(name):
  return TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name)))



def add_event(tagList, name, env=None):
  if env is None:
    env=globals()
  if name[:5]!="name_":
    print("add_event only works with predefined event names")
    return
  tagList.add("country_event", TagList("id", env[name])," #"+name.replace("name_",""))
  return tagList
TagList.add_event=add_event

def ifDelay(name):
  self=TagList()
  self=TagList("limit",TagList("has_global_flag", "custom_difficulty_activate_delay_mode"))
  self.add("every_country", TagList("country_event", TagList("id", name).add("days","1").add("random","180")))
  # ifInstant=TagList("limit",TagList("not", TagList("has_global_flag", "custom_difficulty_activate_delay_mode")))
  return self


class args:
  def __init__(self, level=2):
    self.one_line_level=level


def triggeredHidden(self=None):
  if self==None:
    self=TagList()
  self.add("is_triggered_only", "yes")
  self.add("hide_window","yes")
  return self
TagList.triggeredHidden=triggeredHidden

def variableOpNew(opName, varName, val, sep="=",comment=""):
  self=TagList()
  if type(val)==str and val.startswith("event_target"):
    val=f"{val}.{varName}"
  self.add(opName+"_variable", TagList("which", varName).add("value", val, comment,sep))
  return self
def variableOpNew2(self, opName, varName, val, sep="=",comment="", skipCheck=False):
  if self==None:
    self=TagList()
  t=self
  if type(val)==str and val.startswith("event_target"):
    if opName=="set" and not skipCheck:
      # self.createReturnIf(TagList(val,variableOpNew("check", varName, 0, "="))).add(opName+"_variable", TagList("which", varName).add("value", "0"))
      # t=self.addReturn("else")
      # is_variable_set = clone_pops_missing
      t=self.createReturnIf(TagList(val,TagList("is_variable_set", varName)))
    val=f"{val}.{varName}"
  t.add(opName+"_variable", TagList("which", varName).add("value", val, comment,sep))
  return self
def variableOp(self, opName, varName, val, sep="=",comment=""):
  if self==None:
    self=TagList()
  if type(val)==str and val.startswith("event_target"):
    val=f"{val}.{varName}"
  self.add(opName+"_variable", TagList("which", varName).add("value", val, comment,sep))
  return self
TagList.variableOp=variableOp
TagList.variableOpNew=variableOpNew2

def createEvent(self, id, name="country_event"):
  self.add(name, TagList("id", id))
  return self
TagList.createEvent=createEvent

def createReturnIf(self, limit, addMethod="add"):
  if not isinstance(limit, TagList):
    print("Invalid use of createReturnIf")
    return 0
  ifLoc=TagList("limit", limit)
  getattr(self,addMethod)("if", ifLoc)
  # self.add
  return ifLoc
TagList.createReturnIf=createReturnIf

def createModifierEvents(inDict, outDict, eventTaglist, id, addBool, eventNameSpace="custom_difficulty.{!s}"):
  for i,item in enumerate(inDict.items()):
    name=eventNameSpace.format(id+i)
    event=TagList("id", name )
    outDict[item[0]]=name
    eventTaglist.addComment(item[0])
    eventTaglist.add("country_event",event)
    event.add("is_triggered_only",yes)
    event.add("hide_window",yes)
    event.add("immediate",item[1])
    if addBool:
      item[1].add("set_country_flag", eventNameSpace.format("")[:-1]+"_{}_modifier_active".format(item[0]))
    else:
      item[1].add("remove_country_flag", eventNameSpace.format("")[:-1]+"_{}_modifier_active".format(item[0]))
    if addBool and item[0]=="ai":
      item[1].variableOp("set", "custom_difficulty_randomness_factor",1)
      t=item[1].createReturnIf(TagList("is_variable_set", "custom_difficulty_random_handicap").add("is_variable_set", "custom_difficulty_random_handicap_perc"))
      t.variableOp("set", "custom_difficulty_tmp","custom_difficulty_random_handicap")
      t.variableOp("multiply", "custom_difficulty_tmp","custom_difficulty_random_handicap_perc")
      t.variableOp("divide", "custom_difficulty_tmp",100*20) #100 for from perc, 20 as max handicap
      t.variableOp("subtract", "custom_difficulty_randomness_factor","custom_difficulty_tmp")

def globalAddLocs(locClass):
   #global things: No translation needed (mod name and stuff taken from vanilla translations)
  locClass.addLoc("modName", "Dynamic Difficulty", "all")
  locClass.addLoc("modNameFull", "Dynamic Difficulty - Ultimate Customization", "all")
  locClass.addLoc("station", "Station Output","all")
  locClass.append("mod_stations_produces_mult", "@station") #paradox seems to have forgotten this one!
  locClass.addLoc("jobs", "$mod_planet_jobs_produces_mult$","all")
  locClass.addLoc("ship_cost", "$MOD_STARBASE_SHIPYARD_BUILD_COST_MULT$","all")
  locClass.addLoc("stability", "$PLANET_STABILITY_TITLE$","all")
  locClass.addLoc("diplo_upkeep", "$mod_pop_resettlement_cost_mult$","all")
  locClass.addLoc("fire_rate", "$MOD_SHIP_FIRE_RATE_MULT$","all")
  locClass.addLoc("trade_value", "$MOD_TRADE_VALUE_MULT$","all")
  locClass.addLoc("cap", "$NAVY_SIZE_TITLE$","all")
  locClass.addLoc("hull", "$HULL$","all")
  locClass.addLoc("armor", "$ARMOR$","all")
  locClass.addLoc("shield", "$SHIELD$","all")
  locClass.addLoc("upkeep", "$mod_ships_upkeep_mult$","all")
  # locClass.addLoc("growth", "$POPULATION_GROWTH$","all") #Any Pop Growth Speed","all")
  locClass.addLoc("cadet", "$DIFFICULTY_CADET$","all")
  locClass.addLoc("ensign", "$DIFFICULTY_ENSIGN$","all")
  locClass.addLoc("captain", "$DIFFICULTY_CAPTAIN$","all")
  locClass.addLoc("commodore", "$DIFFICULTY_COMMODORE$","all")
  locClass.addLoc("admiral", "$DIFFICULTY_ADMIRAL$","all")
  locClass.addLoc("grandAdmiral", "$DIFFICULTY_GRAND_ADMIRAL$","all")
  locClass.addLoc("scaling", "$FE_SCALING_DIFFICULTY$$DIFFICULTY_SCALING$","all")



  #IMPORTANT
  #bonusLists
  locClass.addLoc("all", "All")
  locClass.addLoc("allDesc", "Change all available bonuses at once.")
  locClass.addLoc("default", "Standard")
  locClass.addLoc("planets", "Planet Bonuses")
  locClass.addLoc("planetsDesc", "Change job production and stability.")
  locClass.addLoc("systems", "Space Bonuses")
  locClass.addLoc("systemsDesc", "Change space production, naval cap and ships cost bonuses.")
  # locClass.addLoc("resourceProd", "Resource Production")
  # locClass.addLoc("resourceProdDesc", "Change mineral, energy and food bonuses.")
  # locClass.addLoc("humanResources", "Human Resources")
  # locClass.addLoc("humanResourcesDesc", "Change unity, research and naval capacity bonuses.")
  locClass.addLoc("allShip", "All Combat")
  locClass.addLoc("allShipDesc", "Change combat bonuses: weapon damage, hull, shields and armor.")
  #cats
  locClass.addLoc("ai", "AI")
  locClass.addLoc("AI", "AI")
  locClass.addLoc("ai_yearly", "AI Yearly Change")
  locClass.addLoc("fe", "Fallen and Awakened Empires")
  locClass.addLoc("leviathan", "Leviathans")
  locClass.addLoc("player", "Player")
  locClass.addLoc("Player", "Player")
  locClass.addLoc("crisis", "Crisis")
  locClass.addLoc("marauders", "Marauders")
  locClass.addLoc("other", "Other")

  locClass.addLoc("for", "for")
  locClass.addLoc("forAI", "for AI")
  locClass.addLoc("forNPCs", "for NPCs")
  locClass.addLoc("forPlayer", "for Player")
  locClass.addLoc("menu", "Menu")
  locClass.addLoc("options", "Options")
  locClass.addLoc("vanilla", "Vanilla")



  #less important

  # locClass.addLoc("easy", "Easy")
  locClass.addLoc("randomHandicap", "Randomly Decreased Bonuses per Empire")
  locClass.addLoc("steps", "step(s)")
  locClass.addLoc("step", "step")
  locClass.addLoc("damage", "Weapon Damage")
  locClass.addLoc("curBon", "Current Bonuses")
  locClass.addLoc("bonus", "Bonus")
  locClass.addLoc("bonuses", "Bonuses")
  locClass.addLoc("cur", "Currently")
  locClass.addLoc("max", "Max")
  locClass.addLoc("yearlyDesc","Positive year count gives increase, negative year count decrease. Every year is fastest possible. Zero (not displayed) means no change")
  locClass.addLoc("back", "Back")
  locClass.addLoc("cancel", "Cancel and Back")
  locClass.addLoc("close", "Close")
  locClass.addLoc("main", "Main")
  locClass.addLoc("menuDesc", "Triggers an event to let you customize the difficulty of your current game")
  locClass.addLoc("lock", "Lock Settings for the Rest of the Game")
  locClass.addLoc("lockDesc", "Yearly changes will continue up to the maximum/minimum. Can only be unlocked via installing the unlock mod, editing save game or starting a new game.")
  locClass.addLoc("lockActive", "Difficulty locked!")
  locClass.addLoc("lockActiveDesc", "Yearly changes will continue up to the maximum/minimum. Can only be unlocked via installing the unlock mod, editing save game or starting a new game. Might also be locked due to not being host in MP.")
  locClass.addLoc("care", "Use with care!")
  locClass.addLoc("unlock", "Unlock Settings")
  locClass.addLoc("choose", "Choose category to change or show")
  locClass.addLoc("choosePreDef", "Choose predefined setting")
  locClass.addLoc("delWarn", "Deletes previously made settings!")
  locClass.addLoc("combineText", "Colors indicate categories. From each category, one can be chosen. Choosing another one overwrites previous choice.")
  locClass.addLoc("preDef", "Predefined Difficulties")
  locClass.addLoc("years", "year(s)")
  locClass.addLoc("yearly", "yearly")
  locClass.addLoc("every", "every")
  locClass.addLoc("advCust", "Advanced Difficulty Customization")
  locClass.addLoc("nonPlayer", "Non-Player")
  locClass.addLoc("reset", "Reset all settings")
  locClass.addLoc("resetDesc", "Undo all changes and reset to difficulty set before game start")
  locClass.addLoc("resetDescMM", "Resets to clear state of the mod: Removes all modifiers and changed settings")
  locClass.addLoc("confirmation", "Confirmation")
  locClass.addLoc("allCat", "in all Categories")
  locClass.addLoc("no", "No")
  locClass.addLoc("by", "by")
  locClass.addLoc("increase", "Increase")
  locClass.addLoc("decrease", "Decrease")
  locClass.addLoc("change", "Change")
  locClass.addLoc("difficulty", "Difficulty")
  locClass.addLoc("customization", "Customization")
  locClass.addLoc("strength", "Strength")
  locClass.addLoc("example", "Example")
  locClass.addLoc("values", "Values")
  locClass.addLoc("init", "Initialization")
  locClass.addLoc("initDesc", "Thank you for using Dynamic Difficulty. Start the event menu via 'ModMenu' or edict.")
  locClass.addLoc("crisisInit","Since it seems to be impossible to read crisis strength in a mod, you'll have to enter it here."+
    " The option chosen during game start will not have an effect anymore."+
    " The value chosen below is translated into a bonus using the same formula as Vanilla Stellaris and can be customized at any time."+
    " This later custumization also allows values beyond the maximum offered in Vanilla.")
    # locClass.addLoc("crisis_from_galaxy_setup", "Use value from Galaxy setup")
  locClass.addLoc("noCrisisInit","This game has crisis disabled via the game start options. Crisis options are thus also disabled in this mod. You can activate crisis only with a new game or a save-game edit.")
  locClass.addLoc("crisisStrength","Crisis Strength")
  locClass.addLoc("current_options", "Currently active options")
  locClass.addLoc("uninstall", "Uninstall")
  locClass.addLoc("uninstallDesc", "Removes all modifiers, flags and variables. The mod can only be reinstalled in the same save-game via calling 'event custom_difficulty.20' in the console.")
  locClass.addLoc("uninstallDescMM", "Removes all modifiers, flags and variables. Quit the game and disable the mod directly after doing this. Waiting for even a day will re-initialize the mod.")

  #options loc
  locClass.addLoc("activate_custom_mode", "Activate Custom Mode")
  locClass.addLoc("activate_simple_mode", "Activate Simple Mode")
  locClass.addLoc("activate_player_vassal_ai_boni", "Activate Player Vassal full AI Bonus")
  locClass.addLoc("deactivate_player_vassal_ai_boni", "Deactivate Player Vassal full AI Bonus")
  locClass.addLoc("activate_custom_mode"+"Desc", "Specific choice of bonuses to be applied possible.")
  locClass.addLoc("activate_simple_mode"+"Desc", "Only bonus groups and default difficulties can be chosen. Slightly improved performance.")
  locClass.addLoc("activate_player_vassal_ai_boni"+"Desc", "Player vassals will get the same bonuses as other AI empires")
  locClass.addLoc("deactivate_player_vassal_ai_boni"+"Desc", "Vanilla behavior of player vassals getting AI bonus lowered by one difficulty level.")
  locClass.addLoc("activate_delay_mode", "Activate Delay Mode")
  locClass.addLoc("activate_delay_mode"+"Desc", "Update events will happen with a random delay of 1-181 days after the menu is closed or a year ends.")
  locClass.addLoc("deactivate_delay_mode", "Deactivate Delay Mode")
  locClass.addLoc("deactivate_delay_mode"+"Desc", "Update events happen direclty after the menu is closed and at the start of each year.")
  locClass.addLoc("deactivate_edict", "Hide Menu Edict")
  locClass.addLoc("deactivate_edict"+"Desc", "Removes the edict to start the main menu of this mod. Main menu can still be started via Mod Menu or calling 'event custum_difficulty.0' in console")
  locClass.addLoc("activate_edict", "Show Menu Edict")
  locClass.addLoc("activate_edict"+"Desc", "Show the edict to start the main menu of this mod")
  locClass.addLoc("activate_host_only", "Activate Host Changes Only")
  locClass.addLoc("activate_host_only"+"Desc", "Only the host of the game will be able to change any settings. Other players can open the dynamic difficulty menu and see the settings, but won't be able to change anything")
  locClass.addLoc("deactivate_host_only", "Deactivate Host Changes Only")
  locClass.addLoc("deactivate_host_only"+"Desc", "Everybody can change any dynamic difficulty settings, unless settings have been locked")



if __name__ == "__main__":
  main()

