#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList

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
name_removeOLDModifiers="custom_difficulty_old.{}".format(id_removeModifiers+9)
id_addModifiers=80  #reserved range up to 82
id_addGroupModifiers=83  #reserved range up to 85
id_defaultEvents=100 #reserved range up to 199
id_ChangeEvents=1000 #reserved range up to 9999
id_subChangeEvents=10

oldFolder="../gratak_mods/custom_difficulty_beta"
newFolder="../gratak_mods/custom_difficulty"
oldEvents=TagList("namespace", "custom_difficulty_old")
# with open() as file:
modifiers=TagList().readFile(oldFolder+"/common/static_modifiers/custom_difficulty_static_modifiers.txt",0)

removeOldModifiers=TagList("id", name_removeOLDModifiers)
oldEvents.add("country_event", removeOldModifiers)
removeOldModifiers.add("is_triggered_only", "yes")
removeOldModifiers.add("hide_window", "yes")
immediate=TagList()
removeOldModifiers.add("immediate", immediate)
for name, val in modifiers.getNameVal():
	if name:
		immediate.add("remove_modifier", name)

with open(oldFolder+"/events/custom_difficulty_remove_old.txt",'w') as file:
	oldEvents.writeAll(file)
# with open(newFolder+"/events/custom_difficulty_remove_old.txt",'w') as file:
# 	oldEvents.writeAll(file)


locList=LocList()
locList.addLoc("newVersion", "New Mod Version Available")
locList.addLoc("newVersionDesc1","The release version of this mod is now on Steam:")
locList.addLoc("newVersionDesc2","Due to major changes in modifiers and other functions, a reset of the mod settings is required to update. "
	+"You can choose whether to update now or to finish your game first. I'm very sure the update is save, but you will have to configure the difficulty anew. "
	+"If you want to update, click the reset option, save and close the game, activate the new version of the mod and deactivate the beta. "
	+"Then you can start the game again and load this save-game. You should be greeted by the new mod welcome screen after unpausing.")
locList.addLoc("newVersionreset","Remove")
locList.addLoc("newVersionresetDesc","There will be no more difficulty modifiers until you deactivate this beta version of")
locList.addLoc("newVersionresetDesc2","You'll then have to activate the release Version of")
locList.addLoc("newVersionresetDesc3","to have custom difficulty modifiers again.")
locList.addLoc("finishThisGame","I want to complete my game first!")
locList.addLoc("finishThisGameDesc","If you change your mind, the reset can also be called from the Menu.")

locList.addEntry("custom_difficulty_new_version", "Dynamic Difficulty - @newVersion")
locList.addEntry("custom_difficulty_new_version.desc", "@newVersionDesc1 'Dynamic Difficulty - Ultimate Customization'. @newVersionDesc2")
locList.addEntry("custom_difficulty.resetSaveExit", "@newVersionreset Dynamic Difficulty Beta")
locList.addEntry("custom_difficulty.resetSaveExit.desc", "@newVersionresetDesc Dynamic Difficulty! @newVersionresetDesc2 'Dynamic Difficulty - Ultimate Customization' @newVersionresetDesc3")
locList.addEntry("custom_difficulty.finishThisGame", "@finishThisGame")
locList.addEntry("custom_difficulty.finishThisGame.desc", "@finishThisGameDesc")


locList2=deepcopy(locList)
for language in locList.languages:
  outFolderLoc="../gratak_mods/custom_difficulty_beta/localisation/"+language
  if not os.path.exists(outFolderLoc):
    os.makedirs(outFolderLoc)
  locList.write(outFolderLoc+"/custom_difficulty_change_version_l_"+language+".yml",language)

locList2.translateRest=True
for language in locList2.languages:
  outFolderLoc="../gratak_mods/custom_difficulty_translate/localisation/"+language
  if not os.path.exists(outFolderLoc):
    os.makedirs(outFolderLoc)
  locList2.write(outFolderLoc+"/custom_difficulty_change_version_l_"+language+".yml",language)
