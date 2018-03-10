#!/usr/bin/env python
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
from stellarisTxtRead import *
import re
from collections import OrderedDict

def parse(argv, returnParser=False):
  #print(argv)
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('fileNames', nargs = '*', help='File(s)/Path(s) to file(s) to be parsed or .mod file (see "--create_standalone_mod_from_mod). Output is named according to each file name with some extras. Globbing star(*) can be used (even under windows :P)')
  parser.add_argument('-j','--join_files', action="store_true", help="Do not mix different top level tags!")
  parser.add_argument('--filter', action="store_true", help="Will only create tags from the (comma separated) filter file (including all subtags of those and the key tag). Only these will be changed when converting back. Used file: <filename(no .txt)>_filter.txt")
  parser.add_argument('--manual_filter', default="", help="A filter file that willbe used for all input files")
  parser.add_argument('-t','--to_txt', action="store_true", help="The csv file(s) previously created (<filename(no .txt)>.csv) will be used to try and find tags in the opened txt files whos value will be replaced by the entry in the txt files. If the txt file value is a variable, the value will we written in the header (possibly overwriting something else!")
  parser.add_argument('-a','--forbid_additions', action="store_true", help="Check that you do not accidentally add tags to entries. Will only allow value changed in this mode")
  parser.add_argument('--create_new_file', default='', help="Instead of overwriting the input txt file (or the default output csv file) the script creates a new one. Useful if you are not in a repository environment. Be careful to not leave two txt file for the game to load! '@orig' will be replaced by the original file name")
  parser.add_argument('--use_csv', action="store_true", help="Due to problems with quotation marks going missing on opening a file in Excel or OpenOffice I have changed to storing and opening ods files. You can revert to csv using this option")
  parser.add_argument('--changes_to_body', action="store_true", help="Every change is written to body, even if it was previously a header variable ('@')")
  parser.add_argument('--clean_header', action="store_true", help="Header ('@' variables) will be cleaned of unused variables (after the ods file is applied)")
  parser.add_argument('--remove_header', action="store_true", help="Header ('@' variables) will be converted into values inside the tags. Allows easier changes in ods.")
  parser.add_argument('--keep_inlines', action="store_true", help="With this option, the script will try not to split inlines into the long tag form.")
  parser.add_argument('--occ_sheet',action="store_true",help="Depricated. Activates the old occurence mode in a different sheet. I think this is no longer needed with the OCCNUM column (which is certainly able of doing things the occ sheet wasn't able to do)")
  addCommonArgs(parser)
  
  

  # if isinstance(argv, str):
    # argv=argv.split()
  if returnParser:
    return parser
  args=parser.parse_args(argv)
  # args.t0_buildings=args.t0_buildings.split(",")
  
  try:
    import pyexcel_ods
  except ModuleNotFoundError:
    print("'Pyexcel-ods' plugin not found. Install it via 'pip install pyexcel-ods' (or 'pip install pyexcel-ods --user' if you are missing write access to the python folder)")
    print("Using cvs mode. This can cause problems with Excel/OpenOffice removing quotation marks!")
    args.use_csv=True
  args.scriptDescription='#This file was created by script!\n#Instead of editing it, you should change the origin files or the script and rerun the script!\n#Python files that can be directly used for a rerun (storing all parameters from the last run) should be in the main directory\n'

  
  return(args)

        
