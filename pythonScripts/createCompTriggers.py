#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
import glob
from stellarisTxtRead import *
from custom_difficulty_files import *
# import copy

def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="Parses a Stellaris Format File and searches for triggers to create: Star classes, Planet Classes, special resources", formatter_class=RawTextHelpFormatter)
  parser.add_argument('fileNames', nargs = '*' )
  parser.add_argument("--output_folder", default=".", help="do not include common/scripted_triggers as that is added by default!")
  # parser.add_argument('--remove_tags', default="", help="Comma separated list of tags that should be fully removed from the file")
  # parser.add_argument('--replacement_file', default="", help="Executes a very basic conditional replace on buildings. Example: 'IF unique in tagName and is_listed==no newline  ai_weight = { weight = @crucial_2 }': For all buildings that have 'unique' in their name and are not listed, set ai_weight to given value. Any number of such replaces can be in the file. An 'IF' at the very start of a line starts a replace. the next xyz = will be the tag used for replacing. You can also start a line with 'EVAL' instead of 'IF' to write an arbitrary condition. You need to know the class structure for this though.")
  parser.add_argument('-j','--join_files', default="", help="Output from all input files goes into a single file. Give non-empty input as filename/path to store to.")
  # parser.add_argument('-c','--check_if_else', action="store_true", help="checks all input files for incorrect 'pre 2.1 else'. Will not output anything except errors in that respect. Not sure to find all problems! There are cases where stuff is right with regard to the old and new system, but has different meaning. It correct trivial ones.")
  # parser.add_argument('-e','--else_if', action="store_true", help="Turns obvious else={if={}} into else_if")
  if returnParser:
    return parser
  addCommonArgs(parser)
  
  
  args=parser.parse_args(argv)
  
  return(args)


def main(args,*unused):
  lastOutFile=""
  tagList=TagList()
  globbedList=[]
  for b in args.fileNames:
    globbedList+=glob.glob(b)

  for i,fileName in enumerate(globbedList):
    outTag=TagList()
    tagList.readFile(fileName)
    if args.join_files!="" and i<len(globbedList)-1:
      continue
    if args.join_files!="":
      outputFileName=args.join_files
    else:
      outputFileName=os.path.basename(fileName)
    for name,val in tagList.getNameVal():
      if isinstance(val, TagList):
        if "class" in val.names:
          outTag.add("is_star_class_{}".format(name), TagList("is_star_class", name))
        elif "entity" in val.names:
          outTag.add("is_planet_class_{}".format(name), TagList("is_planet_class", name))
        elif val.attemptGet("is_rare")=="yes":
          outTag.add("has_sr_{}".format(name), TagList("has_resource", TagList("type", name).add("amount", 0, "", ">")))
          if val.attemptGet("is_global")=="yes":
            outTag.add("has_country_sr_{}".format(name), TagList("has_country_resource", TagList("type", name).add("amount", 0, "", ">")))


    if not args.test_run:
      # print(outputFileName)
      lastOutFile=outputToFolderAndFile(outTag, "common/scripted_triggers", outputFileName,2,args.output_folder )
    tagList=TagList()
    
  return lastOutFile

if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)