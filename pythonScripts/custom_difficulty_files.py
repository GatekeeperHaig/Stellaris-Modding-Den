#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList

debugMode=True

changeStepYears=[5,4,3,2,1]
changeSteps = [50, 25, 10, 5, 1]
for s in reversed(changeSteps):
  changeSteps.append(-s)
for s in reversed(changeStepYears):
  changeStepYears.append(-s)
possibleBoniNames=["minerals", "energy","food", "research", "unity", "influence", "cap", "damage", "hull","armor","shield","upkeep", "growth"]
npcBoni=[           False,      False,   False,   False,    False,    False,      False,  True,   True,     True, True,   False,    False]
possibleBoniPictures=["GFX_evt_mining_station","GFX_evt_dyson_sphere","GFX_evt_animal_wildlife", "GFX_evt_think_tank", "GFX_evt_ancient_alien_temple","GFX_evt_arguing_senate","GFX_evt_hangar_bay", "GFX_evt_debris", "GFX_evt_sabotaged_ship","GFX_evt_pirate_armada","GFX_evt_fleet_neutral","GFX_evt_city_ruins","GFX_evt_metropolis"]
possibleBoniModifier=["country_resource_minerals_mult", "country_resource_energy_mult", "country_resource_food_mult", "all_technology_research_speed", "country_resource_unity_mult","country_resource_influence_mult","country_naval_cap_mult","ship_weapon_damage","ship_hull_mult","ship_armor_mult","ship_shield_mult",["ship_upkeep_mult",
#"country_building_upkeep_mult", #is there any such modifier except on planet base?!
"country_starbase_upkeep_mult","army_upkeep_mult"],["pop_growth_speed","pop_robot_build_speed_mult"]]
possibleBoniIcons=["£minerals","£energy", "£food", "£physics £society £engineering","£unity", "£influence","£navy_size","£military_power","£ship_stats_hitpoints","£ship_stats_armor","£ship_stats_shield","£ship_stats_maintenance","£pops"]
possibleBoniColor=["P","Y","G","M","E","B","W","R","G","H","B","T","G"]

bonusesListNames=["all","resourceProd","humanResources", "allShip"]
representGroup=dict()
representGroup["minerals"]="resourceProd"
representGroup["research"]="humanResources"
representGroup["damage"]="allShip"
bonusListNPC=[    False,   False, False,  True]
bonusesListEntries=[[0,1,2,3,4,5,6,7,8,9,10,11,12], [0,1,2],[3,4,6], [7,8,9,10]]
bonusesListPictures=["GFX_evt_towel", "GFX_evt_alien_city", "GFX_evt_alien_city","GFX_evt_federation_fleet"] #todo: new picture: resource and human resources
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
catCountryType=[
["default"], 
["default"],
["fallen_empire", "awakened_fallen_empire"],
["guardian", "guardian_dragon", "guardian_stellarite","guardian_wraith","guardian_hiver","guardian_horror","guardian_fortress","guardian_dreadnought", "guardian_sphere"],
[],
["swarm", "extradimensional", "extradimensional_2", "extradimensional_3", "ai_empire","cybrex_empire","sentinels", "portal_holders", "feral_prethoryn","feral_prethoryn_infighting"],
["dormant_marauders","ruined_marauders", "awakened_marauders","marauder_raiders"],
[]]
catNotCountryType=[[], [],[],[],[],[],[],catCountryType]
catPictures=["GFX_evt_throne_room","GFX_evt_organic_oppression","GFX_evt_fallen_empire","GFX_evt_wraith","GFX_evt_towel","GFX_evt_towel","GFX_evt_towel","GFX_evt_towel"] #todo: pictures for new cats!
catColors="BHBBGRBB"

difficulties=["easy", "no_player_bonus", "ensign","captain","commodore","admiral", "grand_admiral", "scaling", "no_scaling"]
vanillaDefaultDifficultyNames=difficulties[2:]
ai_non_scaling_DifficultyNames=difficulties[2:-2]

vanillaDefaultDifficulty=[]
# possibleBoniNames=["Minerals", "Energy","Food", "Research", "Unity", "Influence", "Naval capacity", "Weapon Damage", "Hull","Armor","Shield","Upkeep", "Any Pop growth speed"]
aiDefault=[True, True, True, True, True, False, True, False, False, False, False, False, False]
aiDefaultPrecise=[2, 2, 2, 1, 1, 0, 1, 0,0,0,0,0,0]
npcDefault=[False,False,False,False,False,False,False, True, True, True, True, False, False]
catsWithNPCDefaultBoni=["fe","leviathan","marauders", "other"]
vanillaAItoNPCIndex=7




# doTranslation=True
doTranslation=False
locClass=LocList(doTranslation)
locClass.addLoc("modName", "Dynamic Difficulty", "all")



#IMPORTANT
#bonuses
locClass.addLoc("minerals", "Minerals")
locClass.addLoc("energy", "Energy")
locClass.addLoc("food", "Food")
locClass.addLoc("research", "Research")
locClass.addLoc("unity", "Unity")
locClass.addLoc("influence", "Influence")
locClass.addLoc("cap", "Naval capacity")
locClass.addLoc("damage", "Weapon Damage")
locClass.addLoc("hull", "Hull")
locClass.addLoc("armor", "Armor")
locClass.addLoc("shield", "Shield")
locClass.addLoc("upkeep", "Upkeep")
locClass.addLoc("growth", "Any Pop Growth Speed")
#bonusLists
locClass.addLoc("all", "All")
locClass.addLoc("allDesc", "Change all available bonuses at once.")
locClass.addLoc("default", "Standard")
locClass.addLoc("resourceProd", "Resource Production")
locClass.addLoc("resourceProdDesc", "Change mineral, energy and food bonuses.")
locClass.addLoc("humanResources", "Human Resources")
locClass.addLoc("humanResourcesDesc", "Change unity, research and naval capacity bonuses.")
locClass.addLoc("allShip", "All Combat")
locClass.addLoc("allShipDesc", "Change combat bonuses: weapon damage, hull, shields and armor.")
#cats
locClass.addLoc("ai", "AI")
locClass.addLoc("ai_yearly", "AI Yearly Change")
locClass.addLoc("fe", "Fallen and Awakened Empires")
locClass.addLoc("leviathan", "Leviathans")
locClass.addLoc("player", "Player")
locClass.addLoc("crisis", "Crisis")
locClass.addLoc("marauders", "Marauders")
locClass.addLoc("other", "Other")
#difficiulties, AI, other important things
locClass.addLoc("easy", "Easy")
locClass.addLoc("ensign", "Ensign")
locClass.addLoc("captain", "Captain")
locClass.addLoc("commodore", "Commodore")
locClass.addLoc("admiral", "Admiral")
locClass.addLoc("grandAdmiral", "Grand Admiral")
locClass.addLoc("scaling", "Scaling")
locClass.addLoc("forAI", "for AI")
locClass.addLoc("forNPCs", "for NPCs")
locClass.addLoc("forPlayer", "for Player")
locClass.addLoc("menu", "Menu")
locClass.addLoc("options", "Options")
locClass.addLoc("vanilla", "Vanilla")



