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


ETMM = "event_target:custom_difficulty_MM_var_storage"


eventNameSpace="custom_difficultyMM.{!s}"
# name_randomDiffFireOnlyOnce="custom_difficulty.11"
name_gameStartFireOnlyOnce=eventNameSpace.format(1)

# t_notLockedTrigger=TagList("not", TagList("has_global_flag", "custom_difficulty_locked"))
# t_notLockedTrigger=TagList("custom_difficulty_allow_changes", "yes")
# t_mainMenuEvent=TagList("id",name_mainMenuEvent)
# t_rootUpdateEvent=TagList("id",name_rootUpdateEvent)
# t_backMainOption=TagList("name","custom_difficulty_back").add("hidden_effect", TagList("country_event",TagList("id", name_mainMenuEvent)))
# t_closeOption=TagList("name", "custom_difficulty_close.name").add("hidden_effect", TagList("country_event", t_rootUpdateEvent))

def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  debugMode=False

  mainFileContent=TagList()


  mainFileContent.add("","","#game start init")
  gameStartInitEvent=mainFileContent.addReturn("country_event")
  gameStartInitEvent.add("id", name_gameStartFireOnlyOnce)
  gameStartInitEvent.add("title","custom_difficulty_init" )
  gameStartInitEvent.add("trigger", TagList("is_ai","no").add("not", TagList("has_global_flag", "custom_difficultyMM_active")))
  immediate=TagList()
  gameStartInitEvent.add("immediate",immediate)
  immediate.add_event("name_randomDiffFireOnlyOnce")
  immediate.add("set_country_flag", "custom_difficulty_game_host")
  immediate.add("random_planet", TagList("save_global_event_target_as", "custom_difficultyMM_var_storage"))
  gameStartAfter=TagList()
  gameStartInitEvent.add("after",TagList("hidden_effect", gameStartAfter))
  gameStartAfter.add("set_global_flag", "custom_difficulty_active")


  custom_difficulty_files.outputToFolderAndFile(mainFileContent , "events", "custom_difficultyMM_main.txt" ,2,modFolder="../gratak_mods/custom_difficultyMM")


if __name__ == "__main__":
  main()

