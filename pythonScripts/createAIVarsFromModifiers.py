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
  # parser.add_argument('--traits', default=True, help="")
  if returnParser:
    return parser
  addCommonArgs(parser)
  
  
  args=parser.parse_args(argv)
  
  return(args)

        
def mainOld(args,*unused):
  outFile=""
  for inputFileName in args.inputFileNames:
    varsToValue=TagList(0)
    inputTagList=TagList(0)
    inputTagList.readFile(inputFileName,args, varsToValue)
    outTagList=TagList(0)
    outTagList.add(args.effect_name, TagList(1))

    for name,val in inputTagList.getNameVal():
      # print(val.name)
      if not isinstance(val, TagList):
        continue
      # val.printAll()
      newCheck=TagList(2).add("limit", TagList(3).add("has_modifier",name))
      newCheckBuildingModifier=TagList(2).add("limit", TagList(3).add("has_"+args.type,name))
      newCheckAdjModifier=TagList(2).add("limit", TagList(3).add("has_"+args.type,name)).add("prevprev",TagList(3))
      newCheckBio=TagList("limit", TagList("is robot_pop", "no"))

      for possibleModifierName, pmVal in val.getNameVal():
        # print(possibleModifierName)
        if "tile_resource_" in possibleModifierName:
          newCheck.add("change_variable", TagList(3).add("which",possibleModifierName.replace("tile_resource_","")).add("value",pmVal))

      #BUILDINGS!
      if "planet_modifier" in val.names:
        # print("NAME"+name)
        # val.printAll()
        for modName, modVal in val.get("planet_modifier").getNameVal():
         if "tile_resource_" in modName:
           newCheckBuildingModifier.add("change_variable", TagList(3).add("which",modName.replace("tile_resource_","").replace("_add","_weight")+"_planet_base").add("value",modVal))
      #TRAITS     
      if "trait" in args.type:
        # print("NAME"+name)
        # val.printAll()
        try:
          for modName, modVal in val.get("modifier").getNameVal():
            if "tile_resource_" in modName:
              newCheckBuildingModifier.add("change_variable", TagList(3).add("which",modName.replace("tile_resource_","").replace("_add","_weight")+"_planet_pop").add("value",modVal))
        except:
          print("No modifiers for "+name)
      if "adjacency_bonus" in val.names:
        for modName, modVal in val.get("adjacency_bonus").getNameVal():
          if "tile_building_resource_" in modName:
            newCheckAdjModifier.get("prevprev").add("change_variable", TagList(4).add("which",modName.replace("tile_building_resource_","").replace("_add","_weight")).add("value",modVal))

      if len(newCheck.names)>1:
        outTagList.get(args.effect_name).add("if", newCheck)
      if len(newCheckBuildingModifier.names)>1:
        outTagList.get(args.effect_name).add("if", newCheckBuildingModifier)
      if len(newCheckAdjModifier.get("prevprev").names)>0:
        outTagList.get(args.effect_name).add("every_neighboring_tile", newCheckAdjModifier)
    outFile=args.output_folder+"/"+os.path.basename(inputFileName).replace("txt","ai_weight_static_effects.txt")
    if not args.test_run:
      if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
      with open(outFile,'w') as file:
        outTagList.writeAll(file,args)
  return outFile

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
    outSubTags=[]
    effect=TagList()
    outTagList.add(args.effect_name+"_buildings", effect)
    outSubTags.append(effect)
    effect=TagList()
    ent=TagList()
    outTagList.add(args.effect_name+"_adjacency", effect)
    effect.add("every_neighboring_tile", ent)
    outSubTags.append(ent)
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

  #todo: delete empty!

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
    addFinalModifier(val, ifLoc)
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
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_building", name)).add("prev", prev)
    addFinalModifier(val.get("planet_modifier"), prev, "_planet_base")
    elseTagList=TagList()
    ifLoc.add("else", elseTagList)
    if len(prev)>0:
      outTags[0].add("if", ifLoc)
      outTags[0]=elseTagList
  if "adjacency_bonus" in val.names:
    prev=TagList()
    ifLoc=TagList("limit", TagList("has_building", name)).add("prevprev", prev)
    addFinalModifier(val.get("adjacency_bonus"), prev, "","tile_building_resource_")
    elseTagList=TagList()
    ifLoc.add("else", elseTagList)
    if len(prev)>0:
      outTags[1].add("if", ifLoc)
      outTags[1]=elseTagList

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
  for modName, modVal in input.getNameVal():
    if searchFor in modName:
      output.add("change_variable", TagList("which",modName.replace(searchFor,"").replace("_add","_weight")+extraName).add("value",modVal))


  




if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)