#less important
locClass.addLoc("curBon", "Current Bonuses")
locClass.addLoc("bonus", "Bonus")
locClass.addLoc("bonuses", "Bonuses")
locClass.addLoc("cur", "Currently")
locClass.addLoc("yearlyDesc","Positive year count gives increase, negative year count decrease. Every year is fastest possible. Zero (not displayed) means no change")
locClass.addLoc("back", "Back")
locClass.addLoc("cancel", "Cancel and Back")
locClass.addLoc("close", "Close")
locClass.addLoc("main", "Main")
locClass.addLoc("menuDesc", "Triggers an event to let you customize the difficulty of your current game")
locClass.addLoc("lock", "Lock Settings for the Rest of the Game")
locClass.addLoc("lockDesc", "Yearly changes will continue up to the maximum/minimum. Can only be unlocked via installing the unlock mod, editing save game or starting a new game.")
locClass.addLoc("lockActive", "Difficulty locked!")
locClass.addLoc("lockActiveDesc", "Yearly changes will continue up to the maximum/minimum. Can only be unlocked via installing the unlock mod, editing save game or starting a new game.")
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
locClass.addLoc("confirmation", "Confirmation")
locClass.addLoc("allCat", "in all Categories")
locClass.addLoc("no", "No")
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
  " The chosen value will be translated into a bonus according to the same formula as in vanilla and can be customized at any time.")
locClass.addLoc("noCrisisInit","This game has crisis disabled via the game start options. Crisis options are thus also disabled in this mod. You can activate crisis only with a new game or a save-game edit.")
locClass.addLoc("crisisStrength","Crisis Strength")
locClass.addLoc("current_options", "Currently active options")

#options loc
locClass.addLoc("activate_custom_mode", "Activate Custom Mode")
locClass.addLoc("activate_simple_mode", "Activate Simple Mode")
locClass.addLoc("activate_player_vassal_ai_boni", "Activate Player Vassal AI Bonus")
locClass.addLoc("deactivate_player_vassal_ai_boni", "Deactivate Player Vassal AI Bonus")
locClass.addLoc("activate_custom_mode"+"Desc", "Specific choice of bonuses to be applied possible.")
locClass.addLoc("activate_simple_mode"+"Desc", "Only bonus groups and default difficulties can be chosen.")# Slightly improved performance.")
locClass.addLoc("activate_player_vassal_ai_boni"+"Desc", "Player vassals will get the same bonuses as other AI empires")
locClass.addLoc("deactivate_player_vassal_ai_boni"+"Desc", "Vanilla behavior of player vassals not getting AI bonuses. They will get player bonuses though if any such have been activated.")
locClass.addLoc("activate_delay_mode", "Activate Delay Mode")
locClass.addLoc("activate_delay_mode"+"Desc", "Update events will happen with a random delay of 1-181 days after the menu is closed or a year ends.")
locClass.addLoc("deactivate_delay_mode", "Deactivate Delay Mode")
locClass.addLoc("deactivate_delay_mode"+"Desc", "Update events happen direclty after the menu is closed and at the start of each year.")







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
locClass.addEntry("custom_difficulty_init_crisis_desc", "@crisisInit")
locClass.addEntry("custom_difficulty_init_no_crisis_desc", "@noCrisisInit")
locClass.addEntry("custom_difficulty_options.name", "@options")
locClass.addEntry("custom_difficulty_choose_desc", "@choose")
locClass.addEntry("custom_difficulty_predef_head.name", "@modName - @preDef")
locClass.addEntry("custom_difficulty_predefined_colored.name", "§G@preDef")
locClass.append("custom_difficulty_crisis_colored.name","§R@crisis @strength")
locClass.append("custom_difficulty_customize_colored.name","§Y@difficulty @customization")
locClass.append("custom_difficulty_customize.name","§Y@difficulty @customization")
locClass.addEntry("custom_difficulty_choose", "@choosePreDef.§R @delWarn§! @combineText")
locClass.addEntry("custom_difficulty_easy.name", "§G@easy - 20% @bonus @allCat @forPlayer§!")
locClass.addEntry("custom_difficulty_no_player_bonus.name", "§G@no @bonus @forPlayer§!")
locClass.addEntry("custom_difficulty_ensign.name", "§B@ensign - @no @bonus @forAI. @no @bonus @forNPCs§!")
locClass.addEntry("custom_difficulty_captain.name", "§B@captain - 15-25% @bonus @forAI. 25% @forNPCs§!")
locClass.addEntry("custom_difficulty_commodore.name", "§B@commodore - 30-50% @bonus @forAI. 50% @forNPCs§!")
locClass.addEntry("custom_difficulty_admiral.name", "§B@admiral - 45-75% @bonus @forAI. 75% @forNPCs§!")
locClass.addEntry("custom_difficulty_grand_admiral.name", "§B@grandAdmiral - 60-100% @bonus @forAI. 100% @forNPCs§!")
locClass.addEntry("custom_difficulty_scaling.name", "§H@scaling - @increase @bonus @forAI @every 4 @years§!")
locClass.addEntry("custom_difficulty_no_scaling.name", "§H@no @scaling§!")
locClass.addEntry("custom_difficulty_advanced_configuration.name", "§B@advCust @nonPlayer§!")
locClass.addEntry("custom_difficulty_advanced_configuration_player.name", "§G@advCust @player§!")
locClass.addEntry("custom_difficulty_advanced_configuration_scaling.name", "§H@advCust @yearly§!")
locClass.addEntry("custom_difficulty_reset.name", "@reset")
locClass.addEntry("custom_difficulty_reset_conf.name", "@reset - @confirmation")
locClass.addEntry("custom_difficulty_reset.desc", "@resetDesc")
# locClass.addEntry(, [])
# locClass.addEntry(, [])






