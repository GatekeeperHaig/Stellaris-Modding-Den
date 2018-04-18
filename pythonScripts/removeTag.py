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
  parser.add_argument('tagName')
  parser.add_argument('fileNames', nargs = '*' )
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
    if item[0]==args.tagName:
      return True
    else:
      return False
  for fileName in globbedList:
    tagList.readFile(fileName)
    tagList.deleteOnLowestLevel(deleteIfTag)
    with open(fileName, "w") as file:
      tagList.writeAll(file, args)


if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)