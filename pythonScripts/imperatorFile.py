#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
import custom_difficulty_files as cdf
import math

def main():
  fileContent=TagList()

  races=["noldor", "teleri", "edain", "dwarf","orc"]
  raceGrowth={"noldor":-1,"teleri":-1,"edain":-0.8, "dwarf":-0.8,"orc":4}
  raceCombat={"noldor":1,"teleri":1,"edain":0.8, "dwarf":0.8,"orc":0}
  raceCommerce={"noldor":0.5,"teleri":.5,"edain":.5, "dwarf":1,"orc":0}
  # raceGrowth={"noldor":-1,"teleri":-1,"edain":-0.8, "dwarf":-0.8,"orc":4}

  for race in races:
    for i in range(1,11):
      t=fileContent.addReturn(f"{i*10}_{race}")
      if race!="orc":
        t.add("land_morale_modifier", round(i*0.04*raceCombat[race],3))
        t.add("land_morale_recovery", round(i*0.01*raceCombat[race],3))
        t.add("discipline", round(i*0.04*raceCombat[race],3))
        t.add("global_commerce_modifier", round(i*0.06*raceCommerce[race],3))
      t.add("global_population_growth", round(i*0.015*raceGrowth[race],3))

  # print(f'fileContent = "{fileContent}"')
  cdf.outputToFolderAndFile(fileContent , ".", "br_racial_modifiers.txt" ,2,".")

  # relations = { #VANILLA (ignoring camels)
    # "archers": { "archers":0, "chariots":0, "heavyCavalry":-10, "heavyInfantry":10, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":0 },
    # "chariots": { "archers":20, "chariots":0 ,"heavyCavalry":-50, "heavyInfantry":-10, "horseArchers":10, "lightCavalry":0, "lightInfantry":35, "elephants":-50},
    # "heavyCavalry": { "archers":50, "chariots":25, "heavyCavalry":0, "heavyInfantry":-10, "horseArchers":0, "lightCavalry":20, "lightInfantry":25, "elephants":-50},
    # "heavyInfantry": { "archers":0, "chariots":25, "heavyCavalry":20, "heavyInfantry":0, "horseArchers":-25, "lightCavalry":-10, "lightInfantry":20, "elephants":0},
    # "horseArchers": { "archers":25, "chariots":25, "heavyCavalry":-10, "heavyInfantry":25, "horseArchers":0 "lightCavalry":-10, "lightInfantry":25, "elephants":-20},
    # "lightCavalry": { "archers":25, "chariots":25, "heavyCavalry":-20, "heavyInfantry":-50, "horseArchers":25 "lightCavalry":0, "lightInfantry":25, "elephants":-50},
    # "lightInfantry": { "archers":-10, "chariots":-10, "heavyCavalry":-25, "heavyInfantry":-20, "horseArchers":-50 "lightCavalry":0, "lightInfantry":0, "elephants":-20},
    # "elephants": { "archers":50, "chariots":50, "heavyCavalry":-10, "heavyInfantry":40, "horseArchers":-10 "lightCavalry":-10, "lightInfantry":30, "elephants":0},
  # }

  relations = {
    "archers": { "archers":0, "chariots":0, "heavyCavalry":-10, "heavyInfantry":10, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":0 },
    "chariots": { "archers":20, "chariots":0 ,"heavyCavalry":-50, "heavyInfantry":-10, "horseArchers":10, "lightCavalry":0, "lightInfantry":35, "elephants":-50},
    "heavyCavalry": { "archers":50, "chariots":25, "heavyCavalry":0, "heavyInfantry":-10, "horseArchers":0, "lightCavalry":20, "lightInfantry":25, "elephants":-50},
    "heavyInfantry": { "archers":0, "chariots":25, "heavyCavalry":20, "heavyInfantry":0, "horseArchers":-25, "lightCavalry":-10, "lightInfantry":20, "elephants":0},
    "horseArchers": { "archers":25, "chariots":25, "heavyCavalry":-10, "heavyInfantry":25, "horseArchers":0, "lightCavalry":-10, "lightInfantry":25, "elephants":-20},
    "lightCavalry": { "archers":25, "chariots":25, "heavyCavalry":-20, "heavyInfantry":-50, "horseArchers":25, "lightCavalry":0, "lightInfantry":25, "elephants":-50},
    "lightInfantry": { "archers":-10, "chariots":-10, "heavyCavalry":-25, "heavyInfantry":-20, "horseArchers":-50, "lightCavalry":0, "lightInfantry":0, "elephants":-20},
    "elephants": { "archers":50, "chariots":50, "heavyCavalry":-10, "heavyInfantry":40, "horseArchers":-10, "lightCavalry":-10, "lightInfantry":30, "elephants":0},
  }
  properties = {
    "archers": { "cost":8, "assault":True, "speed":2.5, "maneuver":2, "morale":-30, "strength":0, "attrition":-10, "attritionLoss":5, "food":2.4, "consumption":0.1, "ai_max_percentage":15  },
    "chariots": { "cost":8, "assault":False, "speed":2.5, "maneuver":1, "morale":0, "strength":0, "attrition":0, "attritionLoss":5, "food":2.4, "consumption":0.2  },
    "heavyCavalry": { "cost":18, "assault":False, "speed":3.5, "maneuver":2, "morale":0, "strength":0, "attrition":100, "attritionLoss":5, "food":2.4, "consumption":0.25  },
    "heavyInfantry": { "cost":16, "assault":True, "speed":2.5, "maneuver":1, "morale":10, "strength":0, "attrition":50, "attritionLoss":5, "food":2.4, "consumption":0.2  },
    "horseArchers": { "cost":16, "assault":False, "speed":4, "maneuver":5, "morale":-25, "strength":0, "attrition":50, "attritionLoss":5, "food":3, "consumption":0.25  },
    "lightCavalry": { "cost":10, "assault":False, "speed":4, "maneuver":3, "morale":0, "strength":0, "attrition":50, "attritionLoss":5, "food":2.4, "consumption":0.25  },
    "lightInfantry": { "cost":8, "assault":True, "speed":2.5, "maneuver":1, "morale":30, "strength":0, "attrition":-50, "attritionLoss":2.5, "food":2.4, "consumption":0.1  },
    "elephants": { "cost":35, "assault":False, "speed":2.5, "maneuver":0, "morale":-20, "strength":50, "attrition":200, "attritionLoss":10, "food":1, "consumption":0.3  },
    "supply_train": { "cost":20, "assault":False, "speed":2.5, "maneuver":1, "morale":-100, "strength":0, "attrition":0, "attritionLoss":10, "food":50, "consumption":0.05  },
    "engineer_cohort": { "cost":40, "assault":False, "speed":2.5, "maneuver":1, "morale":-100, "strength":0, "attrition":0, "attritionLoss":10, "food":5, "consumption":0.05  },
    "rangers": { "cost":10, "assault":True, "speed":2.5, "maneuver":2, "morale":0, "strength":0, "attrition":-20, "attritionLoss":5, "food":2.4, "consumption":0.1  },
    "troll_infantry": { "cost":10, "assault":True, "speed":2.5, "maneuver":1, "morale":0, "strength":0, "attrition":150, "attritionLoss":5, "food":3, "consumption":0.3  },
  }

  units = [
    Unit("archers", "archers"), Unit("chariots", "chariots"), Unit("heavy_cavalry", "heavyCavalry"), Unit("heavy_infantry", "heavyInfantry"), Unit("horse_archers", "horseArchers"), Unit("light_cavalry", "lightCavalry"), Unit("light_infantry", "lightInfantry"), Unit("warelephant", "elephants"),Unit("supply_train", "support"),Unit("engineer_cohort", "support"),

    Unit("dol_amroth_knights", "heavyCavalry", 1.5, 2, 2),
    Unit("dwarven_goat_riders", "heavyCavalry", 2, 2, 2),
    Unit("dunedain_archers", "archers", 2.5, 1, 1.5),
    Unit("dwarven_archers", "archers", 1.5, 1.5, 1.5),
    Unit("elvish_archers", "archers", 3, 1.25, 1.5),
    Unit("uruk_crossbows", "archers", 1.5, 1, 1.25),
    Unit("dunedain_cavalry", "lightCavalry", 2.5, 1, 1.5),
    Unit("elvish_cavalry_archers", "horseArchers", 2.5, 1, 1.5),
    Unit("dunedain_infantry", "heavyInfantry", 1.5, 2, 2),
    Unit("dwarven_infantry", "heavyInfantry", 2, 2.5, 2),
    Unit("elvish_infantry", "heavyInfantry", 2.5, 2.25, 2.5),
    Unit("uruk_heavy_infantry", "heavyInfantry", 1.25, 1.5, 1.25),
    Unit("halfling_infantry", "lightInfantry", 0.75, 1, 1),
    Unit("orc_infantry", "lightInfantry", 1, 1, 0.5),
    Unit("uruk_infantry", "lightInfantry", 1.25, 1.25, 1),
    Unit("rangers", "alrounder", 2, 2, 1.5),
    Unit("troll_infantry", "alrounder", 3, 3, 2),
    # Unit("mumakils", "elephants", 3, 3, 2), ???
    Unit("warg_riders", "heavyCavalry", 1, 1, 1, { "archers":15, "chariots":30, "heavyCavalry":15, "heavyInfantry":-30, "horseArchers":15, "lightCavalry":30, "lightInfantry":0, "elephants":0 }),
  ]

  for unit in units:
    unit.computeAllDamages(units,relations)
    print(f"  cost = {unit.computeCosts(properties)}")
    print(f"  strength_damage_taken = {unit.computeArmor(properties)}")




class Unit:
  def __init__(self, name, category, attackFactor=1, armorFactor=1, moraleFactor=1, customRelation=None):
    self.name=name
    self.category=category
    self.attackFactor=attackFactor
    self.armorFactor=1+(armorFactor-1)/2
    self.moraleFactor=moraleFactor
    self.customRelation=customRelation
    self.foodFactor=0.1
    self.attritionFactor=0.01 #weight, not loss, might need to round up a bit?
  def computeDamageVS(self, other, relations):
    relation=None
    if not self.customRelation is None:
      relation=self.customRelation
    elif self.category in relations:
      relation=relations[self.category]
    base = 0
    if not relation is None:
      if other.category in relation:
        base=relation[other.category]
      elif other.category=="support":
        base = 100
    elif self.category == "support":
      base=-90
    baseFactor=1+base/100
    return round(baseFactor*self.attackFactor,2)
  def computeAllDamages(self,allUnits, relations):
    print(f"{self.name} = "+"{")
    for other in allUnits:
      dmg=self.computeDamageVS(other, relations)
      # if abs(dmg-1)<1e-2:
      #   continue
      print(f"  {other.name} = {dmg} #{other.category}")
  def computeCosts(self, properties):
    properties=self.getProperties(properties)
    base=properties["cost"]
    return round(base*self.attackFactor*self.armorFactor*math.sqrt(self.moraleFactor)/3)
  def computeArmor(self, properties):
    properties=self.getProperties(properties)
    base=(1-properties["strength"]/100)
    return round(base/self.armorFactor,2)

  def getProperties(self, properties):
    if self.name in properties:
      return properties[self.name]
    else:
      return properties[self.category]



if __name__ == "__main__":
  main()