ET = "event_target:custom_difficulty_var_storage"

yes="yes"


CuDi="custom_difficulty.{!s}"

name_mainMenuEvent="custom_difficulty.0"
name_defaultMenuEvent="custom_difficulty.1"
name_customMenuEvent="custom_difficulty.2"
name_optionsEvent="custom_difficulty.3"
name_gameStartFireOnlyOnce="custom_difficulty.10"
name_resetEvent="custom_difficulty.20" # same as above with triggered_only instead of fire_only_once
name_resetConfirmationEvent="custom_difficulty.21" # same as above with triggered_only instead of fire_only_once
name_resetFlagsEvent="custom_difficulty.22"
name_resetAIFlagsEvent="custom_difficulty.23"
name_resetYearlyFlagsEvent="custom_difficulty.24"
name_resetPlayerFlagsEvent="custom_difficulty.25"
name_rootYearlyEvent="custom_difficulty.30"
name_rootUpdateEvent="custom_difficulty.40"
# name_rootUpdateEventSimple="custom_difficulty.41"
name_countryUpdateEvent="custom_difficulty.50"
name_countryUpdateEventSimple="custom_difficulty.51"
name_lockEvent="custom_difficulty.60"
id_removeModifiers=70  #reserved range up to 72
id_removeGroupModifiers=73  #reserved range up to 75
name_removeAllModifiers=CuDi.format(id_removeModifiers+9)
name_removeEventTarget=CuDi.format(id_removeModifiers+8)
id_addModifiers=80  #reserved range up to 82
id_addGroupModifiers=83  #reserved range up to 85
id_defaultEvents=100 #reserved range up to 199
id_ChangeEvents=1000 #reserved range up to 9999
id_subChangeEvents=10


def outputToFolderAndFile(tagList, folder, file, level=2, modFolder="../gratak_mods/custom_difficulty"):
  folder=modFolder+"/"+folder
  if not os.path.exists(folder):
    os.makedirs(folder)
  with open(folder+"/"+file,'w') as file:
    tagList.writeAll(file, args(level))

t_notLockedTrigger=TagList("not", TagList("has_global_flag", "custom_difficulty_locked"))
t_mainMenuEvent=TagList("id",name_mainMenuEvent)
t_rootUpdateEvent=TagList("id",name_rootUpdateEvent)
t_backMainOption=TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name_mainMenuEvent)))
t_closeOption=TagList("name", "custom_difficulty_close.name").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

def t_back(name):
  return TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name)))

