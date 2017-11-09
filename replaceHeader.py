#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
import copy
import io
import codecs
import glob

def parse(argv):
  parser = argparse.ArgumentParser(description="Overwrites the headers of all files with the content of the file given as first input. End of header is defined by last '@' (and stops searching at first building)", formatter_class=RawTextHelpFormatter)
  parser.add_argument('headerFileName', help='File to replace the other headers')
  parser.add_argument('fileNames', nargs = '*', help='File(s)/Path(s) to file(s) to be parsed. Overwrites the files!. Globbing star(*) can be used (even under windows :P)')

  
  if isinstance(argv, str):
    argv=argv.split()
  args=parser.parse_args(argv)

  
  return(args)
    
def main(argv):
  args=parse(argv)
  
  with open(args.headerFileName,'r') as file:
    headerContent=[line for line in file]
  
  globbedList=[]
  for b in args.fileNames:
    globbedList[0:0]=glob.glob(b)
  for buildingFileName in globbedList:
    with open(buildingFileName,'r') as file:
      fileContent=[line for line in file]
    if len(fileContent)<10:
      continue
    endOfHeader=0
    curI=-1
    for line in fileContent:
      curI+=1
      if len(line.strip())>0:
        if line[0]=="@":
          endOfHeader=curI
        elif line[0]!='#':
          break
    headerContent.append("\n")
    fileContent[:endOfHeader+1]=headerContent[:]
    with open(buildingFileName,'w') as file:
      for line in fileContent:
        file.write(line)
    
  
if __name__ == "__main__":
  main(sys.argv[1:])