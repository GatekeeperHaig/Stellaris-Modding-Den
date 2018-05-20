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

ET = "event_target:cgm_var_storage"
eventNameSpace="core_game_mechanics_and_ai_base.{!s}"
eventNames="core_game_mechanics_and_ai_base_{!s}"
def main():
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  debugMode=True

  changeSteps = [50, 20, 10]
  for s in reversed(changeSteps):
    changeSteps.append(-s)
  bonusNames=[]
  bonusNames.append(["planet_building"])
  bonusNames.append(["capital_building","empire_unique_building","planet_unique_building","military_building","standard_resource_building","research_resource_building","unity_resource_building","special_resource_building","replicator_building", "all"])
  bonusPictures=["GFX_CGM_buildings_menu" for entry in bonusNames]
  cats=["build_speed_mult","build_cost_mult"]

  modifierFuns=dict()
  modifierFuns["build_speed_mult"]=lambda i: 10*i
  modifierFuns["build_cost_mult"]=lambda i: 10*i

  modifierRange=dict()
  modifierRange["build_speed_mult"]=[-10, 10] #[0]*10 to [1]*10
  modifierRange["build_cost_mult"]=[-10, 10] #[0]*10 to [1]*10
  # buildSpeedBonus=[[entry+"_construction_speed_mult"] for entry in bonusNames if entry !="all"]
  # buildCostBonus=[[entry+"_build_cost_mult"] for entry in bonusNames if entry !="all"]
  # buildSpeedBonus.append(reduce(lambda x,y: x+y, buildSpeedBonus))
  # buildCostBonus.append(reduce(lambda x,y: x+y, buildCostBonus))

  # possibleBoniPictures=["GFX_evt_mining_station","GFX_evt_dyson_sphere","GFX_evt_animal_wildlife", "GFX_evt_think_tank", "GFX_evt_unity_symbol","GFX_evt_arguing_senate","GFX_evt_hangar_bay", "GFX_evt_debris", "GFX_evt_sabotaged_ship","GFX_evt_pirate_armada","GFX_evt_fleet_neutral","GFX_evt_city_ruins","GFX_evt_metropolis"]





  # # doTranslation=True
  doTranslation=1
  locList=LocList(doTranslation)
  locList.addLoc("build_speed_mult", "Building Construction Speed")
  locList.addLoc("build_cost_mult", "Building Costs")
  locList.addLoc("capital_building","Capital Buildings")
  locList.addLoc("empire_unique_building","Empire Unique Buildings")
  locList.addLoc("planet_unique_building","Planet Unique Buildings")
  locList.addLoc("military_building","Military Buildings")
  locList.addLoc("standard_resource_building","Standard Resource Buildings")
  locList.addLoc("research_resource_building","Research Buildings")
  locList.addLoc("unity_resource_building","Unity Buildings")
  locList.addLoc("special_resource_building","Special Resource Buildings")
  locList.addLoc("replicator_building","Replicator Buildings")
  locList.addLoc("all","All Buildings")
  locList.addLoc("planet_building","All Buildings")


  locList.addLoc("mainTitle","Advanced Building Configuration")
  locList.addLoc("mainDesc","Here you can change global costs and build speed of building groups (or all buildings)")
  locList.addLoc("changeDesc1", "Here you can change global")
  locList.addLoc("changeDesc2", "of building groups (or all buildings)")
  locList.addLoc("change", "Change")
  locList.addLoc("changeBy", "Change by")
  locList.addLoc("enableBU", "Enable Direct Construction of High Tier Buildings")
  locList.addLoc("disableBU", "Disable Direct Construction of High Tier Buildings")

  locList.addLoc("build_speed_mult", "Скорость строительства зданий","ru")
  locList.addLoc("build_cost_mult", "Затраты на строительство","ru")
  locList.addLoc("capital_building","главные здания","ru")
  locList.addLoc("empire_unique_building","уникальные здания Империи","ru")
  locList.addLoc("planet_unique_building","уникальные планетарные здания","ru")
  locList.addLoc("military_building","военные здания","ru")
  locList.addLoc("standard_resource_building","стандартные ресурсные здания","ru")
  locList.addLoc("research_resource_building","научные здания","ru")
  locList.addLoc("unity_resource_building","здания единства","ru")
  locList.addLoc("special_resource_building","специальные ресурсные здания","ru")
  locList.addLoc("replicator_building","здания-репликаторы","ru")
  locList.addLoc("all","все здания","ru")
  locList.addLoc("planet_building","все здания","ru")


  locList.addLoc("mainTitle","Продвинутое конфигурирование зданий","ru")
  locList.addLoc("mainDesc","Здесь можно изменить стоимость и скорость постройки для отдельных групп зданий (или для всех сразу)","ru")
  locList.addLoc("changeDesc1", "Здесь можно изменить глобальную","ru")
  locList.addLoc("changeDesc2", "групп зданий (или всех зданий)","ru")
  locList.addLoc("change", "Изменить","ru")
  locList.addLoc("changeBy", "Изменить на","ru")
  locList.addLoc("enableBU", "Включить прямую постройку зданий высокого уровня","ru")
  locList.addLoc("disableBU", "Выключить прямую постройку зданий высокого уровня","ru")



  locList.addLoc("build_speed_mult", "Velocidade de Construção","pt")
  locList.addLoc("build_cost_mult", "Custos de Construção","pt")
  locList.addLoc("capital_building","Construção de Capital","pt")
  locList.addLoc("empire_unique_building","Construções únicas do Império","pt")
  locList.addLoc("planet_unique_building","Construções únicas do Planeta","pt")
  locList.addLoc("military_building","Construções Militares","pt")
  locList.addLoc("standard_resource_building","Construções de Recursos Básicas","pt")
  locList.addLoc("research_resource_building","Construções de Pesquisa","pt")
  locList.addLoc("unity_resource_building","Construções de Unidade","pt")
  locList.addLoc("special_resource_building","Construções de Recursos Especiais","pt")
  locList.addLoc("replicator_building","Construções de Replicadores","pt")
  locList.addLoc("all","Todas as Construções","pt")
  locList.addLoc("planet_building","Todas as Construções","pt")

  locList.addLoc("mainTitle","Configuração Avançada de Construções","pt")
  locList.addLoc("mainDesc","Aqui você pode alterar os custos globais e velocidade de construção dos grupos de construções (ou de todas as construções)","pt")
  locList.addLoc("changeDesc1", "Aqui você pode mudar a global","pt")
  locList.addLoc("changeDesc2", "dos grupos de construções (ou de todas as construções)","pt")
  locList.addLoc("change", "Alterar","pt")
  locList.addLoc("changeBy", "Alterar por","pt")
  locList.addLoc("enableBU", "Ativar a construção direta de edifícios de alto nível","pt")
  locList.addLoc("disableBU", "Desativar a construção direta de edifícios de alto nível","pt")
  # print(locList.dicts['ru'])

  locList.addLoc("build_speed_mult", "Baugeschwindigkeit Gebäude","de")
  locList.addLoc("build_cost_mult", "Gebäudekosten","de")
  locList.addLoc("capital_building","Verwaltungsgebäude","de")
  locList.addLoc("empire_unique_building","Reichseinzigartige Gebäude","de")
  locList.addLoc("planet_unique_building","Einzigartige Gebäude","de")
  locList.addLoc("military_building","Militärische Gebäude","de")
  locList.addLoc("standard_resource_building","Gewöhnliche Ressourcengebäude","de")
  locList.addLoc("research_resource_building","вorschungsgebäude","de")
  locList.addLoc("unity_resource_building","Einheitsgebäude","de")
  locList.addLoc("special_resource_building","Spezielle Ressourcengebäude","de")
  locList.addLoc("replicator_building","Replikator Gebäude","de")
  locList.addLoc("all","Alle Gebäude","de")
  locList.addLoc("planet_building","Alle Gebäude","de")


  locList.addLoc("mainTitle","Fortgeschrittne Gebäude Konfiguration","de")
  locList.addLoc("mainDesc","Hier können globale Kosten und Baugeschwindigkeiten von Gebäudegruppen (oder allen Gebäuden) verändert werden.","de")
  locList.addLoc("changeDesc1", "Hier können globale","de")
  locList.addLoc("changeDesc2", "von Gebäudegruppen (oder allen Gebäude) verändert werden.","de")
  locList.addLoc("change", "Ändern:","de")
  locList.addLoc("changeBy", "Ändern um","de")
  locList.addLoc("enableBU", "Direktes Bauen von hochstufigen Gebäuden aktivieren","de")
  locList.addLoc("disableBU", "Direktes Bauen von hochstufigen Gebäuden deaktivieren","de")







  # locList.addEntry("custom_difficulty_current_bonuses","@curBon:")

  # # locList.addEntry(, [])
  # # locList.addEntry(, [])







  name_mainMenuEvent="core_game_mechanics_and_ai_base.10"
  name_countryUpdateEvent="core_game_mechanics_and_ai_base.19"
  name_updateEvent="core_game_mechanics_and_ai_base.18"
  id_subMainMenuEvent=11 #reserved 11 and 12
  id_Change=[20,30]  #reserved range up to 39
  id_removeModifiers=40  #reserved range up to 41
  id_addModifiers=50  #reserved range up to 51

  buildingOptionsFile=TagList("namespace","core_game_mechanics_and_ai_base")
  mainMenu=TagList("id", name_mainMenuEvent)
  mainMenu.add("is_triggered_only", "yes")
  mainMenu.add("custom_gui","cgm_buildings_advanced_configuration").add("diplomatic","yes").add("force_open", "no") 

  mainMenu.add("title", locList.append(eventNames.format("main_event.name"), "@mainTitle"))
  mainMenu.add("desc", locList.append(eventNames.format("main_event.desc"), "@mainDesc"))
  mainMenu.add("picture_event_data", TagList("room","cgm_menu_room"))
  buildingOptionsFile.addComment("main menu")
  buildingOptionsFile.add("country_event", mainMenu)
  for catI,cat in enumerate(cats):
    mainSubMenu=TagList("id", eventNameSpace.format(id_subMainMenuEvent+catI))
    mainSubMenu.add("is_triggered_only", "yes")
    mainSubMenu.add("custom_gui","cgm_buildings_advanced_configuration").add("diplomatic","yes").add("force_open", "no")
    mainSubMenu.add("title", locList.append(eventNames.format(cat+"_event.name"), "@change @{}".format(cat)))
    mainSubMenu.add("desc", locList.append(eventNames.format(cat+"_event.desc"), "@changeDesc1 @{} @changeDesc2".format(cat)))
    mainSubMenu.add("picture_event_data", TagList("room","cgm_menu_room"))
    buildingOptionsFile.addComment(cat)
    buildingOptionsFile.add("country_event", mainSubMenu)
    mainMenu.add("option", TagList("name", eventNames.format(cat+"_event.name")).add("custom_gui","cgm_option").add("hidden_effect", TagList("country_event", TagList("id",eventNameSpace.format(id_subMainMenuEvent+catI)))))

    # for bonusI,bonus,bonusName in zip(range(len(bonuses)),bonuses, bonusNames):
    for bonusI,bonusName in enumerate(bonusNames[catI]):
      bonusMenu=TagList("id", eventNameSpace.format(id_Change[catI]+bonusI))
      bonusMenu.add("is_triggered_only", "yes")
      bonusMenu.add("custom_gui","cgm_buildings_advanced_configuration").add("diplomatic","yes").add("force_open", "no")
      bonusMenu.add("title", locList.append(eventNames.format("{}_{}_event.name".format(cat, bonusName)), "@change @{}".format(bonusName)))
      bonusMenu.add("desc", locList.append(eventNames.format("{}_{}_event.desc".format(cat, bonusName)), "@change @{}: @{}".format(cat,bonusName)))
      bonusMenu.add("picture_event_data", TagList("room","cgm_menu_room"))
      buildingOptionsFile.addComment(bonusName+" "+cat)
      buildingOptionsFile.add("country_event", bonusMenu)
      mainSubMenu.add("option", TagList("name", eventNames.format("{}_{}_event.name".format(cat, bonusName))).add("custom_gui","cgm_option").add("hidden_effect", TagList("country_event", TagList("id",eventNameSpace.format(id_Change[catI]+bonusI)))))
      for changeStep in changeSteps:
        optName=locList.append(eventNames.format("change_"+str(changeStep).replace("-", "neg")), "@changeBy {}%".format(changeStep))
        bonusMenu.add("option", TagList("name", optName).add("custom_gui","cgm_option").add("hidden_effect", TagList("country_event", TagList("id",eventNameSpace.format(id_Change[catI]+bonusI))).add(ET, TagList("change_variable", TagList("which", "cgm_{}_{}_value".format(cat, bonusName)).add("value", changeStep)))))
      bonusMenu.add("option", TagList("name", "BACK").add("custom_gui","cgm_option").add("hidden_effect", TagList("country_event", TagList("id",eventNameSpace.format(id_subMainMenuEvent+catI)))))
      bonusMenu.add("option", TagList("name", "cgm_main_menu.close.name").add("custom_gui","cgm_option").add("country_event", TagList("id",name_updateEvent)))
    mainSubMenu.add("option", TagList("name", "BACK").add("custom_gui","cgm_option").add("custom_gui","cgm_option").add("hidden_effect", TagList("country_event", TagList("id",name_mainMenuEvent))))
    mainSubMenu.add("option", TagList("name", "cgm_main_menu.close.name").add("custom_gui","cgm_option").add("country_event", TagList("id",name_updateEvent)))
  
  mainMenu.add("option", TagList("name", locList.addEntry("enable_direct_build.name", "@enableBU")).add("custom_gui", "cgm_option").add("trigger", TagList("not", TagList("has_global_flag", "direct_build_enabled"))).add("hidden_effect", TagList("set_global_flag", "direct_build_enabled").createEvent(name_mainMenuEvent)))
  mainMenu.add("option", TagList("name", locList.addEntry("disable_direct_build.name", "@disableBU")).add("custom_gui", "cgm_option").add("trigger", TagList("has_global_flag", "direct_build_enabled")).add("hidden_effect", TagList("remove_global_flag", "direct_build_enabled").createEvent(name_mainMenuEvent)))
  # mainMenu.add("option", TagList("name", locList.addEntry("enable_direct_build.name", "@enableBU")).add("custom_gui", "cgm_option").add("trigger", TagList("not", TagList("has_global_flag", "direct_build_enabled"))).add("hidden_effect", TagList("set_global_flag", "direct_build_enabled").add("remove_global_flag", "display_low_tier_flag").add("remove_global_flag", "do_no_remove_low_tier_flag").createEvent(name_mainMenuEvent)))
  # mainMenu.add("option", TagList("name", locList.addEntry("disable_direct_build.name", "@disableBU")).add("custom_gui", "cgm_option").add("trigger", TagList("has_global_flag", "direct_build_enabled")).add("hidden_effect", TagList("remove_global_flag", "direct_build_enabled").add("set_global_flag", "display_low_tier_flag").add("set_global_flag", "do_no_remove_low_tier_flag").createEvent(name_mainMenuEvent)))
  mainMenu.add("option", TagList("name", "BACK").add("custom_gui","cgm_option").add("hidden_effect", TagList("country_event", TagList("id",eventNameSpace.format(1))).add("country_event", TagList("id",name_updateEvent))))
  mainMenu.add("option", TagList("name", "cgm_main_menu.close.name").add("custom_gui","cgm_option").add("country_event", TagList("id",name_updateEvent)))

  updateEvent=TagList("id", name_updateEvent)
  buildingOptionsFile.add("event", updateEvent)
  updateEvent.add("is_triggered_only","yes")
  updateEvent.add("hide_window","yes")
  updateEvent.add("immediate", TagList("every_country", TagList("country_event", TagList("id", name_countryUpdateEvent))))

  # buildingOptionsFile.printAll()
  outputToFolderAndFile(buildingOptionsFile, "events", "cgm_buildings_modifiers.txt", level=2, modFolder="../CGM/buildings_script_source")


  removeModifierImmediates=dict()
  name_removeModifiers=dict()
  for cat in cats:
    removeModifierImmediates[cat]=TagList()
  addModifierImmediates=dict()
  name_addModifiers=dict()  
  for cat in cats:
    addModifierImmediates[cat]=TagList()


  removeEvents=TagList("namespace", "core_game_mechanics_and_ai_base")
  addEvents=TagList("namespace", "core_game_mechanics_and_ai_base")




  createModifierEvents(removeModifierImmediates,name_removeModifiers,removeEvents,id_removeModifiers,False, eventNameSpace) 
  createModifierEvents(addModifierImmediates,name_addModifiers,addEvents, id_addModifiers,True, eventNameSpace) 

  updateFile=TagList()
  updateFile.add("namespace","core_game_mechanics_and_ai_base")
  staticModifiers=TagList()

  # for groupUpdate in [False,True]:
  updateEvent=TagList()
  updateFile.add("country_event",updateEvent)
  updateEvent.add("id", name_countryUpdateEvent)
  updateEvent.add("is_triggered_only",yes)
  updateEvent.add("hide_window",yes)
  immediate=TagList()
  updateEvent.add("immediate",immediate)
  after=TagList()
  # updateEvent.add("after",after)
  for catI,cat in enumerate(cats):
    bonusModifiers=[[entry+"_"+cat] for entry in bonusNames[catI] if entry !="all"]
    if "all" in bonusName[catI]:
      bonusModifiers.append(reduce(lambda x,y: x+y, bonusModifiers))
    immediate.addComment(cat)
    # ifTagList=TagList()
    # immediate.add("if",ifTagList)
    # limit=TagList()
    # ifTagList.add("limit",limit)


    for bonusName, bonusModifier in zip(bonusNames[catI],bonusModifiers):
      changedFlag="cgm_{}_{}_changed".format(cat, bonusName)
      varName="cgm_{}_{}_value".format(cat, bonusName)
      ifChanged=TagList("limit", TagList("not", 
        TagList("check_variable", 
          TagList("which",varName)
          .add("value", ET))))
      immediate.add("if",ifChanged)
      ifChanged.add("set_country_flag", changedFlag)
      ifChanged.add("set_variable", TagList().add("which", varName).add("value", ET))

      # if cat in modifierCats: #only create the modifier for these cats. Rest use the same as one of those!
        
      removeIFChanged=TagList("limit", TagList("has_country_flag", changedFlag))
      addIFChanged=deepcopy(removeIFChanged)

      removeModifierImmediates[cat].add("if",removeIFChanged)
      addModifierImmediates[cat].add("if",addIFChanged)


      addIFChanged.add("remove_country_flag",changedFlag )
      tmpVar="cgm_tmp"
      addIFChanged.add("set_variable",TagList("which", tmpVar).add("value",varName))


      for i in range(modifierRange[cat][0],modifierRange[cat][1]+1):
        #compare signs and stop for i==0
        if i<0:
          compSign="<"
          sign=-1
          signName="neg"
        elif i>0:
          compSign=">"
          sign=1
          signName="pos"
        else:
          continue
        i=abs(i)
        changeVal=modifierFuns[cat](i)
        ifModifierApplied=TagList()
        if sign>0:
          addIFChanged.insert(addIFChanged.names.index("if"),"if", ifModifierApplied)
        else:
          addIFChanged.add("if", ifModifierApplied)
        ifModifierApplied.add("limit",TagList().add("check_variable",
          TagList().add("which",tmpVar)
          .add("value", str(sign*(changeVal-0.1)),"",compSign)))
        modifierName=locList.append("cgm_{:02d}_{}_{}_{}_value".format(i,bonusName,signName,cat), "@"+cat+": @"+bonusName)
        modifier=TagList()
        if not isinstance(bonusModifier,list):
          bonusModifier=[bonusModifier]
        for modifierEntry in bonusModifier:
          # if bonus=="upkeep":
          #   modifier.add(modifierEntry,str(-sign*changeVal/100))
          # else:
            modifier.add(modifierEntry,str(sign*changeVal/100))
        staticModifiers.add(modifierName,modifier)
        ifModifierApplied.add("add_modifier", TagList().add("modifier",modifierName).add("days","-1"))
        removeIFChanged.add("remove_modifier", modifierName)
        ifModifierApplied.add("change_variable",TagList().add("which",tmpVar).add("value", str(-1*sign*changeVal)))

  # for cat in cats:
    ifCat=TagList("limit", TagList("has_country_flag",eventNameSpace.format("")[:-1]+"_{}_modifier_active".format(cat)))
    ifCat.add("country_event", TagList("id", name_removeModifiers[cat]))
    immediate.addComment("removing {} bonuses if they exist".format(cat))
    immediate.add("if", ifCat)
    immediate.addComment("adding {} bonuses".format(cat))
    immediate.add("country_event", TagList("id", name_addModifiers[cat]))
  # immediate.addTagList(after)
  outputToFolderAndFile(updateFile, "events", "cgm_buildings_modifiers_update.txt", level=2, modFolder="../CGM/buildings_script_source")
  outputToFolderAndFile(removeEvents, "events", "cgm_buildings_modifiers_remove.txt", level=2, modFolder="../CGM/buildings_script_source")
  outputToFolderAndFile(addEvents, "events", "cgm_buildings_modifiers_add.txt", level=2, modFolder="../CGM/buildings_script_source")
  outputToFolderAndFile(staticModifiers, "common/static_modifiers", "cgm_buildings_modifiers.txt", level=2, modFolder="../CGM/buildings_script_source")


  for language in locList.languages:
    outFolderLoc="../CGM/buildings_script_source/localisation/"+language
    if not os.path.exists(outFolderLoc):
      os.makedirs(outFolderLoc)
    locList.write(outFolderLoc+"/cgm_building_customize_l_"+language+".yml",language)

if __name__ == "__main__":
  main()