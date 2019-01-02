#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList
import math
import custom_difficulty_files as cdf
import re

ETMM = "event_target:custom_difficulty_MM_var_storage"


eventNameSpace="custom_difficulty_mm.{!s}"
# name_randomDiffFireOnlyOnce="custom_difficulty.11"
name_gameStartFireOnlyOnce=eventNameSpace.format(0)
name_mainMenuEvent=eventNameSpace.format(1)
name_rootUpdateEvent=eventNameSpace.format(2)
id_groupEvents=10 #reserved to 19
id_updateEvents=20 #reserved to 21
id_modifierEventMenus=100 #reserved to 199

# t_notLockedTrigger=TagList("not", TagList("has_global_flag", "custom_difficulty_locked"))
# t_notLockedTrigger=TagList("custom_difficulty_allow_changes", "yes")
# t_mainMenuEvent=TagList("id",name_mainMenuEvent)
t_rootUpdateEvent=TagList("id",name_rootUpdateEvent)
# t_backMainOption=TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name_mainMenuEvent)))
# t_closeOption=TagList("name", "custom_difficulty_close.name").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

t_backMainOption=TagList("name","custom_difficulty_backMM").add("hidden_effect", TagList("country_event",TagList("id", cdf.name_mainMenuEvent)))
t_closeOption=TagList("name", "custom_difficulty_closeMM").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  # debugMode=False
  #todo: make normal custom difficulty leave menu event call MM update and vise versa

  locList=LocList()
  cdf.globalAddLocs(locList)

  #TODO: File that is overwritten by standard DD that makes sure there is a reduced main menu

  groupList=loadFile(locList)

  mainFileContent=TagList("namespace", eventNameSpace.format("")[:-1])
  staticModifierFile=TagList()
  # groupFileContent=TagList("namespace", eventNameSpace.format("")[:-1])
  modifierMenuFileContent=TagList("namespace", eventNameSpace.format("")[:-1])
  updateFileContent=TagList("namespace", eventNameSpace.format("")[:-1])





  locList.addEntry("custom_difficulty_backMM", "@back")
  locList.addEntry("custom_difficulty_closeMM", "@close @modName @menu")
  locList.addEntry("custom_difficulty_choose_descMM", "@choose")
  locList.addEntry("custom_difficulty_current_bonusesMM","@curBon:")



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
  immediate.add("random_planet", TagList("save_global_event_target_as", "custom_difficulty_MM_var_storage"))
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
  updateImmediate=updateEvent.addReturn("immediate")
  isPlayable=updateImmediate.addReturn("every_country").add("limit",TagList("OR", TagList("is_country_type","default").add("is_country_type","fallen_empire" ).add("is_country_type","awakened_fallen_empire" ).add("is_country_type","ascended_empire" )))
  isPlayable.createReturnIf(TagList("is_ai", "yes")).createEvent(eventNameSpace.format(id_updateEvents))
  isPlayable.addReturn("else").createEvent(eventNameSpace.format(id_updateEvents+1))

  curIdGroupEvent=id_groupEvents
  curIdModifierEvent=id_modifierEventMenus
  for group in groupList:
    option=mainMenuEvent.addReturn("option")
    option.add("name", group.name)
    option.addReturn("hidden_effect").createEvent(eventNameSpace.format(curIdGroupEvent))
    groupEvent=mainFileContent.addReturn("country_event")
    groupEvent.add("id", eventNameSpace.format(curIdGroupEvent))
    groupEvent.add("is_triggered_only", "yes")
    groupEvent.add("title",group.name )
    # groupEvent.add("desc", "custom_difficulty_choose_descMM") #todo: change to display of current bonuses
    desc=groupEvent.addReturn("desc")
    desc=desc.addReturn("trigger")
    desc.add("text", "custom_difficulty_current_bonusesMM")
    groupEvent.add("picture","GFX_evt_synth_sabotage" )
    for modifier in group.modifiers:
      modifierName=modifier.toStaticModifierFiles(staticModifierFile, locList)
      option=groupEvent.addReturn("option")
      option.add("name", modifierName)
      option.addReturn("hidden_effect").createEvent(eventNameSpace.format(curIdModifierEvent))
      modifierEvent=modifierMenuFileContent.addReturn("country_event")
      modifierEvent.add("id", eventNameSpace.format(curIdModifierEvent))
      modifierEvent.add("is_triggered_only", "yes")
      modifierEvent.add("title",modifierName )
      modifierEvent.add("desc",TagList("trigger",desc ))
      modifierEvent.add("picture","GFX_evt_synth_sabotage" )

      for who in ["AI", "Player", "Both"]:
        for amount in [5,1,-1,-5]:
          addChangeOption(modifierEvent, modifier, modifierName, amount, who, locList)
      # addChangeOption(modifierEvent, modifier, modifierName, 5, "AI", locList)
      # addChangeOption(modifierEvent, modifier, modifierName, -1, "Player", locList)
      
      # successText=TagList().add("text","custom_difficulty_locked.name").add("custom_difficulty_allow_changes", "no") #TODO!
      # trigger.add("success_text",successText)
      for category in ["AI", "Player"]:
        for comp in ["<",">"]:
          if (modifier.multiplier<0) == (comp=="<"):
            color="G" #checking smaller than zero and negative is good or checking larger and negativ is bad
          else:
            color="R"
          name="custom_difficulty_MM_{}_{}_curVal_{}".format(modifierName, category,color)
          desc.add("success_text", TagList("text", name).add(ETMM, cdf.variableOpNew("check", modifierName+"_"+category, 0,comp)))
          # desc.add("success_text", TagList("text", name).add(ETMM, TagList("NOT",cdf.variableOpNew("check", modifierName+"_"+category, 0,"="))))
          locList.append(name, "${1}$: §{4}[{0}.{1}_{2}]{3} @for{2}§!".format(ETMM, modifierName, category, modifier.unit, color))


      modifierEvent.addReturn("option").add("name", "custom_difficulty_backMM").createEvent( eventNameSpace.format(curIdGroupEvent))
      modifierEvent.add("option",t_closeOption)
      curIdModifierEvent+=1



    groupEvent.addReturn("option").add("name", "custom_difficulty_backMM").createEvent(name_mainMenuEvent)
    groupEvent.add("option",t_closeOption)
    curIdGroupEvent+=1


  mainMenuEvent.add("option",t_backMainOption)
  mainMenuEvent.add("option",t_closeOption)

  cur_id_updateEvents=id_updateEvents
  for category in ["AI", "Player"]:
    localUpdateEvent=updateFileContent.addReturn("country_event")
    localUpdateEvent.add("id", eventNameSpace.format(cur_id_updateEvents))
    localUpdateEvent.addComment(category)
    localUpdateEvent.add("hide_window","yes" )
    localUpdateEvent.add("is_triggered_only", "yes")
    localUpdateImmediate=localUpdateEvent.addReturn("immediate")
    etUpdate=localUpdateImmediate.addReturn(ETMM)

    if category=="AI":
      localUpdateImmediate.variableOp("set", "custom_difficulty_randomness_factor",1)
      localUpdateImmediate.variableOp("set", "custom_difficulty_tmp","custom_difficulty_random_handicap")
      localUpdateImmediate.variableOp("multiply", "custom_difficulty_tmp","custom_difficulty_random_handicap_perc")
      localUpdateImmediate.variableOp("divide", "custom_difficulty_tmp",100*20) #100 for from perc, 20 as max handicap
      localUpdateImmediate.variableOp("subtract", "custom_difficulty_randomness_factor","custom_difficulty_tmp")

    for group in groupList:
      for modifier in group.modifiers:
        etUpdate.variableOp("set", modifier.modifiername, modifier.modifiername+"_"+category)
        someThingChanged=localUpdateImmediate.createReturnIf(TagList("NOT",cdf.variableOpNew("check", modifier.modifiername, ETMM)))
        someThingChanged.variableOp("set", modifier.modifiername, ETMM)
        removeOld=TagList()
        addNew=TagList("if", TagList("limit",cdf.variableOpNew("check", modifier.modifiername,0)))
        # addNew=cdf.createReturnIf(TagList(), cdf.variableOpNew("check", modifier.modifiername,0))
        # addNewCur=addNew
        # addNew=cdf.createReturnIf(TagList(),TagList("NOT", cdf.variableOpNew("check", modifier.modifiername,0)))
        for r,name in zip(modifier.rangeUsed, modifier.modNames):
          removeOld.add("remove_modifier", name)
          elseif=addNew.addReturn("else_if")
          value=modifier.multiplier*(r+0.5)
          value="{:.3f}".format(value)
          if modifier.multiplier>0:
            comp="<"
          else:
            comp=">"
          elseif.add("limit", cdf.variableOpNew("check", modifier.modifiername, value,comp))
          elseif.add("add_modifier", TagList("modifier", name).add("days",-1))
        someThingChanged.addTagList(removeOld)
        someThingChanged.addTagList(addNew)

        #TODO: remove existing modifiers

    cur_id_updateEvents+=1








  onActions=TagList("on_game_start_country", TagList("events",TagList().add(name_gameStartFireOnlyOnce),"#set flag,set event target, start default events, start updates for all countries"))
  #OUTPUT TO FILE
  cdf.outputToFolderAndFile(onActions, "common/on_actions", "custom_difficultyMM_on_action.txt",2,"../gratak_mods/custom_difficultyMM")
  cdf.outputToFolderAndFile(mainFileContent , "events", "custom_difficultyMM_main.txt" ,2,"../gratak_mods/custom_difficultyMM")
  cdf.outputToFolderAndFile(modifierMenuFileContent , "events", "custom_difficultyMM_modifier_menus.txt" ,2,"../gratak_mods/custom_difficultyMM")
  cdf.outputToFolderAndFile(updateFileContent , "events", "custom_difficultyMM_modifier_update.txt" ,2,"../gratak_mods/custom_difficultyMM")
  cdf.outputToFolderAndFile(staticModifierFile , "common/static_modifiers", "custom_difficultyMM.txt" ,2,"../gratak_mods/custom_difficultyMM")
  locList.writeToMod("../gratak_mods/custom_difficultyMM","custom_difficultyMM")

