#!/usr/bin/env python3
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
import createUpgradedBuildings as BU
import re
from collections import OrderedDict

def parse(argv):
  #print(argv)
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('fileNames', nargs = '*', help='File(s)/Path(s) to file(s) to be parsed or .mod file (see "--create_standalone_mod_from_mod). Output is named according to each file name with some extras. Globbing star(*) can be used (even under windows :P)')
  parser.add_argument('-j','--join_files', action="store_true", help="Do not mix different top level tags!")
  parser.add_argument('--filter', action="store_true", help="Use a comma separated file to determine with tags that are to be outputted. Everything below that key will be used. Filter file that will we tried to use is <filename(no .txt)>_filter.txt")
  parser.add_argument('-t','--to_txt', action="store_true", help="The csv file(s) previously created (<filename(no .txt)>.csv) will be used to try and find tags in the opened txt files whos value will be replaced by the entry in the txt files. If the txt file value is a variable, the value will we written in the header (possibly overwriting something else!")
  parser.add_argument('-a','--allow_additions', action="store_true", help="Columns that are added in the csv files are actually added to the txt files. So far no addition of rows (aka new components)")
  parser.add_argument('--overwrite', action="store_true", help="Overwrites the original txt file when converting to txt. By default the script creates an additional one. CSV files are always overwritten!")
  parser.add_argument('--test_run', action="store_true", help="No Output.")
  parser.add_argument('--use_csv', action="store_true", help="Due to problems with quotation marks going missing on opening a file in Excel or OpenOffice I have changed to storing and opening ods files. You can revert to csv using this option")
  
  try:
    import pyexcel_ods
  except ModuleNotFoundError:
    print("'Pyexcel-ods' plugin not found. Install it via 'pip install pyexcel-ods' (or 'pip install pyexcel-ods --user' if you are missing write access to the python folder)")
    print("Using cvs mode. This can cause problems with Excel/OpenOffice removing quotation marks!")
    args.use_csv=True
  
  if isinstance(argv, str):
    argv=argv.split()
  args=parser.parse_args(argv)
  # args.t0_buildings=args.t0_buildings.split(",")
  
  args.scriptDescription='#This file was created by script!\n#Instead of editing it, you should change the origin files or the script and rerun the script!\n#Python files that can be directly used for a rerun (storing all parameters from the last run) should be in the main directory\n'

  
  return(args)

        
def main(args):
  if args.use_csv:
    tableFileEnding=".csv"
  else:
    tableFileEnding=".ods"
  args.just_copy_and_check=False
  lastOutFile=""
  fileIndex=-1
  globbedList=[]
  for b in args.fileNames:
    globbedList.extend(glob.glob(b.strip('"')))
  for fileName in globbedList:
    if args.to_txt:
      if fileName[-4:]==tableFileEnding:
        fileName=fileName.replace(tableFileEnding,".txt")
    fileIndex+=1
    if fileIndex==0 or not args.join_files:
      varsToValue=BU.NamesToValue(0)
      nameToData=BU.NamesToValue(0)
      tagList=BU.NamesToValue(0)
      
      
    if fileName.replace(".txt",tableFileEnding)==fileName:
      print("Non .txt file!")
      continue
    if args.filter:
      filterFile=fileName.replace(".txt",".filter")
      if os.path.exists(filterFile):
        with open(filterFile) as file:
          args.filter=[word.strip() for line in file for word in line.split(",") ]
        if not "key" in args.filter:
          args.filter[0:0]=["key"]#always need to be able to convert back to txt
      else:
        print("No filter file for: "+fileName)
      
    #READ FILE
    if args.to_txt:
      keepExtraLines=True
    else:
      keepExtraLines=False
    nameToData.readFile(fileName,args, varsToValue, keepExtraLines) 
    nameToData.addTags(tagList)
    
    if args.to_txt:
      csvFile=fileName.replace(".txt",tableFileEnding)
      if not os.path.exists(csvFile):
        print("No "+tableFileEnding+" file for: "+fileName)
        continue
      if args.use_csv:
        with open(csvFile) as file:
          csvContent=[re.split(",|;",line.strip()) for line in file]
      else:
        import pyexcel_ods
        sheets=pyexcel_ods.get_data(csvFile)
        sheet=sheets.popitem() #should be the first sheet. Others are ignored!
        csvContent=sheet[1] #0 is the sheetname
        csvContent=[[str(e) for e in line] for line in csvContent]
        #print(csvContent)
      for i in range(len(csvContent)):
        # print("".join(csvContent[i]))
        if "".join(csvContent[i])=="":
          header=csvContent[:i+1]
          body=csvContent[i+1:]
          break
      if i==len(csvContent)-1:
        print("Error: No end of header found. There needs to be an empty line!")
        sys.exit(1)
      for name, val in nameToData.getAll():
        if name!=header[0][0]:
          continue;
        key=val.get("key")#.strip('"')
        keyCSVIndex=header[1].index("key")
        # print(key)
        found=0
        for bodyEntry in body:
          if "".join(bodyEntry):
            #print("'"+"".join(bodyEntry)+'"')
            #print(keyCSVIndex)
            if found>0:
              if bodyEntry[keyCSVIndex]:
                break
              else:
                val.setValFromCSV(header, bodyEntry,varsToValue,args,found)
                found+=1
            
            # print(bodyEntry[keyCSVIndex])
            # if bodyEntry[keyCSVIndex].strip('"')==key:
            if bodyEntry[keyCSVIndex]==key:
              #print(key)
              val.setValFromCSV(header, bodyEntry,varsToValue,args)
              found+=1
              # break
      if args.overwrite:
        outFileName=fileName
      else:
        outFileName=fileName.replace(".txt","_csvMod.txt")
      lastOutFile=outFileName
      if not args.test_run:
        nameToData.deleteMarked()
        with open(outFileName,'w') as file:       
          varsToValue.writeAll(file)
          nameToData.writeAll(file)
      continue
      
    if args.join_files:
      if fileIndex<len(globbedList)-1:
        continue
        
    # nameToData.printAll()
    lineArrayT=['' for i in range(tagList.countDeepestLevelEntries(args, True))]
    headerArray=[copy.deepcopy(lineArrayT) for i in range(tagList.determineDepth())]
    tagList.toCSVHeader(headerArray,args)
    if args.join_files:
      csvFileName=fileName.replace(".txt","JOINED"+tableFileEnding)
    else:
      csvFileName=fileName.replace(".txt",tableFileEnding)
    lastOutFile=csvFileName
    if not args.test_run:
      try:
        if os.path.exists(csvFileName):
          os.remove(csvFileName) #hopyfully fixing the strange bug for ExNihil that he can't overwrite the file...
        bodyArray=[]
        for name, val in nameToData.getAll():
          lineArray=[copy.deepcopy(lineArrayT)]
          val.toCSV(lineArray, tagList.get(name),varsToValue,args)
          bodyArray+=lineArray
        if args.use_csv:
          with open(csvFileName,'w') as file:         
            for headerLine in headerArray:
              file.write(";".join(headerLine)+";\n")            
            for bodyLine in lineArray:
              file.write(";".join(bodyLine)+";\n")
              # file.write("\n")
        else:
          data=OrderedDict()
          data.update({"DataSheet": headerArray+bodyArray})
          import pyexcel_ods
          pyexcel_ods.save_data(csvFileName, data)
      except PermissionError:
        print("PermissionError on file write. You must close "+csvFileName+" before running the script")
    # for compName, component in nameToData.getAll():
      # print(compName)
      # for name,val in component.getAll():
        
        # print(name)
        # print(val)
  return(lastOutFile)
  
 
if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)
