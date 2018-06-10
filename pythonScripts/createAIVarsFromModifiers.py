#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
import glob
from copy import deepcopy
from stellarisTxtRead import *
from custom_difficulty_files import *
# import copy

def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('inputFileNames', nargs = '*' )
  parser.add_argument('--output_folder',default="." )
  parser.add_argument('-n','--effect_name', default='check', help="The name that will be given to the generated scripted_effect")
  # parser.add_argument('-t','--type', default="trait", help="Type of objects that are used: 'has_<value>' will be the check. Not needed for planet based modifiers. Reasonable values are 'building'(default)/'blocker/trait' and possible others")
  # parser.add_argument('-a','--adjacency',action="store_true", help="qu")
  parser.add_argument('-d','--debug', action="store_true", help="Gives output when entries are ignored. Does not mean that this is an error, but you can check this if something you expect does not appear")
  parser.add_argument('--no_traits', action="store_true", help="Does NOT search for traits in given files")
  parser.add_argument('--no_buildings', action="store_true", help="Does NOT search for buildings in given files (for adjacency and planet bonuses)")
  parser.add_argument('--no_modifiers', action="store_true", help="Does NOT search for any static modifiers in given files. Supported at the time I write this: Pop and Planet modifier")
  parser.add_argument('--no_blocker', action="store_true", help="Does NOT search for adjacency bonus blockers in given files")
  parser.add_argument('--output_used_things_to_extra_file', action="store_true", help="ignores buildings since they are copied by BU anyway!")
  # parser.add_argument('--multiple_bonus_buildings', action="store_true", help="Check number of planet wide bonus buildings, rather than checking whether at least one exists on a planet.")
  # parser.add_argument('--traits', default=True, help="")
  if returnParser:
    return parser
  addCommonArgs(parser)
  
  
  args=parser.parse_args(argv)
  
  return(args)

traitsCollection=TagList()
modifierCollection=TagList()
blockerCollection=TagList()


