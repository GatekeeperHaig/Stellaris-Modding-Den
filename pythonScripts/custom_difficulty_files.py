#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList

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
possibleBoniIcons=["£minerals","£energy", "£food", "£physics £society £engineering","£unity", "£influence","","","","","","",""]
possibleBoniColor=["P","Y","G","M","E","B","W","R","G","H","B","T","G"]

bonusesListNames=["all","default", "allShip"]
bonusListNPC=[    True,   False,    False]
bonusesListEntries=[[0,1,2,3,4,5,6,7,8,9,10,11,12], [0,1,2,3,4,6], [7,8,9,10]]
bonusesListPictures=["GFX_evt_towel", "GFX_evt_alien_city","GFX_evt_federation_fleet"]

cats=["ai","ai_yearly","fe","leviathan","player","crisis","marauders", "other"]
timesTenCats=["crisis", "leviathan"]
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
catPictures=["GFX_evt_throne_room","GFX_evt_organic_oppression","GFX_evt_fallen_empire","GFX_evt_wraith","GFX_evt_towel","GFX_evt_towel","GFX_evt_towel","GFX_evt_towel"]

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

#BIG TODO Add update flags! Only update when needed!
#BIG TODO Implement the options!
#BIG TODO I don't think "times 10" modifiers are removed so far before update. Update events have to be reworked first though!

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
locClass.addLoc("default", "Standard")
locClass.addLoc("allShip", "All Ship")
#cats
locClass.addLoc("ai", "AI Default Empire")
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






