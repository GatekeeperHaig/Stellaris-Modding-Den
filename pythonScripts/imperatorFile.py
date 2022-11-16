#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
import custom_difficulty_files as cdf
import math
import yaml
from yaml.loader import SafeLoader
from locList import LocList
from random import randint
from PIL import Image
from copy import copy
import pickle
import random





def main():


  # im = Image.open("heightmap.png") # Can be many different formats.


  # # im = im.convert("HSV")
  # pix = im.load()
  # def p(x,y):
  #   print(f"({x},{y}):{pix[x,im.size[1]-y]}")
  # print(im.size)  # Get the width and hight of the image for iterating over
  # # print(f'im.getpixel((3807,2920)) = "{im.getpixel((3807,2920))}"')
  # # print(f'im.getpixel((1000,1000)) = "{im.getpixel((1000,1000))}"')
  # # print(f'pix[3000,1800] = "{pix[3000,1800]}"')
  # # print(f'pix[2458,3432] = "{pix[2458,3432]}"')
  # p(1000, 1000)
  # p(3807, 2920)
  # p(3000, 1800)
  # p(2458, 3432)
  # # pix[2458,3432]
  # # print(pix[3807,2920])  # Get the RGBA Value of the a pixel of an image
  # # pix[x,y] = value  # Set the RGBA Value of the image (tuple)
  # # im.save('alive_parrot.png')  # Save the modified pixels as .png

  # return


  fileContent=TagList()

  locClass=LocList()
  locClass.limitLanguage(["en"])

  races=["Noldor", "Teleri", "Edain", "Dwarf","Orc"]
  raceGrowth={"Noldor":-1.4,"Teleri":-1.4,"Edain":-0.6666, "Dwarf":-1,"Orc":1}
  raceCombat={"Noldor":1.2,"Teleri":1,"Edain":0.8, "Dwarf":0.8,"Orc":0}
  raceCommerce={"Noldor":0.5,"Teleri":0.7,"Edain":.5, "Dwarf":1,"Orc":0}
  raceDesc={"Noldor":"The Noldor where the second clan of elves to reach Valinor in the years of the trees and later where led back to Middle-earth by Fëanor. These elves have a long list of famous heroes and take pride in their combat ability. You have access to this modifier as your primary culture is Noldor.","Teleri":"The Teleri were the last clan of elves to reach Valinor in the years of the trees, though many remained in Middle-earth in the first place. They have always been the greatest seafarers of Middle-earth. As many of their breathren were slaughtered by Fëanor's host on his way back to Middle-earth, it took a long time for them to forgive the Noldor elves. You have access to this modifier as your primary culture is Teleri.","Edain":"The Edain were the group of mankind that reached Beleriand in the First Age. Many of them have fought Morgoth in the Battle of Beleriand and they and their ancestors have thus been rewarded with long life. You have access to this modifier as your primary culture is Edain. Lesser dunedain, corsairs and dol amrothian only count half.", "Dwarf":"The Masters of Stone were created by Aulë even before Ilúvatar created the elves, but slept underground until about a century after the elves awoke. Dwarves spend most of their time crafting, smithying and mining. You have access to this modifier as your primary culture is dwarven.","Orc":"Melkor created the orcs by twisting kidnapped elves in the Years of the Lamps. Without the guidance of Melkor or a fallen Maia, they are usually disorganized and pose little thread to any of the other races. Now that the Lord of the Rings is returning to his power though, the Age of the Orcs will come. You have access to this modifier as your primary culture is orcish."}
  # raceGrowth={"Noldor":-1,"Teleri":-1,"Edain":-0.8, "Dwarf":-0.8,"Orc":4}

  lotr_pops=TagList("namespace", "lotr_pops")
  foreignPopsEvent=lotr_pops.addReturn("lotr_pops.1")
  foreignPopsEvent.add("type", "country_event").add("hidden","yes")
  trigger=foreignPopsEvent.addReturn("trigger")
  trigger.addReturn("NOT").add("has_law","age_of_the_orc")
  immediate=foreignPopsEvent.addReturn("immediate")
  option=foreignPopsEvent.addReturn("option")
  option.add("name", "OK")

  for race in races:
    for i in range(1,11):
      name=f"{i*10}_{race}".lower()
      t=fileContent.addReturn(name)
      if race!="Orc":
        t.add("land_morale_modifier", round(i*0.06*raceCombat[race],3))
        t.add("land_morale_recovery", round(i*0.01*raceCombat[race],3))
        t.add("discipline", round(i*0.06*raceCombat[race],3))
        t.add("global_commerce_modifier", round(i*0.06*raceCommerce[race],3))
      else:
        t.add("global_pop_assimilation_speed_modifier", round(i/10,2))
      if race in ["Noldor","Teleri"]:
        t.add("movement_speed_if_no_road", round(i/50,2))
      elif race == "Dwarf":
        t.add("army_movement_speed", round(i/200,2))
      if raceGrowth[race] > 0:
        t.add("global_population_growth", round(i*0.015*raceGrowth[race],3))
      else:
        t.add("global_population_growth", round(i**0.5*10**0.5*0.015*raceGrowth[race],3))
      locClass.addEntry(name, f"{i*10}% {race}")
      locClass.addEntry("desc_"+name, raceDesc[race])


  for i in reversed(range(1,20)):
    name=f"foreign_support_{i*5}"
    t=fileContent.addReturn(name)
    t.add("levy_size_multiplier",round(0.025*i,2))
    locClass.addEntry(name, f"{i*5}% Foreign Culture Support")
    locClass.addEntry("desc_"+name, "Non-integrated culture do not direcly increase the number of possible levies (and thus legion size) and due to a bug in the vanilla game we cannot allow their integration outside of your culture group. Instead they will slightly increase the numbers of your integrated culture levies.")
    immediate.add("remove_country_modifier", name)
    option.createReturnIf(TagList("local_var:foreign_pop_percentage", round(i*5/100,2),"",">="),condType="else_if" if i!=19 else "if").add("add_country_modifier", TagList("name",name))

  immediate.variableOpImp("set_local", "total_pops", 0)
  immediate.variableOpImp("set_local", "foreign_pops", 0)
  everyPop=immediate.addReturn("every_owned_province").addReturn("every_pops_in_province")
  everyPop.add("save_scope_as","pop")
  everyPop.variableOpImp("change_local", "total_pops", 1, valName="add")
  foreignPop=everyPop.createReturnIf(TagList("NOT", TagList("ROOT", TagList("any_integrated_culture", TagList("this.culture", "scope:pop.culture")))))
  foreignPop.variableOpImp("change_local", "foreign_pops", 1, valName="add")
  immediate.variableOpImp("set_local", "foreign_pop_percentage", "local_var:foreign_pops")
  immediate.createReturnIf(TagList("local_var:total_pops", "0", "", ">")).variableOpImp("change_local", "foreign_pop_percentage", "local_var:total_pops", valName="divide")
  immediate.addReturn("else").variableOpImp("set_local", "foreign_pop_percentage", 0 )
  halfLevy=immediate.createReturnIf(TagList("OR", TagList("has_country_modifier","harassed_by_corsairs").add("has_country_modifier","influenced_by_saruman")))
  halfLevy.variableOpImp("change_local", "foreign_pop_percentage",2, valName="divide")
  # print(f'fileContent = "{fileContent}"')
  locClass.writeToMod(".","lotr_country_modifiers_from_script","z")
  cdf.outputToFolderAndFile(fileContent , "common/modifiers", "br_racial_modifiers.txt" ,2,".", encoding="utf-8-sig")
  cdf.outputToFolderAndFile(lotr_pops , "events/", "LOTR_pops.txt" ,1,".", encoding="utf-8-sig")

  relations = {
    "archers":        { "archers":0, "camels":-10, "chariots":0, "heavyCavalry":-10, "heavyInfantry":10, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":0 },
    "camels":         { "archers":10, "camels":0, "chariots":10, "heavyCavalry":-20, "heavyInfantry":-10, "horseArchers":10, "lightCavalry":0, "lightInfantry":10, "elephants":-50 },
    "chariots":       { "archers":20, "camels":-10, "chariots":0 ,"heavyCavalry":-50, "heavyInfantry":-10, "horseArchers":10, "lightCavalry":0, "lightInfantry":35, "elephants":-50},
    "heavyCavalry":   { "archers":50, "camels":10, "chariots":25, "heavyCavalry":0, "heavyInfantry":-10, "horseArchers":0, "lightCavalry":20, "lightInfantry":25, "elephants":-50},
    "heavyInfantry":  { "archers":0, "camels":-10, "chariots":25, "heavyCavalry":20, "heavyInfantry":0, "horseArchers":-25, "lightCavalry":-10, "lightInfantry":20, "elephants":0},
    "horseArchers":   { "archers":25, "camels":-10, "chariots":25, "heavyCavalry":-10, "heavyInfantry":25, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":-20},
    "lightCavalry":   { "archers":25, "camels":0, "chariots":25, "heavyCavalry":-20, "heavyInfantry":-50, "horseArchers":25, "lightCavalry":0, "lightInfantry":25, "elephants":-50},
    "lightInfantry":  { "archers":-10, "camels":0, "chariots":-10, "heavyCavalry":-25, "heavyInfantry":-20, "horseArchers":-50, "lightCavalry":0, "lightInfantry":0, "elephants":-20},
    "elephants":      { "archers":50, "camels":-10, "chariots":50, "heavyCavalry":-10, "heavyInfantry":40, "horseArchers":-10, "lightCavalry":-10, "lightInfantry":30, "elephants":0},
  }
  properties = {
    "archers":        { "cost":8, "assault":True, "speed":2.5, "maneuver":2, "morale":-30, "strength":0, "attrition":-10, "attritionLoss":5, "food":2.4, "consumption":0.1, "ai_max_percentage":15  },
    "camels":         { "cost":15, "assault":False, "speed":3.5, "maneuver":4, "morale":0, "strength":0, "attrition":0, "attritionLoss":2.5, "food":3.6, "consumption":0.2, "tradeGood":"camel","flank":"yes"},
    "chariots":       { "cost":8, "assault":False, "speed":2.5, "maneuver":1, "morale":0, "strength":0, "attrition":0, "attritionLoss":5, "food":2.4, "consumption":0.2  },
    "heavyCavalry":   { "cost":18, "assault":False, "speed":3.5, "maneuver":2, "morale":0, "strength":0, "attrition":100, "attritionLoss":5, "food":2.4, "consumption":0.25, "tradeGood":"horses", "levy_tier":"advanced" },
    "heavyInfantry":  { "cost":16, "assault":True, "speed":2.5, "maneuver":1, "morale":10, "strength":0, "attrition":50, "attritionLoss":5, "food":2.4, "consumption":0.2, "tradeGood":"iron", "levy_tier":"advanced" },
    "horseArchers":   { "cost":16, "assault":False, "speed":4, "maneuver":5, "morale":-25, "strength":0, "attrition":50, "attritionLoss":5, "food":3, "consumption":0.25, "tradeGood":"steppe_horses","flank":"yes"  },
    "lightCavalry":   { "cost":10, "assault":False, "speed":4, "maneuver":3, "morale":0, "strength":0, "attrition":50, "attritionLoss":5, "food":2.4, "consumption":0.25, "tradeGood":"horses","flank":"yes"  },
    "lightInfantry":  { "cost":8, "assault":True, "speed":2.5, "maneuver":1, "morale":30, "strength":0, "attrition":-50, "attritionLoss":2.5, "food":2.4, "consumption":0.1  },
    "elephants":      { "cost":35, "assault":False, "speed":2.5, "maneuver":0, "morale":-20, "strength":50, "attrition":200, "attritionLoss":10, "food":1, "consumption":0.3, "tradeGood":"elephants", "levy_tier":"advanced", "ai_max_percentage":15  },
    "supply_train":   { "cost":20, "assault":False, "speed":2.5, "maneuver":1, "morale":-100, "strength":-100, "attrition":0, "attritionLoss":10, "food":50, "consumption":0.05, "ai_max_percentage":15, "levy_tier":"none"  },
    "engineer_cohort":{ "cost":40, "assault":False, "speed":2.5, "maneuver":1, "morale":-100, "strength":-100, "attrition":0, "attritionLoss":10, "food":5, "consumption":0.05, "ai_max_percentage":15, "levy_tier":"none"  },
    "rangers":        { "cost":10, "assault":True, "speed":2.5, "maneuver":2, "morale":0, "strength":0, "attrition":-20, "attritionLoss":5, "food":2.4, "consumption":0.1  },
    "troll_infantry": { "cost":10, "assault":True, "speed":2.5, "maneuver":1, "morale":0, "strength":0, "attrition":150, "attritionLoss":5, "food":3, "consumption":0.3, "tradeGood":"iron", "levy_tier":"advanced", "ai_max_percentage":15  },
  }

  units = [
    Unit("supply_train", "support"),
    Unit("engineer_cohort", "support"),
    Unit("archers", "archers"),
    Unit("dunedain_archers", "archers", 2.5, 1, 1.3),
    Unit("dwarven_archers", "archers", 1.5, 1.5, 1.3, AP=True),
    Unit("elvish_archers", "archers", 3, 1.25, 1.3),
    Unit("uruk_crossbows", "archers", 1.5, 1, 1),
    Unit("camels", "camels"),
    Unit("chariots", "chariots"),
    Unit("heavy_cavalry", "heavyCavalry"),
    Unit("dol_amroth_knights", "heavyCavalry", 1.5, 2, 1.5),
    Unit("dwarven_goat_riders", "heavyCavalry", 1.5, 2, 1.5, AP=True),
    Unit("warg_riders", "heavyCavalry", 1, 1, 1, { "archers":15, "chariots":30, "heavyCavalry":15, "heavyInfantry":-30, "horseArchers":15, "lightCavalry":30, "lightInfantry":0, "elephants":0 }),
    Unit("heavy_infantry", "heavyInfantry"),
    Unit("dunedain_infantry", "heavyInfantry", 1.4, 2, 1.75),
    Unit("dwarven_infantry", "heavyInfantry", 1.4, 2.5, 1.75, AP=True),
    Unit("elvish_infantry", "heavyInfantry", 1.6, 2.25, 2),
    Unit("uruk_heavy_infantry", "heavyInfantry", 1.25, 1.5, 1.25),
    Unit("troll_infantry", "heavyInfantry", 2, 4, 1, AP=True),
    Unit("rangers", "heavyInfantry", 1.6, 2, 1.5, { "archers":0, "chariots":0, "heavyCavalry":0, "heavyInfantry":0, "horseArchers":0, "lightCavalry":0, "lightInfantry":30, "elephants":0 }),
    Unit("horse_archers", "horseArchers"),
    Unit("elvish_cavalry_archers", "horseArchers", 2.5, 1.5, 1),
    Unit("light_cavalry", "lightCavalry"),
    Unit("dunedain_cavalry", "lightCavalry", 2.5, 1, 1.5),
    Unit("light_infantry", "lightInfantry"),
    Unit("halfling_infantry", "lightInfantry", 0.75, 1, 1),
    Unit("orc_infantry", "lightInfantry", 1, 1, 0.5),
    Unit("uruk_infantry", "lightInfantry", 1.25, 1.25, 0.7),
    Unit("warelephant", "elephants"),

    # Unit("mumakils", "elephants", 3, 3, 2), ???
  ]

  os.makedirs("units",exist_ok=True)
  for unit in units:
    d=unit.assemble(relations, properties, units)
    fileName=unit.name
    if unit.name=="warelephant":
      fileName="warelephants"
    cdf.outputToFolderAndFile(d , "common/units", f"army_{fileName}.txt" ,2,".",encoding="utf-8-sig")

    # unit.computeAllDamages(units,relations,properties)
    # print(f"  cost = {unit.computeCosts(properties)}")
    # if unit.category=="support":
    # print(f"  morale_damage_taken = {unit.computeMoraleDamageTaken(properties)}")
  # return

  output_folder="."

  provinceNames={}
  provinceNamesInv={}
  with open("localization/english/provincenames_l_english.yml",encoding='utf-8-sig') as f:
    for line in f.readlines():
      # print(line)
      split=line.split()
      key=split[0]
      if key=="l_english:":
        continue
      # print(f'key = "{key}"')
      key=key.replace("PROV", "").replace(":0", "")
      # print(f'key = "{key}"')
      rest=" ".join(split[1:]).replace('"', "")
      # print(f'rest = "{rest}"')
      provinceNames[key]=rest
      if not rest in provinceNamesInv:
        provinceNamesInv[rest]=[]
      provinceNamesInv[rest].append(key)

  moveGroupNamesToNormal=False
  if moveGroupNamesToNormal:
    removeList=[]
    for p,name in provinceNames.items():
      if "_group" in p:
        for i,s in enumerate(p):
          if not s.isnumeric():
            break
        else:
          i+=1
        removeList.append(p)
        newKey=p[:i]
        print(f"Replacing {provinceNames[newKey]} with {name}")
        provinceNames[newKey]=name
    for p in removeList:
      del provinceNames[p]



  provinceFile=TagList(0)
  provinceFile.readFile("setup/provinces/00_default.txt",encoding='utf-8-sig')
  applyModificationOnProvinces=False
  if applyModificationOnProvinces:
    provinceFileLatest=TagList(0)
    provinceFileLatest.readFile("00_default_new.txt",encoding='utf-8-sig')
    provinceFileOld=TagList(0)
    provinceFileOld.readFile("00_default_old.txt",encoding='utf-8-sig')
  terrainFile=TagList(0)
  terrainFile.readFile("common/province_terrain/00_province_terrain.txt",encoding='utf-8-sig')
  countryFile=TagList(0)
  countryFile.readFile("setup/main/00_default.txt")
  treasureFile=TagList(0)
  treasureFile.readFile("setup/main/lotr_treasures.txt")
  climateFile=TagList(0)
  climateFile.readFile("map_data/climate.txt",encoding='utf-8')
  areaFile=TagList(0)
  areaFile.readFile("map_data/areas.txt",encoding='utf-8')
  regionFile=TagList(0)
  regionFile.readFile("map_data/regions.txt",encoding='utf-8')
  provinceLocators=TagList(0)
  provinceLocators.readFile("gfx/map/map_object_data/vfx_locators.txt",encoding='utf-8-sig')
  cityLocators=TagList(0)
  cityLocators.readFile("gfx/map/map_object_data/city_locators.txt",encoding='utf-8-sig')

  # with open("gfx/map/map_object_data/oak_tree_generator_3.txt",'r', encoding='utf-8-sig') as inputFile:
  #   oakFile=[line for line in inputFile]
  #   oakFile=oakFile[:9] #just use the header, rest is added by script
  # with open("gfx/map/map_object_data/pine_tree_generator_2.txt",'r', encoding='utf-8-sig') as inputFile:
  #   pineFile=[line for line in inputFile]
  #   pineFile=pineFile[:9] #just use the header, rest is added by script
  # fortLocators=TagList(0)
  # fortLocators.readFile("gfx/map/map_object_data/fort_locators.txt",encoding='utf-8-sig')
  # combatLocators=TagList(0)
  # combatLocators.readFile("gfx/map/map_object_data/combat_locators.txt",encoding='utf-8-sig')

  locs=provinceLocators.get("game_object_locator").get("instances")
  provinceToLocation=[None for _ in locs.vals]
  provinceToCityLocation=[None for _ in locs.vals]
  # provinceToFortLocation=[None for _ in locs.vals]
  # provinceToCombatLocation=[None for _ in locs.vals]
  for loc in locs.vals:
    provinceToLocation[int(loc.get("id"))]=[int(float(a)) for a in loc.get("position").names]
  locs=cityLocators.get("game_object_locator").get("instances")
  for loc in locs.vals:
    provinceToCityLocation[int(loc.get("id"))]=[int(float(a)) for a in loc.get("position").names]
  # locs=fortLocators.get("game_object_locator").get("instances")
  # for loc in locs.vals:
  #   provinceToFortLocation[int(loc.get("id"))]=[int(float(a)) for a in loc.get("position").names]
  # locs=combatLocators.get("game_object_locator").get("instances")
  # for loc in locs.vals:
  #   provinceToCombatLocation[int(loc.get("id"))]=[int(float(a)) for a in loc.get("position").names]

  # cdf.outputToFolderAndFile(climateFile , ".", "climateFile.txt" ,4,".",encoding="utf-8-sig")

  # print(f'climateFile.vals[0].names = "{climateFile.vals[0].names}"')

  # print(f'climateFile.names = "{climateFile.names}"')
  # print(f'climateFile.seperators = "{climateFile.seperators}"')
  # print(f'climateFile.get("mild_winter") = "{climateFile.get("mild_winter")}"')
  # print(f'climateFile.get("mild_winter").names = "{climateFile.get("mild_winter").names}"')



  uninhabitable = set(map(str,list(range(4969,4988+1))+list(range(5453,5459+1))+list([52,2616,3765,577,564,563,576,575,604,605,606,607,608,602,603,2696,2697,2698,2607,2604,2605,3402,3403,3404,476,475,478,479,2961,2960,2959,2954,2955,2984,2985,2986,540,539,538,537,536,535,547,546,545,544,543,542,2617,594,595,596,597,94,27,95,91,92,581,582,2046,2045,2044,87,85,89,88,83,82,80,2375,2376,7,3,17,23,48,1965,583,584,585,586,587,588,589,590,2997,2998,3000,3001,2988,2991,2989,2992,2994,3003,2990,2995,2996,2993,3002,579,578,2048,2049,2050,2051,2052,2053,593,3142,3143,3146,3144,3145,3147,3148,3149,3150,51,2378,2377,3638,3639,3678,3679,3680,3681,3682,3683,3684,3685,3686,3687,3688,3689,3690,3691,3692,3693,3694,3593,3709,3719,3611,3613,3612,3653,3654,3656,3660,3718,3626,3659,3706,3607,3608,3609,3740,3741,3742,3743,3744,3745,3746,3747,3787,3781,3779,3778,3777,3784,3793,3794,3792,3790,3789,3791,3775,3776,3771,3795,3797,2730,2731,2732,2733,2739,2737,2741,2735,2740,2742,2745,2744,2743,3860,3862,3863,3864,3865,3866,3874,3867,3881,3871,3869,3552,3553,3880,3879,3868,3872,3873,3870,3554,2738,2750,2749,2748,2747,2746,2751,3875,2729,2769,2728,3582,3581,3580,3643,3637,3904,3909,3910,3937,3938,3939,5215,5217,5218,5174,5176,5291,5306,5307,5308,5309,5310,5311,5312,5313,5314,5315,5317,5318,5319,5320,5321,5322,5323,5324,5326,5327,5328,5329,5330,5331,5332,5333,5334,5336,5337,5338,5339,5340,5341,5342,5343,5344,5345,5348,5386,5387,5388,5389,5390,5433,5434,5435,5399,5400,5401,5378,5379,5375,5274,5275,5276,5277,5278,5281,5279,5282,5283,5406,5429,5430,5297,5298,5299,5437,5024,5025,5443,5444,5445,5446,5447,5448,5449,5450,5451,5067,5463,5396,5395,5409,5280,5462,5466,5284,5286,5287,5296,5452,5410,5411,5412,5216,5252,5285,5288,5060,5273])))

  # print(f'uninhabitable = "{uninhabitable}"')

  addNumbersToDuplicateNames=False
  if addNumbersToDuplicateNames:
    sea_of_rhun=list(range(3500,3505+1))
    Haragaer=list(range(4744,4894+1))
    EdgeSee=list(range(5478,5499+1))
    Belegaer=list(range(5500,5687+1))
    river_provinces = list(range(4895,4988+1))
    allSeas=sea_of_rhun+Haragaer+EdgeSee+Belegaer+river_provinces
    numbers=["","Mîn","Tâd","Neledh","Canad","Leben","Eneg","Odog","Tolodh","Neder","Pae","Minib","Ýneg","Neleb","Canab","Lebem","Eneph","Odoph","Toloph","Nederph"]
    cardinals=["","","Taphaen","Nelphaen","Cambaen","Lephaen","Enephaen","Odophaen","Tolophaen","Nederphaen"]
    for name in provinceNamesInv:
      if len(provinceNamesInv[name])>=2:
        hab=[]
        other=[]
        for j in provinceNamesInv[name]:
          i=int(j)-1
          terrain=provinceFile.vals[i].get("terrain").strip('"')
          is_impassable=(terrain=='impassable_terrain')
          if not is_impassable and not terrain=='coastal_terrain' and not j in uninhabitable and not int(j) in allSeas:
            hab.append(j)
          else:
            other.append(j)
        cur=1
        for h in hab:
          provinceNames[h]+=" "+numbers[cur]
          cur+=1
        for h in other:
          if cur<20:
            provinceNames[h]+=" "+numbers[cur]
          else:
            a=cur//10
            b=cur%10
            provinceNames[h]+=f" {cardinals[a]}"
            if b:
              provinceNames[h]+=f" a {numbers[b]}"
          cur+=1

            # print(f'name = "{name}"{len(provinceNamesInv[name])}')

    # os.makedirs("out/localization/english", exist_ok=True)
    with open("localization/english/provincenames_l_english.yml","w",encoding='utf-8-sig') as f:
      f.write("l_english:\n")
      for p,i in provinceNames.items():
        f.write(f' PROV{p}:0 "{i}"\n')
    return


  provinceToCapitalType=dict()
  countries=countryFile.get("country").get("countries")
  # ownedProvinces=set()
  ownerCountry=dict()
  countryCulture=dict()
  countryProvinces=dict()
  for name,vals in zip(countries.names, countries.vals):
    # print(f'vals = "{vals}"')
    if vals=="":
      continue
    cores=vals.get("own_control_core")
    countryCulture[name]=vals.get("primary_culture")
    provinceToCapitalType[vals.get("capital")]="country_capital"
    # print(f'cores = "{cores.vals}"')
    countryProvinces[name]=cores.names
    for core in cores.names:
      # ownedProvinces.add(core)
      ownerCountry[core]=name
    # print(f'cores = "{cores}"')


  provinceToArea=dict()
  areaToRegion=dict()
  provinceToRegion=dict()
  regionToArea=dict()
  regionToProvince=dict()
  regionToNum=dict()
  areaToProvince=dict()

  for name, val in areaFile.getNameVal():
    if name:
      cap=val.get("provinces").names[0]
      if not cap in provinceToCapitalType:
        provinceToCapitalType[cap]="state_capital"
      for p in val.get("provinces").names:
        provinceToArea[p]=name
        if not name in areaToProvince:
          areaToProvince[name]=[]
        areaToProvince[name].append(p)
  for name, val in regionFile.getNameVal():
    regionToProvince[name]=[]
    if name:
      for p in val.get("areas").names:
        areaToRegion[p]=name
        if not name in regionToArea:
          regionToArea[name]=[]
          regionToNum[name]=0
        for pp in areaToProvince[p]:
          regionToProvince[name].append(pp)
        regionToArea[name].append(p)
        regionToNum[name]+=len(areaToProvince[p])
  for province, area in provinceToArea.items():
    if area in areaToRegion:
      provinceToRegion[province]=areaToRegion[area]

  # print(f'regionToNum = "{sorted(regionToNum.items(), key=lambda x:x[1])}"')
  for item in sorted(regionToNum.items(), key=lambda x:x[1]):
    print(item)

  provinceToTerrain=dict()
  for name, val in provinceFile.getNameVal():
    if name:
      provinceToTerrain[name]=val.get("terrain")

  heightMap=ImageRead("map_data/heightmap.png")


  provinceToPixels,_,_,_ = getProvinceToPixels()

  makeTrees=False
  if makeTrees:
    oakLayer="oak_tree_layer"
    oakA="tree_oak_2_mesh"
    oakB="tree_oak_2_variation_1_mesh"
    oakC="tree_oak_2_variation_2_mesh"
    oakTrees=[]
    oakTreeSplit=[[] for _ in range(3)]

    treeLayer="tree_layer"
    pine="tree_pine_01_mesh"
    pineTrees=[]
    "tree_olive_01_mesh"
    "tree_palm_mesh"
    "tree_india_01_mesh"
    "tree_cypress_01_mesh"

    def makeTree(c, rotation=[0,random.random(),0,random.random()], size=random.uniform(0.9,1)):
      coord=[c[0]+random.uniform(-0.45,0.45),0,c[1]+random.uniform(-0.45,0.45)]
      return " ".join(map('{:.6f}'.format,coord+rotation+[size for _ in range(3)]))


    def generateTrees(provinceId, number):
      t=provinceToPixels[provinceId]
      t2=[None for _ in range(len(t)//2)]
      for i in range(len(t)//2):
        t2[i]=(t[2*i],t[2*i+1])
      r=random.choices(t2, k=number)
      for c in r:
        h = heightMap.p(*c)
        if h<7.5 or h>18:
          continue
        # coord=[c[0]+random.uniform(-0.45,0.45),0,c[1]+random.uniform(-0.45,0.45)]
        # rotation=[0,random.random(),0,random.random()]
        # size=random.uniform(0.9,1)
        if h<random.randint(15,16):
          oakTrees.append(makeTree(c))
          # oakFile.append(" ".join(map('{:.6f}'.format,coord+rotation+[size for _ in range(3)]))+"\n")
        else:
          pineTrees.append(makeTree(c))
          # pineFile.append(" ".join(map('{:.6f}'.format,coord+rotation+[size for _ in range(3)]))+"\n")
    for area in ["jayir_ahar_area","murgarm_area","lokhas_area"]:
      for province in areaToProvince[area]:
        generateTrees(int(province), random.randint(100,300))
    generateTrees(2898, 500)
    
    for oak in oakTrees:
      oakTreeSplit[random.randint(0, 2)].append(oak)


  # return


  # print(f'provinceToPixels = "{provinceToPixels}"')
  # som.work()

  # print(f'provinceToPixels = "{provinceToPixels}"')

  # print(f'provinceImage.h(provinceToLocation[1]) = "{provinceImage.col(provinceToLocation[1])}"')
  # print(f'colorToProvince[colorToString(provinceImage.col(provinceToLocation[1]))] = "{colorToProvince[colorToString(provinceImage.col(provinceToLocation[1]))]}"')


  # print(f'heightMap.h(provinceToLocation[1]) = "{heightMap.h(provinceToLocation[1])}"')

  # print(f'heightMap.h(provinceToLocation[5025]) = "{heightMap.h(provinceToLocation[5025])}"')
  # print(f'heightMap.h(provinceToLocation[4126]) = "{heightMap.h(provinceToLocation[4126])}"')
  # heightMap.h(provinceToLocation[1])

  newClimate=TagList(0)
  forceTerrainGeneral=dict()
  forceTerrainGeneral["pend_hithaeglir_region"]="forest"
  forceTerrainGeneral["chail_caerdh_area"]="forest"
  forceTerrainGeneral["gwaelad_area"]="forest"
  forceTerrainGeneral["ivrien_area"]="forest"
  forceTerrainGeneral["falas_i_myl_area"]="forest"
  forceTerrainGeneral["1566"]="hills"
  forceTerrainGeneral["2442"]="hills"
  forceTerrainGeneral["2468"]="hills"
  forceTerrainGeneral["2453"]="forest"
  forceTerrainGeneral["2544"]="forest"
  forceTerrainGeneral["2725"]="forest"
  forceTerrainGeneral["2543"]="forest"
  forceTerrainGeneral["2541"]="forest"
  forceTerrainGeneral["2542"]="forest"
  forceTerrainGeneral["2231"]="forest"
  forceTerrainGeneral["1880"]="forest"
  forceTerrainGeneral["1892"]="forest"
  forceTerrainGeneral["1560"]="forest"
  forceTerrainGeneral["1013"]="marsh"
  forceTerrainGeneral["1015"]="marsh"
  forceTerrainGeneral["3255"]="arctic"
  forceTerrainGeneral["3249"]="arctic"
  forceTerrainGeneral["3258"]="arctic"
  forceTerrainGeneral["5429"]="arctic"
  forceTerrainGeneral["5430"]="arctic"
  forceTerrainGeneral["1097"]="arctic"
  forceTerrainGeneral["5306"]="arctic"
  forceTerrainGeneral["5024"]="mountain"
  forceTerrainGeneral["5025"]="mountain"
  forceTerrainGeneral["5027"]="hills"
  for i in [5074,5073,5072,5068,5019,5018,3964,3963,3960,3958,3957,3956,3955,3954,3953,3952,3950,3949]:
    forceTerrainGeneral[str(i)]="forest"
  forceTerrainGeneral["durganla_area"]="arctic"
  forceTerrainGeneral["lothren_baul_area"]="arctic"

  forceTerrain=dict()
  for name, terrain in forceTerrainGeneral.items():
    if name.endswith("region"):
      for a in regionToArea[name]:
        for p in areaToProvince[a]:
          forceTerrain[p]=terrain
  for name, terrain in forceTerrainGeneral.items():
    if name.endswith("area"):
      for p in areaToProvince[name]:
        forceTerrain[p]=terrain
  for name, terrain in forceTerrainGeneral.items():
    if name.isdigit():
      forceTerrain[name]=terrain

  forceClimate=dict()
  #remember to remove stuff after it is done
  # forceClimate["umbar_region"]="mild_winter"
  # forceClimate["harnendor_region"]="mild_winter"
  # forceClimate["harondor_region"]="mild_winter"
  # forceClimate["dacranamel_region"]="mild_winter"
  # forceClimate["dor_rhunen_region"]="mild_winter"
  # forceClimate["anorien_region"]="mild_winter"
  # forceClimate["rhuvenlhad_region"]="mild_winter"
  # forceClimate["belfalas_region"]="mild_winter"
  # forceClimate["anfalas_region"]="mild_winter"
  # forceClimate["calenardhon_region"]="mild_winter"
  # forceClimate["dunendor_region"]="mild_winter"
  # forceClimate["druwaith_region"]="mild_winter"
  # forceClimate["enedhwaith_region"]="mild_winter"
  # forceClimate["andrast_region"]="mild_winter"
  # forceClimate["forlindon_region"]="mild_winter"
  # forceClimate["dor_wathui_region"]="mild_winter"
  # forceClimate["siragale_region"]="mild_winter"
  # forceClimate["minhiriath_region"]="mild_winter"
  # forceClimate["cardolan_region"]="mild_winter"
  # forceClimate["tawar_norndor_region"]="mild_winter"
  # forceClimate["mintyrnath_region"]="mild_winter"
  # forceClimate["mithlond_region"]="mild_winter"
  # forceClimate["harlindon_region"]="mild_winter"
  # forceClimate["arthedain_region"]="mild_winter"
  # forceClimate["rhudaur_region"]="normal_winter"
  # forceClimate["dyr_erib_region"]="normal_winter"
  # forceClimate["pend_hithaeglir_region"]="normal_winter"
  # forceClimate["lorien_region"]="normal_winter"
  # forceClimate["taur_romen_region"]="normal_winter"
  # forceClimate["menelothriand_region"]="normal_winter"
  # forceClimate["logathavuld_region"]="normal_winter"
  # forceClimate["rhovanion_region"]="normal_winter"
  # forceClimate["ered_mithrin_region"]="normal_winter"
  # forceClimate["uvanwaith_region"]="normal_winter"
  # forceClimate["anduin_region"]="normal_winter"
  # forceClimate["dyr_erib_region"]="normal_winter"
  # forceClimate["rhudaur_region"]="normal_winter"
  # forceClimate["numeriador_region"]="normal_winter"
  # forceClimate["kykurian_kyn_region"]="normal_winter"
  # forceClimate["lygar_kraw_region"]="normal_winter"
  # forceClimate["ubain_region"]="normal_winter"
  # forceClimate["eryn_galen_region"]="normal_winter"
  # forceClimate["angmar_region"]="severe_winter"
  # forceClimate["dyr_region"]="severe_winter"
  # forceClimate["lugnimbar_region"]="severe_winter"
  # forceClimate["lu_tyr_su_region"]="severe_winter"
  # forceClimate["felaya_region"]="arid"
  # forceClimate["bellakar_region"]="arid"
  # forceClimate["mardruak_region"]="arid"
  # forceClimate["an_balkumagan_region"]="arid"
  # forceClimate["bozisha_miraz_region"]="arid"
  # forceClimate["sirayn_region"]="arid"
  # forceClimate["cennacatt_region"]="arid"
  # forceClimate["harshandatt_region"]="arid"
  # forceClimate["nafarat_region"]="arid"
  # forceClimate["khand_region"]="arid"
  # forceClimate["nurn_region"]="arid"
  forceClimate["tulwang_region"]="mild_winter"
  # forceClimate["khailuza_region"]="arid"
  # forceClimate["kykurian_kyn_region"]="arid"
  # forceClimate["kargagis_ahar_region"]="arid"
  # forceClimate["gathgykarkan_region"]="arid"
  forceClimate["anarike_region"]="mild_winter"
  forceClimate["yopi_region"]="mild_winter"
  forceClimate["nikkea_region"]="mild_winter"
  forceClimate["shay_region"]="mild_winter"
  forceClimate["lokhas_drus_region"]="mild_winter"
  # forceClimate["ibav_region"]="arid"
  forceClimate["wer_falin_region"]="mild_winter"
  forceClimate["ralian_region"]="mild_winter"
  forceClimate["lenitan_region"]="mild_winter"
  forceClimate["kalz_raishoul_area"]="mild_winter"
  forceClimate["lokhurush_area"]="mild_winter"
  forceClimate["nithilfalas_area"]="mild_winter"
  forceClimate["bellazen_area"]="mild_winter"
  forceClimate["2093"]="mild_winter"
  # forceClimate["burskadekar_region"]="arid"
  # forceClimate["alduryaknar_region"]="arid"


  for name, terrain in provinceToTerrain.items():
    if terrain.strip('"') in ["caverns", "halls"] and name in provinceToArea:
      forceClimate[name]="mild_winter"
  forceClimate["lorien_area"]="perfect"
  forceClimate["1936"]="perfect"
  forceClimate["lothlann_area"]="normal_winter"
  forceClimate["tyrn_formen_area"]="normal_winter"
  forceClimate["rykholiz_area"]="normal_winter"
  forceClimate["thult_area"]="normal_winter"
  forceClimate["en_engladil_area"]="mild_winter"
  forceClimate["pend_eregion_area"]="mild_winter"
  forceClimate["sarch_nia_linquelie_area"]="severe_winter"
  ###arthedain
  forceClimate["1701"]="normal_winter"
  forceClimate["1877"]="normal_winter"
  forceClimate["1815"]="normal_winter"
  forceClimate["1814"]="normal_winter"
  forceClimate["1709"]="normal_winter"
  forceClimate["1710"]="normal_winter"
  forceClimate["1634"]="normal_winter"
  forceClimate["1822"]="normal_winter"
  forceClimate["2420"]="normal_winter"
  forceClimate["2423"]="normal_winter"
  forceClimate["2551"]="normal_winter"
  forceClimate["3729"]="normal_winter"
  forceClimate["3730"]="normal_winter"
  forceClimate["3736"]="normal_winter"
  forceClimate["2190"]="mild_winter"
  forceClimate["1747"]="mild_winter"
  forceClimate["1790"]="mild_winter"
  for name, climate in forceClimate.items():
    if climateFile.count(climate)>0:
      currentCLimate=climateFile.get(climate)
      if name.endswith("region"):
        for a in regionToArea[name]:
          for p in areaToProvince[a]:
            currentCLimate.add(p)
        pass
      elif name.endswith("area"):
        for p in areaToProvince[name]:
          currentCLimate.add(p)
      else:
        currentCLimate.add(name)
  nonPerfect=set()
  provinceToClimate=dict()
  # climateFile.addReturn("perfect") #probably need to be removed as it might confuse the game
  for climate, entries in climateFile.getNameVal():
    if not climate:
      continue
    if climate=="perfect":
      # perfect=[]
      for key in provinceToArea:
        if not key in nonPerfect:
          # perfect.append(key)
          entries.add(key)
    currentNewClimate=newClimate.addReturn(climate,"= LIST")
    provinceSet=set()
    for provinceId in entries.names:
      if provinceId:
        provinceSet.add(int(provinceId))
    provinceList=list(map(str,sorted(provinceSet,reverse=True)))
    while provinceList:
      province=provinceList[-1]
      # print(f'province = "{province}"')
      try:
        region=provinceToRegion[province]
      except:
        provinceList.pop()
        continue
      # if region in forceClimate:
      if region in forceClimate and forceClimate[region]!=climate:
        provinceList.pop()
        continue
      currentNewClimate.addComment("## "+region+" ###")
      regionCommentId=len(currentNewClimate.comments)-1
      for area in regionToArea[region]:
      # area=provinceToArea[province]
        # currentNewClimate.add(province)
        searchForList=areaToProvince[area]
        newArea=True
        found=[]
        for searchFor in searchForList:
          try:
            i=provinceList.index(searchFor)
            p=provinceList.pop(i)
            # if area in forceClimate or p in forceClimate:
            if area in forceClimate and forceClimate[area]!=climate or p in forceClimate and forceClimate[p]!=climate:
              continue
            found.append(p)
            nonPerfect.add(p)
            provinceToClimate[p]=climate
            if newArea:
              currentNewClimate.add(p)
              newArea=False
            else:
              currentNewClimate.names[-1]+=" "+p
          except ValueError:
            pass
        if not newArea:
          currentNewClimate.comments[-1]="#"+area
          if len(found)<len(searchForList):
            if len(found)>len(searchForList)/2:
              currentNewClimate.comments[-1]+=" (mostly: "
            elif len(found)>1:
              currentNewClimate.comments[-1]+=" (partly: "
            else:
              currentNewClimate.comments[-1]+=" (only: "
            for p in found:
              currentNewClimate.comments[-1]+=f"{provinceNames[p]}, "
            currentNewClimate.comments[-1]=currentNewClimate.comments[-1][:-2]+")"
            if len(found)>1:
              currentNewClimate.comments[-1]+=" (misses: "
              for p in searchForList:
                if not p in found:
                  currentNewClimate.comments[-1]+=f"{p}:{provinceNames[p]}, "
              currentNewClimate.comments[-1]=currentNewClimate.comments[-1][:-2]+")"
        else:
          currentNewClimate.comments[regionCommentId]+=" not "+area



    # print(f'provinceSet = "{provinceSet}"')

  # print(f'newClimate.get("severe_winter").names = "{.names}"')
  harsh=newClimate.get("severe_winter")
  harsh.addComment("## uninhabitable (to apply dynamic snow) ###")
  harsh.add("")
  harshUninhab=len(harsh.names)-1
  harsh.addComment("## unpassable (to apply dynamic snow) ###")
  harsh.add("")
  harshUnpass=len(harsh.names)-1
  def testCold(j):
    j=int(j)
    if j in range(4066,4073): #mordor interior
      return False
    if provinceToLocation[j][2]>3000:
      return True
    elif provinceToLocation[j][2]>1800:
      if heightMap.h(provinceToLocation[j])>15:
        return True
    elif heightMap.h(provinceToLocation[j])>20:
      return True
    return False

  def removeComment(t):
    if type(t)==TagList:
      for i in range(len(t.comments)):
        t.comments[i]=""
  def empty(t):
    return t[0]=='' and t[1]=='' and t[2]==''

  strengthenSauron=False
  strengthenCarnDum=False
  weakenAvari=False
  weakenSouthernGoblins=False

  if applyModificationOnProvinces:
    for i in range(len(provinceFile.names)):
      j=provinceFile.names[i]
      if j in provinceNames:
        if not provinceFileLatest.vals[i].compare(provinceFileOld.vals[i]):
          provinceFile.vals[i]=provinceFileLatest[i]

  def setTerrain(i, terrain):
    j=provinceFile.names[i]
    provinceFile.vals[i].set("terrain",f'"{terrain}"')
    try:
      terrainFile.set(j, terrain)
    except:
      terrainFile.add(j, terrain)
  a=[]
  b=[]

  provinceFile.applyOnAllLevel(removeComment)
  provinceFile.deleteOnLowestLevel(empty)
  tooManyNonOwnedPops=[ "balchoth", "rachoth", "nurnim", "variag", "nuriag", "khundolar", "jangovar", "yarlung", "tsang", "haradrim", "qarsag", "siranian", "yopi", "shayna", "mumakanim", "tulwany"]
  haladrin = [ "dunlending", "calending", "druwaithing", "daoine", "andrasting", "eredrim", "ethirfolk", "ishmalogim"]
  haradrim = [ "haradrim", "qarsag", "siranian" ]
  tooFewNonOwnedPops=[ "stonefoot", "stiffbeard"]
  elven = ["sindar","silvan","galadhrim","nandor","gondolin","lindon","eregion","imladris","feanorian"]
  dwarven = ["longbeard","firebeard","ironfist","stiffbeard","blacklock","broadbeam","stonefoot"]
  pops=["slaves", "tribesmen", "freemen", "citizen", "nobles"]
  ownedNoSlavesList=[]

  addTradeGoods=False #don't enable for regions where this was already applied!
  if addTradeGoods:

    numWildGames=dict()
    areasNeedTradeGoods=[]
    for area in areaFile.names:
      numWildGames[area]=0
    for i in range(len(provinceFile.names)):
      j=provinceFile.names[i]
      try:
        if provinceFile.vals[i].get("trade_goods").strip('"')=="wild_game":
          numWildGames[provinceToArea[j]]+=1
      except ValueError:
        pass
    for i in range(len(provinceFile.names)):
      j=provinceFile.names[i]
      if j in provinceToCapitalType and provinceToCapitalType[j]=="country_capital" and numWildGames[provinceToArea[j]]>2:
        # print(f'provinceToArea[j] = "{provinceToArea[j]}"')
        areasNeedTradeGoods.append(provinceToArea[j])
    print(f'areasNeedTradeGoods = "{areasNeedTradeGoods}"')
    return


    # provinceNeedTradeGoods=["ibav_region","ralian_region","lenitan_region","wer_falin_region","burskadekar_region","ubain_region","kargagis_ahar_region","lygar_kraw_region","lugnimbar_region","orgothrath_region","alduryaknar_region","gathgykarkan_region"]
    dessertTadeGoods={"iron":5,"camels":20,"stone":20,"base_metals":10, "elephants":10, "dates":10,"incense":10}
    hillTradeGoods={"iron":10, "precious_metals":5,"cattle":10,"stone":20,"base_metals":20,"gems":3,"marble":5}
    woodTradeGoods={"wild_game":10, "fur":10,"wood":20,"leather":10, "woad":10}
    coastalTradeGoods={"fish":40,"spices":5,"glass":5,"papyrus":5, "earthware":5,"hemp":10, "whale":5, "cloth":5,"dye":5, "incense":5, "silk":5, "wine":10, "dates":5, "olive":5}
    planeTradeGoods={"horses":10, "steppe_horses":10, "grain":15, "salt":10, "cattle":8, "vegetables":10, "wild_game":10, "woad":10, "dates":5, "olive":5, "honey":5}
    with open("coastal.txt") as file:
      coastalProvinces=[entry for line in file for entry in line.split()]
      # print(f'coastalProvinces = "{coastalProvinces}"')
      # return

  # test=random.choices(list(hillTradeGoods.keys()), list(hillTradeGoods.values()), k=1000)

  for i in range(len(provinceFile.names)):
    j=provinceFile.names[i]
    # if int(j) in [269,270,275,279,280,284,285,286,292,2719,111,112,113,114,115,116,117,118,120,239,722,2040,122,123,124,125,126,128,240,241,263,264,229,271,272,273,274,276,277,278,282,3912,119,121,261,262,265,266,267,268,323,320,321,322,361,314,765,981,255,257,258,259,260,330,331,334,338,795,333,335,337,340,342,792,797,1277,690,691,129,130,166,326,327,332,360,359,729,249,250,251,252,253,254,440]:
    #   if provinceFile.vals[i].get("culture").strip('"')=="jangovar":
    #     a.append(j)
    #   else:
    #     b.append(j)
    if j in forceTerrain:
      setTerrain(i, forceTerrain[j])
    culture=provinceFile.vals[i].get("culture").strip('"')
    terrain=provinceFile.vals[i].get("terrain").strip('"')
    is_impassable=(terrain=='impassable_terrain')
    if j in provinceNames:
      provinceFile.comments[i]="#"+provinceNames[ j]
      if len(provinceNamesInv[provinceNames[ j]])>1 and not is_impassable and not terrain=='coastal_terrain' and not j in uninhabitable:
        print(f'provinceNames[ j] = "{provinceNames[ j]}"')

    if terrain in ["plains","hills","mountain"] and not j in forceTerrain:
      # if terrainFile.count(j) and terrainFile.get(j)!="plains":
        # print(f'terrainFile.get(j) = "{terrainFile.get(j)}"')
        # print(f'j = "{j}"')
      jj=int(j)
      loc=provinceToCityLocation[jj]
      if loc is None:
        loc=provinceToLocation[jj]
      hCenter=heightMap.h(loc)
      hMax=hCenter
      hMin=hCenter
      hMaxClose=hCenter
      hMinClose=hCenter

      for dir in [0,2]:
        for s in range(-10,11):
          locB=copy(loc)
          locB[dir]+=s
          h=heightMap.h(locB)
          hMax=max(h, hMax)
          hMin=min(h, hMin)
          if abs(s)<6:
            hMaxClose=max(h, hMax)
            hMinClose=min(h, hMin)
      for dirA,dirB in [(0,2),(2,0)]:
        for s in range(-10,11):
          locB=copy(loc)
          locB[dirA]+=s/math.sqrt(2)
          locB[dirB]-=s/math.sqrt(2)
          h=heightMap.h(locB)
          hMax=max(h, hMax)
          hMin=min(h, hMin)
          if abs(s)<6:
            hMaxClose=max(h, hMax)
            hMinClose=min(h, hMin)

      if hMax>20 and hCenter>10 and hMax-hMin>7 and hMaxClose-hMinClose>5:
        setTerrain(i, "mountain")
        # provinceFile.vals[i].set("terrain",'"mountain"')
        # try:
        #   terrainFile.set(j, "mountain")
        # except:
        #   terrainFile.add(j, "mountain")
        # print(f'mountain[ j] = "{provinceNames[ j]}"')
      elif hMax>15 and hCenter>8 and hMax-hMin>3.5 and hMaxClose-hMinClose>2.5:
        setTerrain(i, "hills")
        # provinceFile.vals[i].set("terrain",'"hills"')
        # try:
        #   terrainFile.set(j, "hills")
        # except:
        #   terrainFile.add(j, "hills")
      else:
        setTerrain(i, "plains")
        # provinceFile.vals[i].set("terrain",'"plains"')
        # try:
        #   terrainFile.set(j, "plains")
        # except:
        #   terrainFile.add(j, "plains")
      # locB=provinceToFortLocation[jj]
      # if locB is None:
      # locB=provinceToCombatLocation[jj]

      # mo=20
      # hi=15
      # try:
      #   h2=heightMap.h(locB)
      # except:
      #   print(f'j = "{j}"')
      #   h2=h1

      # if (h1>mo or h2>mo) and abs(h1-h2)>3:
      #   provinceFile.vals[i].set("terrain",'"mountain"')
      #   try:
      #     terrainFile.set(j, "mountain")
      #   except:
      #     terrainFile.add(j, "mountain")
      #   # print(f'mountain[ j] = "{provinceNames[ j]}"')
      # elif (h1>hi or h2>hi) and abs(h1-h2)>2:
      #   provinceFile.vals[i].set("terrain",'"hills"')
      #   try:
      #     terrainFile.set(j, "hills")
      #   except:
      #     terrainFile.add(j, "hills")
        # print(f'hill[ j] = "{provinceNames[ j]}"')
      # else:
        # print(f'provinceNames[ j] = "{j} {provinceNames[ j]}:{heightMap.h(loc)}({loc})"')


    if addTradeGoods:
      # print(f'areasNeedTradeGoods = "{areasNeedTradeGoods}"')
      if j in provinceToArea and provinceToArea[j] in areasNeedTradeGoods and provinceFile.vals[i].get("trade_goods").strip('"')=="wild_game":
      # if j in provinceToRegion and provinceToRegion[j] in provinceNeedTradeGoods and provinceFile.vals[i].get("trade_goods").strip('"')=="wild_game":
        if terrain in ["desserts"]:
          provinceFile.vals[i].set("trade_goods",f'"{random.choices(list(dessertTadeGoods.keys()), list(dessertTadeGoods.values()))[0]}"')
        if terrain in ["hills","mountain"]:
          provinceFile.vals[i].set("trade_goods",f'"{random.choices(list(hillTradeGoods.keys()), list(hillTradeGoods.values()))[0]}"')
        elif terrain in ["forest","deep_forest"] or provinceToClimate[j] in "severe_winter":
          provinceFile.vals[i].set("trade_goods",f'"{random.choices(list(woodTradeGoods.keys()), list(woodTradeGoods.values()))[0]}"')
        elif j in coastalProvinces:
          while True:
            t=random.choices(list(coastalTradeGoods.keys()), list(coastalTradeGoods.values()))[0]
            #restrictions:
            if t in ["incense","dates","dye","spices","olive"] and not provinceToClimate[j]=="arid":
              continue
            if t in ["wine"] and provinceToClimate[j]=="normal_winter":
              continue
            if t in ["whale"] and provinceToClimate[j]=="arid":
              continue
            break
          provinceFile.vals[i].set("trade_goods",f'"{t}"')
        else:
          while True:
            t=random.choices(list(planeTradeGoods.keys()), list(planeTradeGoods.values()))[0]
            #restrictions:
            if t in ["dates","olive"] and not provinceToClimate[j]=="arid":
              continue
            if t in ["honey"] and provinceToClimate[j]=="arid":
              continue
            if t in ["horses","grain"] and terrain=="steppe":
              continue
            if t in ["steppe_horses"] and terrain!="steppe":
              continue
            break
          provinceFile.vals[i].set("trade_goods",f'"{t}"')


    if j in ownerCountry:
      provinceFile.comments[i]+=f" ({ownerCountry[j]})"
      if weakenSouthernGoblins:
        if ownerCountry[j]=="XLX":
          reduceTribesmen(j, provinceFile.vals[i], provinceToCapitalType, 4, 6)
        # and provinceFile.vals[i].count("tribesmen"):
        #   tribes=provinceFile.vals[i].get("tribesmen").get("amount")
        #   provinceFile.vals[i].get("tribesmen").set("amount",max(1,int(tribes)-randint(4,5)))
      if weakenAvari:
        if culture=="nandor":
          reduceTribesmen(j, provinceFile.vals[i], provinceToCapitalType, 3, 4)
        # and provinceFile.vals[i].count("tribesmen"):
        #   tribes=provinceFile.vals[i].get("tribesmen").get("amount")
        #   provinceFile.vals[i].get("tribesmen").set("amount",max(1,int(tribes)-randint(3,4)))

      if not provinceFile.vals[i].count("slaves"):
        ownedNoSlavesList.append(j)

      if provinceFile.vals[i].count("tribesmen") and not provinceFile.vals[i].count("slaves"):
        tribes=provinceFile.vals[i].get("tribesmen").get("amount")
        if int(tribes)>4:
          provinceFile.vals[i].get("tribesmen").set("amount",int(tribes)-1)
          # print(f'tribes = "{tribes}"')
        provinceFile.vals[i].addReturn("slaves").add("amount","1")
      # print(f'provinceFile.vals[i].get("culture") = "{provinceFile.vals[i].get("culture")}"')
      if strengthenSauron:
        if provinceFile.vals[i].count("tribesmen") and provinceFile.vals[i].get("culture").strip('"')=="orcish":
          tribes=provinceFile.vals[i].get("tribesmen").get("amount")
          provinceFile.vals[i].get("tribesmen").set("amount",int(tribes)+4)
      if strengthenCarnDum:
        # print(f'ownerCountry = "{ownerCountry}"')
        if provinceFile.vals[i].count("tribesmen") and ownerCountry[j]=="XXQ":
          tribes=provinceFile.vals[i].get("tribesmen").get("amount")
          provinceFile.vals[i].get("tribesmen").set("amount",int(tribes)+4)
      addCiv=0
      if provinceFile.vals[i].get("province_rank").strip('"') == "city":
        addCiv=5
      elif provinceFile.vals[i].get("province_rank").strip('"') == "city_metropolis":
        addCiv=10
      if culture in elven+dwarven and addCiv==0: #elven and dwarven settlement
        provinceFile.vals[i].set("civilization_value", 40)
      elif addCiv == 0 and int(provinceFile.vals[i].get("civilization_value"))>35:
        provinceFile.vals[i].set("civilization_value", 35)
      if culture in haladrin:
        if j!="1546": #Isengard
          provinceFile.vals[i].set("civilization_value", 10+addCiv)
      elif culture in haradrim:
        provinceFile.vals[i].set("civilization_value", 20+addCiv)
      elif culture == "harondorian":
        if ownerCountry[j]=="XXJ" or ownerCountry[j]=="XXK": #not tribal
          provinceFile.vals[i].set("civilization_value", 25+addCiv)
        else:
          provinceFile.vals[i].set("civilization_value", 15+addCiv)
      # if culture!=countryCulture[ownerCountry[j]]:
      #   print(f"{j} owned by {countryCulture[ownerCountry[j]]} but has {culture} culture")
      if culture=="beasts":
        provinceFile.vals[i].set("culture", f'"{countryCulture[ownerCountry[j]]}"')
        print(f"{j} owned but beast culture")
      if j in uninhabitable:
        print(f"{j} owned but uninhabitable")
    else:
      for area in ["thurl_ralian_fen_area","klyan_area","arg_simorig_area"]:
        if j in areaToProvince[area]:
          provinceFile.vals[i].set("culture",'"beasts"')
          for p in pops:
            try:
              provinceFile.vals[i].remove(p)
            except ValueError:
              pass
      if j in uninhabitable:
        provinceFile.comments[i]+=" (uninhabitable)"
        try:
          provinceFile.vals[i].set("trade_goods", '""')
        except ValueError:
          pass
        if testCold(j):
          harsh.names[harshUninhab]+=f" {j}"
      else:
        if is_impassable:
          provinceFile.comments[i]+=" (impassable)"
        else:
          provinceFile.comments[i]+=" (unowned)"
        if is_impassable and testCold(j):
          harsh.names[harshUnpass]+=f" {j}"
        # if not is_impassable:
      if not culture in ["silvan","stonefoot","ironfist"]:
        provinceFile.vals[i].set("civilization_value", 0)
      else:
        provinceFile.vals[i].set("civilization_value", 20)


        # if culture in ["yopi", "qarsag"]:
        #   if provinceFile.vals[i].count("tribesmen"):
        #     provinceFile.vals[i].get("tribesmen").set("amount",2)
        #   if provinceFile.vals[i].count("slaves"):
        #     provinceFile.vals[i].get("slaves").set("amount",1)
        # if culture in ["yopi"]:
        #   provinceFile.vals[i].set("civilization_value",15)
        if culture=="beasts":
          for pop in pops:
            if provinceFile.vals[i].count(pop):
              provinceFile.vals[i].remove(pop)
        elif culture and culture!="beasts" and culture !="spider" and not is_impassable:# or culture=="silvan":
          empty=True
          for pop in pops:
            if provinceFile.vals[i].count(pop):
              empty=False
          if empty:
            provinceFile.vals[i].set("culture",'"beasts"')
      if provinceFile.vals[i].count("nobles"):
        print(f"{j} unowned but nobles")
        # if provinceFile.vals[i].count("tribesmen") and not provinceFile.vals[i].count("slaves"):
        #   tribes=provinceFile.vals[i].get("tribesmen").get("amount")
        #   if int(tribes)>2:
        #     if culture in tooManyNonOwnedPops:
        #       provinceFile.vals[i].get("tribesmen").set("amount",2)
        #   elif int(tribes)>6:
        #     provinceFile.vals[i].get("tribesmen").set("amount",6)
        # elif provinceFile.vals[i].count("tribesmen")==0 and provinceFile.vals[i].count("slaves")==0 and provinceFile.vals[i].count("freemen")==0:
        #   if culture in tooFewNonOwnedPops:
        #     provinceFile.vals[i].addReturn("tribesmen").add("amount",2)
    if j in provinceToArea:
      provinceFile.comments[i]+=f" ({provinceToArea[j]})"
    if j in provinceToRegion:
      provinceFile.comments[i]+=f" ({provinceToRegion[j]})"
      # print(f'provinceNames[i] = "{provinceNames[ provinceFile.names[i]]}"')

  # provinceFile.writeAll(open("provinceFile.txt","w",encoding='utf-8-sig'),cdf.args(2))
  # countryFile.writeAll(open("countryFile.txt","w",encoding='utf-8-sig'),cdf.args(4))

  for no_s in ownedNoSlavesList:
    region=provinceToRegion[no_s]
    for core in countryProvinces[ownerCountry[no_s]]:
      if core in regionToProvince[region] and not core in ownedNoSlavesList:
        break
    else:
      print(f"{no_s} no slave in region {region} for {ownerCountry[no_s]}")

  for v in countryFile.get("family").get("families").vals:
    if type(v)==TagList:
      v.forceMultiLineOutput = True
  terrainFile.forceNoSpace = True
  terrainFile.sort(int,2)

  removeList=[]
  # countries = countryFile.get("country").get("countries")
  for provinceId, provinceContent in treasureFile.get("provinces").getNameVal():
    # print(f'provinceId = "{provinceId}"')
    localTreasures=provinceContent.get("treasure_slots").get("treasures")
    num=len(localTreasures.names)
    province=provinceFile.get(provinceId)
    if province.count("holy_site")==0:
      removeList.append(provinceId)
      country=countries.get(ownerCountry[provinceId])
      treasures=country.getOrCreate("treasures")
      for t in localTreasures.names:
        treasures.add(t)
      print(f'cannot hold any = "{provinceNames[provinceId]}". Moved to {ownerCountry[provinceId]}')
    elif num==2 and province.get("province_rank").strip('"') in ["settlement",""]:
      country=countries.get(ownerCountry[provinceId])
      treasures=country.getOrCreate("treasures")
      for t in localTreasures.names[1:]:
        treasures.add(t)
      localTreasures.names=localTreasures.names[:1]
      print(f'cannot hold two = "{provinceNames[provinceId]}". Moved to {ownerCountry[provinceId]}')
    elif num==3 and province.get("province_rank").strip('"') in ["city", "settlement",""]:
      country=countries.get(ownerCountry[provinceId])
      treasures=country.getOrCreate("treasures")
      for t in localTreasures.names[2:]:
        treasures.add(t)
      localTreasures.names=localTreasures.names[:2]
      print(f'cannot hold three = "{provinceNames[provinceId]}". Moved to {ownerCountry[provinceId]}')
  for p in removeList:
    treasureFile.get("provinces").remove(p)
    # print(f'province = "{province.names}"')


  print(" ".join(a))
  print("\n")
  print(" ".join(b))
  
  cdf.outputToFolderAndFile(provinceFile , "setup/provinces", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(countryFile , "setup/main", "00_default.txt" ,4,output_folder,False)
  cdf.outputToFolderAndFile(treasureFile , "setup/main", "lotr_treasures.txt" ,2,output_folder,False)
  cdf.outputToFolderAndFile(newClimate , "map_data", "climate.txt" ,4,output_folder,encoding="utf-8")
  cdf.outputToFolderAndFile(terrainFile , "common/province_terrain", "00_province_terrain.txt" ,2,output_folder,False,encoding="utf-8-sig")

  if makeTrees:
    def saveTrees(file, name, layer, mesh, treeList):
      br="{"
      br2="}"
      nl="\n"
      file.write(f"""object={br}
    name="{name}"
    clamp_to_water_level=no
    render_under_water=no
    generated_content=yes
    layer="{layer}"
    pdxmesh="{mesh}"
    count={len(treeList)}
    transform="{nl.join(treeList)}
  "{br2}
  """)
    with open("gfx/map/map_object_data/script_trees.txt", "w", encoding='utf-8-sig') as file:
      saveTrees(file, "oak_tree_by_script_A", oakLayer, oakA, oakTreeSplit[0])
      saveTrees(file, "oak_tree_by_script_B", oakLayer, oakB, oakTreeSplit[1])
      saveTrees(file, "oak_tree_by_script_C", oakLayer, oakC, oakTreeSplit[2])
      saveTrees(file, "pine_tree_by_script", treeLayer, pine, pineTrees)
  # with open("gfx/map/map_object_data/oak_tree_generator_3.txt",'w', encoding='utf-8-sig') as file:
  #   oakFile[7]=f"\tcount={len(oakFile)-8}\n"
  #   for line in oakFile:
  #     file.write(line)
  #   file.write('"}\n')
  # with open("gfx/map/map_object_data/pine_tree_generator_2.txt",'w', encoding='utf-8-sig') as file:
  #   pineFile[7]=f"\tcount={len(pineFile)-8}\n"
  #   for line in pineFile:
  #     file.write(line)
  #   file.write('"}\n')
  # cdf.outputToFolderAndFile(provinceFile , ".", "provinceFile.txt" ,2,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(countryFile , ".", "countryFile.txt" ,4,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(newClimate , ".", "climateFile.txt" ,4,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(areaFile , ".", "areaFile.txt" ,4,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(regionFile , ".", "regionFile.txt" ,4,".",encoding="utf-8-sig")


def reduceTribesmen(id, province, provinceToCapitalType, minRed, maxRed=None, stateCapitalFactor=0.5, capitalFactor=0):
  if maxRed is None:
    maxRed = minR
  if province.count("tribesmen"):
    factor = 1
    if id in provinceToCapitalType:
      if provinceToCapitalType[id]=="country_capital":
        factor=capitalFactor
      elif provinceToCapitalType[id]=="state_capital":
        factor = stateCapitalFactor
    tribes=province.get("tribesmen").get("amount")
    province.get("tribesmen").set("amount",max(1,int(int(tribes)-factor*randint(minRed,maxRed))))



class Unit:
  def __init__(self, name, category, attackFactor=1, armorFactor=1, moraleFactor=1, customRelation=None, AP=False):
    self.name=name
    self.category=category
    self.attackFactor=self.reducedFactor(4.0/3.0,attackFactor)
    self.armorFactor=armorFactor
    self.armorFactor=self.reducedFactor(2) #values chosen probably too high
    self.moraleFactor=moraleFactor
    self.customRelation=customRelation
    self.AP=AP
    self.foodFactor=0.1
    self.attritionFactor=0.1 #weight, not loss, might need to round up a bit?
  def reducedFactor(self, fac=2, armorFactor=None):
    if armorFactor is None:
      armorFactor=self.armorFactor
    return 1+(armorFactor-1)/fac
  def computeDamageVS(self, other, relations, properties):
    if other.category=="support":
      return 1
    relation=None
    if not self.customRelation is None:
      relation=self.customRelation
    elif self.category in relations:
      relation=relations[self.category]
    base = 0
    if not relation is None:
      if other.category in relation:
        base=relation[other.category]
    elif self.category == "support":
      base=-90
    baseFactor=1+base/100

    otherArmor=other.computeArmorFactor(properties) #support units are already excluded above
    if self.AP:
      otherArmor=other.reducedFactor(2, otherArmor)

    return round(baseFactor*self.attackFactor/otherArmor,2)
  def computeAllDamages(self,allUnits, relations, properties, data=None):
    # print(f"{self.name} = "+"{")
    lastType=""
    for other in allUnits:
      dmg=self.computeDamageVS(other, relations, properties)
      if abs(dmg-1)<1e-2:
        continue
      if data:
        if lastType!=other.category:
          data.addComment(other.category+":")
          lastType=other.category
        data.add(other.name, dmg)
      else:
        print(f"  {other.name} = {dmg} #{other.category}")
  def computeCosts(self, properties):
    properties=self.getProperties(properties)
    base=properties["cost"]
    if self.AP:
      base*=1.2
    return round(base*self.attackFactor*self.armorFactor*math.sqrt(self.moraleFactor)/3)
  def computeArmorFactor(self, properties):
    properties=self.getProperties(properties)
    base=1/(1-properties["strength"]/100)
    return base*self.armorFactor
  def computeStrengthDamageTaken(self, properties): #only for support units now. The rest is done via directly changing damage done by all units
    properties=self.getProperties(properties)
    base=(1-properties["strength"]/100)
    return round(base/self.armorFactor,2)
  def computeMoraleDamageTaken(self, properties):
    properties=self.getProperties(properties)
    base=properties["morale"]
    base=(1-base/100)
    return round(base/self.moraleFactor,2)

  def getProperties(self, properties):
    if self.name in properties:
      return properties[self.name]
    else:
      return properties[self.category]

  def assemble(self, relations, properties,allUnits):
    props=self.getProperties(properties)
    topTag=TagList(0)
    data=topTag.addReturn(self.name)
    data.add("army", "yes")
    # if props["assault"]:
    if self.category == "support":
      data.add("support", "yes")
      data.add("merc_cohorts_required", 4)
      if self.name == "engineer_cohort":
        data.add("reduces_road_building_cost", "yes")
        data.add("watercrossing_negation", "1.0")
        data.add("siege_impact", "1.0")
    data.add("assault", "yes" if props["assault"] else "no")
    data.add("levy_tier", props["levy_tier"] if "levy_tier" in props else "basic")
    if "tradeGood" in props:
      data.addReturn("allow").addReturn("trade_good_surplus").add("target", props["tradeGood"]).add("value",0,"", ">")
    if "flank" in props:
      data.add("is_flank", props["flank"])
    data.add("maneuver", props["maneuver"])
    data.add("movement_speed", props["speed"])
    data.add("build_time", props["cost"]) #no longer used?!
    self.computeAllDamages(allUnits, relations, properties, data)
    data.add("attrition_weight", round((100+props["attrition"])/100*self.attritionFactor,2))
    data.add("attrition_loss", props["attritionLoss"]/100)
    data.add("food_consumption", props["consumption"])
    data.add("food_storage", props["food"])
    if "ai_max_percentage" in props:
      data.add("ai_max_percentage", props["ai_max_percentage"])
    cost=data.addReturn("build_cost")
    cost.add("gold", self.computeCosts(properties))
    cost.add("manpower",1)
    if props["strength"]<0:
      data.add("strength_damage_taken", self.computeStrengthDamageTaken(properties))
    data.add("morale_damage_taken", self.computeMoraleDamageTaken(properties))




    return topTag


class ImageRead:
  def __init__(self, fileName):
    self.im = Image.open(fileName) # Can be many different formats.
    self.yM = self.im.size[1]
    self.pix = self.im.load()
  def p(self, x,y):
    return self.pix[x, self.yM-1-y]/1000
  def c(self, x,y):
    return self.pix[x, self.yM-1-y]
  def h(self, l):
    return self.p(l[0],l[2])
  def col(self, l):
    return self.c(l[0],l[2])
      # print(f"({x},{y}):{pix[x,im.size[1]-y]}")

def getProvinceToPixels(updateProvincePixels=False):
  if updateProvincePixels or not os.path.exists("assign.bin"):
    with open("map_data/definition.csv",'r') as file:
      provinceDefinitions=[line.strip().split(";") for line in file if len(line.split(";"))>1 and not line.startswith("#")]
    provinceToColor=[None for _ in provinceDefinitions]
    colorToProvince=dict()
    provinceToPixels=[ [] for _ in provinceDefinitions]

    def colorToString(l):
      s=""
      for e in l:
        s+=f"{e:03}"
      return s
    for line in provinceDefinitions:
      provinceToColor[int(line[0])]=list(map(int,line[1:4]))
      colorToProvince[colorToString(map(int,line[1:4]))]=int(line[0])
    # print(f'colorToProvince = "{colorToProvince}"')
    del provinceDefinitions
    provinceImage=ImageRead("map_data/provinces.png")
    xM=provinceImage.im.size[0]
    yM=provinceImage.im.size[1]
    pixelToProvince=[ -1 for _ in range(xM*yM)]
    riverImage=ImageRead("map_data/rivers.png")
    for i in range(xM):
      for j in range(yM):
        provinceId=colorToProvince[colorToString(provinceImage.c(i,j))]
        pixelToProvince[i*yM+j]=provinceId
        # print(f'riverImage.c(i,j) = "{riverImage.c(i,j)}"')
        valid=True
        for x in range(-1,2):
          for y in range(-1,2):
            ii=i+x
            jj=j+y
            if ii>=0 and ii<xM and jj>=0 and jj<yM and riverImage.c(ii,jj)<250:
              valid=False
        if valid:
        # if riverImage.c(i,j)>250:
          provinceToPixels[provinceId]+=(i,j)


    with open("assign.bin",'wb') as file:
      pickle.dump(provinceToPixels, file)
      pickle.dump(pixelToProvince, file)
      pickle.dump(xM, file)
      pickle.dump(yM, file)
  else:
    with open("assign.bin",'rb') as file:
      provinceToPixels = pickle.load(file)
      pixelToProvince = pickle.load(file)
      xM = pickle.load(file)
      yM = pickle.load(file)
  return provinceToPixels, pixelToProvince, xM, yM


  # im = im.convert("HSV")

if __name__ == "__main__":
  main()

