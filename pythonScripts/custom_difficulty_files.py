#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy

changeStepYears=[5,4,3,2,1]
changeSteps = [50, 25, 10, 5, 1]
for s in reversed(changeSteps):
  changeSteps.append(-s)
for s in reversed(changeStepYears):
  changeStepYears.append(-s)
possibleBoniNames=["Minerals", "Energy","Food", "Research", "Unity", "Influence", "Naval capacity", "Weapon Damage", "Hull","Armor","Shield","Upkeep", "Any Pop growth speed"]
possibleBoniPictures=["GFX_evt_mining_station","GFX_evt_dyson_sphere","GFX_evt_animal_wildlife", "GFX_evt_think_tank", "GFX_evt_ancient_alien_temple","GFX_evt_arguing_senate","GFX_evt_hangar_bay", "GFX_evt_debris", "GFX_evt_sabotaged_ship","GFX_evt_pirate_armada","GFX_evt_fleet_neutral","GFX_evt_city_ruins","GFX_evt_metropolis"]
possibleBoniModifier=["country_resource_minerals_mult", "country_resource_energy_mult","country_resource_influence_mult", "country_resource_food_mult", "all_technology_research_speed", "country_resource_unity_mult","country_naval_cap_mult","ship_weapon_damage","ship_hull_mult","ship_armor_mult","ship_shield_mult",["ship_upkeep_mult",
#"country_building_upkeep_mult", #is there any such modifier except on planet base?!
"country_starbase_upkeep_mult","army_upkeep_mult"],["pop_growth_speed","pop_robot_build_speed_mult"]]
possibleBoniIcons=["£minerals","£energy", "£food", "£physics £society £engineering","£unity", "£influence","","","","","","",""]
possibleBoniColor=["P","Y","G","M","E","B","W","R","G","H","B","T","G"]
boniListNames=["All","Vanilla Default Empire", "All ship bonuses"]
boniListEntries=[[0,1,2,3,4,5,6,7,8,9,10,11,12], [0,1,2,3,4,6], [7,8,9,10]]
boniListPictures=["GFX_evt_towel", "GFX_evt_alien_city","GFX_evt_federation_fleet"]
cats=["ai","ai_yearly","fe","leviathan","player"]
catNames=["AI Default Empire", "AI Yearly Change", "Fallen and Awakened Empires", "Leviathans and other NPCs", "Player"]
catCountryType=["default", "default","awakened_fallen_empire","",""]
catNotCountryType=["", "","",["default","awakened_fallen_empire"],""]
catPictures=["GFX_evt_throne_room","GFX_evt_organic_oppression","GFX_evt_fallen_empire","GFX_evt_wraith","GFX_evt_towel"]
locList=[]
locList.append(["custom_difficulty.current_bonuses", "Current Bonuses:"])
locList.append(["custom_difficulty.current_yearly_desc", "Positive year count gives increase, negative year count decrease. Every year is fastest possible. Zero (not displayed) means no change:"])
locList.append(["custom_difficulty.back", "Back"])
locList.append(["custom_difficulty.cancel", "Cancel and Back"])
locList.append(["close_custom_difficulty.name", "Close Custom Difficulty menu"])
locList.append(["custom_difficulty.0.lock.name", "Lock settings for the rest of the game"])
locList.append(["custom_difficulty.0.lock.desc", "Yearly changes will continue up to the maximum/minimum. Can only be unlocked via installing the unlock mod, editing save game or starting a new game. Use with care!"])
locList.append(["custom_difficulty.0.locked.desc", "Difficulty locked. Yearly changes will continue up to the maximum/minimum. Can only be unlocked via installing the unlock mod, editing save game or starting a new game. Use with care!"])
locList.append(["custom_difficulty.0.unlock.name", "Unlock settings"])
locList.append(["custom_difficulty.0.unlock.desc", "Todo: Move to separate mod!"])
locList.append(["custom_difficulty.0.name", "Ultimate Custom Difficulty Main Menu"])
# locList.append(["custom_difficulty.0.name", "Ultimate Custom Difficulty Advanced Configuration"])
locList.append(["custom_difficulty.0.desc", "Choose category to change or show"])
# locList.append(["custom_difficulty.1.name", "Ultimate Custom Difficulty Main Menu"])
locList.append(["custom_difficulty.1.name", "Ultimate Custom Difficulty Predefined Difficulty"])
locList.append(["custom_difficulty_currently_active", "Currently active:"])
locList.append(["custom_difficulty_choose", "Choose predefined setting.§R Deletes previously made settings!§! Easy and vanilla can be combined. Easy does not overwrite non-player bonuses and Vanilla does not overwrite player bonuses."])
locList.append(["custom_difficulty_easy.name", "Easy - 20% Bonus in all categories for player"])
locList.append(["custom_difficulty_ensign.name", "Ensign - No Bonus for empires. 33% for NPCs"])
locList.append(["custom_difficulty_captain.name", "Captain - 15-25% Bonus for AI. 50% fo NPCs"])
locList.append(["custom_difficulty_commodore.name", "Commodore - 30-50% Bonus for AI. 66% fo NPCs"])
locList.append(["custom_difficulty_admiral.name", "Admiral - 45-75% Bonus for AI+NPCs"])
locList.append(["custom_difficulty_grand_admiral.name", "Grand Admiral - 60-100% Bonus for AI+NPCs"])
# locList.append(["custom_difficulty_grand_admiral.name", "Grand Admiral - 60-100% for AI"])
locList.append(["custom_difficulty_scaling.name", "Scaling - 0-50% Bonus for AI+NPCs"])
locList.append(["custom_difficulty_advanced_configuration.name", "Advanced Difficulty Customization non-player"])
locList.append(["custom_difficulty_advanced_configuration_player.name", "Advanced Difficulty Customization player"])
locList.append(["custom_difficulty_reset.name", "Reset all settings"])
locList.append(["custom_difficulty_reset_conf.name", "Reset settings - Confirmation"])
locList.append(["custom_difficulty_reset.desc", "Undo all changes and reset to difficulty set before game start"])
locList.append(["custom_difficulty.predefined_difficulties", "§GPredefined Difficulties"])