locClass.addEntry("custom_difficulty_current_bonuses","@curBon:")
locClass.addEntry("custom_difficulty_current_yearly_desc", "@yearlyDesc. @cur:")
locClass.addEntry("custom_difficulty_back", "@back")
locClass.addEntry("custom_difficulty_cancel", "@cancel")
locClass.addEntry("custom_difficulty_close.name", "@close @modName @menu")
locClass.addEntry("custom_difficulty_lock.name", "@lock")
locClass.addEntry("custom_difficulty_lock.desc", "@lockDesc @care")
locClass.addEntry("custom_difficulty_locked.name", "@lockActive")
locClass.addEntry("custom_difficulty_locked.desc", "@lockActive @lockActiveDesc")
# locClass.addEntry("custom_difficulty_lockActive.desc", "@lockActive @lockActiveDesc")
locClass.addEntry("custom_difficulty_unlock.name", "@unlock")
locClass.addEntry("edict_custom_difficulty", "@modName - @main @menu") #also used for menu title. Has to be named edict for the edict
locClass.addEntry("edict_custom_difficulty_desc", "@menuDesc")
locClass.addEntry("custom_difficulty_options.name", "@options")
locClass.addEntry("custom_difficulty_choose_desc", "@choose")
locClass.addEntry("custom_difficulty_predef_head.name", "@modName - @preDef")
locClass.addEntry("custom_difficulty_predefined_colored.name", "§G@preDef")
locClass.append("custom_difficulty_crisis_colored.name","§R@crisis @strength")
locClass.append("custom_difficulty_customize_colored.name","§Y@difficulty @customization")
locClass.append("custom_difficulty_customize.name","§Y@difficulty @customization")
locClass.addEntry("custom_difficulty_choose", "@choosePreDef.§R @delWarn§! @combineText")
locClass.addEntry("custom_difficulty_easy.name", "§G@easy - 20% @bonus @allCat @forPlayer") #TODO: color coding in custom menu same as here! To make clearer what overwrites what. "R" for crisis
locClass.addEntry("custom_difficulty_ensign.name", "§B@ensign - @no @bonus @forAI. 33% @forNPCs")
locClass.addEntry("custom_difficulty_captain.name", "§B@captain - 15-25% @bonus @forAI. 50% @forNPCs")
locClass.addEntry("custom_difficulty_commodore.name", "§B@commodore - 30-50% @bonus @forAI. 66% @forNPCs")
locClass.addEntry("custom_difficulty_admiral.name", "§B@admiral - 45-75% @bonus @forAI. 75% @forNPCs")
locClass.addEntry("custom_difficulty_grand_admiral.name", "§B@grandAdmiral - 60-100% @bonus @forAI. 100% @forNPCs")
locClass.addEntry("custom_difficulty_scaling.name", "§H@scaling - @increase @bonus @forAI @every 4 @years")
locClass.addEntry("custom_difficulty_advanced_configuration.name", "@advCust @nonPlayer")
locClass.addEntry("custom_difficulty_advanced_configuration_player.name", "@advCust @player")
locClass.addEntry("custom_difficulty_advanced_configuration_yearly.name", "@advCust @yearly")
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
name_rootUpdateEventDelay="custom_difficulty.41"
name_countryUpdateEvent="custom_difficulty.50"
name_lockEvent="custom_difficulty.60"
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
    locClass.append("custom_difficulty_crisis_strength_desc", "@vanilla @example @values: @grandAdmiral + x5 @crisis @strength: 1000%. @ensign + x5 @crisis @strength: xxx%. @ensign + x0.25 @crisis @strength: xxx%.") #TODO: get correct values!
  if cat=="ai_yearly":
    trigger.add("text", "custom_difficulty_current_yearly_desc") #loc global
  else:
    trigger.add("text", "custom_difficulty_current_bonuses") #loc global

  #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before)
  optionIndex=0
  for bonusesListName in bonusesListNames:
    optionIndex+=1
    option=TagList().add("name", "custom_difficulty_{}_change_{}_name".format(cat,bonusesListName))
    option.add("trigger", TagList().add("not", TagList().add("has_global_flag","custom_difficulty_locked")))
    locClass.addEntry("custom_difficulty_{}_change_{}_name".format(cat,bonusesListName), "@change @{} @bonuses".format(bonusesListName))
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", CuDi.format(mainIndex*id_ChangeEvents+optionIndex*id_subChangeEvents))))
    if not cat in timesTenCats or bonusListNPC[optionIndex-1]:
      choiceEvent.add("option",option)

  for bonusI, bonus in enumerate(possibleBoniNames):
    optionIndex+=1
    localVarName="custom_difficulty_{}_{}_value".format(cat,bonus)
    if cat=="ai_yearly":
      checkVar=TagList().add("which", localVarName).add("value","0","",">")
      trigger.add("success_text",TagList().add("text","custom_difficulty_{}_{}_inc_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)))
      checkVar=TagList().add("which", localVarName).add("value","0","","<")
      trigger.add("success_text",TagList().add("text","custom_difficulty_{}_{}_dec_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)))
      locClass.addEntry("custom_difficulty_{}_{}_inc_desc".format(cat,bonus),"{} §{}@{} : 1% @increase @every [this.custom_difficulty_{}_{}_value] @years".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonus)) #local tmp var
      locClass.addEntry("custom_difficulty_{}_{}_dec_desc".format(cat,bonus),"{} §{}@{} : 1% @decrease @every [this.custom_difficulty_{}_{}_value] @years".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonus)) #local tmp var
      #create a local variable and make sure it is positive!
      immediate.add("set_variable", TagList().add("which", localVarName).add("value",ET))
      immediateIf=TagList().add("limit",TagList().add("check_variable",checkVar)) #<0
      immediateIf.add("multiply_variable", TagList().add("which", localVarName).add("value","-1"))
      immediate.add("if",immediateIf)
    else:
      checkVar=TagList().add("which", localVarName).add("value","0")
      trigger.add("fail_text",TagList().add("text","custom_difficulty_{}_{}_desc".format(cat,bonus)).add(ET,TagList().add("check_variable", checkVar)))
      locClass.append("custom_difficulty_{}_{}_desc".format(cat,bonus),"{} §{}@{} : [{}.custom_difficulty_{}_{}_value]% ".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, ET, cat,bonus))

    #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before the loop)
    option=TagList().add("name", "custom_difficulty_{}_change_{}_button.name".format(cat,bonus))
    option.add("trigger", TagList().add("not", TagList().add("has_global_flag","custom_difficulty_locked")))
    locClass.append("custom_difficulty_{}_change_{}_button.name".format(cat,bonus), "@change @{} @bonuses".format(bonus))
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", CuDi.format(mainIndex*id_ChangeEvents+optionIndex*id_subChangeEvents))))
    if not cat in timesTenCats or npcBoni[bonusI]:
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
    if not cat in timesTenCats or (bonusListNPC+npcBoni)[bonusIndex-1]:
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
        if cat in timesTenCats:
          changeStep*=10
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
            if not cat in timesTenCats or npcBoni[bonusListIndex]:
              bonusListValue=possibleBoniNames[bonusListIndex]
              et.add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusListValue)).add("value",str(changeStep)))
        hidden_effect.add("country_event", TagList().add("id",CuDi.format(mainIndex*id_ChangeEvents+bonusIndex*id_subChangeEvents)))
        if cat=="player":
          hidden_effect.add("country_event", TagList().add("id",name_resetPlayerFlagsEvent)) #remove flags
        elif cat=="ai_yearly":
          hidden_effect.add("country_event", TagList().add("id",name_resetYearlyFlagsEvent)) #remove flags
        else:
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


