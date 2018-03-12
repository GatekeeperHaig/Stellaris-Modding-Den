#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
from stellarisTxtRead import *
# import copy

def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('inputFileNames', nargs = '*' )
  parser.add_argument('--output_folder',default="common/scripted_effect" )
  parser.add_argument('-n','--effect_name', default='check_planet_modifier', help="The name that will be given to the generated scripted_effect")
  parser.add_argument('-t','--type', default="building", help="Type of objects that are used: 'has_<value>' will be the check. Not needed for planet based modifiers. Reasonable values are 'building'(default)/'blocker' and possible others")
  # parser.add_argument('-a','--adjacency',action="store_true", help="qu")
  if returnParser:
    return parser
  addCommonArgs(parser)
  
  
  args=parser.parse_args(argv)
  
  return(args)

        
def main(args,*unused):
  outFile=""
  for inputFileName in args.inputFileNames:
    varsToValue=TagList(0)
    inputTagList=TagList(0)
    inputTagList.readFile(inputFileName,args, varsToValue)
    outTagList=TagList(0)
    outTagList.add(args.effect_name, TagList(1))

    for name,val in inputTagList.getAll():
      if not isinstance(val, TagList):
        continue
      # val.printAll()
      newCheck=TagList(2).add("limit", TagList(3).add("has_modifier",name))
      newCheckBuildingModifier=TagList(2).add("limit", TagList(3).add("has_"+args.type,name))
      newCheckAdjModifier=TagList(2).add("limit", TagList(3).add("has_"+args.type,name)).add("prev",TagList(3))

      for possibleModifierName, pmVal in val.getAll():
        if "tile_resource_" in possibleModifierName:
          newCheck.add("change_variable", TagList(3).add("which",possibleModifierName.replace("tile_resource_","")).add("value",pmVal))
      if "planet_modifier" in val.names:
        # print("NAME"+name)
        # val.printAll()
        for possPlanetModName, ppmVal in val.get("planet_modifier").getAll():
         if "tile_resource_" in possPlanetModName:
           newCheckBuildingModifier.add("change_variable", TagList(3).add("which",possPlanetModName.replace("tile_resource_","").replace("_add","_weight")).add("value",ppmVal))
      if "adjacency_bonus" in val.names:
        for possPlanetModName, ppmVal in val.get("adjacency_bonus").getAll():
          if "tile_building_resource_" in possPlanetModName:
            newCheckAdjModifier.get("prev").add("change_variable", TagList(4).add("which",possPlanetModName.replace("tile_building_resource_","").replace("_add","_weight")).add("value",ppmVal))

      if len(newCheck.names)>1:
        outTagList.get(args.effect_name).add("if", newCheck)
      if len(newCheckBuildingModifier.names)>1:
        outTagList.get(args.effect_name).add("if", newCheckBuildingModifier)
      if len(newCheckAdjModifier.get("prev").names)>0:
        outTagList.get(args.effect_name).add("every_neighboring_tile", newCheckAdjModifier)
    outFile=args.output_folder+"/"+os.path.basename(inputFileName).replace("txt","ai_weight_static_effects.txt")
    if not args.test_run:
      if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
      with open(outFile,'w') as file:
        outTagList.writeAll(file,args)
  return outFile



if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)