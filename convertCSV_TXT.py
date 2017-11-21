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

def parse(argv):
  parser = argparse.ArgumentParser(description="", formatter_class=RawTextHelpFormatter)
  parser.add_argument('fileNames', nargs = '*', help='File(s)/Path(s) to file(s) to be parsed or .mod file (see "--create_standalone_mod_from_mod). Output is named according to each file name with some extras. Globbing star(*) can be used (even under windows :P)')
  
  if isinstance(argv, str):
    argv=argv.split()
  args=parser.parse_args(argv)

  # args.t0_buildings=args.t0_buildings.split(",")
  
  args.scriptDescription='#This file was created by script!\n#Instead of editing it, you should change the origin files or the script and rerun the script!\n#Python files that can be directly used for a rerun (storing all parameters from the last run) should be in the main directory\n'

  
  return(args)

class NamesToValue:
  # def __init__(self,level):
    # self.names=[]
    # self.vals=[]
    # self.comments=[]
    # self.bracketLevel=level
  # def get(self,name): #allows changing of content if vals[i] is an object
    # return self.vals[self.names.index(name)]
  # def getOrCreate(self,name): #required to add something a a category that may already exist "getOrCreate(name).add..."
    # if not name in self.names:
      # self.add2(name, NamesToValue(self.bracketLevel+1))
    # return self.vals[self.names.index(name)]  
  # def attemptGet(self,name): 
    # try:
      # return self.get(name)
    # except ValueError:
      # return NamesToValue(0) #empty list
  # def getAll(self):
    # return [[self.names[i],self.vals[i]] for i in range(len(self.names))]
  # def insert(self,array,index): #insert via index
    # self.names[index:index]=[array[0].strip()]
    # val=array[1]
    # self.vals[index:index]=[val]
    # if len(array)>2:
      # comment=array[2]
    # else:
      # comment=""
    # self.comments[index:index]=[comment]
  # def add(self,array): #add a 2-size array
    # self.names.append(array[0].strip())
    # val=array[1]
    # self.vals.append(val)
    # if len(array)>2:
      # comment=array[2]
    # else:
      # comment=""
    # self.comments.append(comment)
  # def add2(self,name,val, comment=''): #add via two separate pre-formated variables
    # self.names.append(name)
    # self.vals.append(val)
    # self.comments.append(comment)
  # def addString(self, string): #add via raw data. Only works for lines that are bracketClosed within
    # array=string.split("=")
    # array[1:]=["=".join(array[1:]).strip()]
    # indexComment=array[1].find("#")
    # if indexComment>0:
      # comment=array[1][indexComment:]
      # array[1]=array[1][:indexComment]
      # array.append(comment)
    # self.add(array)
  # def remove(self, name): #remove via name
    # i=self.names.index(name)
    # self.removeIndex(i)
  # def removeIndex(self, i): #remove via name
    # del self.names[i]
    # del self.vals[i]
    # del self.comments[i]
  # def replace(self, name,val,comment=''): #replace via name
    # try:
      # i=self.names.index(name)
      # self.vals[i]=val
      # self.comments[i]=comment
    # except ValueError:
      # self.add2(name,val,comment)
  # def splitToListIfString(self,name): #I do not generally split lines that open and close brackets within the line (to prevent enlarging the file). Yet sometimes it's necessary...
    # try:
      # i=self.names.index(name)
    # except ValueError:
      # return NamesToValue(0)
    # if not isinstance(self.vals[i],NamesToValue):
      # string=self.vals[i].strip()
      # if string[0]=="{":
        # string=string[1:-1].strip() #remove on bracket layer
      # self.vals[i]=NamesToValue(self.bracketLevel+1)
      # if len(string)>0:
        # self.vals[i].addString(string)
    # return self.vals[i]
  # def increaseLevelRec(self): #increase the bracket level for this object and every object below. Beware that as the head name of this object is stored one level higher, the head name of the object is not shifted
    # self.bracketLevel+=1
    # for val in self.vals:
      # if isinstance(val, NamesToValue):
        # val.increaseLevelRec()
  # def printAll(self): #primitive print. Just for testing
    # for i in range(len(self.names)):
      # for b in range(self.bracketLevel):
        # print("\t",end="")
      # if not isinstance(self.vals[i],NamesToValue):
        # print(self.names[i],end="")
        # if len(self.vals[i])>0:
          # print(" = "+self.vals[i],end="")
      # else:
        # if self.bracketLevel==1:
          # print("\n",end="")
          # for b in range(self.bracketLevel):
            # print("\t",end="")
        # print(self.names[i]+" = {\n",end="")
        # self.vals[i].printAll()
        # for b in range(self.bracketLevel):
          # print("\t",end="")
        # print("}",end="")
      # print(self.comments[i],end="")
      # print("\n",end="")
  # def writeAll(self,file): #formatted writing. Paradox style minus most whitespace tailing errors
    # for i in range(len(self.names)):
      # self.writeEntry(file, i)
  # def writeEntry(self, file,i):
    # for b in range(self.bracketLevel):
      # file.write("\t")
    # if not isinstance(self.vals[i],NamesToValue):
      # file.write(self.names[i])
      # if len(self.vals[i])>0:
        # file.write(" = "+self.vals[i])
    # else:
      # if self.bracketLevel==1:
        # file.write("\n")
        # for b in range(self.bracketLevel):
          # file.write("\t")
      # file.write(self.names[i]+" = {\n")
      # self.vals[i].writeAll(file)
      # for b in range(self.bracketLevel):
        # file.write("\t")
      # file.write("}")
    # file.write(self.comments[i])
    # file.write("\n")
  # def replaceAllHasBuildings(self, args): #"has_building=" fails working if different version of the same building exist (Paradox should have realised this on creation of machine empire capital buildings but they didn't... They simply created very lengthy conditions. Shame...). We replace them by scripted_triggers. Due to cross-reference in between files I do this for EVERY building, even the ones I did not copy.
  # #beware that this function will not replace "has_building" hidden in the name (i.e. a longer name including it somewhere in the middle). This is WAD. This can only be added like this manually. This can be used to prevent a replace.
    # for i in range(len(self.names)):
      # if isinstance(self.vals[i], NamesToValue):
        # self.vals[i].replaceAllHasBuildings(args)
      # elif self.names[i]=="has_building" and self.vals[i]!="no":
        # if self.vals[i].strip('"') in args.copiedBuildings:
          # self.names[i]="has_"+(self.vals[i].replace('"',''))
          # self.vals[i]="yes"
      # else: #find hidden "has_building"
        # index=0
        # while index>=0 and (self.vals[i].find("has_building ",index)!=-1 or self.vals[i].find("has_building=",index)!=-1):# and self.vals[i].find("has_building = no")==-1:
          # index=max(self.vals[i].find("has_building ",index),self.vals[i].find("has_building=",index))        #find one that is not -1
          # #hidden one must have two brackets around. find those
          # leftBracked=self.vals[i].rfind("{",0,index)
          # rightBracked=self.vals[i].find("}",index)
          # toBeReplaced=self.vals[i][leftBracked:rightBracked+1]
          # # print(leftBracked)
          # # print(rightBracked)
          # # print(self.vals[i])
          # # print(index)
          # # print(self.vals[i][index])
          # # print(toBeReplaced)
          # buildingName=toBeReplaced.split("=")[1].replace("}","").replace('"','').strip()
          # if buildingName in args.copiedBuildings:
            # self.vals[i]=self.vals[i].replace(toBeReplaced,"{ has_"+buildingName+" = yes }")
            # # print(toBeReplaced)
            
          # index+=1 #prevent finding the same has_building again!
  # def removeDuplicatesRec(self):
    # # try :
      # # print(self.buildingName)
    # # except AttributeError:
      # # pass
    # duplicates=[]
    # for i in range(len(self.names)):
      # if i in duplicates:
        # continue
      # for j in range(i+1, len(self.names)):
        # if j in duplicates:
          # continue
        # if self.names[i]==self.names[j]:
          # if isinstance(self.vals[i],NamesToValue):
            # if isinstance(self.vals[j],NamesToValue):
              # if self.vals[i].compare(self.vals[j]):
                # duplicates.append(j)
          # else:
            # if self.vals[i]==self.vals[j]: #string compare (or string vs object which gives correct 0)
              # duplicates.append(j)
    # for i in reversed(sorted(duplicates)):      #delete last first to make sure indices stay valid
      # # self.printAll()
      # self.removeIndex(i)
    # for i in range(len(self.names)): #recurively through remaining elements
      # if isinstance(self.vals[i], NamesToValue):
        # self.vals[i].removeDuplicatesRec()
  # def compare(self, other):
    # if len(self.names)!=len(other.names):
      # return 0
    # for i in range(len(self.names)):
      # if self.names[i]!=other.names[i]:
        # return 0
      # if isinstance(self.vals[i],NamesToValue):
        # if isinstance(other.vals[i],NamesToValue):
          # if not self.vals[i].compare(other.vals[i]):
            # return 0
        # else:
          # return 0
      # else:
        # if self.vals[i]!=other.vals[i]:
          # return 0
    # return 1
  # def removeDuplicateNames(self):
    # duplicates=[]
    # for i in range(len(self.names)):
      # if i in duplicates:
        # continue
      # for j in range(i+1, len(self.names)):
        # if j in duplicates:
          # continue
        # if self.names[i]==self.names[j]:
          # duplicates.append(j)
    # for i in reversed(sorted(duplicates)):      #delete last first to make sure indices stay valid
      # self.removeIndex(i)
  # def computeNewVals(self, other, tag, discount, varsToValue, inverse=False):
    # # magnitude=[entryA.get(tag), entryB.get(tag)]
    # magnitude=[]
    # try:
      # magnitude.append(other.get(tag))
    # except ValueError:
      # magnitude.append("0")  
    # try:
      # magnitude.append(self.get(tag))
      # alreadyExists=1
    # except ValueError:
      # magnitude.append("0")
      # alreadyExists=0
    # for i in range(len(magnitude)):
      # if magnitude[i][0]=="@":
        # magnitude[i]=varsToValue.get(magnitude[i])
      # magnitude[i]=float(magnitude[i])
    # if inverse:
      # finalVal=int((magnitude[1]-magnitude[0])/(1-discount)) #Making sure the the new t1 "direct build" will have the same costs as in the original version where t1 was also direct build. The t1 upgrade version on the other hand will be cheaper now!
    # else:
      # finalVal=int(magnitude[0]+(1-discount)*magnitude[1]) #TODO possibly you would want some rounding here
      # if (finalVal<magnitude[1]):
        # finalVal=int(magnitude[1])
      
    # finalVal=str(finalVal)
    # if alreadyExists:
      # self.replace(tag,finalVal)
    # else:
      # self.add([tag, finalVal])
  # def readFile(self,fileName,args, varsToValue):#stores content of buildingFileName in self and varsToValue
    # bracketLevel=0
    # objectList=[] #objects currently open objectList[0] would be lowest bracket object (a building), etc
    # with open(fileName,'r') as inputFile:
      # print("Start reading "+fileName)
      # if args.just_copy_and_check:
        # args.outPath=args.output_folder
      # else:
        # args.outPath=args.output_folder+"/common/buildings/"
      # if not args.just_copy_and_check or not args.create_standalone_mod_from_mod:
        # with open(args.outPath+os.path.basename(inputFile.name),'w') as outputFile:
          # outputFile.write(args.scriptDescription)
          # outputFile.write("#overwrite\n")
      # lineIndex=0
      # for line in inputFile:
        # lineIndex+=1
        # line=line.strip()
        # if len(line)>0 :
          # if line[0]=="@":
            # varsToValue.addString(line)
          # elif line[0]!="#" or bracketLevel>0:
            # bracketOpen=line.count("{")
            # bracketClose=line.count("}")
            # if bracketLevel==0:
              # if (bracketOpen!=1 or bracketClose!=0):
                # if not args.just_copy_and_check:
                  # print("Error in line {!s}:\n{}\nInvalid building start line".format(lineIndex,line))
                  # sys.exit(1)
                # else:
                  # self.addString(line)
                  # args.preventLinePrint.append(lineIndex)
                  # # print(line)
              # else:
                # buildingName=line.split("=")[0].strip()
                # objectList.append(Building(lineIndex,buildingName))
                # self.add2(buildingName,objectList[-1])
            # else:
              # if bracketOpen>bracketClose:
                # newObject=NamesToValue(bracketLevel+1)
                # objectList[-1].add([line.split("=")[0],newObject])
                # objectList.append(newObject)
              # elif bracketOpen==bracketClose:
                # objectList[-1].addString(line)
            # bracketDiff=bracketOpen-bracketClose
            # bracketLevel+=bracketDiff
            # # print(line)
            # if bracketLevel==0 and bracketDiff<0:
              # self.vals[-1].lineEnd=lineIndex
            # objectList=objectList[0:bracketLevel]
  def test():
    pass
      

        
def main(args):
  args.just_copy_and_check=False
  fileIndex=-1
  globbedList=[]
  for b in args.fileNames:
    globbedList.extend(glob.glob(b))
  for fileName in globbedList:
    if fileName.replace(".txt",".csv")==fileName:
      print("Non .txt file!")
      continue
    varsToValue=BU.NamesToValue(0)
    nameToData=BU.NamesToValue(0)
    tagList=BU.NamesToValue(0)
    fileIndex+=1
    #READ FILE
    nameToData.readFile(fileName,args, varsToValue) 
    nameToData.addTags(tagList)
    # nameToData.printAll()
    headerString=["" for i in range(tagList.determineDepth())]
    tagList.toCSVHeader(headerString)
    with open(fileName.replace(".txt",".csv"),'w') as file:
      for line in headerString:
        file.write(line+"\n")
      for name, val in nameToData.getAll():
        val.toCSV(file, tagList.get(name),varsToValue)
        file.write("\n")
    # for compName, component in nameToData.getAll():
      # print(compName)
      # for name,val in component.getAll():
        
        # print(name)
        # print(val)
        
  
 
if __name__ == "__main__":
  args=parse(sys.argv[1:])
  main(args)