ET = "event_target:custom_difficulty_var_storage"

yes="yes"

difficultyChangeWindows = []
mainIndex=0
for cat in cats:
  mainIndex+=1 #starting with event 1000
  tagList=TagList()
  difficultyChangeWindows.append(tagList)
  tagList.add("namespace", "custom_difficulty")
  choiceEvent=TagList()
  tagList.add("country_event", choiceEvent)
  choiceEvent.add("id","custom_difficulty.{!s}000".format(mainIndex))
  choiceEvent.add("is_triggered_only", yes)
  choiceEvent.add("title","custom_difficulty_{}.name".format(cat))
  choiceEvent.add("picture",'"'+catPictures[mainIndex-1]+'"')
  locList.append(["custom_difficulty_{}.name".format(cat),"Change {} bonuses".format(catNames[mainIndex-1])])
  trigger=TagList()
  choiceEvent.add("desc", TagList().add("trigger",trigger))
  if cat=="ai_yearly":
    immediate=TagList()
    choiceEvent.add("immediate",immediate)
  if cat=="ai_yearly":
    trigger.add("text", "custom_difficulty.current_yearly_desc") #loc global
  else:
    trigger.add("text", "custom_difficulty.current_bonuses") #loc global

  #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before)
  optionIndex=0
  for boniListName in boniListNames:
    optionIndex+=1
    boniListNameR=boniListName.lower().replace(" ","_")
    option=TagList().add("name", "custom_difficulty_{}_change_{}_name".format(cat,boniListNameR))
    locList.append(["custom_difficulty_{}_change_{}_name".format(cat,boniListNameR), "Change {} bonuses".format(boniListName)])
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", "custom_difficulty.{:01d}{:02d}0".format(mainIndex,optionIndex))))
    choiceEvent.add("option",option)

  for bonusI, bonus in enumerate(possibleBoniNames):
    optionIndex+=1
    bonusR=bonus.lower().replace(" ","_")
    localVarName="custom_difficulty_{}_{}_value".format(cat,bonusR)
    if cat=="ai_yearly":
      checkVar=TagList().add("which", localVarName).add("value","0","",">")
      trigger.add("success_text",TagList().add("text","custom_difficulty_{}_{}_inc_desc".format(cat,bonusR)).add(ET,TagList().add("check_variable", checkVar)))
      checkVar=TagList().add("which", localVarName).add("value","0","","<")
      trigger.add("success_text",TagList().add("text","custom_difficulty_{}_{}_dec_desc".format(cat,bonusR)).add(ET,TagList().add("check_variable", checkVar)))
      locList.append(["custom_difficulty_{}_{}_inc_desc".format(cat,bonusR),"{} §{}{} : 1% increase every [this.custom_difficulty_{}_{}_value] year(s)".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonusR)]) #local tmp var
      locList.append(["custom_difficulty_{}_{}_dec_desc".format(cat,bonusR),"{} §{}{} : 1% decrease every [this.custom_difficulty_{}_{}_value] year(s)".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonusR)]) #local tmp var
      #create a local variable and make sure it is positive!
      immediate.add("set_variable", TagList().add("which", localVarName).add("value",ET))
      immediateIf=TagList().add("limit",TagList().add("check_variable",checkVar)) #<0
      immediateIf.add("multiply_variable", TagList().add("which", localVarName).add("value","-1"))
      immediate.add("if",immediateIf)
    else:
      checkVar=TagList().add("which", localVarName).add("value","0")
      trigger.add("fail_text",TagList().add("text","custom_difficulty_{}_{}_desc".format(cat,bonusR)).add(ET,TagList().add("check_variable", checkVar)))
      locList.append(["custom_difficulty_{}_{}_desc".format(cat,bonusR),"{} §{}{} : [{}.custom_difficulty_{}_{}_value]% ".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, ET, cat,bonusR)])

    #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before the loop)
    option=TagList().add("name", "custom_difficulty_{}_change_{}_button.name".format(cat,bonusR))
    locList.append(["custom_difficulty_{}_change_{}_button.name".format(cat,bonusR), "Change {} bonus".format(bonus)])
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", "custom_difficulty.{:01d}{:02d}0".format(mainIndex,optionIndex))))
    choiceEvent.add("option",option)

  option=TagList().add("name","custom_difficulty.back") #loc global
  option.add("hidden_effect", TagList().add("country_event",TagList().add("id", "custom_difficulty.0")))
  choiceEvent.add("option",option)
  option=TagList().add("name","close_custom_difficulty.name") #loc global
  option.add("hidden_effect", TagList().add("country_event",TagList().add("id", "custom_difficulty.9999")))
  choiceEvent.add("option",option)

  

  bonusIndex=0
  for bonus in boniListNames+possibleBoniNames:
    bonusIndex+=1
    bonusR=bonus.lower().replace(" ","_")
    changeEvent=TagList()
    tagList.add("country_event", changeEvent)
    changeEvent.add("id","custom_difficulty.{:01d}{:02d}0".format(mainIndex,bonusIndex))
    changeEvent.add("is_triggered_only", yes)
    changeEvent.add("title","custom_difficulty_{}_change_{}.name".format(cat,bonusR))
    locList.append(["custom_difficulty_{}_change_{}.name".format(cat,bonusR), "Change {} bonus ({})".format(bonus,catNames[mainIndex-1])])
    changeEvent.add("desc", TagList().add("trigger",trigger)) #same desc trigger as above?
    changeEvent.add("picture",'"'+(boniListPictures+possibleBoniPictures)[bonusIndex-1]+'"')
    if cat=="ai_yearly":
      changeEvent.add("immediate",immediate)

    if cat=="ai_yearly":
      changeStepListUsed=changeStepYears
    else:
      changeStepListUsed=changeSteps
    for changeStep in changeStepListUsed:
      if cat=="player" and (abs(changeStep)==1 or abs(changeStep)==5 or abs(changeStep)==25):
        continue
      if changeStep>0:
        option=TagList().add("name","custom_difficulty_{}_{}_increase_{!s}".format(cat,bonusR, changeStep))
        if cat=="ai_yearly":
          locList.append(["custom_difficulty_{}_{}_increase_{!s}".format(cat,bonusR, changeStep), "Increase {} years by {}".format(bonus, changeStep)])
        else:
          locList.append(["custom_difficulty_{}_{}_increase_{!s}".format(cat,bonusR, changeStep), "Increase {} bonuses by {}%".format(bonus, changeStep)])
      else:
        option=TagList().add("name","custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonusR, -changeStep))
        if cat=="ai_yearly":
          locList.append(["custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonusR, -changeStep), "Decrease {} years by {}".format(bonus, -changeStep)])
        else:
          locList.append(["custom_difficulty_{}_{}_decrease_{!s}".format(cat,bonusR, -changeStep), "Decrease {} bonuses by {}%".format(bonus, -changeStep)])

      hidden_effect=TagList()
      if bonusIndex>len(boniListNames):
        hidden_effect.add(ET,TagList().add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value",str(changeStep))))
      else:
        et=TagList()
        hidden_effect.add(ET,et)
        for bonusListIndex in boniListEntries[bonusIndex-1]:
          bonusListValue=possibleBoniNames[bonusListIndex].lower().replace(" ","_")
          et.add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusListValue)).add("value",str(changeStep)))
      hidden_effect.add("country_event", TagList().add("id","custom_difficulty.{:01d}{:02d}0".format(mainIndex,bonusIndex)))
      if cat!="player":
        hidden_effect.add("country_event", TagList().add("id","custom_difficulty.98".format(mainIndex,bonusIndex))) #remove flags
      else:
        hidden_effect.add("country_event", TagList().add("id","custom_difficulty.97".format(mainIndex,bonusIndex))) #remove flags
      hidden_effect.add("set_global_flag", "custom_difficulty_advanced_configuration")
      option.add("hidden_effect",hidden_effect)
      changeEvent.add("option",option)


    option=TagList().add("name","custom_difficulty.back")
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", "custom_difficulty.{}000".format(mainIndex))))
    changeEvent.add("option",option)
    option=TagList().add("name","close_custom_difficulty.name")
    option.add("hidden_effect", TagList().add("country_event",TagList().add("id", "custom_difficulty.9999")))
    changeEvent.add("option",option)

  # difficultyChangeWindows[-1].printAll()
  # break


class args:
  def __init__(self):
    self.one_line_level=2

outFolder="../gratak_mods/custom_difficulty/events"
if not os.path.exists(outFolder):
  os.mkdir(outFolder)
for cat, eventFileCont in zip(cats, difficultyChangeWindows):
  with open(outFolder+"/"+"custom_difficulty_"+cat+".txt",'w') as file:
    eventFileCont.writeAll(file,args())



defaultEventTemplate=TagList()
defaultEventTemplate.add("id")
defaultEventTemplate.add("is_triggered_only",yes)
defaultEventTemplate.add("hide_window",yes)
immediate=TagList()
defaultEventTemplate.add("immediate",immediate)

defaultEvents=TagList()
defaultEvents.add("namespace", "custom_difficulty")
eventIndex=9


vanillaDefault=[]
# possibleBoniNames=["Minerals", "Energy","Food", "Research", "Unity", "Influence", "Naval capacity", "Weapon Damage", "Hull","Armor","Shield","Upkeep", "Any Pop growth speed"]
scaleDefault=[True, True, True, True, True, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
vanillaAItoNPCIndex=7
vanillaDefault.append([0,0,0,0,0,0,0,33,33,33,33,0,0])
vanillaDefault.append([25,25,25,15,15,0,15,50,50,50,50,0,0])
vanillaDefault.append([50,50,50,30,30,0,30,66,66,66,66,0,0])
vanillaDefault.append([75,75,75,45,45,0,45,75,75,75,75,0,0])
vanillaDefault.append([100,100,100,60,60,0,60,100,100,100,100,0,0])
vanillaDefault.append([0,0,0,0,0,0,0,33,33,33,33,0,0])
vanillaDefaultNames=["ensign","captain","commodore","admiral", "grand_admiral", "scaling"]


#easy
newEvent=deepcopy(defaultEventTemplate)
eventIndex+=1
defaultEvents.add("country_event", newEvent)
newEvent.replace("id","custom_difficulty.{:02d}".format(eventIndex))
immediate=newEvent.get("immediate")
immediate.add("country_event",TagList().add("id","custom_difficulty.97"))
immediate.add("set_global_flag","custom_difficulty_easy")
et=TagList()
immediate.add(ET,et)
for cat in cats:
  for bonus in possibleBoniNames:
    bonusR=bonus.lower().replace(" ","_")
    if cat=="player":
      et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", "20"))
    # else:
    #   immediate.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", "0"))

# defaultIndex=-1
for name, values in zip(vanillaDefaultNames, vanillaDefault):
  # defaultIndex+=1
  newEvent=deepcopy(defaultEventTemplate)
  eventIndex+=1
  defaultEvents.add("country_event", newEvent)
  newEvent.replace("id","custom_difficulty.{:02d}".format(eventIndex))
  immediate=newEvent.get("immediate")
  immediate.add("country_event",TagList().add("id","custom_difficulty.98"))
  immediate.add("set_global_flag","custom_difficulty_"+name)
  et=TagList()
  immediate.add(ET,et)
  for cat in cats:
    for i,bonus in enumerate(possibleBoniNames):
      bonusR=bonus.lower().replace(" ","_")
      if cat=="ai" and i<vanillaAItoNPCIndex:
        et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(values[i])))
      elif cat=="leviathan" and i>=vanillaAItoNPCIndex:
        et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(values[i])))
      elif cat=="fe" and i>=vanillaAItoNPCIndex:
        et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(values[i])))
      # elif "yearly" in cat and (not name=="scaling" or not scaleDefault[i]):
      #   et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", "0"))
      elif "yearly" in cat and name=="scaling" and scaleDefault[i]:
        et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", "4"))
      elif cat!="player":
        et.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", "0"))

