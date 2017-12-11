#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import shlex

class TagList: #Basically everything is stored recursively in objects of this class. Each file is one such object. Each tag within is one such object. The variables defined in a file are one such object. Only out-of-building comments are ignored and simply copied file to file.
  def __init__(self,level):
    self.names=[]
    self.vals=[]
    self.comments=[]
    self.bracketLevel=level
  def __getitem__(self, index):
    return self.vals[index]
  def get(self,name): #allows changing of content if vals[i] is an object
    return self.vals[self.names.index(name)]  
  def getN_th(self,name,n): #allows changing of content if vals[i] is an object
    index=self.n_thIndex(name,n)
    return self.vals[index]
  def n_thIndex(self,name,n):
    indexedOccurences=[i for i, n in enumerate(self.names) if n == name]
    if len(indexedOccurences)<=n:
      raise ValueError("Not enough occurences in list!")
    return indexedOccurences[n]
  def getOrCreate(self,name): #required to add something a a category that may already exist "getOrCreate(name).add..."
    if not name in self.names:
      self.add2(name, TagList(self.bracketLevel+1))
    return self.vals[self.names.index(name)]  
  def attemptGet(self,name): 
    try:
      return self.get(name)
    except ValueError:
      return TagList(0) #empty list
  def getAll(self):
    return [[self.names[i],self.vals[i]] for i in range(len(self.names))]
  def insert(self,array,index): #insert via index
    self.names[index:index]=[array[0].strip()]
    val=array[1]
    self.vals[index:index]=[val]
    if len(array)>2:
      comment=array[2]
    else:
      comment=""
    self.comments[index:index]=[comment]
  def add(self,array): #add a 2-size array
    self.names.append(array[0].strip())
    val=array[1]
    self.vals.append(val)
    if len(array)>2:
      comment=array[2]
    else:
      comment=""
    self.comments.append(comment)
  def add2(self,name,val, comment=''): #add via two separate pre-formated variables
    self.names.append(name)
    self.vals.append(val)
    self.comments.append(comment)
  def addString(self, string): #add via raw data. Only works for lines that are bracketClosed within
    array=string.split("=")
    array[1:]=["=".join(array[1:]).strip()]
    indexComment=array[1].find("#")
    if indexComment>0:
      comment=array[1][indexComment:]
      array[1]=array[1][:indexComment]
      array.append(comment)
    # print(array[0])
    # print("'"+array[1]+"'")
    self.add(array)
  def remove(self, name): #remove via name
    i=self.names.index(name)
    self.removeIndex(i)
  def removeIndex(self, i): #remove via name
    del self.names[i]
    del self.vals[i]
    del self.comments[i]
  def removeIndexList(self, indexList):
    for i in reversed(sorted(indexList)):      #delete last first to make sure indices stay valid
      self.removeIndex(i)
  def clear(self):
    self.names=[]
    self.vals=[]
  def replace(self, name,val,comment=''): #replace via name
    try:
      i=self.names.index(name)
      self.vals[i]=val
      self.comments[i]=comment
    except ValueError:
      self.add2(name,val,comment)
  def splitToListIfString(self,name,n=0): #I do not generally split lines that open and close brackets within the line (to prevent enlarging the file). Yet sometimes it's necessary...
    try:
      if n==0:
        i=self.names.index(name)
      else:
        i=self.n_thIndex(name,n)
    except ValueError:
      return TagList(0)
    if not isinstance(self.vals[i],TagList):
      self.vals[i]=TxtReadHelperFunctions.splitAlways(self.vals[i], self.bracketLevel)
    #   string=self.vals[i].strip()
    #   if string[0]=="{":
    #     string=string[1:-1].strip() #remove on bracket layer
    #   self.vals[i]=TagList(self.bracketLevel+1)
    #   if len(string)>0:
    #     self.vals[i].addString(string)
    return self.vals[i]
  def increaseLevelRec(self, amount=1): #increase the bracket level for this object and every object below. Beware that as the head name of this object is stored one level higher, the head name of the object is not shifted
    self.bracketLevel+=amount
    for val in self.vals:
      if isinstance(val, TagList,):
        val.increaseLevelRec(amount)
  def printAll(self): #primitive print. Just for testing
    for i in range(len(self.names)):
      for b in range(self.bracketLevel):
        print("\t",end="")
      if not isinstance(self.vals[i],TagList):
        print(self.names[i],end="")
        if len(self.vals[i])>0:
          print(" = "+self.vals[i],end="")
      else:
        if self.bracketLevel==1:
          print("\n",end="")
          for b in range(self.bracketLevel):
            print("\t",end="")
        print(self.names[i]+" = {\n",end="")
        self.vals[i].printAll()
        for b in range(self.bracketLevel):
          print("\t",end="")
        print("}",end="")
      print(self.comments[i],end="")
      print("\n",end="")
  def writeAll(self,file): #formatted writing. Paradox style minus most whitespace tailing errors
    for i in range(len(self.names)):
      self.writeEntry(file, i)
  def writeEntry(self, file,i):
    for b in range(self.bracketLevel):
      file.write("\t")
    if not isinstance(self.vals[i],TagList):
      file.write(self.names[i])
      if len(str(self.vals[i]))>0:
        file.write(" = "+str(self.vals[i]))
    else:
      if self.bracketLevel==1:
        file.write("\n")
        for b in range(self.bracketLevel):
          file.write("\t")
      file.write(self.names[i]+" = {\n")
      self.vals[i].writeAll(file)
      for b in range(self.bracketLevel):
        file.write("\t")
      file.write("}")
    file.write(self.comments[i])
    file.write("\n")
  def replaceAllHasBuildings(self, args): #"has_building=" fails working if different version of the same building exist (Paradox should have realised this on creation of machine empire capital buildings but they didn't... They simply created very lengthy conditions. Shame...). We replace them by scripted_triggers. Due to cross-reference in between files I do this for EVERY building, even the ones I did not copy.
  #beware that this function will not replace "has_building" hidden in the name (i.e. a longer name including it somewhere in the middle). This is WAD. This can only be added like this manually. This can be used to prevent a replace.
    for i in range(len(self.names)):
      if isinstance(self.vals[i], TagList):
        self.vals[i].replaceAllHasBuildings(args)
      elif self.names[i]=="has_building" and self.vals[i]!="no":
        if self.vals[i].strip('"') in args.copiedBuildings:
          self.names[i]="has_"+(self.vals[i].replace('"',''))
          self.vals[i]="yes"
      else: #find hidden "has_building"
        index=0
        while index>=0 and (self.vals[i].find("has_building ",index)!=-1 or self.vals[i].find("has_building=",index)!=-1):# and self.vals[i].find("has_building = no")==-1:
          index=max(self.vals[i].find("has_building ",index),self.vals[i].find("has_building=",index))        #find one that is not -1
          #hidden one must have two brackets around. find those
          leftBracked=self.vals[i].rfind("{",0,index)
          rightBracked=self.vals[i].find("}",index)
          toBeReplaced=self.vals[i][leftBracked:rightBracked+1]
          # print(leftBracked)
          # print(rightBracked)
          # print(self.vals[i])
          # print(index)
          # print(self.vals[i][index])
          # print(toBeReplaced)
          tagName=toBeReplaced.split("=")[1].replace("}","").replace('"','').strip()
          if tagName in args.copiedBuildings:
            self.vals[i]=self.vals[i].replace(toBeReplaced,"{ has_"+tagName+" = yes }")
            # print(toBeReplaced)
            
          index+=1 #prevent finding the same has_building again!
  def removeDuplicatesRec(self):
    # try :
      # print(self.tagName)
    # except AttributeError:
      # pass
    duplicates=[]
    for i in range(len(self.names)):
      if i in duplicates:
        continue
      for j in range(i+1, len(self.names)):
        if j in duplicates:
          continue
        if self.names[i]==self.names[j]:
          if isinstance(self.vals[i],TagList):
            if isinstance(self.vals[j],TagList):
              if self.vals[i].compare(self.vals[j]):
                duplicates.append(j)
          else:
            if self.vals[i]==self.vals[j]: #string compare (or string vs object which gives correct 0)
              duplicates.append(j)
    self.removeIndexList(duplicates)
    for i in range(len(self.names)): #recurively through remaining elements
      if isinstance(self.vals[i], TagList):
        self.vals[i].removeDuplicatesRec()
  def compare(self, other):
    if len(self.names)!=len(other.names):
      return 0
    for i in range(len(self.names)):
      if self.names[i]!=other.names[i]:
        return 0
      if isinstance(self.vals[i],TagList):
        if isinstance(other.vals[i],TagList):
          if not self.vals[i].compare(other.vals[i]):
            return 0
        else:
          return 0
      else:
        if self.vals[i]!=other.vals[i]:
          return 0
    return 1
  def removeDuplicateNames(self):
    duplicates=[]
    for i in range(len(self.names)):
      if i in duplicates:
        continue
      for j in range(i+1, len(self.names)):
        if j in duplicates:
          continue
        if self.names[i]==self.names[j]:
          duplicates.append(j)
    self.removeIndexList(duplicates)
  def computeNewVals(self, other, tag, discount, varsToValue, inverse=False):
    # magnitude=[entryA.get(tag), entryB.get(tag)]
    magnitude=[]
    try:
      magnitude.append(other.get(tag))
    except ValueError:
      magnitude.append("0")  
    try:
      magnitude.append(self.get(tag))
      alreadyExists=1
    except ValueError:
      magnitude.append("0")
      alreadyExists=0
    for i in range(len(magnitude)):
      if magnitude[i][0]=="@":
        magnitude[i]=varsToValue.get(magnitude[i])
      magnitude[i]=float(magnitude[i])
    if inverse:
      finalVal=int((magnitude[1]-magnitude[0])/(1-discount)) #Making sure the the new t1 "direct build" will have the same costs as in the original version where t1 was also direct build. The t1 upgrade version on the other hand will be cheaper now!
    else:
      finalVal=int(magnitude[0]+(1-discount)*magnitude[1]) #TODO possibly you would want some rounding here
      if (finalVal<magnitude[1]):
        finalVal=int(magnitude[1])
      
    finalVal=str(finalVal)
    if alreadyExists:
      self.replace(tag,finalVal)
    else:
      self.add([tag, finalVal])
  def applyOnLowestLevel(self, func, argList=[],attributeList=[]):
    for i in range(len(self.vals)):
      if not isinstance(self.vals[i], TagList):
        FilledAttributeList=[vars(self)[a] for a in attributeList]
        self.vals[i]=func(self.vals[i],self,*argList, *FilledAttributeList)
      if isinstance(self.vals[i],TagList): #might be one now!
        self.vals[i].applyOnLowestLevel(func, argList,attributeList)
  def readFile(self,fileName,args, varsToValue,keepEmptryLinesAndComments=False):#stores content of buildingFileName in self and varsToValue
    bracketLevel=0
    objectList=[] #objects currently open objectList[0] would be lowest bracket object (a building), etc
    currentlyInHeader=True
    with open(fileName,'r') as inputFile:
      print("Start reading "+fileName)
      lineIndex=0
      for line in inputFile:
        lineIndex+=1
        line=line.strip()
        if len(line)>0 and (line[0]!="#" or bracketLevel>0) :
          if line[0]=="@":
            varsToValue.addString(line)
          elif line[0]!="#" or bracketLevel>0:
            if line[0]=="#":
              objectList[-1].add2("","",line)
              continue
            currentlyInHeader=False
            bracketOpen=line.count("{")
            bracketClose=line.count("}")
            if bracketLevel==0:
              if (bracketOpen!=1 or bracketClose!=0):
                if not args.just_copy_and_check:
                  print("Error in line {!s}:\n{}\nInvalid building start line".format(lineIndex,line))
                  sys.exit(1)
                else:
                  self.addString(line)
                  args.preventLinePrint.append(lineIndex)
                  # print(line)
              else:
                tagName=line.split("=")[0].strip()
                objectList.append(NamedTagList(lineIndex,tagName))
                self.add2(tagName,objectList[-1])
            else:
              if bracketOpen>bracketClose:
                newObject=TagList(bracketLevel+1)
                objectList[-1].add([line.split("=")[0],newObject])
                objectList.append(newObject)
              elif bracketOpen==bracketClose:
                objectList[-1].addString(line)
            bracketDiff=bracketOpen-bracketClose
            bracketLevel+=bracketDiff
            # print(line)
            if bracketLevel==0 and bracketDiff<0:
              self.vals[-1].lineEnd=lineIndex
            objectList=objectList[0:bracketLevel]
        elif keepEmptryLinesAndComments:
          if currentlyInHeader:
            varsToValue.addString(line)
          elif bracketLevel==0:
            self.addString(line)
  def addTags(self, tagList):
    for name, entry in self.getAll():
      if entry:
        tagEntry=tagList.getOrCreate(name)
        # print (name)
        # print(entry)
        if isinstance(entry, TagList):
          entry.addTags(tagEntry)
      # else:
        # tagList.replace(name,"")
  def countDeepestLevelEntries(self,args, active=False):
    if len(self.names)==0:
      return 1
    count=0
    for name,val in self.getAll():
      if active or not args.filter or name in args.filter:
        count+=val.countDeepestLevelEntries(args,True)
      elif len(val.vals)>0:
        count+=val.countDeepestLevelEntries(args)
    return count
  def determineDepth(self):
    depth=self.bracketLevel+1 #one extra depth on purpose. Empty line to determine end of header
    for val in self.vals:
      if isinstance(val, TagList):
        depth=max(depth, val.determineDepth())
    return depth
  def toCSVHeader(self, outArray,args, active=False, curIndex=0): #called using taglist!
    if len(self.names)==0:
      curIndex+=1
      #for i in range(self.bracketLevel,len(outStrings)):
        #outStrings[i]+=";"
    for name,val in self.getAll():
      # print(val.countDeepestLevelEntries(args))
      if active or not args.filter or name in args.filter or (len(val.vals)>0 and val.countDeepestLevelEntries(args)>0):
        # print(len(val.vals))
        #print(curIndex)
        #print(len(outArray[0]))
        outArray[self.bracketLevel][curIndex]=name
       # curIndex+=1
        #for i in range(val.countDeepestLevelEntries(args,True)):
          #outStrings[self.bracketLevel]+=";"
        if active or not args.filter or name in args.filter:
          nextActive=True
        else:
          nextActive=False
        curIndex=val.toCSVHeader(outArray,args,nextActive,curIndex)
      else:
        self.remove(name)
    return curIndex
  def toCSV(self, lineArray, tagList,varsToValue,args,curIndex=0, curLineIndex=0):
    for name,val in tagList.getAll():
      # print(name)
      occurences=self.names.count(name)
      # if name in self.names:
      curIndexTmp=curIndex
      for occurenceIndex in range(occurences):
        curIndex=curIndexTmp
        if occurenceIndex+curLineIndex>= len(lineArray):
          lineArray.append(['' for i in lineArray[0]])
        
        if len(val.names)>0:
          # print(name)
          # print(self.get(name))
          curIndex=self.splitToListIfString(name,occurenceIndex).toCSV(lineArray, val,varsToValue,args,curIndex, curLineIndex+occurenceIndex)
        else:
          output=self.getN_th(name,occurenceIndex)
          if isinstance(output,TagList):
            output=" ".join(output.names)
          if len(output)>0 and output[0]=="@":
            try:
              output=varsToValue.get(output)
            except ValueError:
              print("Missing variable: "+output)
          lineArray[curLineIndex+occurenceIndex][curIndex]=output
          curIndex+=1
      if occurences==0:
        if isinstance(val, TagList):
          curIndex+=val.countDeepestLevelEntries(args, True)
        else:
          curIndex+=1
    return curIndex
        # for i in range(val.countDeepestLevelEntries(args)):
          # file.write(",")
  def setValFromCSV(self, header, bodyEntry, varsToValue,args, minIndex=0, maxIndex=-1, n_th_occurence=0):
    # print(header[self.bracketLevel])
    # print(self.names)
    # print(n_th_occurence)
    # print(minIndex)
    # print(maxIndex)
    if maxIndex==-1:
      maxIndex=len(header[self.bracketLevel])-1
    headerIndex=minIndex-1
    for headerName in header[self.bracketLevel][minIndex:(maxIndex+1)]:
      headerName=headerName.strip()
      headerIndex+=1
      if headerName=="" or len(bodyEntry)<=headerIndex:# or bodyEntry[headerIndex]=="":
        continue
      nextMaxIndex=nextMinIndex=headerIndex
      while nextMaxIndex+1<len(header[self.bracketLevel]) and not header[self.bracketLevel][nextMaxIndex+1]:
        nextMaxIndex+=1
      if nextMaxIndex+1>=len(header[self.bracketLevel]):
        nextMaxIndex=-1 #end of list reached. make all possible (ods lists are shorter if only empty elements are following)
      if not args.forbid_additions and not headerName in self.names and bodyEntry[headerIndex]:
        if len(header)>self.bracketLevel+1 and len(header[self.bracketLevel+1])>headerIndex and header[self.bracketLevel+1][headerIndex]!="":
          val=self.getOrCreate(headerName)
          val.setValFromCSV(header, bodyEntry,varsToValue,args, nextMinIndex, nextMaxIndex,n_th_occurence)
        else:
          self.add2(headerName,bodyEntry[headerIndex]) 
        continue
      valIndex=-1
      local_n_th_occurence=n_th_occurence
      if n_th_occurence>0:
        if self.names.count(headerName)>=1:
          try:
            valIndex=self.n_thIndex(headerName,n_th_occurence)
          except ValueError:
            if bodyEntry[headerIndex]:
              if not args.forbid_additions:
                if isinstance(self.getN_th(headerName, n_th_occurence-1), TagList):
                  self.add2(headerName, TagList(self.bracketLevel+1))
                else:
                  self.add2(headerName, "")
                # self.add2(headerName,copy.deepcopy(self.getN_th(headerName, n_th_occurence-1)))
                valIndex=self.n_thIndex(headerName,n_th_occurence)
              else:
                raise
              local_n_th_occurence=0
            # else:
            #  no continue! empty things will be ignored anyway. And there might be some extra tags lower down
      if valIndex<=0:
        try:
          valIndex=self.names.index(headerName)
        except ValueError:
          if bodyEntry[headerIndex]:
            print("Invalid tag '{}' with data '{}'. You need to allow additions if you add tags".format(headerName,bodyEntry[headerIndex]))
            print(n_th_occurence)
            print(self.names)
          continue
      if isinstance(self.vals[valIndex], TagList):
        self.vals[valIndex].setValFromCSV(header, bodyEntry,varsToValue,args, nextMinIndex, nextMaxIndex,local_n_th_occurence)
      else:
        entry=bodyEntry[headerIndex]
        # print(entry)         
        if entry:
          if self.vals[valIndex][0]=="@" and entry!="#delete" and entry[0]!="@":
            varsToValueIndex=varsToValue.names.index(self.vals[valIndex])
            if (varsToValue[varsToValueIndex]==entry): #nothing changed
              continue
            if varsToValue.changed[varsToValueIndex]>0:
              if args.changes_to_body:
                self.vals[valIndex]=entry
              else:
                print("Trying to change variable {} in header for {!s}. time! It can only have one value! This call from {} (header {}) is ignored. Use '--remove_header', '--changes_to_body' or enter variable names into the ods file instead!".format(self.vals[valIndex],varsToValue.changed[varsToValueIndex]+1, bodyEntry[0], headerName ))
            else:
              varsToValue.replace(self.vals[valIndex],entry)
            varsToValue.changed[varsToValueIndex]+=1
          else:
            self.vals[valIndex]=entry
  def deleteMarked(self):
    delete=[]
    for i in range(len(self.names)):
      if isinstance(self.vals[i],TagList):
        if self.vals[i].deleteMarked():
          delete.append(i)
      else:
        if self.vals[i]=="#delete":# or not self.vals[i]:
          delete.append(i)
    if len(self.names)>0 and (len(delete)==len(self.names) or len(delete)==len(self.names)-1 and ("key" in self.names or "name" in self.names)):
      return True #fully deleted. Delete head tag
    self.removeIndexList(delete)
    return False
          
