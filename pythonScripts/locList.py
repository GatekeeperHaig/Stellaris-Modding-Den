#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from googletrans import Translator
import re


class LocList:
  def __init__(self, translateRest=False):
    self.languages=["braz_por","english","french","german","polish","russian","spanish"]
    self.languageCodes=["pt","en","fr", "de","pl","ru", "es"]
    # self.entries=[]
    self.entries=dict()
    self.dicts=dict()
    self.translateRest=translateRest
    for languageCode in self.languageCodes:
      self.dicts[languageCode]=dict()

  def addLoc(self, id, loc, language="en"):
    if language=="all":
      for k,d in self.dicts.items():
        d[id]=loc
    else:
      self.dicts[language][id]=loc
    return id
  def addEntry(self, gameLocId, string, complainOnOverwrite=False):
    if complainOnOverwrite:
      if gameLocId in self.entries:
        print("Warning: Overwriting loc entry!")
    self.entries[gameLocId]=string
    # self.entries.append([gameLocId, string])
    return gameLocId
  def append(self, gameLocId, string, complainOnOverwrite=False):
    return self.addEntry(gameLocId,string,complainOnOverwrite)
  def write(self,fileName, language, yml=True):
    if len(language)==2:
      languageCode=language
      language=self.languages[self.languageCodes.index(language)]
    else:
      languageCode=self.languageCodes[self.languages.index(language)]
    if self.translateRest:
      translator=Translator()

    localDict=self.dicts[languageCode]
    for englishKey, englishLoc in self.dicts["en"].items():
      # print(self.translateRest)
      if not englishKey in localDict:
        if self.translateRest:
          localDict[englishKey]=translator.translate(text=englishLoc, src="en", dest=languageCode).text
        else:
          localDict[englishKey]=englishLoc

    with io.open(fileName,'w', encoding="utf-8") as file:
      if yml:
        file.write(u'\ufeff')
        file.write("l_"+language+':\n')
      for key,entry in self.entries.items():
        if yml:
          file.write(" "+key+':0 "')
        awaitingVar=False
        for loc in re.split("(@| |\.|,|:|§|\)|\\n)",entry):
          if loc=="":
            continue
            # print("blub")
          if loc[0]=="@":
            awaitingVar=True
            # file.write(localDict[loc[1:]])
          elif awaitingVar:
            try:
              file.write(localDict[loc].replace("\n","\\n"))
              awaitingVar=False
            except:
              print(entry)
              print(loc)
              raise
          else:
            if loc=="\n":
              loc="\\n"
            file.write(loc)
        if yml:
          file.write('"')
        file.write("\n")

import shlex
import argparse
import glob

def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="")
  parser.add_argument('inputFileNames', nargs = '*' )
  parser.add_argument('--output_folder',default="test" )
  if returnParser:
    return parser
  parser.add_argument('--test_run', action="store_true", help="No Output.")
  
  
  args=parser.parse_args(argv)
  
  return(args)

def readYMLCreatePy(args,fileName="../cgm_buildings_script_source/localisation/english/cgm_building_l_english.yml",createMain=True):
  languageInFile=0
  locList=LocList()
  outArray=[]
  trivialAssignment=[]
  with io.open(fileName,'r', encoding="utf-8") as file:
    for line in file:
      lineArray=shlex.split(line)
      if not languageInFile and len(lineArray)!=0:
        for lang, langCode in zip(locList.languages, locList.languageCodes):
          if "l_"+lang in lineArray[0]:
            languageInFile=langCode
            break
        continue
      # print(line)
      outArray.append("")
      if ":" in line:
        key=lineArray[0].split(":")[0]
        outArray[-1]+='locList.addLoc("{}","{}","{}")'.format(key.replace(".","_"), lineArray[1],languageInFile)
        if createMain:
          trivialAssignment.append('locList.addEntry("{}","@{}")'.format(key,key.replace(".","_")))
        # contents.append(lineArray[1])
      for i,entry in enumerate(lineArray):
        if entry[0]=="#":
          outArray[-1]+=" ".join(lineArray[i:])
          break

  if createMain:
    with open("test.py", "w") as file:
      file.write("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nimport os\n")
      file.write("from locList import LocList\nlocList=LocList()\n")
      for language in locList.languages:
        file.write("try:\n")
        file.write("\timport test_"+language+"\n")
        file.write("\ttest_"+language+".locs(locList)\n")
        file.write("except:\n")
        file.write("\tprint('No localisation given for {}')\n".format(language))
      # for entry in outArray:
      #   file.write(entry+"\n")
      for entry in trivialAssignment:
        file.write(entry+"\n")
      file.write('for language in locList.languages:\n'+
                  '\toutFolderLoc="testOut2/localisation/"+language\n'+
                  '\tif not os.path.exists(outFolderLoc):\n'+
                    '\t\tos.makedirs(outFolderLoc)\n'+
                  '\tlocList.write(outFolderLoc+"/cgm_building_customize_l_"+language+".yml",language)')
  with open("test_"+languageInFile+".py", "w") as file:
    file.write("def locs(locList):\n")
    for entry in outArray:
      file.write("\t"+entry+"\n")



if __name__== "__main__":
  args=parse(sys.argv[1:])
  globbedList=[]
  for b in args.inputFileNames:
    globbedList+=glob.glob(b)

  for inputFileName in globbedList:
    if inputFileName[-4:].lower()==".yml":
      readYMLCreatePy(args, inputFileName)