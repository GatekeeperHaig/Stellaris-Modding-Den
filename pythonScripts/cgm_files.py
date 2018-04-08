#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList
from custom_difficulty_files import *
from functools import reduce

debugMode=True

changeStepYears=[5,4,3,2,1]
changeSteps = [50, 25, 10, 5, 1]
for s in reversed(changeSteps):
  changeSteps.append(-s)
for s in reversed(changeStepYears):
  changeStepYears.append(-s)
boniNames=["capital_building","empire_unique_building","planet_unique_building","military_building","standard_resource_building","research_resource_building","unity_resource_building","special_resource_building","replicator_building", "all"]
boniPictures=["GFX_CGM_buildings_menu" for entry in boniNames]
buildSpeedBonus=[[entry+"_building_time_mult"] for entry in boniNames if entry !="all"]
buildCostBonus=[[entry+"_building_cost_mult"] for entry in boniNames if entry !="all"]
buildSpeedBonus.append(reduce(lambda x,y: x+y, buildSpeedBonus))
buildCostBonus.append(reduce(lambda x,y: x+y, buildCostBonus))

# possibleBoniPictures=["GFX_evt_mining_station","GFX_evt_dyson_sphere","GFX_evt_animal_wildlife", "GFX_evt_think_tank", "GFX_evt_unity_symbol","GFX_evt_arguing_senate","GFX_evt_hangar_bay", "GFX_evt_debris", "GFX_evt_sabotaged_ship","GFX_evt_pirate_armada","GFX_evt_fleet_neutral","GFX_evt_city_ruins","GFX_evt_metropolis"]




print(buildSpeedBonus)
print(buildCostBonus)

# # doTranslation=True
# doTranslation=False
# locClass=LocList(doTranslation)
# #global things: No translation needed (mod name and stuff taken from vanilla translations)
# locClass.addLoc("modName", "Dynamic Difficulty", "all")
# locClass.addLoc("minerals", "$minerals$","all")
# locClass.addLoc("energy", "$energy$","all")
# locClass.addLoc("food", "$food$","all")
# locClass.addLoc("research", "$RESEARCH$","all")
# locClass.addLoc("unity", "$unity$","all")
# locClass.addLoc("influence", "$influence$","all")
# locClass.addLoc("cap", "$NAVY_SIZE_TITLE$","all")







# locClass.addEntry("custom_difficulty_current_bonuses","@curBon:")

# # locClass.addEntry(, [])
# # locClass.addEntry(, [])






eventNameSpace="core_game_mechanics_and_ai_base.{!s}"

name_mainMenuEvent="core_game_mechanics_and_ai_base.10"
id_Change_Speed=20  #reserved range up to 29
id_Change_Cost=30  #reserved range up to 39