def add_event(tagList, name):
  if name[:5]!="name_":
    print("add_event only works with predefined event names")
    return
  tagList.add("country_event", TagList("id", eval(name))," #"+name.replace("name_",""))
  return tagList


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
  choiceEvent.add("id",CuDi.format(mainIndex*id_ChangeEvents))
  choiceEvent.add("is_triggered_only", yes)
  choiceEvent.add("title","custom_difficulty_{}.name".format(cat))
  choiceEvent.add("picture",'"'+catPictures[mainIndex-1]+'"')
  trigger=TagList()
  locClass.addEntry("custom_difficulty_{}.name".format(cat), "@change @{} @bonuses".format(cat))
  choiceEvent.add("desc", TagList().add("trigger",trigger))
  successText=TagList().add("text","custom_difficulty_locked.name").add("has_global_flag","custom_difficulty_locked")
  trigger.add("success_text",successText)
  if cat=="ai_yearly":
    immediate=TagList()
    choiceEvent.add("immediate",immediate)
  if cat=="crisis":
    trigger.add("text", "custom_difficulty_crisis_strength_desc")
    locClass.append("custom_difficulty_crisis_strength_desc", "@vanilla @example @values: @grandAdmiral + x5 @crisis @strength: 1500%. @ensign + x5 @crisis @strength: 495%. @ensign + x0.25 @crisis @strength: 24.75%.")
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
    option.add("trigger", TagList().add("not", TagList().add("has_global_flag","custom_difficulty_locked")))
    locClass.addEntry("custom_difficulty_{}_change_{}_desc".format(cat,bonusesListName), "@{}Desc".format(bonusesListName))
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", CuDi.format(mainIndex*id_ChangeEvents+optionIndex*id_subChangeEvents))))
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
        locClass.addEntry("custom_difficulty_{}_{}_inc_desc".format(cat,bonusesListName),"{0} @{1} : 1% @increase @every [this.custom_difficulty_{2}_{3}_value] @years".format(icons, bonusesListName, cat,firstVarName)) #local tmp var
        locClass.addEntry("custom_difficulty_{}_{}_dec_desc".format(cat,bonusesListName),"{0} @{1} : 1% @decrease @every [this.custom_difficulty_{2}_{3}_value] @years".format(icons, bonusesListName, cat,firstVarName)) #local tmp var
        #create a local variable and make sure it is positive!
        immediate.add("set_variable", TagList().add("which", localVarName).add("value",ET))
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
      locClass.addEntry("custom_difficulty_{}_{}_inc_desc".format(cat,bonus),"{} §{}@{} : 1% @increase @every [this.custom_difficulty_{}_{}_value] @years".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonus)) #local tmp var
      locClass.addEntry("custom_difficulty_{}_{}_dec_desc".format(cat,bonus),"{} §{}@{} : 1% @decrease @every [this.custom_difficulty_{}_{}_value] @years".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonus)) #local tmp var
      #create a local variable and make sure it is positive!
      immediate.add("set_variable", TagList().add("which", localVarName).add("value",ET))
      immediateIf=TagList().add("limit",TagList().add("check_variable",checkVar)) #<0
      immediateIf.add("multiply_variable", TagList().add("which", localVarName).add("value","-1"))
      immediate.add("if",immediateIf)
    else:
      checkVar=TagList().add("which", localVarName).add("value","0")
      # trigger.add("fail_text",TagList().add("text","custom_difficulty_{}_{}_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)))
      trigger.add("success_text",TagList()
        .add("text","custom_difficulty_{}_{}_desc".format(cat,bonus)).add(ET,TagList()
          .add("not", TagList("check_variable", checkVar))).add("has_global_flag", "custom_difficulty_activate_custom_mode"))
      locClass.append("custom_difficulty_{}_{}_desc".format(cat,bonus),"{} §{}@{} : [{}.custom_difficulty_{}_{}_value]% ".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, ET, cat,bonus))

    #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before the loop)
    option=TagList().add("name", "custom_difficulty_{}_change_{}_button.name".format(cat,bonus))
    option.add("trigger", TagList().add("NOR", TagList().add("has_global_flag","custom_difficulty_locked").add("has_global_flag", "custom_difficulty_activate_simple_mode")))
    locClass.append("custom_difficulty_{}_change_{}_button.name".format(cat,bonus), "@change {} @{} @bonuses".format(possibleBoniIcons[bonusI],bonus))
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", CuDi.format(mainIndex*id_ChangeEvents+optionIndex*id_subChangeEvents))))
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
  option.add("hidden_effect", TagList().add("country_event",TagList().add("id", name_rootUpdateEvent)))
  choiceEvent.add("option",option)

  

  bonusIndex=0
  for bonus in bonusesListNames+possibleBoniNames:
    bonusIndex+=1
    changeEvent=TagList()
    if not catToModifierType[cat]=="crisis" or (bonusListNPC+npcBoni)[bonusIndex-1]:
      tagList.add("country_event", changeEvent)
      changeEvent.add("id",CuDi.format(mainIndex*id_ChangeEvents+bonusIndex*id_subChangeEvents))
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
            locClass.append("custom_difficulty_{}_{}_increase_{!s}".format(cat,bonus, changeStep), "@increase @{} @years by {}".format(bonus, changeStep))
          else:
            locClass.append("custom_difficulty_{}_{}_increase_{!s}".format(cat,bonus, changeStep), "@increase @{} @bonuses by {}%".format(bonus, changeStep))
        else:
          option=TagList().add("name","custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonus, -changeStep))
          if cat=="ai_yearly":
            locClass.append("custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonus, -changeStep), "@decrease @{} @years by {}".format(bonus, -changeStep))
          else:
            locClass.append("custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonus, -changeStep), "@decrease @{} @bonuses by {}%".format(bonus, -changeStep))

        hidden_effect=TagList()
        if bonusIndex>len(bonusesListNames):
          hidden_effect.add(ET,TagList().add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value",str(changeStep))))
        else:
          et=TagList()
          hidden_effect.add(ET,et)
          for bonusListIndex in bonusesListEntries[bonusIndex-1]:
            if not catToModifierType[cat]=="crisis" or npcBoni[bonusListIndex]:
              bonusListValue=possibleBoniNames[bonusListIndex]
              et.add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusListValue)).add("value",str(changeStep)))
        hidden_effect.add("country_event", TagList().add("id",CuDi.format(mainIndex*id_ChangeEvents+bonusIndex*id_subChangeEvents)))
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
      option.add("hidden_effect", TagList().add("country_event",TagList().add("id", CuDi.format(mainIndex*id_ChangeEvents))))
      changeEvent.add("option",option)
      option=TagList().add("name","custom_difficulty_close.name")
      option.add("hidden_effect", TagList().add("country_event",TagList().add("id", name_rootUpdateEvent)))
      changeEvent.add("option",option)

  # difficultyChangeWindows[-1].printAll()
  # break


class args:
  def __init__(self, level=2):
    self.one_line_level=level

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
condValPrec = lambda x1,x2,y: x1 if y==1 else (x2 if y==2  else 0)
difficultiesPresetProperties=dict()
for difficulty in difficulties:
  difficultiesPresetProperties[difficulty]=dict()
difficultiesPresetProperties["easy"]["player"]=[20 for b in possibleBoniNames]
difficultiesPresetProperties["no_player_bonus"]["player"]=[0 for b in possibleBoniNames]
difficultiesPresetProperties["scaling"]["ai_yearly"]=[condVal(4,s) for s in aiDefault]
difficultiesPresetProperties["no_scaling"]["ai_yearly"]=[0 for b in possibleBoniNames]

diffLevels=dict() 
diffLevels["ensign"]=[33, 0,0 ] # crisis, high ai and npc, low ai
diffLevels["captain"]=[50, 25,15 ]
diffLevels["commodore"]=[66, 50,30 ]
diffLevels["admiral"]=[75, 75,45 ]
diffLevels["grand_admiral"]=[100, 100,60 ]
# diffLevels["ensign"]=[0, 0,0 ] # npc, high ai, low ai
# diffLevels["captain"]=[25, 25,15 ]
# diffLevels["commodore"]=[50, 50,30 ]
# diffLevels["admiral"]=[75, 75,45 ]
# diffLevels["grand_admiral"]=[100, 100,60 ]
for diff, level in diffLevels.items():
  difficultiesPresetProperties[diff]["ai"]=[condValPrec(level[2], level[1],b) for b in aiDefaultPrecise]
  difficultiesPresetProperties[diff]["crisis"]=[condVal(level[0],b) for b in npcDefault]
  for cat in catsWithNPCDefaultBoni:
    difficultiesPresetProperties[diff][cat]=[condVal(level[1],b) for b in npcDefault]

#CRISIS DEFAULTS scheint nicht zu klappen!
#get_galaxy_setup_value = { 
# setting = crises
# which = localVar
#scale_by = 3
#}

playerFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_player")
scalingFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_scaling")
otherFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_other")

for difficultyIndex, difficulty in enumerate(difficulties):
  defaultDifficultyEvent=TagList("id", CuDi.format(id_defaultEvents+difficultyIndex))
  defaultEvents.add("country_event",defaultDifficultyEvent)
  defaultDifficultyEvent.add("is_triggered_only",yes)
  defaultDifficultyEvent.add("hide_window",yes)
  immediate=TagList()
  defaultDifficultyEvent.add("immediate",immediate)
  if "scaling" in difficulty:
    immediate.add("country_event",TagList().add("id",name_resetYearlyFlagsEvent))
    scalingFlags.add("remove_global_flag","custom_difficulty_"+difficulty)
  elif "player" in difficulty or "easy" in difficulty:
    immediate.add("country_event",TagList().add("id",name_resetPlayerFlagsEvent))
    playerFlags.add("remove_global_flag","custom_difficulty_"+difficulty)
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
    # et.add("get_galaxy_setup_value", TagList("setting", "crises").add("which", "custom_difficulty_crisis_strength").add("scale_by", "3"))
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


def createModifierEvents(inDict, outDict, eventTaglist, id, addBool):
  for i,item in enumerate(inDict.items()):
    name=CuDi.format(id+i)
    event=TagList("id", name )
    outDict[item[0]]=name
    eventTaglist.addComment(item[0])
    eventTaglist.add("country_event",event)
    event.add("is_triggered_only",yes)
    event.add("hide_window",yes)
    event.add("immediate",item[1])
    if addBool:
      item[1].add("set_country_flag", "custom_difficulty_{}_modifier_active".format(item[0]))
    else:
      item[1].add("remove_country_flag", "custom_difficulty_{}_modifier_active".format(item[0]))

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
modifierRange["crisis"]=[-5, 11] #10*(2^([0]-1)-1) to 10*(2^([1]-1)-1)

updateFile=TagList()
updateFile.add("namespace","custom_difficulty")

for groupUpdate in [False,True]:
  updateEvent=TagList()
  updateFile.add("country_event",updateEvent)

  if groupUpdate:
    updateEvent.add("id", name_countryUpdateEventSimple)
  else:
    updateEvent.add("id", name_countryUpdateEvent)
  updateEvent.add("is_triggered_only",yes)
  updateEvent.add("hide_window",yes)
  immediate=TagList()
  updateEvent.add("immediate",immediate)
  after=TagList()
  # updateEvent.add("after",after)
  for catI,cat in enumerate(cats):
    if catToModifierType[cat]=="none":
      continue
    immediate.addComment(cat)
    ifTagList=TagList()
    immediate.add("if",ifTagList)
    limit=TagList()
    ifTagList.add("limit",limit)
    et=TagList()
    ifTagList.add(ET,et)
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
      for entry in norSet:
        norTagList.add("is_country_type", entry)
    if "player"==cat or "ai" in cat:
      orTagList=TagList()
      if cat=="player":
        orTagList.add("is_ai", "no")
        orTagList.add("and", TagList().add("has_global_flag", "deactivate_player_vassal_ai_boni").add("exists","overlord").add("overlord",TagList().add("is_ai","no")))
      else:
        limit.add("is_ai", yes)
        orTagList.add("has_global_flag", "activate_player_vassal_ai_boni")
        orTagList.add("not", TagList().add("exists","overlord"))
        orTagList.add("and", TagList().add("exists","overlord").add("overlord",TagList().add("is_ai","yes")))
      limit.add("or",orTagList)
    # afterIfTaglist=deepcopy(ifTagList)
    # after.add("if",afterIfTaglist)
    shortened=False

    for bonus, bonusModifier in zip(possibleBoniNames,possibleBoniModifier):
      if groupUpdate and not bonus in representGroup:
        continue
      et.add("set_variable", TagList().add("which", "custom_difficulty_{}_value".format(bonus)).add("value", "custom_difficulty_{}_{}_value".format(cat,bonus)))
      ifChanged=TagList("limit", TagList("not", 
        TagList("check_variable", 
          TagList("which","custom_difficulty_{}_value".format(bonus))
          .add("value", ET))))
      # ifChanged=TagList("limit", TagList("not", 
      #   TagList("check_variable", 
      #     TagList("which","custom_difficulty_{}_value".format(bonus))
      #     .add("value", ET+":custom_difficulty_{}_value".format(bonus)))))
      ifTagList.add("if",ifChanged)
      ifChanged.add("set_country_flag", "custom_difficulty_{}_changed".format(bonus))
      if debugMode:
        ifChanged.add("log",'"setting flag {}"'.format("custom_difficulty_{}_changed".format(bonus)))
      ifChanged.add("set_variable", TagList().add("which", "custom_difficulty_{}_value".format(bonus)).add("value", ET))
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
        addIFChanged.add("set_variable",TagList("which", "custom_difficulty_tmp").add("value","custom_difficulty_{}_value".format(bonus)))
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
          changeVal=modifierFuns[cat](i)
          ifModifierApplied=TagList()
          if sign>0:
            addIFChanged.insert(addIFChanged.names.index("if"),"if", ifModifierApplied)
          else:
            addIFChanged.add("if", ifModifierApplied)
          ifModifierApplied.add("limit",TagList().add("check_variable",
            TagList().add("which","custom_difficulty_tmp")
            .add("value", str(sign*(changeVal-0.1)),"",compSign)))
          if groupUpdate:
            modifierName="custom_difficulty_{:02d}_{}_{}_{}_value".format(i,representGroup[bonus],signName,cat)
          else:
            modifierName="custom_difficulty_{:02d}_{}_{}_{}_value".format(i,bonus,signName,cat)
          modifier=TagList()
          if groupUpdate:
            bonusModifier=[]
            for i in bonusesListEntries[bonusesListNames.index(representGroup[bonus])]:
              localModifier=possibleBoniModifier[i]
              if isinstance(localModifier,list):
                bonusModifier+=localModifier
              else:
                bonusModifier.append(localModifier)
          else:
            if not isinstance(bonusModifier,list):
              bonusModifier=[bonusModifier]
          for modifierEntry in bonusModifier:
            if bonus=="upkeep":
              modifier.add(modifierEntry,str(-sign*changeVal/100))
            else:
              modifier.add(modifierEntry,str(sign*changeVal/100))
          locClass.append(modifierName,"@difficulty")
          staticModifiers.add(modifierName,modifier)
          ifModifierApplied.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
          if debugMode:
            ifModifierApplied.add("log",'"adding modifier {}"'.format(modifierName))
          removeIFChanged.add("remove_modifier", modifierName)
          if debugMode and i==1:
            removeIFChanged.add("log",'"removing modifiers (all of them, not only 1) {}"'.format(modifierName))
          ifModifierApplied.add("change_variable",TagList().add("which","custom_difficulty_tmp").add("value", str(-1*sign*changeVal)))
    for modifierCat in modifierCats:
      ifModifierCat=TagList("limit", TagList("has_country_flag","custom_difficulty_{}_modifier_active".format(modifierCat)))
      if groupUpdate:
        ifModifierCat.add("country_event", TagList("id", name_removeGroupModifiers[modifierCat]))
      else:
        ifModifierCat.add("country_event", TagList("id", name_removeModifiers[modifierCat]))
      ifTagList.addComment("removing {} bonuses if they exist".format(modifierCat))
      ifTagList.add("if", ifModifierCat)
    ifTagList.addComment("adding {} bonuses".format(catToModifierType[cat]))
    if groupUpdate:
      ifTagList.add("country_event", TagList("id", name_addGroupModifiers[catToModifierType[cat]]))
    else:
      ifTagList.add("country_event", TagList("id", name_addModifiers[catToModifierType[cat]]))
  # immediate.addTagList(after)




removeALLmodifiersEvent=TagList("id", name_removeAllModifiers)
removeEvents.addComment("remove ALL modifier no matter what. Slow but sure. Not called on yearly stuff.")
removeEvents.add("event", removeALLmodifiersEvent)
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
removeEvents.add("event", removeEventTargetEvent)
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
  ifTagList.add("change_variable", TagList().add("which", bonusVar).add("value", "1"))

  ifTagList=TagList()
  ifNeg.add("multiply_variable", TagList().add("which", yearLimitVar).add("value","-1"))
  ifNeg.add("if",ifTagList)
  ifNeg.add("multiply_variable", TagList().add("which", yearLimitVar).add("value","-1"))
  ifTagList.add("limit", TagList().add("not",TagList().add("check_variable", TagList().add("which", yearCountVar).add("value",yearLimitVar,"","<"))))
  ifTagList.add("set_variable", TagList().add("which", yearCountVar).add("value", "0"))
  ifTagList.add("change_variable", TagList().add("which", bonusVar).add("value", "-1"))

with open(outFolder+"/"+"custom_difficulty_yealy_event.txt",'w') as file:
  yearlyFile.writeAll(file, args())





edict=TagList().add("name","custom_difficulty").add("length","0").add("cost",TagList())
edict.add("effect", TagList("hidden_effect",TagList("country_event",TagList("id",name_mainMenuEvent))))
edict.add("potential", TagList("is_ai","no"))
edictFile=TagList().add("country_edict", edict)
outputToFolderAndFile(edictFile, "common/edicts", "custom_difficulty_edict.txt")

onActions=TagList()
onActions.add("on_yearly_pulse", TagList("events",TagList().add(name_rootYearlyEvent,""," #rootYearly").add(name_rootUpdateEvent,""," #rootUpdate")))
onActions.add("on_game_start_country", TagList("events",TagList().add(name_gameStartFireOnlyOnce),"#set flag,set event target, start default events, start updates for all countries"))
# onActions.add("on_game_start", TagList("events",TagList().add(name_rootUpdateEvent))) #is called by "fire only once"
outputToFolderAndFile(onActions, "common/on_actions", "custom_difficulty_on_action.txt")

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
outputToFolderAndFile(scriptedModifiers, "common/static_modifiers","!_custom_difficulty_00_static_modifier.txt")


mainFileContent=TagList("namespace","custom_difficulty")
mainFileContent.add("","","#main menu")
# main Menu (including unlock output)
mainMenu=TagList()
mainFileContent.add("country_event",mainMenu)
for allowUnlock in [False]:#[False,True]:
  mainMenu.add("id", name_mainMenuEvent)
  mainMenu.add("is_triggered_only", yes)
  mainMenu.add("title", "edict_custom_difficulty")
  mainMenu.add("picture", "GFX_evt_towel")
  trigger=TagList()
  mainMenu.add("desc", TagList("trigger", trigger))
  trigger.add("fail_text", TagList().add("text", "custom_difficulty_choose_desc").add("has_global_flag", "custom_difficulty_locked"))
  trigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("has_global_flag", "custom_difficulty_locked"))
  mainMenu.add("option", TagList("name","custom_difficulty_predefined_colored.name").add("hidden_effect", TagList("country_event", TagList("id", name_defaultMenuEvent))))
  mainMenu.add("option", TagList("name","custom_difficulty_crisis_colored.name").add("trigger", TagList("is_crises_allowed", yes)).add("hidden_effect", TagList("country_event", TagList("id", CuDi.format(id_ChangeEvents+cats.index("crisis")*id_ChangeEvents))).add("remove_global_flag","custom_difficulty_menu_crisis_from_custom")))
  mainMenu.add("option", TagList("name","custom_difficulty_customize_colored.name").add("hidden_effect", TagList("country_event", TagList("id", name_customMenuEvent))))
  mainMenu.add("option", TagList("name","custom_difficulty_options.name").add("hidden_effect", TagList("country_event", TagList("id", name_optionsEvent))))
  # mainMenu.add("option", TagList("name","custom_difficulty_lock.name").add("trigger", t_notLockedTrigger).add("hidden_effect", TagList("country_event", TagList("id",name_lockEvent))))
  # if allowUnlock:
  #   mainMenu.add("option",TagList("name","custom_difficulty_unlock.name").add("trigger", TagList("has_global_flag","custom_difficulty_locked")).add("hidden_effect",TagList("remove_global_flag", "custom_difficulty_locked").add("country_event", t_mainMenuEvent)))
  mainMenu.add("option", t_closeOption)

  # mainMenu=TagList()
  # if allowUnlock:
  #   mainFileUnlock=TagList("namespace", "custom_difficulty")
  #   mainFileUnlock.add("country_event", mainMenu)
  #   outputToFolderAndFile(mainFileUnlock, "events", "!_custom_difficulty_unlock.txt", 1, "../gratak_mods/custom_difficulty_unlock/")

