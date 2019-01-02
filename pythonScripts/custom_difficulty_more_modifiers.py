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
name_rootUpdateEvent=eventNameSpace.format(2)
id_groupEvents=10 #reserved to 19
id_modifierEventMenus=100 #reserved to 199

# t_notLockedTrigger=TagList("not", TagList("has_global_flag", "custom_difficulty_locked"))
# t_notLockedTrigger=TagList("custom_difficulty_allow_changes", "yes")
# t_mainMenuEvent=TagList("id",name_mainMenuEvent)
t_rootUpdateEvent=TagList("id",name_rootUpdateEvent)
# t_backMainOption=TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name_mainMenuEvent)))
# t_closeOption=TagList("name", "custom_difficulty_close.name").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

t_backMainOption=TagList("name","custom_difficulty_backMM").add("hidden_effect", TagList("country_event",TagList("id", custom_difficulty_files.name_mainMenuEvent)))
t_closeOption=TagList("name", "custom_difficulty_closeMM").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  # debugMode=False

  locList=LocList()
  custom_difficulty_files.globalAddLocs(locList)

  #TODO: File that is overwritten by standard DD that makes sure there is a reduced main menu

  groupList=loadFile(locList)

  mainFileContent=TagList("namespace", eventNameSpace.format("")[:-1])
  staticModifierFile=TagList()
  # groupFileContent=TagList("namespace", eventNameSpace.format("")[:-1])
  modifierMenuFileContent=TagList("namespace", eventNameSpace.format("")[:-1])





  locList.addEntry("custom_difficulty_backMM", "@back")
  locList.addEntry("custom_difficulty_closeMM", "@close @modName @menu")
  locList.addEntry("custom_difficulty_choose_descMM", "@choose")



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
  mainMenuEvent.add("is_triggered_only", "yes")
  mainMenuEvent.add("title","custom_difficulty_MM" )
  mainMenuEvent.add("desc", "custom_difficulty_choose_descMM")
  locList.append("custom_difficulty_MM", "Dynamic Difficulty - More Modifiers")
  mainMenuEvent.add("picture","GFX_evt_synth_sabotage" )

  mainFileContent.add("","","#more modifiers update event")
  updateEvent=mainFileContent.addReturn("country_event")
  updateEvent.add("id", name_rootUpdateEvent)
  updateEvent.add("hide_window","yes" )
  updateEvent.add("is_triggered_only", "yes")


  curIdGroupEvent=id_groupEvents
  curIdModifierEvent=id_modifierEventMenus
  for group in groupList:
    option=mainMenuEvent.addReturn("option")
    option.add("name", group.name)
    callEvent=option.addReturn("hidden_effect")
    groupEvent=mainFileContent.addReturn("country_event")
    groupEvent.add("id", eventNameSpace.format(curIdGroupEvent))
    groupEvent.add("is_triggered_only", "yes")
    groupEvent.add("title",group.name )
    groupEvent.add("desc", "custom_difficulty_choose_descMM") #todo: change to display of current bonuses
    groupEvent.add("picture","GFX_evt_synth_sabotage" )
    callEvent.createEvent(eventNameSpace.format(curIdGroupEvent))
    for modifier in group.modifiers:
      modifierName=modifier.toStaticModifierFiles(staticModifierFile, locList)
      option=groupEvent.addReturn("option")
      option.add("name", modifierName)
      callEvent=option.addReturn("hidden_effect")
      modifierEvent=modifierMenuFileContent.addReturn("country_event")
      modifierEvent.add("id", eventNameSpace.format(curIdModifierEvent))
      modifierEvent.add("is_triggered_only", "yes")
      modifierEvent.add("title",modifierName )
      modifierEvent.add("desc", "change_bonusTODO")
      modifierEvent.add("picture","GFX_evt_synth_sabotage" )
      callEvent.createEvent(eventNameSpace.format(curIdModifierEvent))
      modifierEvent.addReturn("option").add("name", "custom_difficulty_backMM").createEvent( eventNameSpace.format(curIdGroupEvent))
      modifierEvent.add("option",t_closeOption)
      curIdModifierEvent+=1



    groupEvent.addReturn("option").add("name", "custom_difficulty_backMM").createEvent(name_mainMenuEvent)
    groupEvent.add("option",t_closeOption)
    curIdGroupEvent+=1


  mainMenuEvent.add("option",t_backMainOption)
  mainMenuEvent.add("option",t_closeOption)








  onActions=TagList("on_game_start_country", TagList("events",TagList().add(name_gameStartFireOnlyOnce),"#set flag,set event target, start default events, start updates for all countries"))
  #OUTPUT TO FILE
  custom_difficulty_files.outputToFolderAndFile(onActions, "common/on_actions", "custom_difficultyMM_on_action.txt",2,"../gratak_mods/custom_difficultyMM")
  custom_difficulty_files.outputToFolderAndFile(mainFileContent , "events", "custom_difficultyMM_main.txt" ,2,"../gratak_mods/custom_difficultyMM")
  custom_difficulty_files.outputToFolderAndFile(modifierMenuFileContent , "events", "custom_difficultyMM_modifier_menus.txt" ,2,"../gratak_mods/custom_difficultyMM")
  custom_difficulty_files.outputToFolderAndFile(staticModifierFile , "common/static_modifiers", "custom_difficultyMM.txt" ,2,"../gratak_mods/custom_difficultyMM")
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
        if extraProperty=="%":
          currentModifier.setUnit("%")
        elif extraProperty.startswith('"'):
          currentModifier.changeName(extraProperty.strip('"'))
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
    self.name="custom_difficulty_mm_group_"+name.replace(" ","_").replace("$","").lower()
    self.modifiers=[]
    locList.append(self.name, "§B"+name+"§!")
  def add(self, modifier):
    self.modifiers.append(modifier)