class PreDefinedDifficulty:
  def __init__(self):
    self.dict=dict()

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
diffLevels["ensign"]=[33, 0,0 ] # npc, high ai, low ai
diffLevels["captain"]=[50, 25,15 ]
diffLevels["commodore"]=[66, 50,30 ]
diffLevels["admiral"]=[75, 75,45 ]
diffLevels["grand_admiral"]=[100, 100,60 ]
for diff, level in diffLevels.items():
  difficultiesPresetProperties[diff]["ai"]=[condValPrec(level[2], level[1],b) for b in aiDefaultPrecise]
  for cat in catsWithNPCDefaultBoni:
    difficultiesPresetProperties[diff][cat]=[condVal(level[0],s) for b in npcDefault]

#TODO CRISIS DEFAULTS


playerFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_player")
scalingFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_scaling")
otherFlags=TagList("remove_global_flag", "custom_difficulty_advanced_configuration_other")
# for difficulty in ai_non_scaling_DifficultyNames:
#   otherFlags.add("remove_global_flag", "custom_difficulty_{}".format(difficulty))

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
    for i, value in enumerate(values):
      et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,possibleBoniNames[i])).add("value", str(value)))



#easy



# et=TagList()
# immediate.add(ET,et)
# for cat in cats:
#   for bonus in possibleBoniNames:
#     if cat=="player":
#       et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", "20"))
#     # else:
#     #   immediate.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", "0"))

# # defaultIndex=-1
# for name, values in zip(vanillaDefaultDifficultyNames, vanillaDefaultDifficulty):
#   # defaultIndex+=1
#   newEvent=deepcopy(defaultEventTemplate)
#   eventIndex+=1
#   defaultEvents.add("country_event", newEvent)
#   newEvent.replace("id",CuDi.format(eventIndex))
#   immediate=newEvent.get("immediate")
#   if "scaling"==name:
#     immediate.add("country_event",TagList().add("id",name_resetYearlyFlagsEvent))
#   else:
#     immediate.add("country_event",TagList().add("id",name_resetAIFlagsEvent))
#   immediate.add("set_global_flag","custom_difficulty_"+name)
#   et=TagList()
#   immediate.add(ET,et)
#   for cat in cats:
#     for i,bonus in enumerate(possibleBoniNames):
#       if cat=="ai" and i<vanillaAItoNPCIndex:
#         et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(values[i])))
#       elif cat=="leviathan" and i>=vanillaAItoNPCIndex:
#         et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(values[i])))
#       elif cat=="fe" and i>=vanillaAItoNPCIndex:
#         et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(values[i])))
#       # elif "yearly" in cat and (not name=="scaling" or not scaleDefault[i]):
#       #   et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", "0"))
#       elif "yearly" in cat and name=="scaling" and scaleDefault[i]:
#         et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", "4"))
#       elif cat!="player":
#         et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", "0"))

with open(outFolder+"/"+"custom_difficulty_defaults.txt",'w') as file:
  defaultEvents.writeAll(file, args())


staticModifiers=TagList()

updateFile=TagList()
updateFile.add("namespace","custom_difficulty")
updateEvent=TagList()
updateFile.add("country_event",updateEvent)