customMenu=TagList()
mainFileContent.addComment("custom Menu")
mainFileContent.add("country_event",customMenu)
customMenu.add("id", name_customMenuEvent)
customMenu.add("is_triggered_only", yes)
customMenu.add("title", "custom_difficulty_customize.name")
customMenu.add("picture", "GFX_evt_towel")
trigger=TagList()
customMenu.add("desc", TagList("trigger", trigger))
trigger.add("fail_text", TagList().add("text", "custom_difficulty_choose_desc").add("has_global_flag", "custom_difficulty_locked"))
trigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("has_global_flag", "custom_difficulty_locked"))
for i,cat in enumerate(cats):
  hidden_effect=TagList("country_event", TagList("id", CuDi.format(id_ChangeEvents+i*id_ChangeEvents)))
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
trigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("has_global_flag", "custom_difficulty_locked"))
trigger.add("text", "custom_difficulty_current_bonuses")
for difficulty in difficulties:
  trigger.add("success_text", TagList("text", "custom_difficulty_{}.name".format(difficulty)).add("has_global_flag", "custom_difficulty_{}".format(difficulty)))
trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_player.name").add("has_global_flag", "custom_difficulty_advanced_configuration_player"))
trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration.name").add("has_global_flag", "custom_difficulty_advanced_configuration"))
trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_scaling.name").add("has_global_flag", "custom_difficulty_advanced_configuration_scaling"))
# trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_crisis.name").add("has_global_flag", "custom_difficulty_advanced_configuration_crisis"))
trigger.add("fail_text", TagList("text", "custom_difficulty_choose").add("has_global_flag", "custom_difficulty_locked"))
for i,difficulty in enumerate(difficulties):
  option=TagList("name","custom_difficulty_{}.name".format(difficulty))
  defaultMenuEvent.add("option", option)
  option.add("trigger", deepcopy(t_notLockedTrigger).add("not",TagList("has_global_flag", "custom_difficulty_{}".format(difficulty))))
  option.add("hidden_effect", TagList("country_event", TagList("id", CuDi.format(id_defaultEvents+i))).add("country_event", TagList("id", name_defaultMenuEvent)))
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
immediate=TagList()
rootUpdateMenu.add("immediate",immediate)
def ifDelay(name):
  self=TagList()
  self=TagList("limit",TagList("has_global_flag", "custom_difficulty_delay_mode"))
  self.add("every_country", TagList("country_event", TagList("id", name).add("days","1").add("random","180")))
  # ifInstant=TagList("limit",TagList("not", TagList("has_global_flag", "custom_difficulty_delay_mode")))
  self.add("else", TagList("every_country", TagList("country_event", TagList("id", name))))
  return self
