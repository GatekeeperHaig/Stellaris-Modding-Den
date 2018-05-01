#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
import re
from locList import LocList
from custom_difficulty_files import *


def main():
  out=TagList()
  current=out.addReturn("while")
  for i in reversed(range(12)):
    ifLoc=current.add("limit",variableOpNew("check", "reserve_transport", pow(2,i)-0.001, ">"))
    ifLoc.add("add_minerals", -pow(2,i))
    ifLoc.variableOp("change", "reserve_transport", -pow(2,i))
    current=out.addReturn("if")
  out.deleteOnLowestLevel(checkTotallyEmpty)
  with open("test.txt","w") as file:
    out.writeAll(file, args())

if __name__ == "__main__":
  main()