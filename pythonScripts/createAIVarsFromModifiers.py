#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
import glob
from stellarisTxtRead import *
# import copy

def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('inputFileNames', nargs = '*' )
  parser.add_argument('--output_folder',default="common/scripted_effect" )
  parser.add_argument('-n','--effect_name', default='check', help="The name that will be given to the generated scripted_effect")
  # parser.add_argument('-t','--type', default="trait", help="Type of objects that are used: 'has_<value>' will be the check. Not needed for planet based modifiers. Reasonable values are 'building'(default)/'blocker/trait' and possible others")
  # parser.add_argument('-a','--adjacency',action="store_true", help="qu")
  parser.add_argument('-d','--debug', action="store_true", help="Gives output when entries are ignored. Does not mean that this is an error, but you can check this if something you expect does not appear")
  parser.add_argument('--no_traits', action="store_true", help="Does NOT search for traits in given files")
  parser.add_argument('--no_buildings', action="store_true", help="Does NOT search for buildings in given files (for adjacency and planet bonuses)")
  parser.add_argument('--no_modifiers', action="store_true", help="Does NOT search for any static modifiers in given files. Supported at the time I write this: Pop and Planet modifier")
  parser.add_argument('--no_blocker', action="store_true", help="Does NOT search for adjacency bonus blockers in given files")
  # parser.add_argument('--multiple_bonus_buildings', action="store_true", help="Check number of planet wide bonus buildings, rather than checking whether at least one exists on a planet.")
  # parser.add_argument('--traits', default=True, help="")
  if returnParser:
    return parser
  addCommonArgs(parser)
  
  
  args=parser.parse_args(argv)
  
  return(args)


def main(args,*unused):
  inputTagList=TagList()
  outTagList=TagList()
  globbedList=[]
  for b in args.inputFileNames:
    globbedList+=glob.glob(b)

  outFile=args.output_folder+"/"+args.effect_name+"_ai_weight_static_effects.txt"
  for inputFileName in globbedList:
    inputTagList.readFile(inputFileName)

  funsToApply=[]

  outSubTagLists=[]
  if not args.no_traits:
    outSubTags=[]
    effect=TagList()
    outTagList.add(args.effect_name+"_trait", effect)
    outSubTags.append(effect)
    bios=TagList("limit", TagList("is robot_pop", "no"))
    effect.add("if", bios)
    outSubTags.append(bios)
    robots=TagList("limit", TagList("is robot_pop", "yes"))
    effect.add("if", robots)
    outSubTags.append(robots)
    funsToApply.append(addTrait)
    outSubTagLists.append(outSubTags)
  if not args.no_modifiers:
    outSubTags=[]
    effect=TagList()
    outTagList.add(args.effect_name+"_planet_modifier", effect)
    outSubTags.append(effect)
    effect=TagList()
    outTagList.add(args.effect_name+"_pop_modifier", effect)
    outSubTags.append(effect)
    outSubTagLists.append(outSubTags)
    funsToApply.append(addStaticModifiers)
  if not args.no_buildings:
    outSubTags=dict()
    name=args.effect_name+"_buildings_non_unique"
    effect=TagList()
    outTagList.add(name,TagList("every_tile",effect))
    outSubTags[name]=effect

    name=args.effect_name+"_buildings_unique"
    effect=TagList()
    outTagList.add(name,effect)
    outSubTags[name]=effect

    name=args.effect_name+"_buildings_adjacency"
    effect=TagList()
    ent=TagList()
    outTagList.add(name, effect)
    effect.add("every_neighboring_tile", ent)
    outSubTags[name]=ent

    name=args.effect_name+"_buildings_triggered_non_unique"
    effect=TagList()
    outTagList.add(name,TagList("every_tile",effect))
    outSubTags[name]=effect

    name=args.effect_name+"_buildings_triggered_unique"
    effect=TagList()
    outTagList.add(name, effect)
    outSubTags[name]=effect

    outSubTagLists.append(outSubTags)
    funsToApply.append(addBuildings)
  if not args.no_blocker:
    outSubTags=[]
    effect=TagList()
    ent=TagList()
    outTagList.add(args.effect_name+"_blocker_adjacency", effect)
    effect.add("every_neighboring_tile", ent)
    outSubTags.append(ent)
    outSubTagLists.append(outSubTags)
    funsToApply.append(addBlockers)

  for name,val in inputTagList.getNameVal():
      if not isinstance(val, TagList):
        continue
      for fun, outSubTag in zip(funsToApply, outSubTagLists):
        fun(outSubTag, name, val,args)

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
    if isinstance(val, TagList) and (len(val)==0 or name=="if" and len(val)==1):
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


  if not args.test_run:
    if not os.path.exists(args.output_folder):
      os.makedirs(args.output_folder)
    with open(outFile,'w') as file:
      outTagList.writeAll(file,args)
  print(outFile)
  return outFile