def addChangeOption(event, modifier, modifierName, amount, category, locList):
  option=event.addReturn("option")
  # if isinstance(modifier, Modifier):
  name="custom_difficulty_change_{}_{!s}_{}".format(modifierName,amount, category)
  option.add("name",name)
  val=amount*modifier.multiplier
  forWhom="@for"
  if category=="Both":
    forWhom+="AI + @Player"
    categories=["AI", "Player"]
  else:
    forWhom+=category
    categories=[category]
  if amount<0:
    color="R"
  else:
    color="G"
  if val<0:
    locList.append(name,"§{}@decrease ${}$ @by {:g}{} {}§!".format(color,modifierName,-val, modifier.unit, forWhom) )
  else:
    locList.append(name,"§{}@increase ${}$ @by {:g}{} {}§!".format(color,modifierName,val, modifier.unit, forWhom) )

  trigger=option.addReturn("trigger").addReturn(ETMM)
  effect=option.addReturn("hidden_effect")
  et=effect.addReturn(ETMM)

  for category in categories:
    if amount>0:
      limit=modifier.rangeUsed[-1]
      # trigger.variableOp("check", modifierName+"_"+category, modifier.rangeUsed[-1]-amount+1, "<")
    else:
      limit=modifier.rangeUsed[0]
    if val<0:
      comp=">"
    else:
      comp="<"
    # trigger.variableOp("check", modifierName+"_"+category, modifier.rangeUsed[0]-amount-1, ">")
    trigger.variableOp("check", modifierName+"_"+category, "{:.3f}".format((limit*modifier.multiplier-val)*1.01), comp)


    et.variableOp("change",modifierName+"_"+category,val)
  effect.createEvent(event.get("id"))


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
    self.unit=""
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
    # self.values=[]
    self.modNames=[]

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
    if 0 in rangeUsed:
      rangeUsed=list(rangeUsed)
      rangeUsed.remove(0)
    self.rangeUsed=rangeUsed
    value=self.multiplier;
    if self.unit=="%":
      value/=100
    elif self.unit!="" and self.unit!="1":
      print("ERROR: INVALID UNIT")

    
    
    for m in rangeUsed:
      # if m==0:
      #   continue
      if not locList is None:
        modName="custom_difficulty_MM_mod_{}_{!s}".format(self.modifier, m)
        self.modNames.append(modName)
        modifierList=modifierTagList.addReturn(modName)
        locList.append(modName, "$FE_DIFFICULTY$: "+self.name)
      else:
        modifierList=modifierTagList #used by ModifierSubGroup
      # self.values.append("{:.3f}".format(value*m))
      modifierList.add(self.modifier,"{:.3f}".format(value*m) )

    if not locList is None:
      modOptionName="custom_difficulty_MM_mod_{}".format(self.modifier)
      locList.append(modOptionName, "§B"+self.name+"§!")
      self.modifiername=modOptionName
      return modOptionName


