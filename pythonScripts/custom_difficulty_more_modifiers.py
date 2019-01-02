#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList
import math
import custom_difficulty_files
import re

ETMM = "event_target:custom_difficulty_MM_var_storage"


eventNameSpace="custom_difficulty_mm.{!s}"
# name_randomDiffFireOnlyOnce="custom_difficulty.11"
name_gameStartFireOnlyOnce=eventNameSpace.format(0)
name_mainMenuEvent=eventNameSpace.format(1)

# t_notLockedTrigger=TagList("not", TagList("has_global_flag", "custom_difficulty_locked"))
# t_notLockedTrigger=TagList("custom_difficulty_allow_changes", "yes")
# t_mainMenuEvent=TagList("id",name_mainMenuEvent)
# t_rootUpdateEvent=TagList("id",name_rootUpdateEvent)
# t_backMainOption=TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name_mainMenuEvent)))
# t_closeOption=TagList("name", "custom_difficulty_close.name").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  # debugMode=False

  locList=LocList()

  groupList=loadFile(locList)
  mainFileContent=TagList()

  mainFileContent.add("namespace", eventNameSpace.format("")[:-1])
  mainFileContent.add("","","#game start init")
  gameStartInitEvent=mainFileContent.addReturn("country_event")
  gameStartInitEvent.add("id", name_gameStartFireOnlyOnce)
  gameStartInitEvent.add("title","custom_difficulty_init" )
  gameStartInitEvent.add("trigger", TagList("is_ai","no").add("not", TagList("has_global_flag", "custom_difficultyMM_active")))
  gameStartInitEvent.add("hide_window", "yes")
  immediate=TagList()
  gameStartInitEvent.add("immediate",immediate)
  # immediate.add_event("name_randomDiffFireOnlyOnce")
  immediate.add("set_country_flag", "custom_difficulty_game_host")
  immediate.add("random_planet", TagList("save_global_event_target_as", "custom_difficultyMM_var_storage"))
  gameStartAfter=TagList()
  gameStartInitEvent.add("after",TagList("hidden_effect", gameStartAfter))
  gameStartAfter.add("set_global_flag", "custom_difficultyMM_active")


  mainFileContent.add("","","#more modifiers main event")
  mainMenuEvent=mainFileContent.addReturn("country_event")
  mainMenuEvent.add("id", name_mainMenuEvent)
  mainMenuEvent.add("title","test" )
  mainMenuEvent.add("picture","GFX_evt_synth_sabotage" )
  for group in groupList:
    option=mainMenuEvent.addReturn("option")
    option.add("name", group.name)

  onActions=TagList()
  onActions.add("on_game_start_country", TagList("events",TagList().add(name_gameStartFireOnlyOnce),"#set flag,set event target, start default events, start updates for all countries"))
  # onActions.add("on_game_start", TagList("events",TagList().add(name_rootUpdateEvent))) #is called by "fire only once"
  custom_difficulty_files.outputToFolderAndFile(onActions, "common/on_actions", "custom_difficultyMM_on_action.txt",2,"../gratak_mods/custom_difficultyMM")


  custom_difficulty_files.outputToFolderAndFile(mainFileContent , "events", "custom_difficultyMM_main.txt" ,2,"../gratak_mods/custom_difficultyMM")
  locList.writeToMod("../gratak_mods/custom_difficultyMM","custom_difficultyMM")