ifSimple=TagList("limit",TagList("has_global_flag", "custom_difficulty_activate_simple_mode"))
ifSimple.add("if", ifDelay(name_countryUpdateEventSimple)).add("else", TagList("if",ifDelay(name_countryUpdateEvent)))
immediate.add("if", ifSimple)



mainFileContent.add("","","#game start init")
gameStartInitEvent=TagList("id", name_gameStartFireOnlyOnce) #TODO BILD
gameStartInitEvent.add("title","custom_difficulty_init" )
trigger=TagList()
gameStartInitEvent.add("desc", TagList("trigger", trigger)) #"" )
trigger.add("text","custom_difficulty_init_desc")
trigger.add("success_text", TagList("text","custom_difficulty_init_crisis_desc").add("is_crises_allowed", "yes"))
trigger.add("success_text", TagList("text", "custom_difficulty_init_no_crisis_desc").add("is_crises_allowed", "no"))
mainFileContent.add("country_event", gameStartInitEvent)
gameStartInitEvent.add("fire_only_once", yes)
# gameStartInitEvent.add("hide_window", yes)
gameStartInitEvent.add("trigger", TagList("is_ai","no").add("not", TagList("has_global_flag", "custom_difficulty_active")))
immediate=TagList()
gameStartInitEvent.add("immediate",immediate)
immediate.add("random_planet", TagList("save_global_event_target_as", "custom_difficulty_var_storage"))
for strength in [0.25, 0.5, 1, 2,3,4,5]:
  gameStartInitEvent.add("option", TagList("name", "custom_difficulty_{!s}_crisis.name".format(strength))
    .add("trigger", TagList("is_crises_allowed", yes))
    .add("hidden_effect", TagList(ET,TagList("set_variable", TagList("which","custom_difficulty_crisis_strength").add("value",str(strength))))))
  locClass.addEntry("custom_difficulty_{!s}_crisis.name".format(strength), "§R{}x @crisisStrength§!".format(strength))