class ModifierSubGroup(Modifier):
  def __init__(self, name=''):
    self.name=name
    self.modifiers=[]
    self.modNames=[]
    # self.multiplier=multiplier
  def addModifier(self, modifier):
    self.modifiers.append(modifier)
    self.multiplier=modifier.multiplier
    self.unit=modifier.unit
    # self.values=modifier.values
  def __str__(self):
    out="Group Name: {}, ".format(self.name)
    for mod in self.modifiers:
      out+="\n\t"+str(mod)
    return out
  def __repr__(self):
    return self.__str__()+"\n"


  def toStaticModifierFiles(self, modifierTagList, locList, rangeUsed=range(-2,11)):
    if 0 in rangeUsed:
      rangeUsed=list(rangeUsed)
      rangeUsed.remove(0)
    self.rangeUsed=rangeUsed
    for m in rangeUsed:
      if m==0:
        continue
      modName="custom_difficulty_MM_{}_{!s}".format(self.name.replace(" ","_"), m)
      self.modNames.append(modName)
      modifierList=modifierTagList.addReturn(modName)
      locList.append(modName, "$FE_DIFFICULTY:$"+self.name)
      for mod in self.modifiers:
        mod.toStaticModifierFiles(modifierList,None, range(m,m+1))
    modOptionName="custom_difficulty_MM_mod_{}".format(self.name.replace(" ","_"))
    locList.append(modOptionName, "§B"+self.name+"§!")
    self.modifiername=modOptionName
    return modOptionName

if __name__ == "__main__":
  main()

