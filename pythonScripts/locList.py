#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
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
      from googletrans import Translator
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
  parser.add_argument('--output_folder',default="test/localisation/" )
  parser.add_argument('--create_main_file', action="store_true")
  if returnParser:
    return parser
  parser.add_argument('--test_run', action="store_true", help="No Output.")
  
  
  args=parser.parse_args(argv)
  
  return(args)

def readYMLCreatePy(args,filePath="../cgm_buildings_script_source/localisation/english/cgm_building_l_english.yml"):
  fileName=os.path.basename(filePath)
  print(fileName)
  langCodeInFile=0
  locList=LocList()
  outArray=[]
  trivialAssignment=[]
  with io.open(filePath,'r', encoding="utf-8") as file:
    for line in file:
      lineArray=shlex.split(line)
      if not langCodeInFile and len(lineArray)!=0:
        for lang, langCode in zip(locList.languages, locList.languageCodes):
          if "l_"+lang in lineArray[0]:
            langCodeInFile=langCode
            languageInFile=lang
            break
        continue
      # print(line)
      outArray.append("")
      if ":" in line:
        locContent=lineArray[1]
        pureRef=False
        if locContent.count("$")==2 and locContent[0]=="$" and locContent[-1]=="$":
          pureRef=True
        key=lineArray[0].split(":")[0]
        if pureRef:
          del outArray[-1]
        else:
          outArray[-1]+='locList.addLoc("{}","{}","{}")'.format(key.replace(".","_"), lineArray[1],langCodeInFile)
        if args.create_main_file:
          if pureRef:
            trivialAssignment.append('locList.addEntry("{}","{}")'.format(key,locContent))
          else:
            trivialAssignment.append('locList.addEntry("{}","@{}")'.format(key,key.replace(".","_")))
        # contents.append(lineArray[1])
      for i,entry in enumerate(lineArray):
        if entry[0]=="#":
          outArray[-1]+=" ".join(lineArray[i:])
          break

  lastOutFile=""
  outFile=args.output_folder+"/locs/"+fileName.replace(".yml",".py")
  lastOutFile=outFile
  if not args.test_run:
    with io.open(outFile, "w", encoding='utf-8') as file:
      # file.write(u'\ufeff')
      # file.write("def locs(locList):\n")
      for entry in outArray:
        file.write(entry+"\n")
        # file.write("\t"+entry+"\n")
  simpleName=fileName.replace(".yml","").replace("_l_"+languageInFile, "")
  if args.create_main_file:
    outFile=args.output_folder+"/"+simpleName+"_main.py"
    # outFile=args.output_folder+"/"+fileName.replace(".yml","_main.py").replace("_l_"+languageInFile, "")
    lastOutFile=outFile
    if not args.test_run:
      with open(outFile, "w") as file:
        absPath=os.path.abspath(args.output_folder)
        commonPath=os.path.commonprefix([absPath, sys.path[0]])
        # print(commonPath)
        relPath=os.path.relpath(commonPath,absPath)
        if commonPath!=sys.path[0]:
          relPath+="/"+os.path.relpath(sys.path[0],commonPath)
        # print(relPath)
        file.write("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nimport os,sys,glob,io\n")
        file.write("os.chdir(os.path.dirname(__file__))\n")
        file.write("sys.path.insert(1, '"+relPath+"')\n")
        file.write("from locList import LocList\nlocList=LocList()\n")
        # file.write("import allModules,importlib\n")
        file.write("for fileName in glob.glob('locs/*.py'):\n")
        file.write("\twith io.open(fileName,'r', encoding='utf-8') as file:\n")
        file.write("\t\t exec(file.read())\n")
        for entry in trivialAssignment:
          file.write(entry+"\n")
        file.write('for language in locList.languages:\n'+
                    '\toutFolderLoc=language\n'+
                    '\tif not os.path.exists(outFolderLoc):\n'+
                      '\t\tos.makedirs(outFolderLoc)\n'+
                    '\tlocList.write(outFolderLoc+"/'+simpleName+'_l_"+language+".yml",language)')
  return lastOutFile


def main(args,*unused): #for gui compatibility

  if not os.path.exists(args.output_folder+"/locs"):
    os.makedirs(args.output_folder+"/locs")
    # with open(args.output_folder+"/locs/__init__.py","w") as file:
      # file.write(" ")
  globbedList=[]
  for b in args.inputFileNames:
    globbedList+=glob.glob(b)

  lastOutFile=""
  for inputFileName in globbedList:
    if inputFileName[-4:].lower()==".yml":
      lastOutFile=readYMLCreatePy(args, inputFileName)
  return lastOutFile

if __name__== "__main__":
  args=parse(sys.argv[1:])
  main(args)
  