def addTrait(outTags, name, val,args): #outTags[0]: any outTags[1]: bio outTags[2]: robots 
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
  addFinalModifier(val.get("modifier"), prev, "_planet_pop")
  # for modName, modVal in val.get("modifier").getNameVal():
  #   if "tile_resource_" in modName:
  #     prev.add("change_variable", TagList("which",modName.replace("tile_resource_","").replace("_add","_weight")+"_planet_pop").add("value",modVal))
  if len(prev)>0:
    outTags[cat].add("if", ifLoc)

def addStaticModifiers(outTags, name, val, args):
  if "icon" in val.names: #possibly planet
    ifLoc=TagList("limit", TagList("has_modifier", name))
    addFinalModifier(val, ifLoc, "_planet_base")
    # for possibleModifierName, pmVal in val.getNameVal():
    #   if "tile_resource_" in possibleModifierName:
    #     ifLoc.add("change_variable", TagList(3).add("which",possibleModifierName.replace("tile_resource_","")).add("value",pmVal))
    if len(ifLoc)>1:
      outTags[0].add("if", ifLoc)
  elif name[:3]=="pop": #possibly pop
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_modifier", name)).add("prev", prev)
    addFinalModifier(val, prev,"_planet_pop")
    if len(prev)>0:
      outTags[1].add("if", ifLoc)
  else:
    if args.debug:
      print("Unassigned:"+name)

def addBuildings(outTags, name, val, args):
  if (not args.no_traits or not args.no_blocker or not args.no_modifiers) and name[:8]!="building":
    if args.debug:
      print("Not used for building: "+name)
    return
  if "planet_modifier" in val.names:
    if val.attemptGet("planet_unique")=="yes" or val.attemptGet("empire_unique")=="yes":
      tagName=args.effect_name+"_buildings_unique"
      ifLoc=TagList("limit", TagList("has_building", name))
      addHere=ifLoc
      addElse=False
    else:
      tagName=args.effect_name+"_buildings_non_unique"
      addHere=TagList()
      ifLoc=TagList("limit", TagList("has_building", name)).add("prev", addHere)
      addElse=True

    if addFinalModifier(val.get("planet_modifier"), addHere, "_planet_building"):
      #added something:
      outTags[tagName].add("if", ifLoc)
      if addElse:
        elseTagList=TagList()
        addHere.add("else", elseTagList)
        outTags[tagName]=elseTagList

  if "adjacency_bonus" in val.names:
    tagName=args.effect_name+"_buildings_adjacency"
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_building", name)).add("prevprev", prev)
    if addFinalModifier(val.get("adjacency_bonus"), prev, "","tile_building_resource_"):
      elseTagList=TagList()
      ifLoc.add("else", elseTagList)
      outTags[tagName].add("if", ifLoc)
      outTags[tagName]=elseTagList

  triggeredNum=val.count("triggered_planet_modifier")
  if triggeredNum>0:
    # print(val)
    if val.attemptGet("planet_unique")=="yes" or val.attemptGet("empire_unique")=="yes":
      tagName=args.effect_name+"_buildings_triggered_unique"
      ifLoc=TagList("limit", TagList("has_building", name))
      addHere=ifLoc
      addElse=False
    else:
      tagName=args.effect_name+"_buildings_triggered_non_unique"
      addHere=TagList()
      ifLoc=TagList("limit", TagList("has_building", name)).add("prev", addHere)
      addElse=True

    addedSomething=False
    for i in range(triggeredNum):
      tpm=val.getN_th("triggered_planet_modifier",i)
      addHere2=TagList("limit", tpm.get("potential"))
      addHere.add("if",addHere2 )
      if addFinalModifier(tpm.get("modifier"), addHere2, "_planet_bulding"):
        addedSomething=True

    if addedSomething:
      outTags[tagName].add("if", ifLoc)
      if addElse:
        elseTagList=TagList()
        ifLoc.add("else", elseTagList)
        outTags[tagName]=elseTagList


def addBlockers(outTags, name, val, args):
  if not "spawn_chance" in val.names:# and not name[:2]==tb:
    if args.debug:
      print("Not used for tile blocker: "+name)
    return
  if "adjacency_bonus" in val.names:
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_blocker", name)).add("prevprev", prev)
    addFinalModifier(val.get("adjacency_bonus"), prev, "","tile_building_resource_")
    elseTagList=TagList()
    ifLoc.add("else", elseTagList)
    if len(prev)>0:
      outTags[0].add("if", ifLoc)
      outTags[0]=elseTagList


def addFinalModifier(input, output, extraName="", searchFor="tile_resource_"):
  addedSomething=False
  for modName, modVal in input.getNameVal():
    if searchFor in modName:
      output.add("change_variable", TagList("which",modName.replace(searchFor,"").replace("_add","_weight")+extraName).add("value",modVal))
      addedSomething=True
  return addedSomething


  




if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)