gameStartInitEvent.add("option", TagList("name", "OK").add("trigger", TagList("is_crises_allowed", "no")))
gameStartAfter=TagList()
gameStartInitEvent.add("after",TagList("hidden_effect", gameStartAfter))
gameStartAfter.add("set_global_flag", "custom_difficulty_active")
gameStartAfter.add("set_global_flag","custom_difficulty_no_player_bonus")
gameStartAfter.add("set_global_flag","custom_difficulty_no_scaling")
for i, difficulty in enumerate(difficulties):
  if difficulty=="scaling":
    k=1 #scaling with stupid place in between ensign and captain
    gameStartAfter.addComment("#execute enisgn event to get the flag and non-ai stuff (that does not scale for my mod!)")
    gameStartAfter.add("if", TagList("limit", TagList("is_difficulty", str(k))).add("country_event",TagList("id", CuDi.format(id_defaultEvents+difficulties.index("ensign")))))
  elif difficulty=="ensign":
    k=0
  elif difficulty in vanillaDefaultDifficultyNames:
    k=vanillaDefaultDifficultyNames.index(difficulty)+1
  else:
    continue #those cannot be preset in game creation
  gameStartAfter.add("","","#"+difficulty)
  gameStartAfter.add("if", TagList("limit", TagList("is_difficulty", str(k))).add("country_event",TagList("id", CuDi.format(id_defaultEvents+i))))
