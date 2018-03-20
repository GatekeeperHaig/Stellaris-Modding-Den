#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
from stellarisTxtRead import *

changeSteps = [50, 25, 10, 5, 1]
for s in reversed(changeSteps):
  changeSteps.append(-s)
possibleBoniNames=["Minerals", "Energy","Food", "Research", "Unity", "Influence", "Naval capacity", "Weapon Damage", "Hull","Armor","Shield","Upkeep"]
possibleBoniModifier=["country_resource_minerals_mult", "country_resource_energy_mult","country_resource_influence_mult", "country_resource_food_mult", "all_technology_research_speed", "country_resource_unity_mult","","ship_weapon_damage","ship_hull_mult","ship_armor_mult","ship_shield_mult",["country_ship_upkeep_mult","country_building_upkeep_mult","country_starbase_upkeep_mult","country_army_upkeep_mult"]]
possibleBoniIcons=["£minerals","£energy", "£food", "£physics££society££engineering","£unity", "£influence","","","","","",""]
possibleBoniColor=["P","Y","G","L","E","B","W","T","G","H","B","T"]
boniListNames=["General income", "All ship bonuses"]
boniListEntries=[[0,1,2,3,4], [6,7,8,9]]
cats=["ai","fe","leviathan","player"]
catNames=["AI Custom Empire", "Fallen and Awakened Empires", "Leviathans", "Player"]
locList=[]
locList.append(["custom_difficulty.current_bonuses", "Current Bonuses"])
locList.append(["custom_difficulty.back", "Back"])
locList.append(["close_custom_difficulty.name", "Close Custom Difficulty menu"])

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
  locList.append(["custom_difficulty_{}.name".format(cat),"Change {} bonuses".format(catNames[mainIndex-1])])
  trigger=TagList()
  choiceEvent.add("desc", TagList().add("trigger",trigger))
  trigger.add("text", "custom_difficulty.current_bonuses") #loc global
  trigger.add("text", "newline")

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
    checkVar=TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusR)).add("value","0")
    trigger.add("fail_text",TagList().add("text","custom_difficulty_{}_{}_desc".format(cat,bonusR)).add("check_variable", checkVar))
    locList.append(["custom_difficulty_{}_{}_desc".format(cat,bonusR),"{} §{}{} : [root.custom_difficulty_{}_{}_value]% ".format(possibleBoniIcons[bonusI], possibleBoniColor[bonusI], bonus, cat,bonusR)])

    #stuff that is added here will be output AFTER all trigger (as the whole trigger is added before the loop)
    option=TagList().add("name", "custom_difficulty_{}_change_{}.name".format(cat,bonusR))
    locList.append(["custom_difficulty_{}_change_{}.name".format(cat,bonusR), "Change {} bonus".format(bonus)])
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
    bonus=bonus.lower().replace(" ","_")
    changeEvent=TagList()
    tagList.add("country_event", changeEvent)
    changeEvent.add("id","custom_difficulty.{:01d}{:02d}0".format(mainIndex,bonusIndex))
    changeEvent.add("is_triggered_only", yes)
    changeEvent.add("title","custom_difficulty_{}_change_{}.name".format(cat,bonus)) #loc same as on the button
    changeEvent.add("desc", TagList().add("trigger",trigger)) #same desc trigger as above?

    for changeStep in changeSteps:
      if cat=="player" and (abs(changeStep)==1 or abs(changeStep)==5 or abs(changeStep)==25):
        continue
      if changeStep>0:
        option=TagList().add("name","custom_difficulty_{}_increase_{!s}".format(bonus, changeStep))
        if mainIndex==1:
          locList.append(["custom_difficulty_{}_increase_{!s}".format(bonus, changeStep), "Increase {} by {}%".format(bonus, changeStep)])
      else:
        option=TagList().add("name","custom_difficulty_{}_decrease_{!s}".format(bonus, -changeStep))
        if mainIndex==1:
          locList.append(["custom_difficulty_{}_decrease_{!s}".format(bonus, -changeStep), "Decrease {} by {}%".format(bonus, -changeStep)])

      hidden_effect=TagList()
      if bonusIndex>len(boniListNames):
        hidden_effect.add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonus)).add("value",str(changeStep)))
      else:
        for bonusListIndex in boniListEntries[bonusIndex-1]:
          bonusListValue=possibleBoniNames[bonusListIndex].lower().replace(" ","_")
          hidden_effect.add("change_variable", TagList().add("which", "custom_difficulty_{}_{}_value".format(cat,bonusListValue)).add("value",str(changeStep)))
      hidden_effect.add("country_event", TagList().add("id","custom_difficulty.{:01d}{:02d}0".format(mainIndex,bonusIndex)))
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

outFolder="../gratak_mods/custom_difficulty/localisation/english"
if not os.path.exists(outFolder):
  os.makedirs(outFolder)
with open(outFolder+"/custom_difficulty_l_english.yml",'w') as file:
  file.write(u'\ufeff')
  file.write("l_english:\n")
  for locEntry in locList:
    file.write(" "+locEntry[0]+":0 "+'"'+locEntry[1]+'"\n')



