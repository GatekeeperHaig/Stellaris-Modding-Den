#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
import custom_difficulty_files as cdf
import math
import yaml
from yaml.loader import SafeLoader
from locList import LocList


def main():
  fileContent=TagList()

  locClass=LocList()
  locClass.limitLanguage(["en"])

  races=["Noldor", "Teleri", "Edain", "Dwarf","Orc"]
  raceGrowth={"Noldor":-1.2,"Teleri":-1.2,"Edain":-0.8, "Dwarf":-1,"Orc":1}
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
      t.add("global_population_growth", round(i*0.015*raceGrowth[race],3))
      locClass.addEntry(name, f"{i*10}% {race}")
      locClass.addEntry("desc_"+name, raceDesc[race])

  for i in reversed(range(1,20)):
    name=f"foreign_support_{i*5}"
    t=fileContent.addReturn(name)
    t.add("levy_size_multiplier",round(0.05*i,2))
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
  cdf.outputToFolderAndFile(fileContent , ".", "common/modifiers/br_racial_modifiers.txt" ,2,".", encoding="utf-8-sig")
  cdf.outputToFolderAndFile(lotr_pops , ".", "events/lotr_pops.txt" ,1,".", encoding="utf-8-sig")

  relations = {
    "archers":        { "archers":0, "chariots":0, "heavyCavalry":-10, "heavyInfantry":10, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":0 },
    "chariots":       { "archers":20, "chariots":0 ,"heavyCavalry":-50, "heavyInfantry":-10, "horseArchers":10, "lightCavalry":0, "lightInfantry":35, "elephants":-50},
    "heavyCavalry":   { "archers":50, "chariots":25, "heavyCavalry":0, "heavyInfantry":-10, "horseArchers":0, "lightCavalry":20, "lightInfantry":25, "elephants":-50},
    "heavyInfantry":  { "archers":0, "chariots":25, "heavyCavalry":20, "heavyInfantry":0, "horseArchers":-25, "lightCavalry":-10, "lightInfantry":20, "elephants":0},
    "horseArchers":   { "archers":25, "chariots":25, "heavyCavalry":-10, "heavyInfantry":25, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":-20},
    "lightCavalry":   { "archers":25, "chariots":25, "heavyCavalry":-20, "heavyInfantry":-50, "horseArchers":25, "lightCavalry":0, "lightInfantry":25, "elephants":-50},
    "lightInfantry":  { "archers":-10, "chariots":-10, "heavyCavalry":-25, "heavyInfantry":-20, "horseArchers":-50, "lightCavalry":0, "lightInfantry":0, "elephants":-20},
    "elephants":      { "archers":50, "chariots":50, "heavyCavalry":-10, "heavyInfantry":40, "horseArchers":-10, "lightCavalry":-10, "lightInfantry":30, "elephants":0},
  }
  properties = {
    "archers":        { "cost":8, "assault":True, "speed":2.5, "maneuver":2, "morale":-30, "strength":0, "attrition":-10, "attritionLoss":5, "food":2.4, "consumption":0.1, "ai_max_percentage":15  },
    "chariots":       { "cost":8, "assault":False, "speed":2.5, "maneuver":1, "morale":0, "strength":0, "attrition":0, "attritionLoss":5, "food":2.4, "consumption":0.2  },
    "heavyCavalry":   { "cost":18, "assault":False, "speed":3.5, "maneuver":2, "morale":0, "strength":0, "attrition":100, "attritionLoss":5, "food":2.4, "consumption":0.25, "tradeGood":"horses", "levy_tier":"advanced" },
    "heavyInfantry":  { "cost":16, "assault":True, "speed":2.5, "maneuver":1, "morale":10, "strength":0, "attrition":50, "attritionLoss":5, "food":2.4, "consumption":0.2, "tradeGood":"iron", "levy_tier":"advanced" },
    "horseArchers":   { "cost":16, "assault":False, "speed":4, "maneuver":5, "morale":-25, "strength":0, "attrition":50, "attritionLoss":5, "food":3, "consumption":0.25, "tradeGood":"steppe_horses"  },
    "lightCavalry":   { "cost":10, "assault":False, "speed":4, "maneuver":3, "morale":0, "strength":0, "attrition":50, "attritionLoss":5, "food":2.4, "consumption":0.25, "tradeGood":"horses"  },
    "lightInfantry":  { "cost":8, "assault":True, "speed":2.5, "maneuver":1, "morale":30, "strength":0, "attrition":-50, "attritionLoss":2.5, "food":2.4, "consumption":0.1  },
    "elephants":      { "cost":35, "assault":False, "speed":2.5, "maneuver":0, "morale":-20, "strength":50, "attrition":200, "attritionLoss":10, "food":1, "consumption":0.3, "tradeGood":"elephants", "levy_tier":"advanced", "ai_max_percentage":15  },
    "supply_train":   { "cost":20, "assault":False, "speed":2.5, "maneuver":1, "morale":-100, "strength":-100, "attrition":0, "attritionLoss":10, "food":50, "consumption":0.05, "ai_max_percentage":15  },
    "engineer_cohort":{ "cost":40, "assault":False, "speed":2.5, "maneuver":1, "morale":-100, "strength":-100, "attrition":0, "attritionLoss":10, "food":5, "consumption":0.05, "ai_max_percentage":15  },
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
    cdf.outputToFolderAndFile(d , ".", f"common/units/army_{unit.name}.txt" ,2,".",encoding="utf-8-sig")

    # unit.computeAllDamages(units,relations,properties)
    # print(f"  cost = {unit.computeCosts(properties)}")
    # if unit.category=="support":
    # print(f"  morale_damage_taken = {unit.computeMoraleDamageTaken(properties)}")
  # return

  provinceNames={}
  with open("localization/english/provincenames_l_english.yml",encoding='utf-8-sig') as f:
    for line in f.readlines():
      # print(line)
      split=line.split()
      key=split[0]
      # print(f'key = "{key}"')
      key=key.replace("PROV", "").replace(":0", "")
      # print(f'key = "{key}"')
      rest=" ".join(split[1:]).replace('"', "")
      # print(f'rest = "{rest}"')
      provinceNames[key]=rest


  provinceFile=TagList(0)
  provinceFile.readFile("setup/provinces/00_default.txt",encoding='utf-8-sig')
  countryFile=TagList(0)
  countryFile.readFile("setup/main/00_default.txt",encoding='utf-8-sig')
  climateFile=TagList(0)
  climateFile.readFile("map_data/climate.txt",encoding='utf-8')
  areaFile=TagList(0)
  areaFile.readFile("map_data/areas.txt",encoding='utf-8')
  regionFile=TagList(0)
  regionFile.readFile("map_data/regions.txt",encoding='utf-8')
  # cdf.outputToFolderAndFile(climateFile , ".", "climateFile.txt" ,4,".",encoding="utf-8-sig")

  # print(f'climateFile.vals[0].names = "{climateFile.vals[0].names}"')

  # print(f'climateFile.names = "{climateFile.names}"')
  # print(f'climateFile.seperators = "{climateFile.seperators}"')
  # print(f'climateFile.get("mild_winter") = "{climateFile.get("mild_winter")}"')
  # print(f'climateFile.get("mild_winter").names = "{climateFile.get("mild_winter").names}"')



  uninhabitable = set(map(str,list(range(4969,4988))+list(range(5453,5459))+list([52,2616,577,564,563,576,575,604,605,606,607,608,602,603,2696,2697,2698,2607,2604,2605,3402,3403,3404,476,475,478,479,2961,2960,2959,2954,2955,2984,2985,2986,540,539,538,537,536,535,547,546,545,544,543,542,2617,594,595,596,597,94,27,95,91,92,581,582,2046,2045,2044,87,85,89,88,83,82,80,2375,2376,7,3,17,23,48,1965,583,584,585,586,587,588,589,590,2997,2998,3000,3001,2988,2991,2989,2992,2994,3003,2990,2995,2996,2993,3002,579,578,2048,2049,2050,2051,2052,2053,593,3142,3143,3146,3144,3145,3147,3148,3149,3150,51,2378,2377,3638,3639,3678,3679,3680,3681,3682,3683,3684,3685,3686,3687,3688,3689,3690,3691,3692,3693,3694,3593,3709,3719,3611,3613,3612,3653,3654,3656,3660,3718,3626,3659,3706,3607,3608,3609,3740,3741,3742,3743,3744,3745,3746,3747,3787,3781,3779,3778,3777,3784,3793,3794,3792,3790,3789,3791,3775,3776,3771,3795,3797,2730,2731,2732,2733,2739,2737,2741,2735,2740,2742,2745,2744,2743,3860,3862,3863,3864,3865,3866,3874,3867,3881,3871,3869,3552,3553,3880,3879,3868,3872,3873,3870,3554,2738,2750,2749,2748,2747,2746,2751,3875,2729,2769,2728,3582,3581,3580,3643,3637,3904,3909,3910,3937,3938,3939,5215,5217,5218,5174,5176,5291,5292,5293,5300,5301,5302,5303,5304,5305,5306,5307,5308,5309,5310,5311,5312,5313,5314,5315,5317,5318,5319,5320,5321,5322,5323,5324,5326,5327,5328,5329,5330,5331,5332,5333,5334,5336,5337,5338,5339,5340,5341,5342,5343,5344,5345,5348,5386,5387,5388,5389,5390,5433,5434,5435,5399,5400,5401,5378,5379,5375,5274,5275,5276,5277,5278,5281,5279,5282,5283,5406,5429,5430,5297,5298,5299,5437,5023,5024,5443,5444,5445,5446,5447,5448,5449,5450,5451,5067,5463,5396,5395,5409,5280,5462,5466,5284,5286,5287,5294,5296,5452,5410,5411,5412,5216,5252,5285,5288,5060,5273])))

  # print(f'uninhabitable = "{uninhabitable}"')


  countries=countryFile.get("country").get("countries")
  # ownedProvinces=set()
  ownerCountry=dict()
  countryCulture=dict()
  for name,vals in zip(countries.names, countries.vals):
    # print(f'vals = "{vals}"')
    if vals=="":
      continue
    cores=vals.get("own_control_core")
    countryCulture[name]=vals.get("primary_culture")
    # print(f'cores = "{cores.vals}"')
    for core in cores.names:
      # ownedProvinces.add(core)
      ownerCountry[core]=name
    # print(f'cores = "{cores}"')


  provinceToArea=dict()
  areaToRegion=dict()
  provinceToRegion=dict()
  regionToArea=dict()
  areaToProvince=dict()

  for name, val in areaFile.getNameVal():
    if name:
      for p in val.get("provinces").names:
        provinceToArea[p]=name
        if not name in areaToProvince:
          areaToProvince[name]=[]
        areaToProvince[name].append(p)
  for name, val in regionFile.getNameVal():
    if name:
      for p in val.get("areas").names:
        areaToRegion[p]=name
        if not name in regionToArea:
          regionToArea[name]=[]
        regionToArea[name].append(p)
  for province, area in provinceToArea.items():
    if area in areaToRegion:
      provinceToRegion[province]=areaToRegion[area]

  provinceToTerrain=dict()
  for name, val in provinceFile.getNameVal():
    if name:
      provinceToTerrain[name]=val.get("terrain")

  newClimate=TagList(0)
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
  # forceClimate["tulwang_region"]="arid"
  # forceClimate["khailuza_region"]="arid"
  # forceClimate["kykurian_kyn_region"]="arid"
  # forceClimate["kargagis_ahar_region"]="arid"
  # forceClimate["gathgykarkan_region"]="arid"
  # forceClimate["anarike_region"]="arid"
  # forceClimate["yopi_region"]="arid"
  # forceClimate["nikkea_region"]="arid"
  # forceClimate["shay_region"]="arid"
  # forceClimate["lokhas_drus_region"]="arid"
  # forceClimate["ibav_region"]="arid"
  # forceClimate["wer_falin_region"]="arid"
  # forceClimate["ralian_region"]="arid"
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
      region=provinceToRegion[province]
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

  def removeComment(t):
    if type(t)==TagList:
      for i in range(len(t.comments)):
        t.comments[i]=""
  def empty(t):
    return t[0]=='' and t[1]=='' and t[2]==''

  strengthenSauron=False
  strengthenCarnDum=False
  provinceFile.applyOnAllLevel(removeComment)
  provinceFile.deleteOnLowestLevel(empty)
  tooManyNonOwnedPops=[ "balchoth", "rachoth", "nurnim", "variag", "nuriag", "khundolar", "jangovar", "yarlung", "tsang", "haradrim", "qarsag", "siranian", "yopi", "shayna", "mumakanim", "tulwany"]
  tooFewNonOwnedPops=[ "stonefoot", "stiffbeard"]
  pops=["slaves", "tribesmen", "freemen", "citizen", "nobles"]
  for i in range(len(provinceFile.names)):
    j=provinceFile.names[i]
    if j in provinceNames:
      provinceFile.comments[i]="#"+provinceNames[ j]
      culture=provinceFile.vals[i].get("culture").strip('"')
    # if not j in ownedProvinces:
    #   provinceFile.comments[i]+=" (unowned)"
    if j in ownerCountry:
      provinceFile.comments[i]+=f" ({ownerCountry[j]})"
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
      # if culture!=countryCulture[ownerCountry[j]]:
      #   print(f"{j} owned by {countryCulture[ownerCountry[j]]} but has {culture} culture")
      if culture=="beasts":
        provinceFile.vals[i].set("culture", f'"{countryCulture[ownerCountry[j]]}"')
        print(f"{j} owned but beast culture")
      if j in uninhabitable:
        print(f"{j} owned but uninhabitable")
    else:
      if j in uninhabitable:
        provinceFile.comments[i]+=" (uninhabitable)"
      else:
        provinceFile.comments[i]+=" (unowned)"
        if culture=="beasts":
          for pop in pops:
            if provinceFile.vals[i].count(pop):
              provinceFile.vals[i].remove(pop)
        elif culture=="goblins" or culture=="silvan":
          empty=True
          for pop in pops:
            if provinceFile.vals[i].count(pop):
              empty=False
          if empty:
            provinceFile.vals[i].set("culture",'"beasts"')
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

  cdf.outputToFolderAndFile(provinceFile , ".", "setup/provinces/00_default.txt" ,2,".",False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(newClimate , ".", "map_data/climate.txt" ,4,".",encoding="utf-8")
  # cdf.outputToFolderAndFile(provinceFile , ".", "provinceFile.txt" ,2,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(countryFile , ".", "countryFile.txt" ,4,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(newClimate , ".", "climateFile.txt" ,4,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(areaFile , ".", "areaFile.txt" ,4,".",encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(regionFile , ".", "regionFile.txt" ,4,".",encoding="utf-8-sig")







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
    data.add("assault", "yes" if props["assault"] else "no")
    data.add("levy_tier", "advanced" if "levy_tier" in props else "basic")
    if "tradeGood" in props:
      data.addReturn("allow").addReturn("trade_good_surplus").add("target", props["tradeGood"]).add("value",0,"", ">")
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



if __name__ == "__main__":
  main()