def loadFile(locList):
  currentGroup=None
  groupList=[]
  inSubGroup=0
  currentSubGroup=None
  currentModifier=None
  with open("MM_modifierLists.txt",'r') as file:
    for line in file:
      if "#" in line:
        line=line[:line.index("#")]
      line=line.strip()
      if line=="":
        if currentGroup:
          # groupList.append(currentGroup)
          currentGroup=None
        continue
      lineSplit=re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)
      if currentGroup==None:
        currentGroup=ModifierGroup(lineSplit[0].strip('"'),locList)
        groupList.append(currentGroup)
        continue
      if lineSplit[0].startswith('"'):
        if inSubGroup!=0:
          print("Error: SubGroup within subgroup not possible! Line: {!s}".format(line))
          sys.exit(1)
        currentSubGroup=ModifierSubGroup(lineSplit[0].strip('"'))
        currentGroup.add(currentSubGroup)
        inSubGroup=int(lineSplit[1])
        continue
      currentModifier=Modifier(lineSplit[0])
      if inSubGroup:
        currentSubGroup.addModifier(currentModifier)
        inSubGroup-=1
      else:
        currentGroup.add(currentModifier)
      for extraProperty in lineSplit[1:]:
        if extraProperty.startswith('"'):
          currentModifier.addToName(extraProperty)
        else:
          currentModifier.addMultiplier(extraProperty)
  return groupList

  # test=TagList()
  # locTest=LocList()
  # for mod in groupList[-1].modifiers:
  #   mod.toStaticModifierFiles(test,locTest)
  # # groupList[0].modifiers[0].toStaticModifierFiles(test, locTest)
  # print(test)
  # locTest.write("test.yml","en")



      # print(lineSplit)
  # if currentGroup: #no extra line at end of file
  #   groupList.append(currentGroup)

class ModifierGroup:
  def __init__(self, name, locList):
    self.name="custom_difficulty_mm_group_"+name.replace(" ","_").replace("$","")
    self.modifiers=[]
    locList.append(self.name, name)
  def add(self, modifier):
    self.modifiers.append(modifier)

class Modifier:
  def __init__(self, modifier):
    # self.name=name
    percentDefault=10
    self.modifier=modifier.lower()
    self.multiplier=percentDefault 
    self.unit="%"
    if "_cost" in modifier or "_upkeep" in modifier:
      self.multiplier*=-1
    if "_add" in modifier:
      self.unit="1"
      self.multiplier/=percentDefault
    self.name="$MOD_"+modifier.upper()+"$"

  def addMultiplier(self, mult):
    mult=float(mult)
    self.multiplier*=mult

  def addToName(self, extra):
    self.name+=extra

  def __str__(self):
    return "Mod: {}, Name: {}, Mult: {!s}, Unit: {}".format(self.modifier, self.name, self.multiplier,self.unit)
  def __repr__(self):
    return self.__str__()+"\n"


  def toStaticModifierFiles(self, modifierTagList, locClass, rangeUsed=range(-2,11)):
    value=self.multiplier;
    if self.unit=="%":
      value/=100
    elif self.unit!="" and self.unit!="1":
      print("ERROR: INVALID UNIT")

    for m in rangeUsed:
      if m==0:
        continue
      if not locClass is None:
        modName="custom_difficulty_MM_{}_{!s}".format(self.modifier, m)
        modifierList=modifierTagList.addReturn(modName)
        locClass.append(modName, "$FE_DIFFICULTY$: "+self.name)
      else:
        modifierList=modifierTagList #used by ModifierSubGroup
      modifierList.add(self.modifier,"{:.3f}".format(value*m) )



class ModifierSubGroup(Modifier):
  def __init__(self, name=''):
    self.name=name
    self.modifiers=[]
    # self.multiplier=multiplier
  def addModifier(self, modifier):
    self.modifiers.append(modifier)
  def __str__(self):
    out="Group Name: {}, ".format(self.name)
    for mod in self.modifiers:
      out+="\n\t"+str(mod)
    return out
  def __repr__(self):
    return self.__str__()+"\n"


  def toStaticModifierFiles(self, modifierTagList, locClass, rangeUsed=range(-2,11)):
    for m in rangeUsed:
      if m==0:
        continue
      modName="custom_difficulty_MM_{}_{!s}".format(self.name.replace(" ","_"), m)
      modifierList=modifierTagList.addReturn(modName)
      locClass.append(modName, "$FE_DIFFICULTY:$"+self.name)
      for mod in self.modifiers:
        mod.toStaticModifierFiles(modifierList,None, range(m,m+1))

if __name__ == "__main__":
  main()

