#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
from argparse import RawTextHelpFormatter
import math
from stellarisTxtRead import *
import pyexcel_ods

def parse(argv, returnParser=False):
  #print(argv)
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('inputFileName',default=None, nargs='?',help="ods file. Has to be in certain format. There is an example in the git repository" )
  parser.add_argument('outputFileName', default=None, nargs='?', help="txt file")
  addCommonArgs(parser)
  
  if returnParser:
    return parser

  args=parser.parse_args(argv)
  # args.t0_buildings=args.t0_buildings.split(",")
  

  
  return(args)

class dictMatrix:
  def __init__(self, inputList):
    # self.body=[row[1:] for row in inputList[1:] if "".join(row)!=""]
    self.rowIdent=[row[0] for row in inputList[1:] if "".join(row).strip()!=""]
    self.colIdent=inputList[0][1:]
    self.body=[["" for j in self.colIdent] for i in self.rowIdent]
    for i in range(len(self.rowIdent)):
      for j in range(len(self.colIdent)):
        if len(inputList)>i+1  and len(inputList[i+1])>j+1:
          self.body[i][j]=inputList[i+1][j+1]
    # print(self.body)
  def __getitem__(self, index):
    rowName, colName=index
    return self.body[self.rowIdent.index(rowName)][self.colIdent.index(colName)]
  def __str__(self):
    sizeRowIdent=max(map(lambda x:len(x),self.rowIdent))+1
    sizeCol=max(map(lambda x:len(x),self.colIdent))
    for row in self.body:
      sizeCol=max(sizeCol, max(map(lambda x:len(x),row)))
    sizeCol+=1
    outStr=('{0: <'+str(sizeRowIdent)+'}').format('')
    for e in self.colIdent:
      outStr+=(('{0: <'+str(sizeCol)+'}').format(e))
    for h,row in zip(self.rowIdent,self.body):
      outStr+=('\n{0: <'+str(sizeRowIdent)+'}').format(h)
      for e in row:
        outStr+=('{0: <'+str(sizeCol)+'}').format(e)
    return outStr

        
def main(args,*unused):
  if args.inputFileName==None:
    return ""
  if args.outputFileName==None:
    args.outputFileName=args.inputFileName.replace(".ods", ".txt")


  sheets=pyexcel_ods.get_data(args.inputFileName)
  costs,techs,properties,categories=[0,0,0,0]
  yes="yes"
  while 1:
    try:
      sheet=sheets.popitem()
      if sheet[0]=="costs":
        costs=sheet[1] #0 is the sheetname
        costs=dictMatrix([[str(e) for e in line] for line in costs])
      elif sheet[0]=="techs":
        techs=sheet[1] #0 is the sheetname
        techs=dictMatrix([[str(e) for e in line] for line in techs])
      elif sheet[0]=="properties":
        properties=sheet[1] #0 is the sheetname
        properties=dictMatrix([[str(e) for e in line] for line in properties])
      elif sheet[0]=="categories":
        categories=dict()
        for i in range(len(sheet[1][0])):
          categories[sheet[1][0][i]]=[line[i] for line in sheet[1][1:] if len(line)>i and line[i]!=""]
    except KeyError: #KeyError: 'dictionary is empty'
      break
  if costs==0 or techs==0 or properties==0 or categories==0:
    print("MISSING SHEET! Needs costs,techs,properties,categories")
    return ""
  # print(categories)

  outList=TagList(0)
  for fromName in costs.rowIdent:
    for toCat in costs.colIdent:
      if costs[fromName,toCat]=="":
        continue
      for toName in categories[toCat]:
        newEntry=TagList(1)
        newEntry.add("from",fromName)
        newEntry.add("to",toName)
        if fromName==toName:
          newEntry.add("energy","@terraforming_cost_level_0")
          newEntry.add("duration","@terraforming_duration_level_0")
          # newEntry.add("condition","{ has_technology = "+techs[fromName,toName]+" }")
        else:
          newEntry.add("energy","@terraforming_cost_level_"+costs[fromName,toCat])
          newEntry.add("duration","@terraforming_duration_level_"+costs[fromName,toCat])
        techOrPerk=techs[fromName,toCat]
        if techOrPerk[:2]=="ap":
          newEntry.add("condition","{ has_ascension_perk = "+techOrPerk+" }")
        else:
          newEntry.add("condition","{ has_technology = "+techOrPerk+" }")

        potentialList=TagList(2)
        if properties[fromName,"habitable"]!=yes:
          # if properties[toName,"cybertronic"]!=yes:
            potentialList.add("is_terraforming_candidate",yes)
        # if properties[toName,"cybertronic"]==yes:
        #   potentialList.add("is_cybertronic_candidate",yes)
        orFromList=TagList(3)
        orToList=TagList(3)
        for key in properties.colIdent:
          if key!="habitable":# and key!="cybertronic":
            if properties[fromName,key] == yes:
              orFromList.add(key,yes)
            if properties[toName, key] == yes:
              orToList.add(key,yes)
        # if len(orFromList.names)==0 or len(orToList.names)==0:
        #   print("Warning: Unused planet found! {}->{} has at least one unused!".format(fromName,toName))
        #   continue
        if len(orFromList):
          if len(orFromList)>1:
            potentialList.add("or",orFromList)
          else:
            potentialList.addTagList(orFromList)
        if not orToList==orFromList:
          if len(orToList):
            if len(orToList)>1:
              potentialList.add("or",orToList)
            else:
              potentialList.addTagList(orToList)

        if len(potentialList)>0:
          newEntry.add("potential",potentialList)

        newEntry.add("effect",TagList(2).add("ex_terraforming_switch",yes))
        if fromName==toName:
          newEntry.get("effect").add("ex_terraforming_menu",yes)

        newEntry.add("ai_weight",TagList(2).add("weight","0"))

        outList.add("terraform_link",newEntry)
  if not args.test_run:
    with open(args.outputFileName,'w') as file:
      outList.writeAll(file,args)
  return args.outputFileName

  # costDict=dict()
  # for row in costs[1:]:
  #   dict[row[0]]=

  # print(costs)
  # print(techs)
  # print(properties)
  # print(categories)
  # print(techs["pc_arid","hot_dry"])
  # print(categories["hot_dry"])

  # outList=TagList(0)
  # # entryTemplate=TagList(0)
  # # entryTemplate.add("from")
  # # entryTemplate.add("to")
  # # entryTemplate.add("energy")
  # # entryTemplate.add("")

  # varsToValue=TagList(0)
  # eventNameToData=TagList(0)
  # eventNameToData.readFile(args.inputFileName,args, varsToValue)
  # eventNameToData.printAll()
  # with open(args.outputFileName,'w') as file:
  #   eventNameToData.writeEntry(file,0,args)
  #   namespace=eventNameToData.vals[0]
  #   for i in range(1000):
  #     eventNameToData.vals[1].replace("id", namespace+"."+str(i+1))
  #     eventNameToData.writeEntry(file,1,args)


if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)