with open(outFolder+"/"+"custom_difficulty_defaults.txt",'w') as file:
  defaultEvents.writeAll(file, args())


staticModifiers=TagList()

updateFile=TagList()
updateFile.add("namespace","custom_difficulty")
updateEvent=TagList()
updateFile.add("country_event",updateEvent)

updateEvent.add("id", "custom_difficulty.9998")
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
  if catCountryType[catI]!="":
    limit.add("is_country_type", catCountryType[catI])
  if catNotCountryType[catI]!="":
    andTL=TagList()
    for entry in catNotCountryType[catI]:
      andTL.add("not", TagList().add("is_country_type", entry))
    limit.add("and",andTL)
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

  for bonus, bonusModifier in zip(possibleBoniNames,possibleBoniModifier):
    bonusR=bonus.lower().replace(" ","_")
    ifTagList.add("set_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", ET))
    if cat=="player":
      # switchTL=TagList()
      # afterIfTaglist.add("switch",switchTL)
      for sign in [1,-1]:
        if sign==1:
          compSign=">"
        else:
          compSign="<"
        for i in reversed(range(20)):
          ifGT=TagList()
          afterIfTaglist.add("if",ifGT)
          changeVal=10*(i+1)
          ifGT.add("limit", TagList().add("check_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(sign*(changeVal-0.1)),"",compSign)))
          if sign>0:
            modifierName="custom_difficulty_{}_{}_pos_player_value".format(i,bonusR)
          else:
            modifierName="custom_difficulty_{}_{}_neg_player_value".format(i,bonusR)
          modifier=TagList()
          if not isinstance(bonusModifier,list):
            bonusModifier=[bonusModifier]
          for modifierEntry in bonusModifier:
            modifier.add(modifierEntry,str(sign*changeVal/100))
            locList.append([modifierName,"Difficulty"])
          staticModifiers.add(modifierName,modifier)
          ifGT.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
          immediate.add("remove_modifier", modifierName)
          ifGT.add("change_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(-1*sign*changeVal)))
          # ifGT.add("break","yes")
    else:
      for sign in [1,-1]:
        if sign==1:
          compSign=">"
        else:
          compSign="<"
        for i in reversed(range(10)):
          ifGT=TagList()
          afterIfTaglist.add("if",ifGT)
          changeVal=pow(2,i)
          ifGT.add("limit", TagList().add("check_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(sign*(changeVal-0.1)),"",compSign)))
          if sign>0:
            modifierName="custom_difficulty_{}_{}_pos_value".format(i,bonusR)
          else:
            modifierName="custom_difficulty_{}_{}_neg_value".format(i,bonusR)
          modifier=TagList()
          if not isinstance(bonusModifier,list):
            bonusModifier=[bonusModifier]
          for modifierEntry in bonusModifier:
            modifier.add(modifierEntry,str(sign*changeVal/100))
            locList.append([modifierName,"Difficulty"])
          staticModifiers.add(modifierName,modifier)
          ifGT.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
          if cat=="ai": #only add onces as they all have the same name
            immediate.add("remove_modifier", modifierName)
          ifGT.add("change_variable",TagList().add("which","custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value", str(-1*sign*changeVal)))
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
yearlyFile.add("country_event", yearlyEvent)
yearlyEvent.add("id", "custom_difficulty_9990")
yearlyEvent.add("is_triggered_only",yes)
yearlyEvent.add("hide_window",yes)
trigger=TagList()
yearlyEvent.add("trigger",trigger)
trigger.add("has_country_flag","custom_difficulty_game_host")
#todo: host only
immediate=TagList()
yearlyEvent.add("immediate",immediate)
et=TagList()
immediate.add(ET, et)
cat="ai"
for bonus in possibleBoniNames:
  bonusR=bonus.lower().replace(" ","_")
  yearCountVar="custom_difficulty_{}_year_counter".format(bonusR)
  yearLimitVar="custom_difficulty_{}_{}_value".format(cat+"_yearly",bonusR)
  bonusVar="custom_difficulty_{}_{}_value".format(cat,bonusR)
  #todo: negative yearly!
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
  ifTagList.add("limit", TagList().add("not",TagList().add("check_variable", TagList().add("which", yearCountVar).add("value",yearLimitVar,"",">"))))
  ifTagList.add("set_variable", TagList().add("which", yearCountVar).add("value", "0"))
  ifTagList.add("change_variable", TagList().add("which", bonusVar).add("value", "-1"))

with open(outFolder+"/"+"custom_difficulty_yealy_event.txt",'w') as file:
  yearlyEvent.writeAll(file, args())


outFolderLoc="../gratak_mods/custom_difficulty/localisation/english"
if not os.path.exists(outFolderLoc):
  os.makedirs(outFolderLoc)

with io.open(outFolderLoc+"/custom_difficulty_l_english.yml",'w', encoding="utf-8") as file:
  file.write(u'\ufeff')
  file.write("l_english:\n")
  for locEntry in locList:
    file.write(" "+locEntry[0]+":0 "+'"'+locEntry[1]+'"\n')