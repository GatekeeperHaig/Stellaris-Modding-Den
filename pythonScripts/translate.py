#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io

from googletrans import Translator
from locList import LocList
import re

locList=LocList(True)
k=0
with open("../gratak_mods/custom_difficulty_desc.txt",'r') as file:
  for i,line in enumerate(file):
    # header=False
    # image=False
    # if "[h1]" in line:
    #   header=True
    if line.strip()!="":
      s=re.split("(\[url=|\[url\]|\[/url\]|\[img\]|\[/img\]|\[h1\]|\[/h1\]|)",line)
    else:
      s=[]
    locEntry=""
    translate=True
    for entry in s:
      if entry=="":
        continue
      if entry[0]=="[":
        if entry[1]=="/" or entry[1]=="h":
          translate=True
        else:
          translate=False
        locEntry+=entry
      else:
        if translate:
          locEntry+="@{!s} ".format(k)
          locList.addLoc(str(k), entry)
          k+=1
        else:
          locEntry+=entry
    locList.addEntry(str(i),locEntry)
# print(locList.entries)

#     locList.addLoc(str(i), line)
#     locList.addEntry(str(i),"@"+str(i))

for language in locList.languages:
  locList.write(language+".txt", language,False)