def main(args,*unused):
  traitsCollection.clear()
  modifierCollection.clear()
  blockerCollection.clear()
  inputTagList=TagList()
  varList=TagList()
  outTagList=TagList()
  globbedList=[]
  for b in args.inputFileNames:
    globbedList+=glob.glob(b)

  effectFolder=args.output_folder+"/common/scripted_effects"
  outFileEffects=effectFolder+"/cgm_"+args.effect_name+"_ai_weight_API.txt"
  for inputFileName in globbedList:
    inputTagList.readFile(inputFileName,0,varList)

  funsToApply=[]

  outSubTagLists=[]
  triggerSets=[]
  if not args.no_traits:
    outSubTags=[]
    effect=TagList()
    outTagList.add("check_pop_traits_"+args.effect_name, effect)
    outSubTags.append(effect)
    bios=TagList("limit", TagList("is_robot_pop", "no"))
    effect.add("if", bios)
    outSubTags.append(bios)
    robots=TagList("limit", TagList("is_robot_pop", "yes"))
    effect.add("if", robots)
    outSubTags.append(robots)
    funsToApply.append(addTrait)
    outSubTagLists.append(outSubTags)
  if not args.no_modifiers:
    outSubTags=[]
    effect=TagList()
    outTagList.add("check_planet_modifiers_"+args.effect_name, effect)
    outSubTags.append(effect)
    effect=TagList()
    outTagList.add("check_pop_modifiers_"+args.effect_name, effect)
    outSubTags.append(effect)
    outSubTagLists.append(outSubTags)
    funsToApply.append(addStaticModifiers)
  if not args.no_buildings:
    outSubTags=dict()
    # name=args.effect_name+"_buildings_non_unique"
    # effect=TagList()
    # outTagList.add(name,TagList("every_tile",effect))
    # outSubTags[name]=effect

    # name=args.effect_name+"_buildings_unique"
    # effect=TagList()
    # outTagList.add(name,effect)
    # outSubTags[name]=effect

    # name=args.effect_name+"_buildings_adjacency"
    # effect=TagList()
    # ent=TagList()
    # outTagList.add(name, effect)
    # effect.add("every_neighboring_tile", ent)
    # outSubTags[name]=ent

    name="check_neighboring_adj_bonus_buildings_"+args.effect_name
    effect=TagList()
    outTagList.add(name, effect)
    outSubTags[name]=effect
    outSubTags["triggerSet_adjacency"]=set()
    triggerSets.append(outSubTags["triggerSet_adjacency"])

    # name=args.effect_name+"_buildings_triggered_non_unique"
    # effect=TagList()
    # outTagList.add(name,TagList("every_tile",effect))
    # outSubTags[name]=effect

    name="check_planet_bonus_buildings_"+args.effect_name
    effect=TagList()
    outTagList.add(name, effect)
    outSubTags[name]=effect

    outSubTags["triggerSet"]=set()
    triggerSets.append(outSubTags["triggerSet"])

    outSubTagLists.append(outSubTags)
    funsToApply.append(addBuildings)
  if not args.no_blocker:
    outSubTags=[]
    # effect=TagList()
    ent=TagList()
    outTagList.add("check_adj_bonus_blockers_"+args.effect_name, ent)
    # effect.add("every_neighboring_tile", ent)
    outSubTags.append(ent)
    outSubTagLists.append(outSubTags)
    funsToApply.append(addBlockers)

  for name,val in inputTagList.getNameVal():
      if not isinstance(val, TagList):
        continue
      for fun, outSubTag in zip(funsToApply, outSubTagLists):
        fun(outSubTag, name, val,args, varList)

  # #delete empty: Todo: make more general: Recursivly remove emptry "if"?
  # if not args.no_traits:
  #   check_traits=outTagList.get(args.effect_name+"_trait")
  #   for i in reversed(range(2)):
  #     ifTag=check_traits.getN_th("if", i)
  #     if len(ifTag)<2:
  #       check_traits.removeIndex(check_traits.n_thIndex("if", i))
  # for name in outTagList.names:
  #   if name[-10:]=="_adjacency":
  # # for adj in ["check_adjacency","check_blocker_adjacency"]:
  #     adjTag=outTagList.get(name)
  #     if len(adjTag.get("every_neighboring_tile"))==0:
  #       adjTag.remove("every_neighboring_tile")
  # for name,val in outTagList.getNameVal():
  #   if len(val)==0:
  #     outTagList.remove(name)

  def checkEmpty(item):
    name=item[0]
    val=item[1]
    if name=="if":
      for subName in val.names[1:]:
        if subName!="":
          return False
      return True
    if isinstance(val, TagList) and len(val)==0:
      return True
    else:
      return False
  outTagList.deleteOnLowestLevel(checkEmpty)

  # print(outTagList)
# 
  # if args.effect_name+"_buildings" in outTagList.names or args.effect_name+"_buildings_triggered" in outTagList.names:
  #   buildingTag=TagList()
  #   outTagList.insert(0,args.effect_name+"_building_planet_modifiers", buildingTag)
  #   if args.effect_name+"_buildings" in outTagList.names:
  #     buildingTag.add(args.effect_name+"_buildings", "yes")
  #   if args.effect_name+"_buildings_triggered" in outTagList.names:
  #     buildingTag.add(args.effect_name+"_buildings_triggered", "yes")

  triggerList=TagList()
  for i,triggerSet in enumerate(triggerSets):
    triggerContentA=TagList()
    triggerContentB=TagList()
    if i==0:
      nameAddition="adj_bonus"
    else:
      nameAddition="planet_bonus"
    triggerNameA="has_{}_{}_building".format(args.effect_name, nameAddition) #args.effect_name+"_building_trigger_new"
    triggerNameB="had_{}_{}_building".format(args.effect_name, nameAddition) #args.effect_name+"_building_trigger_new"
    # triggerNameB=args.effect_name+"_building_trigger_old"
    triggerList.add(triggerNameA, TagList("OR", triggerContentA))
    triggerList.add(triggerNameB, TagList("OR", triggerContentB))
    for building in sorted(triggerSet):
      triggerContentA.add("has_building", building)
      triggerContentB.add("has_prev_building", building)

  triggerList.deleteOnLowestLevel(checkTotallyEmpty)
  if len(triggerList)>0 and not args.test_run:
    triggerFolder=args.output_folder+"/common/scripted_triggers"
    if not os.path.exists(triggerFolder):
      os.makedirs(triggerFolder)
    triggerFile=triggerFolder+"/cgm_"+args.effect_name+"_ai_weight_scripted_trigger.txt"
    with open(triggerFile,"w") as file:
      triggerList.writeAll(file)

  if not args.test_run:
    if not os.path.exists(effectFolder):
      os.makedirs(effectFolder)
    with open(outFileEffects,'w') as file:
      outTagList.writeAll(file,args)

  if args.output_used_things_to_extra_file:
    if len(blockerCollection):
      outputToFolderAndFile(blockerCollection, "common/tile_blockers", "00_cgm_used_blockers_backup_{}.txt".format(args.effect_name),2, args.output_folder)
    if len(modifierCollection):
      outputToFolderAndFile(modifierCollection, "common/static_modifiers", "00_cgm_used_modifiers_backup_{}.txt".format(args.effect_name),2, args.output_folder)
    if len(traitsCollection):
      outputToFolderAndFile(traitsCollection, "common/traits", "00_cgm_used_traits_backup_{}.txt".format(args.effect_name),2, args.output_folder)

  # print(outFileEffects)
  return outFileEffects