gameStartAfter.add("country_event", TagList("id", name_rootUpdateEvent))






optionsEvent.add("id", name_optionsEvent)
optionsEvent.add("is_triggered_only", yes)
optionsEvent.add("title", "custom_difficulty_options.name")
# optionsEvent.add("desc", "custom_difficulty_options.desc")
optionsEvent.add("picture", "GFX_evt_towel")

descTrigger=TagList()
optionsEvent.add("desc", TagList("trigger", descTrigger))
descTrigger.add("success_text", TagList().add("text", "custom_difficulty_locked.desc").add("has_global_flag", "custom_difficulty_locked"))
descTrigger.add("text", "custom_difficulty_current_options")
locClass.append("custom_difficulty_current_options", "@current_options")


optionWithInverse=dict()
# flag is going to be "custom_difficulty_"+key
# name "custom_difficulty_"+key
# desc "custom_difficulty_"+key+".desc"
optionWithInverse["activate_simple_mode"]=["activate_custom_mode"]
optionWithInverse["activate_custom_mode"]=["activate_simple_mode"]
optionWithInverse["deactivate_player_vassal_ai_boni"]=["activate_player_vassal_ai_boni"]
optionWithInverse["activate_player_vassal_ai_boni"]=["deactivate_player_vassal_ai_boni"]
optionWithInverse["deactivate_delay_mode"]=["activate_delay_mode"]
optionWithInverse["activate_delay_mode"]=["deactivate_delay_mode"]
# optionWithInverse[]=[]

optionExtraEvents=dict()
optionExtraEvents["activate_simple_mode"]=["name_removeAllModifiers"]
optionExtraEvents["activate_custom_mode"]=["name_removeAllModifiers"]

optionColors="GGBBYY"
defaultOptions=[]


optionI=-1
for key, inverses in optionWithInverse.items():
  optionI+=1
  seperateDesc=False
  locClass.append("custom_difficulty_"+key+".desc", "§{}@{}Desc§!".format(optionColors[optionI],key))
  locClass.append("custom_difficulty_"+key+".name", "§{}@{}§!".format(optionColors[optionI],key))
  descTrigger.add("success_text", TagList().add("text", "custom_difficulty_"+key+".desc").add("has_global_flag", "custom_difficulty_"+key))
  option=TagList("name","custom_difficulty_{}.name".format(key))
  optionsEvent.add("option", option)
  option.add("custom_tooltip", "custom_difficulty_{}.desc".format(key))
  trigger=deepcopy(t_notLockedTrigger)
  option.add("trigger", trigger)
  trigger.add("not", TagList("has_global_flag", "custom_difficulty_"+key))
  effect=TagList("set_global_flag", "custom_difficulty_"+key)
  inverseIsDefault=False
  for inverse in inverses:
    effect.add("remove_global_flag", "custom_difficulty_"+inverse)
    if inverse in defaultOptions:
      inverseIsDefault=True
  if not inverseIsDefault:
    for name, val in effect.getNameVal():
      gameStartAfter.insert(0, name, deepcopy(val))
    # gameStartAfter.addTagList(deepcopy(effect))
    defaultOptions.append(key)
  if key in optionExtraEvents:
    for e in optionExtraEvents[key]:
      add_event(effect,e)
  add_event(effect,"name_optionsEvent")
  # effect.add("country_event", TagList("id", name_optionsEvent))
  option.add("hidden_effect", effect)
optionsEvent.add("option", TagList("name","custom_difficulty_lock.name").add("trigger", t_notLockedTrigger).add("hidden_effect", TagList("country_event", TagList("id",name_lockEvent))))
optionsEvent.add("option", t_backMainOption )
optionsEvent.add("option", t_closeOption)

optionEventUnlock=deepcopy(optionsEvent)
optionEventUnlock.insert(-2,"option",TagList("name","custom_difficulty_unlock.name").add("trigger", TagList("has_global_flag","custom_difficulty_locked")).add("hidden_effect",TagList("remove_global_flag", "custom_difficulty_locked").add("country_event", t_mainMenuEvent)))
mainFileUnlock=TagList("namespace", "custom_difficulty")
mainFileUnlock.add("country_event", optionEventUnlock)
outputToFolderAndFile(mainFileUnlock, "events", "!_custom_difficulty_unlock.txt", 1, "../gratak_mods/custom_difficulty_unlock_new/")


mainFileContent.add("","","#reset event")
resetEvent=deepcopy(gameStartInitEvent)
resetEvent.replace("id", name_resetEvent)
resetEvent.remove("fire_only_once")
resetEvent.remove("trigger")
resetEvent.add("is_triggered_only",yes)
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



outputToFolderAndFile(mainFileContent , "events", "custom_difficulty_main.txt",1 )


for language in locClass.languages:
  outFolderLoc="../gratak_mods/custom_difficulty/localisation/"+language
  if not os.path.exists(outFolderLoc):
    os.makedirs(outFolderLoc)
  locClass.write(outFolderLoc+"/custom_difficulty_l_"+language+".yml",language)




