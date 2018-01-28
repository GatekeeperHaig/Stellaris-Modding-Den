#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
import copy
import io
import ntpath
import codecs
import glob
from shutil import copyfile
from stellarisTxtRead import TagList
from stellarisTxtRead import NamedTagList
from stellarisTxtRead import TxtReadHelperFunctions
import re
from collections import OrderedDict

def parse(argv):
  # print(argv)
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('fileNameTarget', help='For every entry in this file, tries to overwrite tag_to_be_copied by tag_to_be_copied from a same "key" entry from fileNamesSources')

  if not "--test_run" in argv:
    parser.add_argument('fileNamesSources', nargs = '*', help='File(s)/Path(s) to file(s) to be searched as source. Globbing star(*) can be used (even under windows :P)')
  parser.add_argument('--tag_to_be_copied', default="ai_weight")
  parser.add_argument('--output_folder', default="")
  # parser.add_argument('-j','--join_files', action="store_true", help="Do not mix different top level tags!")
  # parser.add_argument('--filter', action="store_true", help="Use a comma separated file to determine with tags that are to be outputted. Everything below that key will be used. Filter file that will we tried to use is <filename(no .txt)>_filter.txt")
  # parser.add_argument('--manual_filter', default="", help="filter file used for all input files")
  # parser.add_argument('-t','--to_txt', action="store_true", help="The csv file(s) previously created (<filename(no .txt)>.csv) will be used to try and find tags in the opened txt files whos value will be replaced by the entry in the txt files. If the txt file value is a variable, the value will we written in the header (possibly overwriting something else!")
  # parser.add_argument('-a','--forbid_additions', action="store_true", help="Check that you do not accidentally add tags to entries. Will only allow value changed in this mode")
  # parser.add_argument('--create_new_file', default='', help="Instead of overwriting the input txt file (or the default output csv file) the script creates a new one. Useful if you are not in a repository environment. Be careful to not leave two txt file for the game to load! '@orig' will be replaced by the original file name")
  parser.add_argument('--test_run', action="store_true", help="No Output.")
  # parser.add_argument('--use_csv', action="store_true", help="Due to problems with quotation marks going missing on opening a file in Excel or OpenOffice I have changed to storing and opening ods files. You can revert to csv using this option")
  # parser.add_argument('--changes_to_body', action="store_true", help="Every change is written to body, even if it was previously a header variable ('@')")
  # parser.add_argument('--clean_header', action="store_true", help="Header ('@' variables) will be cleaned of unused variables (after the ods file is applied)")
  # parser.add_argument('--remove_header', action="store_true", help="Header ('@' variables) will be converted into values inside the tags. Allows easier changes in ods.")
  # parser.add_argument('--keep_inlines', action="store_true", help="With this option, the script will try not to split inlines into the long tag form.")
  # parser.add_argument('--occ_sheet',action="store_true",help="Create occ sheet. Depricated")
  

  # if isinstance(argv, str):
    # argv=argv.split()
  args=parser.parse_args(argv)
  # args.t0_buildings=args.t0_buildings.split(",")

  
  return(args)

        
def main(args,unused=0):
  args.just_copy_and_check=False
  lastOutFile=""
  if not args.test_run:
    fileIndex=-1
    globbedList=[]
    sourceEntries=TagList(0)
    for b in args.fileNamesSources:
      globbedList.extend(glob.glob(b.strip('"').strip("'")))
    for fileName in globbedList:
      fileIndex+=1
      varsToValue=TagList(0)
      # if fileIndex==0 or not args.join_files:
      #   nameToData=TagList(0)
      #   tagList=TagList(0)
        
      oldEnd=len(sourceEntries.vals)
      sourceEntries.readFile(fileName,args, varsToValue) 
      # sourceEntries.printAll()
      for entry in sourceEntries[oldEnd:]:
        try:
          toBeCopied=entry.splitToListIfString(args.tag_to_be_copied)
          toBeCopied.applyOnLowestLevel( TxtReadHelperFunctions.splitIfSplitable,[], ["bracketLevel"])
          toBeCopied.applyOnLowestLevel( TxtReadHelperFunctions.getVariableValue, [varsToValue]) #remove header variables
        except ValueError:
          pass
  fileName=args.fileNameTarget
  targetEntries=TagList(0)
  varsToValue=TagList(0)
  targetEntries.readFile(fileName,args,varsToValue,True)
  missing=[]

  keyStrings=["key","name","id"]  
  for entry in targetEntries:
    if not isinstance(entry,TagList) or len(entry.names)==0:
      continue
    keyString='addKey'
    for k in keyStrings:
      if k in entry.names:
        keyString=k
    if not args.test_run:
      if keyString=='addKey':
        try:
          copyFrom=sourceEntries.get(entry.tagName)
        except ValueError:
          print("WARNING: Entry {} not found in source files".format(entry.tagName))
          missing.append(entry.tagName)
          continue
      else:
        copyFrom=0
        key=entry.get(keyString)
        for sourceEntry in sourceEntries:
          if isinstance(sourceEntry,TagList) and len(sourceEntry.vals):
            try:
              sourceKey=sourceEntry.get(keyString)
              if sourceKey==key:
                copyFrom=sourceEntry
            except ValueError:
              print("WARNING: Entry in source file that has a different key type")
        if copyFrom==0:
          print("WARNING: Entry with {}={} not found in source files".format(keyString,key))
          missing.append(entry.tagName)
          continue
      entry.getOrCreate(args.tag_to_be_copied)
      entry.replace(args.tag_to_be_copied, copyFrom.getOrCreate(args.tag_to_be_copied))
  # targetEntries.printAll()
  if not args.test_run:
    if args.output_folder=="":
      args.output_folder="." #make sure we don't save to "/"
    else:
      if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    outFile=args.output_folder+"/"+os.path.basename(fileName)
    lastOutFile=outFile
    with open(outFile,'w') as file:
      varsToValue.writeAll(file)
      targetEntries.writeAll(file)
    with open(args.output_folder+"/missing.txt",'a+') as file:
      for mis in missing:
        file.write(mis+"\n")

  return(lastOutFile)
  
 
if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)
