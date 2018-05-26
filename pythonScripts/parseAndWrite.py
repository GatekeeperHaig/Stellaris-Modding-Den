#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
import glob
from stellarisTxtRead import *
# import copy

def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="Parses a Stellaris Format File and writes it again with a given style. In between, one can optionally delete all occurences of a certain tag, apply some replacement routine. Furthermore, in addition to simply writing each file again, this also allows you to merge them and write multiple files to a single one.", formatter_class=RawTextHelpFormatter)
  parser.add_argument('fileNames', nargs = '*' )
  parser.add_argument('--remove_tags', default="", help="Comma separated list of tags that should be fully removed from the file")
  # parser.add_argument('--replacement_file', default="", help="Executes a very basic conditional replace on buildings. Example: 'IF unique in tagName and is_listed==no newline  ai_weight = { weight = @crucial_2 }': For all buildings that have 'unique' in their name and are not listed, set ai_weight to given value. Any number of such replaces can be in the file. An 'IF' at the very start of a line starts a replace. the next xyz = will be the tag used for replacing. You can also start a line with 'EVAL' instead of 'IF' to write an arbitrary condition. You need to know the class structure for this though.")
  parser.add_argument('-j','--join_files', default="", help="Output from all input files goes into a single file. Give non-empty input as filename/path to store to.")
  parser.add_argument('-c','--check_if_else', action="store_true", help="checks all input files for incorrect 'pre 2.1 else'. Will not output anything except errors in that respect. Not sure to find all problems! There are cases where stuff is right with regard to the old and new system, but has different meaning. It correct trivial ones.")
  parser.add_argument('-e','--else_if', action="store_true", help="Turns obvious else={if={}} into else_if")
  if returnParser:
    return parser
  addCommonArgs(parser)
  
  
  args=parser.parse_args(argv)
  
  return(args)


def main(args,*unused):
  tagList=TagList()
  globbedList=[]
  for b in args.fileNames:
    globbedList+=glob.glob(b)

  def deleteIfTag(item):
    if item[0]==deleteTagName.strip():
      return True
    else:
      return False

  for i,fileName in enumerate(globbedList):
    tagList.readFile(fileName)
    outputFileName=fileName
    if args.join_files.strip():
      outputFileName=args.join_files.strip()

    if args.join_files.strip() and i!=len(globbedList)-1:
      continue

    if args.check_if_else:
      tagList.applyOnAllLevel(checkIfElseCount)

    if args.else_if:
      tagList.applyOnAllLevel(createElseIf)


    for deleteTagName in args.remove_tags.split(","):
      if deleteTagName.strip()!="":
        tagList.deleteOnLowestLevel(deleteIfTag)
    if not args.test_run:# and not args.check_if_else:
      with open(outputFileName, "w") as file:
        tagList.writeAll(file, args)
    tagList=TagList()
  return fileName

def checkIfElseCount(tagList):
  # print(names.count("else"))
  # print(names.count("if"))
  if tagList.names.count("else")>tagList.names.count("if"):
    print("ERROR: Invalid else! Probably not changed to 2.1!")
    # print(tagList)
  else:
    if tagList.names.count("else")==0 and tagList.names.count("if")>=1:
      for n in range(tagList.names.count("if")):
        ifIndex=tagList.n_thIndex("if",n)
        ifTag=tagList.vals[ifIndex]
        if ifTag.names.count("else")==1 and ifTag.names.count("if")==0:
          tagList.insert(ifIndex+1,"else", ifTag.get("else"))
          ifTag.remove("else")

    # sys.exit(1)
def createElseIf(tagList):
  restartNeeded=False
  for i, (name, val) in enumerate(tagList.getNameVal()):
    if name=="else" and len(val)>=1 and val.names[0].lower()=="if":
      valid=True
      for j in range(1,len(val)):
        if not val.names[j].lower() in ["else","else_if"]: 
          valid=False
          break
      if valid:
        tagList.names[i]="else_if"
        tagList.vals[i]=val.vals[0]
        for j in range(1,len(val)):
          tagList.insert(i+j,val.names[j],val.vals[j])
          restartNeeded==True
        if restartNeeded:
          createElseIf(tagList)
          break

if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)