def addTrait(outTags, name, val,args, varList): #outTags[0]: any outTags[1]: bio outTags[2]: robots 
  if not "modifier" in val.names:
    if args.debug:
      print("No modifier trait ignored: "+name)
    return
  if not "allowed_archetypes" in val.names:
    if args.debug:
      print("Invalid trait ignored: "+name)
    return
  cat=0
  # if "allowed_archetypes" in val.names:
  allArch=val.get("allowed_archetypes").names
  if "BIOLOGICAL" in allArch and not "ROBOT" in allArch and not "MACHINE" in allArch:
    cat=1
  if not "BIOLOGICAL" in allArch and ("ROBOT" in allArch  or "MACHINE" in allArch):
    cat=2
  prev=TagList()
  ifLoc=TagList("limit", TagList("has_trait", name)).add("prev", prev)
  if addFinalModifier(varList, val.get("modifier"), prev, "_planet_pop"):
    traitsCollection.add(name,val)
  # for modName, modVal in val.get("modifier").getNameVal():
  #   if "tile_resource_" in modName:
  #     prev.add("change_variable", TagList("which",modName.replace("tile_resource_","").replace("_add","_weight")+"_planet_pop").add("value",modVal))
  if len(prev)>0:
    outTags[cat].add("if", ifLoc)

def addStaticModifiers(outTags, name, val, args, varList):
  if "icon" in val.names: #possibly planet
    ifLoc=TagList("limit", TagList("has_modifier", name))
    if addFinalModifier(varList, val, ifLoc, "_planet_base"):
      modifierCollection.add(name,val)
    # for possibleModifierName, pmVal in val.getNameVal():
    #   if "tile_resource_" in possibleModifierName:
    #     ifLoc.add("change_variable", TagList(3).add("which",possibleModifierName.replace("tile_resource_","")).add("value",pmVal))
    if len(ifLoc)>1:
      outTags[0].add("if", ifLoc)
  elif name[:3]=="pop": #possibly pop
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_modifier", name)).add("prev", prev)
    if addFinalModifier(varList, val, prev,"_planet_pop"):
      modifierCollection.add(name,val)
    if len(prev)>0:
      outTags[1].add("if", ifLoc)
  else:
    if args.debug:
      print("Unassigned:"+name)

