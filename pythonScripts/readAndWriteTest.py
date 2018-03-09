#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
from stellarisTxtRead import *

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
  args.just_copy_and_check=True
  args.preventLinePrint=[]
  varsToValue=TagList(0)
  taglist=TagList(0)
  taglist.readFileNew(args.inputfileName,args, varsToValue)
  # taglist.printAll()
  with open(args.outputfileName,'w') as file:
    taglist.writeAll(file,args)
  varsToValue.printAll()


if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)