class Modifier:
  def __init__(self, modifier):
    # self.name=name
    # percentDefault=10
    modifier=modifier.lower()
    self.modifier=modifier
    self.multiplier=1
    self.unit="1"
    if "_cost" in modifier or "_upkeep" in modifier:
      self.multiplier*=-1
    # if "_add" in modifier:
    #   self.unit="1"
    #   self.multiplier/=percentDefault
    #   print(modifier)
    if "_mult" in modifier:
      self.setUnit("%")
    self.name="$MOD_"+modifier.upper()+"$"
    self.name+="$mod_"+modifier.lower()+"$" #some are lower, some are upper. Game does not complain if something misses so I just add both...

  def addMultiplier(self, mult):
    mult=float(mult)
    self.multiplier*=mult

  def changeName(self, extra):
    self.name=extra.replace("<this>",self.name)
    # self.name+=extra

  def setUnit(self,unit):
    self.unit=unit
    if unit=="%":
      self.multiplier*=10 #default percent value

  def __str__(self):
    return "Mod: {}, Name: {}, Mult: {!s}, Unit: {}".format(self.modifier, self.name, self.multiplier,self.unit)
  def __repr__(self):
    return self.__str__()+"\n"


  def toStaticModifierFiles(self, modifierTagList, locList, rangeUsed=range(-2,11)):
    value=self.multiplier;
    if self.unit=="%":
      value/=100
    elif self.unit!="" and self.unit!="1":
      print("ERROR: INVALID UNIT")


    for m in rangeUsed:
      if m==0:
        continue
      if not locList is None:
        modName="custom_difficulty_MM_mod_{}_{!s}".format(self.modifier, m)
        modifierList=modifierTagList.addReturn(modName)
        locList.append(modName, "$FE_DIFFICULTY$: "+self.name)
      else:
        modifierList=modifierTagList #used by ModifierSubGroup
      modifierList.add(self.modifier,"{:.3f}".format(value*m) )

    if not locList is None:
      modOptionName="custom_difficulty_MM_mod_{}".format(self.modifier)
      locList.append(modOptionName, "§B"+self.name+"§!")
      return modOptionName


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


  def toStaticModifierFiles(self, modifierTagList, locList, rangeUsed=range(-2,11)):
    for m in rangeUsed:
      if m==0:
        continue
      modName="custom_difficulty_MM_{}_{!s}".format(self.name.replace(" ","_"), m)
      modifierList=modifierTagList.addReturn(modName)
      locList.append(modName, "$FE_DIFFICULTY:$"+self.name)
      for mod in self.modifiers:
        mod.toStaticModifierFiles(modifierList,None, range(m,m+1))
    modOptionName="custom_difficulty_MM_mod_{}".format(self.name.replace(" ","_"))
    locList.append(modOptionName, "§B"+self.name+"§!")
    return modOptionName

if __name__ == "__main__":
  main()