def addBuildings(outTags, name, val, args, varList):
  if (not args.no_traits or not args.no_blocker or not args.no_modifiers) and name[:8]!="building":
    if args.debug:
      print("Not used for building: "+name)
    return

  potential=val.attemptGet("destroy_if")
  if len(potential)==1:
    if potential.vals[0]=="yes":
      potential.vals[0]="no"
    elif potential.vals[0]=="no":
      potential.vals[0]="yes"
    else:
      potential=TagList("NOT", potential)
  elif len(potential)>1: #don't think this case will ever happen but who knows...
    potential=TagList("NAND", potential)
  if potential.getAnywhere("tile"): #ingore any potential with tile inside since we cannot/don't want to handle this
    potential.clear()

  if "adjacency_bonus" in val.names:
    tagName="check_neighboring_adj_bonus_buildings_"+args.effect_name
    processBuilding(varList, outTags, potential, val,name,"adjacency_bonus",False,tagName,"","tile_building_resource_" )

  if val.attemptGet("planet_unique")=="yes" or val.attemptGet("empire_unique")=="yes":
    buildingUnique=True
  else:
    buildingUnique=False


  if "planet_modifier" in val.names:
    processBuilding(varList, outTags, potential, val,name,"planet_modifier",buildingUnique,"check_planet_bonus_buildings_"+args.effect_name)
    
  triggeredNum=val.count("triggered_planet_modifier")
  if triggeredNum>0:
    for i in range(triggeredNum):
      tpm=val.getN_th("triggered_planet_modifier",i)
      tpmPotential=tpm.get("potential")
      # tpmPotential.addTagList(potential) #too much doubling stuff and hard to remove due to it being in triggers
      processBuilding(varList, outTags, tpmPotential, tpm,name, "modifier", buildingUnique,"check_planet_bonus_buildings_"+args.effect_name)

def processBuilding(varList, outTags, potential, val,name, modifierName, buildingUnique, tagName, extraName="_planet_building", searchFor="tile_resource_"):
  adjacencyCase=False
  if "_adj_bonus_" in tagName:
    adjacencyCase=True
    addHere=TagList()
    ifLoc=TagList("limit", TagList("has_building", name)).add("prevprev", addHere)
  elif buildingUnique:
    ifLoc=TagList("limit", TagList("has_building", name))
    addHere=ifLoc
  else:
    addHere=TagList()
    ifLoc=TagList("limit", TagList("has_building", name)).add("prev", addHere)

  potentialString=tagName+"_"+potential._toLine()
  if not potentialString in outTags:
    if len(potential)>0:
      outTags[potentialString]=TagList()
      outTags[potentialString].add("limit",potential)
      outTags[tagName].add("if", outTags[potentialString])
    else:
     outTags[potentialString]=outTags[tagName] #no potential stuff is directly written into the effect. This cannot be tpms
  specPotentialString=str(buildingUnique)+"_"+potentialString

  if not specPotentialString in outTags:
    if not buildingUnique:
      outTags[specPotentialString]=TagList()
      if not adjacencyCase:
        outTags[potentialString].addComment("NON_UNIQUE").add("every_tile", outTags[specPotentialString])
      else:
        outTags[potentialString].add("every_neighboring_tile", outTags[specPotentialString])
    else:
      outTags[specPotentialString]=outTags[potentialString]
      outTags[specPotentialString].addComment("UNIQUE")

  if addFinalModifier(varList, val.get(modifierName), addHere, extraName,searchFor):
    #added something:
    triggerSetName="triggerSet"
    if adjacencyCase:
      triggerSetName+="_adjacency"
    outTags[triggerSetName].add(name)
    outTags[specPotentialString].add("if", ifLoc)
    if not buildingUnique:
      elseTagList=TagList()
      outTags[specPotentialString].add("else", elseTagList) #fixed 2.1
      outTags[specPotentialString]=elseTagList

def addBlockers(outTags, name, val, args,varList):
  if not "spawn_chance" in val.names:# and not name[:2]==tb:
    if args.debug:
      print("Not used for tile blocker: "+name)
    return
  if "adjacency_bonus" in val.names:
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_blocker", name)).add("prevprev", prev)
    if addFinalModifier(varList, val.get("adjacency_bonus"), prev, "","tile_building_resource_"):
      blockerCollection.add(name,val)
    elseTagList=TagList()
    if len(prev)>0:
      outTags[0].add("if", ifLoc)
      outTags[0].add("else", elseTagList) #fixed 2.1
      outTags[0]=elseTagList 


def addFinalModifier(varList, input, output, extraName="", searchFor="tile_resource_"):
  addedSomething=False
  for modName, modVal in input.getNameVal():
    if searchFor in modName:
      if modVal[0]=="@" and modVal in varList.names:
        modVal=varList.get(modVal)
      output.add("change_variable", TagList("which",modName.replace(searchFor,"").replace("_add","_weight")+extraName).add("value",modVal))
      addedSomething=True
  return addedSomething


  




if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)