updateEvent.add("id", name_countryUpdateEvent)
updateEvent.add("is_triggered_only",yes)
updateEvent.add("hide_window",yes)
immediate=TagList()
updateEvent.add("immediate",immediate)
after=TagList()
# updateEvent.add("after",after)
for catI,cat in enumerate(cats):
  if "yearly" in cat:
    continue
  ifTagList=TagList()
  immediate.add("if",ifTagList)
  limit=TagList()
  ifTagList.add("limit",limit)
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
    limit.add("or",orTagList)
    if cat=="player":
      orTagList.add("is_ai", "no")
      orTagList.add("and", TagList().add("exists","overlord").add("overlord",TagList().add("is_ai","no")))
    else:
      orTagList.add("is_ai", yes)
      orTagList.add("and", TagList().add("exists","overlord").add("overlord",TagList().add("is_ai","yes")))

  afterIfTaglist=deepcopy(ifTagList)
  after.add("if",afterIfTaglist)
  shortened=False

  for bonus, bonusModifier in zip(possibleBoniNames,possibleBoniModifier):
    ifTagList.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", ET))
    if cat=="player":
      # switchTL=TagList()
      # afterIfTaglist.add("switch",switchTL)
      for sign in [1,-1]:
        if sign==1:
          compSign=">"
        else:
          compSign="<"
        for i in reversed(range(20)):
          if shortened:
           if sign<0 and i>5 or i>10:
            continue
          ifGT=TagList()
          afterIfTaglist.add("if",ifGT)
          changeVal=10*(i+1)
          ifGT.add("limit", TagList().add("check_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(sign*(changeVal-0.1)),"",compSign)))
          if sign>0:
            modifierName="custom_difficulty_{}_{}_pos_player_value".format(i,bonus)
          else:
            modifierName="custom_difficulty_{}_{}_neg_player_value".format(i,bonus)
          modifier=TagList()
          if not isinstance(bonusModifier,list):
            bonusModifier=[bonusModifier]
          for modifierEntry in bonusModifier:
            if bonus=="Upkeep":
              modifier.add(modifierEntry,str(-sign*changeVal/100))
            else:
              modifier.add(modifierEntry,str(sign*changeVal/100))
          locClass.append(modifierName,"@difficulty")
          staticModifiers.add(modifierName,modifier)
          ifGT.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
          immediate.add("remove_modifier", modifierName)
          ifGT.add("change_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(-1*sign*changeVal)))
          # ifGT.add("break","yes")
    elif cat=="ai" or cat=="crisis":
      for sign in [1,-1]:
        if sign==1:
          compSign=">"
        else:
          compSign="<"
        for i in reversed(range(10)):
          if shortened:
           if sign<0 and i>5 or i>7:
            continue

          ifGT=TagList()
          afterIfTaglist.add("if",ifGT)
          changeVal=pow(2,i)
          if cat=="crisis":
            changeVal*=10
          ifGT.add("limit", TagList().add("check_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(sign*(changeVal-0.1)),"",compSign)))
          if sign>0:
            modifierName="custom_difficulty_{}_{}_pos_value".format(i,bonus)
          else:
            modifierName="custom_difficulty_{}_{}_neg_value".format(i,bonus)
          if cat=="crisis":
            modifierName+="_times_ten"
          modifier=TagList()
          if not isinstance(bonusModifier,list):
            bonusModifier=[bonusModifier]
          for modifierEntry in bonusModifier:
            if bonus=="Upkeep":
              modifier.add(modifierEntry,str(-sign*changeVal/100))
            else:
              modifier.add(modifierEntry,str(sign*changeVal/100))
          locClass.append(modifierName,"@difficulty")
          staticModifiers.add(modifierName,modifier)
          ifGT.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
          if cat=="ai": #only add onces as they all have the same name
            immediate.add("remove_modifier", modifierName)
          ifGT.add("change_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonus)).add("value", str(-1*sign*changeVal)))
immediate.addTagList(after)


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
onActions.add("on_yearly_pulse", TagList("events",TagList().add(name_rootYearlyEvent).add(name_rootUpdateEvent)))
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
  mainMenu.add("option", TagList("name","custom_difficulty_crisis_colored.name").add("hidden_effect", TagList("country_event", TagList("id", CuDi.format(id_ChangeEvents+cats.index("crisis")*id_ChangeEvents))).add("remove_global_flag","custom_difficulty_menu_crisis_from_custom")))
  mainMenu.add("option", TagList("name","custom_difficulty_customize_colored.name").add("hidden_effect", TagList("country_event", TagList("id", name_customMenuEvent))))
  mainMenu.add("option", TagList("name","custom_difficulty_options.name").add("hidden_effect", TagList("country_event", TagList("id", name_optionsEvent))))
  # mainMenu.add("option", TagList("name","custom_difficulty_lock.name").add("trigger", t_notLockedTrigger).add("hidden_effect", TagList("country_event", TagList("id",name_lockEvent))))
  # if allowUnlock:
  #   mainMenu.add("option",TagList("name","custom_difficulty_unlock.name").add("trigger", TagList("has_global_flag","custom_difficulty_locked")).add("hidden_effect",TagList("remove_global_flag", "custom_difficulty_locked").add("country_event", t_mainMenuEvent)))
  # mainMenu.add("option", t_closeOption)

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
  if cat=="crisis":
    hidden_effect.add("add_global_flag","custom_difficulty_menu_crisis_from_custom")
  customMenu.add("option", TagList("name","custom_difficulty_{}.name".format(cat)).add("hidden_effect", hidden_effect))
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
trigger.add("success_text", TagList("text", "custom_difficulty_advanced_configuration_yearly.name").add("has_global_flag", "custom_difficulty_advanced_configuration_yearly"))
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


mainFileContent.add("","","#game start init")
gameStartInitEvent=TagList("id", name_gameStartFireOnlyOnce)
mainFileContent.add("country_event", gameStartInitEvent)
gameStartInitEvent.add("fire_only_once", yes)
gameStartInitEvent.add("hide_window", yes)
gameStartInitEvent.add("trigger", TagList("is_ai","no").add("not", TagList("has_global_flag", "custom_difficulty_active")))
immediate=TagList()
gameStartInitEvent.add("immediate",immediate)
immediate.add("set_global_flag", "custom_difficulty_active")
immediate.add("random_planet", TagList("save_global_event_target_as", "custom_difficulty_var_storage"))
for i, difficulty in enumerate(difficulties):
  if difficulty=="scaling":
    k=1 #scaling with stupid place in between ensign and captain
  elif difficulty=="ensign":
    k=0
  elif difficulty in vanillaDefaultDifficultyNames:
    k=vanillaDefaultDifficultyNames.index(difficulty)+1
  else:
    continue #those cannot be preset in game creation
  immediate.add("","","#"+difficulty)
  immediate.add("if", TagList("limit", TagList("is_difficulty", str(k))).add("country_event",TagList("id", CuDi.format(id_defaultEvents+i))))
  immediate.add("country_event", TagList("id", name_rootUpdateEvent))


mainFileContent.add("","","#reset event")
resetEvent=deepcopy(gameStartInitEvent)
resetEvent.replace("id", name_resetEvent)
resetEvent.remove("fire_only_once")
resetEvent.remove("trigger")
resetEvent.add("is_triggered_only",yes)
mainFileContent.add("country_event", resetEvent)

mainFileContent.add("","","#reset confirmation")
resetConfirmation=TagList("id", name_resetConfirmationEvent)
mainFileContent.add("country_event", resetConfirmation)
resetConfirmation.add("is_triggered_only",yes)
resetConfirmation.add("title","custom_difficulty_reset_conf.name")
resetConfirmation.add("desc","custom_difficulty_reset.desc")
resetConfirmation.add("picture", "GFX_evt_towel")
effect=TagList().add("country_event", TagList("id", name_resetFlagsEvent)).add("country_event", TagList("id", name_resetEvent)).add("country_event", TagList("id", name_defaultMenuEvent))
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


optionsEvent=TagList()
mainFileContent.addComment("options Event")
mainFileContent.add("country_event", optionsEvent)
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
optionWithInverse["activate_custom_mode"]=["activate_simple_mode"]
optionWithInverse["activate_simple_mode"]=["activate_custom_mode"]
optionWithInverse["activate_player_vassal_ai_boni"]=["deactivate_player_vassal_ai_boni"]
optionWithInverse["deactivate_player_vassal_ai_boni"]=["activate_player_vassal_ai_boni"]
optionWithInverse["activate_delay_mode"]=["deactivate_delay_mode"]
optionWithInverse["deactivate_delay_mode"]=["activate_delay_mode"]
# optionWithInverse[]=[]

#todo: move to top to be translated
locClass.addLoc("current_options", "Currently active options")
locClass.addLoc("activate_custom_mode", "Activate Custom Mode")
locClass.addLoc("activate_simple_mode", "Activate Simple Mode")
locClass.addLoc("activate_player_vassal_ai_boni", "Activate Player Vassal AI Bonus")
locClass.addLoc("deactivate_player_vassal_ai_boni", "Deactivate Player Vassal AI Bonus")
locClass.addLoc("activate_custom_mode"+"Desc", "Specific choice of bonuses to be applied possible.")
locClass.addLoc("activate_simple_mode"+"Desc", "Only bonus groups and default difficulties can be chosen. Slightly improved performance.")
locClass.addLoc("activate_player_vassal_ai_boni"+"Desc", "Player vassals will get the same bonuses as other AI empires")
locClass.addLoc("deactivate_player_vassal_ai_boni"+"Desc", "Vanilla behavior of player vassals not getting AI bonuses. They will get player bonuses though if any such have been activated.")
locClass.addLoc("activate_delay_mode", "Activate Delay Mode")
locClass.addLoc("activate_delay_mode"+"Desc", "Update events will happen with a random delay of 1-181 days after the menu is closed or a year ends.")
locClass.addLoc("deactivate_delay_mode", "Deactivate Delay Mode")
locClass.addLoc("deactivate_delay_mode"+"Desc", "Update events happen direclty after the menu is closed and at the start of each year.")
for key, inverses in optionWithInverse.items():
  seperateDesc=False
  locClass.append("custom_difficulty_"+key+".desc", "@"+key+"Desc")
  locClass.append("custom_difficulty_"+key+".name", "@"+key)
  descTrigger.add("success_text", TagList().add("text", "custom_difficulty_"+key+".desc").add("has_global_flag", key))
  option=TagList("name","custom_difficulty_{}.name".format(key))
  optionsEvent.add("option", option)
  option.add("custom_tooltip", "custom_difficulty_{}.desc".format(key))
  trigger=deepcopy(t_notLockedTrigger)
  option.add("trigger", trigger)
  trigger.add("not", TagList("has_global_flag", "custom_difficulty_"+key))
  effect=TagList("set_global_flag", "custom_difficulty_"+key)
  for inverse in inverses:
    effect.add("remove_global_flag", "custom_difficulty_"+inverse)
  effect.add("country_event", TagList("id", name_optionsEvent))
  option.add("hidden_effect", effect)
optionsEvent.add("option", TagList("name","custom_difficulty_lock.name").add("trigger", t_notLockedTrigger).add("hidden_effect", TagList("country_event", TagList("id",name_lockEvent))))
optionsEvent.add("option", t_backMainOption )
optionsEvent.add("option", t_closeOption)

optionEventUnlock=deepcopy(optionsEvent)
optionEventUnlock.insert(-2,"option",TagList("name","custom_difficulty_unlock.name").add("trigger", TagList("has_global_flag","custom_difficulty_locked")).add("hidden_effect",TagList("remove_global_flag", "custom_difficulty_locked").add("country_event", t_mainMenuEvent)))
mainFileUnlock=TagList("namespace", "custom_difficulty")
mainFileUnlock.add("country_event", optionEventUnlock)
outputToFolderAndFile(mainFileUnlock, "events", "!_custom_difficulty_unlock.txt", 1, "../gratak_mods/custom_difficulty_unlock_new/")
optionsEvent=TagList()




outputToFolderAndFile(mainFileContent , "events", "custom_difficulty_main.txt",1 )


for language in locClass.languages:
  outFolderLoc="../gratak_mods/custom_difficulty/localisation/"+language
  if not os.path.exists(outFolderLoc):
    os.makedirs(outFolderLoc)
  locClass.write(outFolderLoc+"/custom_difficulty_l_"+language+".yml",language)

# doTranslation=False
# for language, lcode in zip(["braz_por","english","french","german","polish","russian","spanish"],["pt","en","fr", "de","pl","ru", "es"]):
#   outFolderLoc="../gratak_mods/custom_difficulty/localisation/"+language
#   if not os.path.exists(outFolderLoc):
#     os.makedirs(outFolderLoc)

#   if doTranslation:
#     translatedDict=dict()
#     translatedDict["["]="["
#     translatedDict["]"]="]"
#     translator=Translator()
#   with io.open(outFolderLoc+"/custom_difficulty_l_"+language+".yml",'w', encoding="utf-8") as file:
#     file.write(u'\ufeff')
#     file.write("l_"+language+":\n")
#     for locEntry in locList:
#       if language=="english" or not doTranslation:
#         file.write(" "+locEntry[0]+":0 "+'"'+locEntry[1]+'"\n')
#       else:
#         locParts=re.split("(\[|\]|§|£)",locEntry[1])
#         for i in reversed(range(len(locParts))):
#           if locParts[i]=="":
#             del locParts[i]
#         for i,locPart in enumerate(locParts):
#           if locPart=="§":
#             if i!=len(locParts)-1:
#               locParts[i]+=locParts[i+1][0]
#               locParts[i+1]=locParts[i+1][1:]
#             continue
#           if locPart=="£":
#             locParts[i]+=locParts[i+1][0:locParts[i+1].index(" ")]
#             locParts[i+1]=locParts[i+1][locParts[i+1].index(" "):]
#             continue
#           if (i==0 or locParts[i-1]!="[") and not locPart.strip()=="":
#             if not locPart in translatedDict:
#               try:
#                 translatedDict[locPart]=translator.translate(text=locPart, src="en", dest=lcode).text
#               except:
#                 print(locPart)
#                 translatedDict[locPart]=locPart
#             locParts[i]=translatedDict[locPart]
#         file.write(" "+locEntry[0]+":0 "+'"'+"".join(locParts)+'"\n')