def main(args,unused=0):
  if args.use_csv:
    tableFileEnding=".csv"
  else:
    tableFileEnding=".ods"
  args.just_copy_and_check=False
  lastOutFile=""
  fileIndex=-1
  globbedList=[]
  for b in args.fileNames:
    globbedList.extend(glob.glob(b.strip('"').strip("'")))
  for fileName in globbedList:
    if args.to_txt:
      if fileName[-4:]==tableFileEnding: #table given as input
        tableFileName=fileName
        fileName=fileName.replace(tableFileEnding,"")
        if not os.path.exists(fileName):
          superFolderFile=os.path.join(os.path.dirname(fileName),"../",os.path.basename(fileName))
          if os.path.exists(superFolderFile):
            fileName=superFolderFile
      else:
        tableFileName=fileName+tableFileEnding
        subFolderTableFileName=os.path.join(os.path.dirname(fileName),"ods/",os.path.basename(fileName))
        if os.path.exists(subFolderTableFileName):
          tableFileName=subFolderTableFileName
    fileIndex+=1
    if fileIndex==0 or not args.join_files:
      varsToValue=TagList(0)
      nameToData=TagList(0)
      tagList=TagList(0)
      
    keyStrings=["key","name","id"]  
    if fileName[-4:]!=".txt" and fileName[-4:]!=".gfx" and fileName[-6:]!=".asset":
      print("Non .txt/.gfx file!")
      continue
    # else:
      # if fileName.replace(".txt",tableFileEnding)!=fileName:
      #   keyString="key"
      #   altkey="name"
      # if fileName.replace(".gfx",tableFileEnding)!=fileName:
      #   keyString="name"
      #   altkey="key"
      
    #READ FILE
    if args.to_txt:
      keepExtraLines=True
    else:
      keepExtraLines=False
    if not args.to_txt or os.path.exists(fileName):
      nameToData.readFileNew(fileName,args, varsToValue) 
    else:
      # print(fileName)
      print("Generating new txt file from {} file. First column in table must be {!s} or addKey depending on file (the unique identifiers)".format(tableFileEnding, keyStrings))

    if args.join_files:
      if fileIndex<len(globbedList)-1:
        continue
    # if fileName[-4:]==".gfx":
    #   nameToData=nameToData.vals[0]
    #   nameToData.increaseLevelRec(-1)   
    keyString='addKey'
    if not args.to_txt or len(nameToData.vals)>0: #skip all this if we create a completely new file. Also possible with empty file that existed
      for k in keyStrings:
        for v in nameToData.vals:
          if isinstance(v,TagList) and len(v.names):
            if k in v.names:
              keyString=k
            break
      if keyString=="addKey":
        for i in range(len(nameToData.vals)):
          if (isinstance(nameToData.vals[i],TagList)):
            nameToData.vals[i].addFront(keyString, nameToData.names[i])
            nameToData.names[i]="keyAdded"

      if args.manual_filter:
        filterFile=args.manual_filter
        if os.path.exists(filterFile):
          with open(filterFile) as file:
            args.filter=[word.strip() for line in file for word in line.split(",") ]
          if not keyString in args.filter:
            args.filter[0:0]=[keyString]#always need to be able to convert back to txt        
        else:
          print("No filter file for: "+fileName)
          args.filter=0
      elif args.filter:
        filterFile=fileName.replace(".txt",".filter")
        if os.path.exists(filterFile):
          with open(filterFile) as file:
            args.filter=[word.strip() for line in file for word in line.split(",") ]
          if not keyString in args.filter:
            args.filter[0:0]=[keyString]#always need to be able to convert back to txt        
        else:
          print("No filter file for: "+fileName)
          args.filter=0

      # if not args.keep_inlines:
      #   nameToData.applyOnLowestLevel( TxtReadHelperFunctions.splitIfSplitable,[], ["bracketLevel"])
      # nameToData.printAll()
      if args.remove_header:
        nameToData.applyOnLowestLevel( TxtReadHelperFunctions.getVariableValue, [varsToValue])
        for name in nameToData.names:
          if name[0]=="@":
            nameToData.remove(name) #removing by name should work while iterating over the list where stuff is removed. I tested this
        varsToValue.clear()
      varsToValue.changed=[0 for i in varsToValue.vals]

      nameToData.addTags(tagList)
    
    if args.to_txt:
      if not os.path.exists(tableFileName):
        print("No "+tableFileEnding+" file for: "+fileName)
        continue
      foundData=False
      if args.use_csv:
        with open(tableFileName) as file:
          csvContent=[re.split(",|;",line.strip()) for line in file]
      else:
        import pyexcel_ods
        sheets=pyexcel_ods.get_data(tableFileName)
        while 1:
          try:
            sheet=sheets.popitem() #should be the first sheet. Others are ignored!
            if sheet[0]=="DataSheet":
              csvContent=sheet[1] #0 is the sheetname
              csvContent=[[str(e) for e in line] for line in csvContent]
              foundData=True
            if foundData:
              break
          except KeyError:
            break
        if not foundData:
          print("ERROR: Invalid ods file. DataSheet missing! Exiting!")
          return ""
      for i in range(len(csvContent)):
        # print("".join(csvContent[i]))
        if "".join(csvContent[i])=="":
          header=csvContent[:i+1]
          body=csvContent[i+1:]
          break
      if i==len(csvContent)-1:
        print("Error: No end of header found. There needs to be an empty line!")
        return("")

      if len(nameToData.vals)==0:
        keyString=header[1][0]
      try:
        # keyCSVIndex=header[1].index(keyString)
      	keyCSVIndices=[i for i,x in enumerate(header[1]) if x==keyString]
      except ValueError:
        print("ERROR: Key not found in table! Expected {} in second row of the table!".format(keyString))
        raise
      topHeaderEntries=[]
      for i,entry in enumerate(header[0]):
        if entry!="":
          topHeaderEntries.append([i,entry])
      # print(topHeaderEntries)



      repeatIndex=0
      for bodyEntry in body:
        if "".join(bodyEntry):
          topHeaderIndex=0

          #check in which part of the file the very first entry is: Assign that "topHeaderIndex". Does basically nothing if there is only on topHeaderEntry
          for i,entry in enumerate(bodyEntry):
            if entry!="":
              for topHeaderEntriesI in range(len(topHeaderEntries)-1):
                if i>=topHeaderEntries[topHeaderEntriesI+1][0]:
                  topHeaderIndex+=1
                else:
                  break
              break
          # print("topheaderIndex")
          # print(topHeaderIndex)
          newEntry=False
          keyCSVIndex=keyCSVIndices[topHeaderIndex]
          if len(bodyEntry)>keyCSVIndex and bodyEntry[keyCSVIndex].strip():
            newEntry=True
            indexLine=keyCSVIndex
            bodyKey=bodyEntry[keyCSVIndex].strip()
          if newEntry:
            for name, val in nameToData.getAll():
              if name!=topHeaderEntries[topHeaderIndex][1]:
                continue;
              if val.get(keyString)==bodyKey:
                break; #name,val should now have the correct value
            repeatIndex=0
            if len(nameToData.vals)==0 or not isinstance(val,TagList) or val.get(keyString)!=bodyKey: #did not find correct one. probably a new one was added
              if args.forbid_additions:
                print("New key found. Additions where forbidden!")
                continue
              nameToData.add(topHeaderEntries[topHeaderIndex][1],TagList(1))
              val=nameToData.vals[-1]
              val.add(keyString, bodyKey)
          else:
            repeatIndex+=1
          try:
            # nameToData[0].printAll()
            # print(topHeaderEntries[topHeaderIndex][0])
            # if topHeaderEntries[topHeaderIndex][0]>0:
            #   val.printAll()
            val.setValFromCSV([h[topHeaderEntries[topHeaderIndex][0]:] for h in header], bodyEntry[topHeaderEntries[topHeaderIndex][0]:],varsToValue,args, 0,-1,repeatIndex)
            # nameToData[0].printAll()
            # sys.exit(0)
          except:
            print("Error trying to write into {}, occurence {!s}".format(bodyKey, repeatIndex))
            print(bodyEntry[topHeaderEntries[topHeaderIndex][0]:])
            raise
      # nameToData[0].printAll()
      if args.create_new_file:
        outFileName=args.create_new_file+".txt"
        outFileName=outFileName.replace("@orig",fileName.replace(".txt",""))
        print("Saving to "+outFileName)
      else:
        outFileName=fileName
      lastOutFile=outFileName
      if not args.test_run:
        nameToData.deleteMarked()
        for i in range(len(varsToValue.changed)):
          if varsToValue.names[i] and varsToValue.names[i][0]=="@":
            if varsToValue.changed[i]==1:
              nameToData.replace(varsToValue.names[i], varsToValue.vals[i]) #write variable changes into nameToData as only that is output later
        if args.clean_header:
          varsToValue.changed=[0 for i in varsToValue.vals]
          nameToData.applyOnLowestLevel( TxtReadHelperFunctions.checkVariableUsage, [varsToValue])
          delList=[]
          for i in range(len(varsToValue.changed)):
            if varsToValue.changed[i]==0 and varsToValue.names[i] and varsToValue.names[i][0]=="@":
              delList.append(i)
              nameToData.remove(varsToValue.names[i])
          varsToValue.removeIndexList(delList)
        if keyString=="addKey":
          for i in range(len(nameToData.vals)):
            if isinstance(nameToData.vals[i],TagList):
              nameToData.names[i]=nameToData.vals[i].get(keyString)
              nameToData.vals[i].remove(keyString)
        with open(outFileName,'w') as file:       
          # varsToValue.writeAll(file)
          # if fileName[-4:]==".gfx":
          #   nameToData.increaseLevelRec(1)
          nameToData.writeAll(file,args)
      continue
      

        
    # nameToData.printAll()
    lineArrayT=['' for i in range(tagList.countDeepestLevelEntries(args, True))]
    headerArray=[copy.deepcopy(lineArrayT) for i in range(tagList.determineDepth())]
    tagList.toCSVHeader(headerArray,args)
    occurenceArray=[]
    # tagList.printAll()
    # nameToData[0].printAll()
    subFolderTable=os.path.join(os.path.dirname(fileName),"ods/")#++os.path.basename(fileName))
    # print(subFolderTable)
    if not args.just_copy_and_check and not os.path.exists(subFolderTable):
      os.mkdir(subFolderTable)
    if args.join_files:
      tableFileNameName=os.path.join(subFolderTable,os.path.basename(fileName)+"JOINED"+tableFileEnding)
    else:
      if args.create_new_file:
        tableFileNameName=args.create_new_file+tableFileEnding
        tableFileNameName=tableFileNameName.replace("@orig",os.path.join(subFolderTable,os.path.basename(fileName)))
        print("Saving to "+tableFileNameName)
      else:
        tableFileNameName=os.path.join(subFolderTable,os.path.basename(fileName)+tableFileEnding)
    print("Saving into subfolder!")
    lastOutFile=tableFileNameName
    if not args.test_run:
      try:
        if os.path.exists(tableFileNameName):
          os.remove(tableFileNameName) #hopyfully fixing the strange bug for ExNihil that he can't overwrite the file...
        bodyArray=[]
        for name, val in nameToData.getAll():
          lineArray=[copy.deepcopy(lineArrayT)]
          if isinstance(val,TagList) and len(val.names):
            indexOfNameInTagList=tagList.names.index(name)
            shiftInOutPut=0
            for i in range(indexOfNameInTagList):
              shiftInOutPut+=tagList.vals[i].countDeepestLevelEntries(args)
            # tagList.get(name).printAll()

            occurenceList=copy.deepcopy(tagList.get(name))
            val.toCSV(lineArray, tagList.get(name),occurenceList,varsToValue,args,shiftInOutPut)
            occurenceEntry=copy.deepcopy(headerArray)
            occurenceList.toCSVHeader(occurenceEntry,args)
            try:
              keyValue=val.vals[val.names.index(keyString)]
            except:
              val.printAll()
              raise
            # keyIndex=tagList.vals.index(keyString)
            occurenceEntry[0][0]=keyValue
            # print(occurenceEntry)
            occurenceArray+=occurenceEntry
            # occurenceList.printAll()
            bodyArray+=lineArray
        if args.use_csv:
          with open(tableFileNameName,'w') as file:         
            for headerLine in headerArray:
              file.write(";".join(headerLine)+";\n")            
            for bodyLine in lineArray:
              file.write(";".join(bodyLine)+";\n")
              # file.write("\n")
        else:
          data=OrderedDict()
          data.update({"DataSheet": headerArray+bodyArray})
          if args.occ_sheet:
            data.update({"OccurenceNumbers": headerArray+occurenceArray})
          import pyexcel_ods
          pyexcel_ods.save_data(tableFileNameName, data)
      except PermissionError:
        print("PermissionError on file write. You must close "+tableFileNameName+" before running the script")
    # for compName, component in nameToData.getAll():
      # print(compName)
      # for name,val in component.getAll():
        
        # print(name)
        # print(val)
  return(lastOutFile)
  
 
if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)
