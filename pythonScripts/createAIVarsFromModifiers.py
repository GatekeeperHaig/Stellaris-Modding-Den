#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
from stellarisTxtRead import *
# import copy

def parse(argv):
  #print(argv)
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('inputfileName', )
  parser.add_argument('outputfileName', )
  addCommonArgs(parser)
  
  
  if isinstance(argv, str):
    argv=argv.split()
  args=parser.parse_args(argv)
  # args.t0_buildings=args.t0_buildings.split(",")
  

  
  return(args)

        
def main(args):
  varsToValue=TagList(0)
  inputTagList=TagList(0)
  inputTagList.readFileNew(args.inputfileName,args, varsToValue)
  outTagList=TagList(0)
  outTagList.add("check_planet_modifiers", TagList(1))
  # outTagTemplate=TagList(2)
  # outTagTemplate.add("limit", TagList(3).add("has_modifier","toFill"))
  # outTagTemplate.add("change_variable", TagList(3).add("which","toFill").add("value","toFill"))
  # outTagTemplate.addString("change_variable = { which = toFill value = toFill }")

  for name,val in inputTagList.getAll():
    if not isinstance(val, TagList):
      continue
    # val.printAll()
    newCheck=TagList(2).add("limit", TagList(3).add("has_modifier",name))
    for possibleModifierName, pmVal in val.getAll():
      if "tile_resource_" in possibleModifierName:
        # newCheck=copy.deepcopy(outTagTemplate)
        # newCheck.get("limit").replace("has_modifier",name)
        newCheck.add("change_variable", TagList(3).add("which",possibleModifierName.replace("tile_resource_","")).add("value",pmVal))
        # newCheck.get("change_variable").replace("which", possibleModifierName.replace("tile_resource_",""))
        # newCheck.get("change_variable").replace("value", pmVal)
        # outTagList.get("check_planet_modifiers").add("if", newCheck)
    if len(newCheck.names)>1:
      outTagList.get("check_planet_modifiers").add("if", newCheck)

  # outTagList.printAll()
  with open(args.outputfileName,'w') as file:
    outTagList.writeAll(file,args)
  #   inputTagList.writeEntry(file,0,args)
  #   namespace=inputTagList.vals[0]
  #   for i in range(1000):
  #     inputTagList.vals[1].replace("id", namespace+"."+str(i+1))
  #     inputTagList.writeEntry(file,1,args)


if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)