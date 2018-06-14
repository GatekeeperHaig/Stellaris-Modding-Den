#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
import re
from functools import reduce


class LocList:
  def __init__(self, translateRest=0):
    self.languages=["braz_por","english","french","german","polish","russian","spanish"]
    self.languageCodes=["pt","en","fr", "de","pl","ru", "es"]
    # self.entries=[]
    self.entries=dict()
    self.dicts=dict()
    self.translateRest=translateRest
    for languageCode in self.languageCodes:
      self.dicts[languageCode]=dict()

  def addLoc(self, id, loc, language="en"):
    # if id=="basic":
    #   print(loc)
    #   print(language)
    if language=="all":
      for k,d in self.dicts.items():
        d[id]=loc
    else:
      self.dicts[language][id]=loc
    # if id=="basic" and language=="en":
      # print(self.dicts)
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
    outputMissing=False
    if len(language)==2:
      languageCode=language
      language=self.languages[self.languageCodes.index(language)]
    else:
      languageCode=self.languageCodes[self.languages.index(language)]
    if self.translateRest:
      from googletrans import Translator
      translator=Translator()

    if languageCode!="en" and outputMissing:
      missingStuffFile= io.open(os.path.dirname(fileName)+"/missing_"+languageCode+".txt", "a+", encoding="utf-8")
    localDict=self.dicts[languageCode]
    if not localDict and self.translateRest<=1:
      translateRest=0
    else:
      translateRest=self.translateRest
    for englishKey, englishLoc in self.dicts["en"].items():
      if not englishKey in localDict:
        if (translateRest>0) and not "$" in englishLoc and not "£" in englishLoc: #full translate mode, or non empty dict and leftover translate mode
          if outputMissing:
            missingStuffFile.write('locList.addLoc("{}", "{}","{}")\n'.format(englishKey,englishLoc,languageCode))
          localDict[englishKey]=translator.translate(text=englishLoc, src="en", dest=languageCode).text
        else:
          localDict[englishKey]=englishLoc
    if languageCode!="en" and outputMissing:
      missingStuffFile.write("#next file\n")
      missingStuffFile.write("\n")
      missingStuffFile.close()    
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
  parser.add_argument('--full_translate', action="store_true")
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
  if filePath.endswith(".yml"):
    with io.open(filePath,'r', encoding="utf-8") as file:
      for line in file:
        try:
          lineArray=shlex.split(line)
        except:
          print("Error in line "+line)
          raise()
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
          if entry:
            if entry[0]=="#":
              outArray[-1]+=" ".join(lineArray[i:])
              break
  else:
    languageInFile="not_needed"
    import pyexcel_ods
    sheets=pyexcel_ods.get_data(filePath)
    args.create_main_file=True
    while 1:
      try:
        sheet=sheets.popitem()
        if sheet[0].lower()=="localisations":
          odsContent=sheet[1] #0 is the sheetname
          odsContent=[[str(e) for e in line] for line in odsContent]
          foundData=True
        if foundData:
          break
      except KeyError:#KeyError: 'dictionary is empty'
        break
    if not foundData:
      print("ERROR: Invalid ods file. 'Localisations' sheet missing! Exiting!")
      return ""
    languages=odsContent[0][1:]
    for i in range(len(languages)):
      if languages[i] in locList.languages:
        languages[i]=locList.languageCodes[locList.languages.index(languages[i])]
      if not languages[i] in locList.languageCodes:
        print("ERROR! Invalid language: "+languages[i])
    outArrays=[[] for _ in languages]
    for line in odsContent[1:]:
      # print(line)
      try:
        key=line[0]
      except IndexError:
        continue;
      locKey=key.replace(".","_")
      #check pure ref with first language (probably english)
      pureRef=False
      try:
        locContent=line[1]
      except IndexError:
        locContent=""
        pureRef=True
      if locContent.count("$")==2 and locContent[0]=="$" and locContent[-1]=="$":
        pureRef=True

      if pureRef:
        trivialAssignment.append('locList.addEntry("{}","{}")'.format(key,locContent))
      else:
        trivialAssignment.append('locList.addEntry("{}","@{}")'.format(key,locKey))
        for i,(language,locContent) in enumerate(zip(languages,line[1:])):
          locContent=locContent.strip().replace('"',"")
          if locContent!="":
            outArrays[i].append('locList.addLoc("{}","{}","{}")'.format(locKey, locContent,language))
    outArray=reduce(lambda x, y: x + y,outArrays)


  lastOutFile=""
  outFile=args.output_folder+"/locs/"+fileName.replace(".yml",".py").replace(".ods",".py")
  lastOutFile=outFile
  if not args.test_run:
    with io.open(outFile, "w", encoding='utf-8') as file:
      # file.write(u'\ufeff')
      # file.write("def locs(locList):\n")
      for entry in outArray:
        file.write(entry+"\n")
        # file.write("\t"+entry+"\n")
  simpleName=fileName.replace(".yml","").replace("_l_"+languageInFile, "").replace(".ods","")
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
        file.write("os.chdir(os.path.dirname(os.path.abspath(__file__)))\n")
        file.write("sys.path.insert(1, '"+relPath+"')\n")
        if args.full_translate:
          file.write("from locList import LocList\nlocList=LocList(2)\n")
        else:
          file.write("from locList import LocList\nlocList=LocList(1)\n")
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
    if inputFileName[-4:].lower() in [".yml",".ods"]:
      lastOutFile=readYMLCreatePy(args, inputFileName)
  return lastOutFile

if __name__== "__main__":
  args=parse(sys.argv[1:])
  main(args)
  