class NamedTagList(TagList): #derived from TagList with four extra variables and a custom initialiser. Stores main tag of each building (and the reduntantly stored building name)
  def __init__(self, lineNbr,tagName):
    self.names=[]
    self.vals=[]
    self.comments=[]
    self.bracketLevel=1
    self.lineStart=lineNbr#line start in original file
    self.lineEnd=lineNbr #line end in original file
    self.lowerTier=0
    self.tagName=tagName
    self.wasVisited=0
  def costChangeUpgradeToDirectBuild(self, lowerTierData, args, varsToValue, inverse=False): #Will change the costs of self from being an upgrade to being direct build (or the other way round if inverse is True):
    #compute build times
    self.computeNewVals(lowerTierData, "base_buildtime", args.time_discount,varsToValue, inverse)
    #compute costs
    costsLowerTier=lowerTierData.splitToListIfString("cost")
    costsSelf=self.splitToListIfString("cost")
    allCostNames=list(set(costsLowerTier.names)|set(costsSelf.names)) #create a list that includes any cost name from either building exactly once
    for name in allCostNames:
      if name[0]!="#":
        costsSelf.computeNewVals(costsLowerTier, name, args.cost_discount,varsToValue, inverse)   #compute costs
    
class TxtReadHelperFunctions:
  def getVariableValue(variable,caller, varsToValue):
    if variable and variable[0]=="@":
      return varsToValue.get(variable)
    else:
      return variable 
  def checkVariableUsage(variable,caller,varsToValue): 
    if variable and variable[0]=="@":
      varsToValue.changed[varsToValue.names.index(variable)]+=1
    return variable
  def splitIfSplitable(variable,caller, bracketLevel):
    if not "=" in variable:# and not "{" in variable:
      return variable
    varSplit=shlex.split(variable)
    #print(varSplit)
    if len(varSplit) >1 and variable.find("{")==-1: #no further subtags but a list of tags
      i=1#first element is value
      while i <len(varSplit):
        if varSplit[i][-1]!="=" and varSplit[i].find("=")!=-1: #equal somewhere in the middle
          caller.addString(varSplit[i])
        elif i<len(varSplit)+1 and varSplit[i][-1]=="=":
          caller.names.append(varSplit[i][:-1])
          caller.vals.append(varSplit[i+1])
          caller.comments.append("")
          i+=1 #extra index increase
        elif  i<len(varSplit)+1 and varSplit[i+1][0]=="=":
          caller.names.append(varSplit[i])
          caller.comments.append("")
          if len(varSplit[i+1])>1:
            caller.vals.append(varSplit[i+1][1:])
          elif i<len(varSplit)+2:
            caller.vals.append(varSplit[i+2])
            i+=1 #extra extra index increase
          else:
            print("Invalid splitting of string "+variable)
            caller.vals.append('')
          i+=1 #extra index increase
        else:
          print("Invalid splitting of string "+variable)
        i+=1
      return varSplit[0]


    return TxtReadHelperFunctions.splitAlways(variable,bracketLevel)
  def splitAlways(variable, bracketLevel):
    string=variable.strip()
      
    if string[0]=="{":
      string=string[1:-1].strip() #remove one bracket layer
    out=TagList(bracketLevel+1)
    if len(string)>0:
      out.addString(string)
    return out
