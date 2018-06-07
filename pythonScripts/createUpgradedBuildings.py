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


def parse(argv, returnParser=False):
  parser = argparse.ArgumentParser(description="From any file containing buildings, creates a new file that allow the direct construction of upgraded buildings while keeping costs correct and ensuring uniquness of unique buildings.\n\nIMPORTANT: If you apply this script to one building file, you need to also apply it to all building file with buildings you depend on (e.g. via 'has_building').\nBuildings need to be sorted by tier!\n\nLower tier versions will be removed if higher tier is available (unless specified otherwise).\nCosts and building times will be added up (with optional discount).\nFurthermore copies icons and descriptions if according folder and file is given.\nThis mod will slightly increase the costs for every building that has a 'tier0' version as those costs are now added to the 'direct construction tier1' version as for every other building. This means those 'tier0' are no waste of resources anymore!\n\nImportant info regarding building file formatting: No 'xyz= newline {'. Open new blocks via 'xyz={ newline' as Paradox seems to have always done in their files. Limitation: Empire unique buildings will never get a direct_build copy (otherwise they would lose uniqueness)!", formatter_class=RawTextHelpFormatter)
  parser.add_argument('buildingFileNames', nargs = '*', help='File(s)/Path(s) to file(s) to be parsed or .mod file (see "--create_standalone_mod_from_mod). Output is named according to each file name with some extras. Globbing star(*) can be used (even under windows :P)')
  parser.add_argument('-l','--languages', default="braz_por,english,french,german,polish,russian,spanish", help="Languages for which files should be created. Comma separated list. Only creates links to existing titles/descriptions (but needs to do so for every language)(default: %(default)s)")
  parser.add_argument('-s','--t0_buildings', default='building_colony_shelter,building_deployment_post', help="Does not change building requirements for buildings in this comma separated list. Furthermore, their cost will not be added to the t1 buildings (but deducted from the upgrade version) (default: %(default)s)")
  parser.add_argument('-t','--time_discount', default=0.25, type=float, help="Total time of tier n will be: Time(tier n-1)+Time(upgrade tier n)*(1-discount), with the restriction that total time will never be lower than 'Time(upgrade tier n)' (default: %(default)s)")
  parser.add_argument('-c','--cost_discount', default=0., type=float, help="Total cost of tier n will be: Cost(tier n-1)+Cost(upgrade tier n)*(1-discount), with the restriction that total cost will never be lower than 'Cost(upgrade tier n)'(default: %(default)s)")
  parser.add_argument('--custom_direct_build_AI_allow', action="store_true", help="By default, the script will replace the direct build AI_allows by the lowest tier AI_allow (since the checks of the lowest tiers are usually meant for tile validity which is also important for direct build high tier, but unessecary for upgrade). This will not happen with this option")
  parser.add_argument('--simplify_upgrade_AI_allow', action="store_true", help="Allows every single upgrade to AI (that means if the player would be able to build it, so does AI)")
  parser.add_argument('--copy_requirements_up', action="store_true", help="If this option is active, requirements (potential+allow) of the lowest tier building will be copied to the direct build versions (unless they are obviously redundant)")
  parser.add_argument('-f','--just_copy_and_check', action="store_true", help="If any non-building file in your mod includes 'has_building' mentions on buildings that will be copied by this script, run this mode once with all such files as input instead of the building files. In this mode the script will simply replace all 'has_building = ...' with scripted_triggers also checking for direct_build versions. IMPORTANT: 1. You need to apply the main script FIRST! 2. --output_folder will have to include the subfolder for this call!")
  parser.add_argument('-o','--output_folder', default="BU", help="Main output folder name. Specific subfolder needs to be included for '--just_copy_and_check' (default: %(default)s)")
  parser.add_argument('--replacement_file', default="", help="Executes a very basic conditional replace on buildings. Example: 'IF unique in tagName and is_listed==no newline	ai_weight = { weight = @crucial_2 }': For all buildings that have 'unique' in their name and are not listed, set ai_weight to given value. Any number of such replaces can be in the file. An 'IF' at the very start of a line starts a replace. the next xyz = will be the tag used for replacing. You can also start a line with 'EVAL' instead of 'IF' to write an arbitrary condition. You need to know the class structure for this though.")
  # parser.add_argument('-j','--join_files', action="store_true", help="Output from all input files goes into a single file. Has to be activated if you have upgrades distributed over different files.")
  parser.add_argument('--different_same_name_vars', action="store_true", help="Activate this if you mod has differently valued variables with the same name across your building files. Be aware, that this removed the support for upgrades among different files. There won't be support for both. Please change your mod if this is an issue. This would horrible style!")
  parser.add_argument('-g','--game_version', default="2.0.*", help="Game version of the newly created .mod file to avoid launcher warning. Ignored for standalone mod creation. (default: %(default)s)")
  parser.add_argument('--tags', default="buildings", help="Comma separated list of mod tags (to be displayed in Steam/launcher). Ignored for standalone mod creation.")
  parser.add_argument('--picture_file', default="", help="Picture file set in the mod file. Ignored for standalone mod creation. This file must be manually added to the mod folder!")
  parser.add_argument('--load_order_priority', action="store_true", help="If enabled, mod will be placed first in mod priority by adding '!' to the mod name and a 'z' to building building and trigger file names. This allows the construction of mod extensions. Alternatively, you can create a standalone version , see '--create_standalone_mod_from_mod'.")
  parser.add_argument('-m','--create_standalone_mod_from_mod', action="store_true", help="If this flag is set, the script will create a copy of a mod folder, changing the building files and has_building triggers. Main input of the script should now be the .mod file.")
  parser.add_argument('--custom_mod_name', default='', help="If set, this will be the name of the new mod")
  parser.add_argument('--helper_file_list', default="", help="Non-separated list of zeros and ones. N-th number defines whether file number n is a helper file (1 helperfile, 0 standard file)")
  parser.add_argument('--make_optional', action="store_true", help="Adds 'direct_build_enabled = yes' as potential to all direct build buildings." )
  parser.add_argument('--scripted_variables', default="", help="Comma separated list of files that contain scripted variables used in the building files. This option is mandatory if you building costs use any of those variables. Recognizable at the spam of missing variable errors you get if not doing this!")
  parser.add_argument('--skip_building', default="", help="Comma separated list of buildings which should remain untouched")
  parser.add_argument('--copy_folder_first', default="", help="Comma separated list of folder that should be copied to target (basically alternative to standalone mod, that works with the GUI and helper files.")
  addCommonArgs(parser)

  if returnParser:
    return parser
  args=parser.parse_args(argv)


  
  args.scriptDescription='#This file was created by script!\n#Instead of editing it, you should change the origin files or the script and rerun the script!\n#Python files that can be directly used for a rerun (storing all parameters from the last run) should be in the main directory\n'

  
  return(args)

 


    
def readAndConvert(args, allowRestart=1):   
  lastOutPutFileName=""

  skipList=args.skip_building.split(",")
  if args.copy_folder_first!="" and not args.test_run:
    foldersToCopy=args.copy_folder_first.split(",")
    for inFolder in foldersToCopy:
      for root, dirnames, filenames in os.walk(inFolder):
        for file in filenames:
          # absPath=os.path.abspath(args.output_folder)
          commonPath=os.path.commonprefix([inFolder, root])
          relPath=os.path.relpath(root,commonPath)
          outFolder=args.output_folder+"/"+relPath
          if not os.path.exists(outFolder):
            os.makedirs(outFolder)
          # print(commonPath)
          # print(relPath)

          copyfile(os.path.join(root,file), outFolder+"/"+file)

  if not args.just_copy_and_check and not args.test_run:
    if not os.path.exists(args.output_folder+"/common"):
      os.mkdir(args.output_folder+"/common")
    if not os.path.exists(args.output_folder+"/common/buildings"):
      os.mkdir(args.output_folder+"/common/buildings")
    # if not os.path.exists(args.output_folder+"/common/scripted_triggers"): #folder always needed parallel to build_upgraded building output!
    #  os.mkdir(args.output_folder+"/common/scripted_triggers")
    
 
  if not args.just_copy_and_check and not args.test_run:
    copiedBuildingsFile=open(args.copiedBuildingsFileName,'w')
  mainFileList=[]
  helperList=[]
  lHFL=len(args.helper_file_list)
  lFL=len(args.buildingFileNames)
  if lHFL!=lFL:
    # if not args.test_run:
      # print("Warning: Invalid helper_file_list got {!s}, expected {!s}".format(lHFL,lFL))
    for i in range(lHFL,lFL):
      args.helper_file_list+="0"
  for i,b in enumerate(args.buildingFileNames):
    if args.helper_file_list[i]=="1":
      helperList+=glob.glob(b)
    else:
      mainFileList+=glob.glob(b)
  if not args.different_same_name_vars:
    globbedList=helperList+mainFileList
    isHelperFileItList=[True for _ in helperList]
    isHelperFileItList+=[False for _ in mainFileList]
  else:
    globbedList=[]
    for file in mainFileList:
      globbedList+=helperList
      isHelperFileItList+=[True for _ in helperList]
      globbedList.append(file)
      isHelperFileItList.append(False)


  for fileIndex,buildingFileName in enumerate(globbedList):
    prioFile=""
    if args.load_order_priority:
      prioFile="z_"
    buildingFileNameWithoutPath=os.path.basename(buildingFileName)
    if isHelperFileItList and isHelperFileItList[fileIndex]:
      thisFileIsAHelper=True
    else:
      thisFileIsAHelper=False
    #READ FILE
    if args.just_copy_and_check:
      args.outPath=args.output_folder
    else:
      args.outPath=args.output_folder+"/common/buildings/"
    if not args.test_run and (not args.just_copy_and_check or not args.create_standalone_mod_from_mod) and not thisFileIsAHelper:
      with open(args.outPath+buildingFileNameWithoutPath,'w') as outputFile:
        outputFile.write(args.scriptDescription)
        outputFile.write("#overwrite\n")
    if fileIndex==0 or args.different_same_name_vars and not isHelperFileItList: #create empty lists. Do only in first iteration when not args.different_same_name_vars is not active as we add to the lists in each iteration here. helper stuff is deleted renewed after writing output file
      varsToValue=TagList(0)
      buildingNameToData=TagList(0)
    # if (args.different_same_name_vars and ((not isHelperFileItList) or (isHelperFileItList and thisFileIsAHelper==False))):
    #   if args.scripted_variables!="":
    #     for scriptVarFile in args.scripted_variables.split(","):
    #       scriptVarFile=scriptVarFile.strip()
    #       varsToValue.readFile(scriptVarFile)
    prevLen=len(buildingNameToData.vals)
    buildingNameToData.readFile(buildingFileName,args, varsToValue,True)
    if isHelperFileItList: #mark helper buildings
      if thisFileIsAHelper:
        for b in buildingNameToData[prevLen:]:
          if isinstance(b,TagList):
            b.helper=True
    
    if not args.different_same_name_vars:
      if fileIndex<len(globbedList)-1:
        continue  #read all Files before processing
      elif isHelperFileItList:
          buildingNameToData.removeDuplicateNames(True) #remove duplicate buildings. Last file that has been read has highest priority (won't be deleted). Thus lowest priority for the helper files.
    elif isHelperFileItList:
      if thisFileIsAHelper:
        continue
      else:
        buildingNameToData.removeDuplicateNames(True) #remove duplicate buildings. Last file that has been read has highest priority (won't be deleted). Thus lowest priority for the helper files.

    #did not read before. do it now. I guess global vars have lower priority so they should come later.
    if args.scripted_variables!="":
      for scriptVarFile in args.scripted_variables.split(","):
        scriptVarFile=scriptVarFile.strip()
        varsToValue.readFile(scriptVarFile)

    if not args.just_copy_and_check:  
      #COPY AND MODIFY WHERE NEEDED       
      buildingNameToDataOrigVals=copy.copy(buildingNameToData.vals) #shallow copy of the buildings: buldingNameToData.vals will later be changed (a lot). Most of these changes reflect in buildingNameToDataOrigVals, except that new entries in the array do not appear!
      triggers=TagList(0) #list of scripted_triggers later to be saved in a file
      locData=[] #list of localisation links later to be saved in a file. One of the few times TagList class is NOT used
      for origBuildI in range(len(buildingNameToDataOrigVals)): #iterate through lowest tier buildings. Higher tier buildings will be ignored (via "is_listed = no",which is even set for tier 1 if tier 0 exists)
        baseBuildingData=buildingNameToDataOrigVals[origBuildI] #data of the lowest tier building
        baseBuildingDataCopy=copy.deepcopy(baseBuildingData)
        if not isinstance(baseBuildingData,NamedTagList):
          continue
        if baseBuildingData.attemptGet("is_listed")=="no":
          continue
        if baseBuildingData.tagName in skipList:
          continue
        
        #ITERATE THROUGH WHOLE BUILDING TREE/LINE
        buildingDataList=[baseBuildingData]
        while len(buildingDataList)>0 and "upgrades" in buildingDataList[0].names: #starting with the lowest tier building we iterate through every single descendent. Upgrade loops would obviously kill the script at this point :P
          #take first element to work with and remove it from to-use-list
          buildingData=buildingDataList[0]
          buildingDataList=buildingDataList[1:]
          upgrades=buildingData.splitToListIfString("upgrades")

          
          #new building requirements to ensure that only the highest currently available is buildable. Keep the building list as short as possible. Done via "potential" to compeltely remove them from the list (not even greyed out)
          newRequirements=TagList()
           
          #iterate through all upgrades: Create a copy of each upgrade, compute costs. Finish requirements for current building and add the copies to the to-use-list
          for upgradeName in upgrades.names:
            if upgradeName=="":
              continue
            try:
              upgradeData=buildingNameToData.get(upgradeName) #allow editing
            except ValueError:
              print("WARNING: Upgrade building {} not found for {}. Either missing or in different file. Cannot apply script to this! In different file will work with '--join_files' option.".format(upgradeName, buildingData.tagName))
              if "planet_unique" in buildingData.names or "empire_unique" in buildingData.names:
                print("EXTRA WARNING: The problematic building is planet_unique or empire_unique. This error might destroy uniqueness!")
              continue
            secondVisit=False
            # try:
            if upgradeData.wasVisited:
              print("Script tried to visit "+upgradeData.tagName +" twice (second time via "+buildingData.tagName+"). This is to be expected if different buildings upgrade into this building, but could also indicate an error in ordering: Of all 'is_listed=yes' buildings in a tree, the lowest tier must always be first!")
              secondVisit=True
            elif buildingData.tagName in args.t0_buildings: #don't do if visited twice!
              upgradeData.costChangeUpgradeToDirectBuild(buildingData, args, varsToValue, True) #fix t0-t1 costs
            # except:
              # print(upgradeName)
              # raise
              
            #this is a higher tier building. If there is no pure upgrade version yet, create it now. A direct build one will be created anyway!
            upgradeData.replace("is_listed","no") #creates if does not exist
            upgradeData.wasVisited=1
            
              
              
            origUpgradeData=upgradeData  
            upgradeData=copy.deepcopy(buildingNameToData.get(upgradeName)) #now copy to prevent further editing
            if not secondVisit:
              if args.copy_requirements_up:
                for cat in ["allow", "potential"]:
                  dat=copy.deepcopy(baseBuildingDataCopy.attemptGet(cat))
                  if len(dat)>0:
                    upgradeData.getOrCreate(cat).addTagList(dat)
                # upgradeData.getOrCreate("potential").addTagList(copy.deepcopy(baseBuildingDataCopy.attemptGet("potential")))
              if not args.custom_direct_build_AI_allow:
                try:
                  upgradeData.replace("ai_allow", baseBuildingData.get("ai_allow"))
                except ValueError:
                  pass
                
            
            # if "empire_unique" in upgradeData.names and upgradeData.get("empire_unique")=="yes":
            #   continue #todo: remove! not reason anymore afaik -> check for "planet_unique checks and add empire unique there"

            #new requirements: Only buildable if one of the conditions of the next higher tier is not satisfied.
            poss=copy.deepcopy([upgradeData.attemptGet("prerequisites"),upgradeData.attemptGet("potential"),upgradeData.attemptGet("allow")])
            for eI in range(len(poss[0].names)): #convert prerequ to potential
              poss[0].vals[eI]='{ has_technology ='+' {} '.format(poss[0].names[eI])+'}'
              poss[0].names[eI]='owner'

            for p in poss:
              for name,val in p.getNameVal():
                #check if some potential of the upgrade is also a potential of the base, if so, do not use that in the newRequirement
                addNameVal=True
                for nameExist, valExists in buildingData.getOrCreate("potential").getNameVal():
                  if name==nameExist and val==valExists:
                    addNameVal=False
                    break
                if addNameVal:
                  newRequirements.add(name,val)
            
            
            if not secondVisit:
              upgradeBuildingIndex=buildingNameToData.names.index(upgradeName) #index of 'upgradeData' building in the list of all buildings (including already copied buildings)
              buildingNameToData.insert(upgradeBuildingIndex,upgradeName,upgradeData) #insert the copy before 'upgradeData'. upgradeBuildingIndex is now the index of the copy!
              buildingNameToData.vals[upgradeBuildingIndex].remove("is_listed") #removing "is_listed = no"
                
              buildingNameToData.names[upgradeBuildingIndex]+="_direct_build" #renaming (as internal name needs to be unique. Not visible in-game
              buildingNameToData.vals[upgradeBuildingIndex].tagName=buildingNameToData.names[upgradeBuildingIndex]
              
              #create a new scripted_trigger, consisting of both the original upgrade and the copy that can be directly build
              # newList=TagList(1)
              # newList.getOrCreate("OR").add("has_building",upgradeName) #creates the "OR" and fills it with the first entry
              # newList.get("OR").add("has_building",buildingNameToData.names[upgradeBuildingIndex]) #second entry to "OR"
              # triggers.add("has_"+upgradeName, newList)
              # newList=TagList(1)
              # newList.getOrCreate("OR").add("has_prev_building",upgradeName) #creates the "OR" and fills it with the first entry
              # newList.get("OR").add("has_prev_building",buildingNameToData.names[upgradeBuildingIndex]) #second entry to "OR"
              # triggers.add("has_prev_"+upgradeName, newList)
              if not args.test_run:
                if not upgradeData.helper:
                  copiedBuildingsFile.write(upgradeName+"\n")
              
              #REMOVE COPY FROM TECH TREE.
              while "show_tech_unlock_if" in buildingNameToData.vals[upgradeBuildingIndex].names:
                buildingNameToData.vals[upgradeBuildingIndex].remove("show_tech_unlock_if")
              buildingNameToData.vals[upgradeBuildingIndex].add("show_tech_unlock_if", TagList().add("always","no"))

              upgradeData.costChangeUpgradeToDirectBuild(buildingData,args, varsToValue)

              #Make sure you cannot replace a building by itself (i.e. upgraded version by same tier direct build)
              upgradeData.getOrCreate("potential").add("NOT",TagList().add("has_building",origUpgradeData.tagName)) #Prevent self replace") 
              if args.make_optional:
                upgradeData.get("potential").add("direct_build_enabled", "yes")
                
              if "upgrades" in upgradeData.names:
                buildingDataList.append(upgradeData)
                
          
              
              #ICON AND LOCALIZATION:
              nameExtra="_direct_build"
                
              if not "icon" in buildingNameToData.vals[upgradeBuildingIndex].names: #if icon was already a link in the original building, we can leave it
                buildingNameToData.vals[upgradeBuildingIndex].add("icon",upgradeName) #otherwise create an icon link to the original building
              locData.append(upgradeName+nameExtra+':0 "$'+upgradeName+'$"') #localisation link. If anyone knows what the number behind the colon means, please PN me (@Gratak in Paradox forum)
              locData.append(upgradeName+nameExtra+'_desc:0 "$'+upgradeName+'_desc$"') #localisation link
                
              #MAKE UNIQUE VIA INTRODUCING A FAKE MAX TIER BUILDING
              if not "upgrades" in upgradeData.names and (upgradeData.attemptGet("planet_unique")=="yes" or upgradeData.attemptGet("empire_unique")=="yes"):  #Max tier unique
                fakeBuilding=NamedTagList(baseBuildingData.tagName+"_hidden_tree_root")
                fakeBuilding.add("potential", TagList().add("always","no"))
                fakeBuilding.add("planet_unique", "yes")
                fakeBuilding.add("icon",baseBuildingData.tagName)
                locData.append(fakeBuilding.tagName+':0 "$'+baseBuildingData.tagName+'$"')
                locData.append(fakeBuilding.tagName+'_desc:0 "$'+baseBuildingData.tagName+'_desc$"')
                upgradeData.getOrCreate("upgrades").add(fakeBuilding.tagName,"")
                origUpgradeData.getOrCreate("upgrades").add(fakeBuilding.tagName,"")
                fakeIndex=buildingNameToData.names.index(baseBuildingData.tagName)
                buildingNameToData.insert(fakeIndex,fakeBuilding.tagName,fakeBuilding) #insert the fake before 'baseBuilding'. upgradeBuildingIndex is now shifted but shouldn't be used anymore
            
          if len(newRequirements.vals)>0 and not buildingData.tagName in args.t0_buildings:
              buildingData.getOrCreate("potential").add("NAND", newRequirements)
              newRequirements.add("NOT", TagList("owner",TagList("has_country_flag","display_low_tier_flag")))
              if args.make_optional:
                newRequirements.add("has_global_flag","direct_build_enabled")
    #END OF COPY AND MODIFY        

    if args.simplify_upgrade_AI_allow:
      for building in buildingNameToData.vals: #Allow all upgrades to AI.
        if isinstance(building, NamedTagList):
          if "is_listed" in building.names and building.get("is_listed")=="no" and "ai_allow" in building.names:
            building.replace("ai_allow", TagList().add("always","yes"))
        
    #buildingNameToData.printAll()
        
    if args.replacement_file!='': #todo rework!
      print("REPLACEMENT FILE CURRENTLY NOT WORKING!")
      # equalConditions=[]
      # inConditions=[]
      # allConditions=[] #allConditions[i][j] will be an array consisting of: negation bool, condition type, keyword 1, keyword 2, 
      # replaceClasses=[]
      # searchingForReplaceKeyword=0
      # activeReplace=0
      # with open(args.replacement_file, 'r') as replacement_file:
      #   for line in replacement_file:
      #     if line[:2]=="IF":
      #       searchingForReplaceKeyword=1
      #       activeReplace=0
      #       allConditions.append([])
      #       conditions=line[2:].split("and")
      #       for condition in conditions:
      #         allConditions[-1].append([])
      #         if condition.split()[0]=="not":
      #           allConditions[-1][-1].append(True)
      #           condition=" ".join(condition.split()[1:])
      #         else:
      #           allConditions[-1][-1].append(False)
      #         if len(condition.strip().split("=="))==2: #len(condition.strip().split(" "))==1 and 
      #           allConditions[-1][-1].append("==")
      #           # allConditions[-1][-1].append(e.strip() for e in condition.strip().split("=="))
      #         elif len(condition.strip().split(" in "))==2:
      #           allConditions[-1][-1].append(" in ")
      #           # allConditions[-1][-1].append(e.strip() for e in condition.strip().split(" in "))
      #         else:
      #           print("Invalid condition in replacement file! Exiting!")
      #           print(line)
      #           print(condition.strip().split("in"))
      #           sys.exit(1)
      #         for e in condition.strip().split(allConditions[-1][-1][-1]):
      #           allConditions[-1][-1].append(e.strip())
      #     elif line[:4]=="EVAL":
      #       searchingForReplaceKeyword=1
      #       activeReplace=0
      #       allConditions.append([[line[:4],line[4:].strip()]])
      #     elif searchingForReplaceKeyword and len(line.strip())>0 and line.strip()[0]!='#':
      #       replaceClasses.append(TagList(1))
      #       replaceClasses[-1].addString(line)
      #       replaceClasses[-1].vals[0]+="\n"
      #       searchingForReplaceKeyword=0
      #       activeReplace=1
      #     elif activeReplace:
      #       replaceClasses[-1].vals[0]+=line
      # for building in buildingNameToData.vals:
      #   if not isinstance(building, NamedTagList):
      #     continue
      #   if len(replaceClasses)==0:
      #     for condition in allConditions[0]:
      #       # print(condition)
      #       if condition[0]=="EVAL":
      #         # print(condition[1])
      #         eval(condition[1])
      #         continue
      #   for i in range(len(replaceClasses)):
      #     replace=1
      #     for condition in allConditions[i]:
      #       # print(condition)
      #       if condition[0]=="EVAL":
      #         print(condition[1])
      #         if eval(condition[1]):
      #           replace=1
      #         else:
      #           replace=0
      #       elif condition[1]=="==":
      #         if condition[0]:  #negated
      #           if (condition[2] in building.names) and (building.get(condition[2])==equalCondition[3]):
      #             replace=0
      #         else:
      #           if (not condition[2] in building.names) or (building.get(condition[2])!=condition[3]):
      #             # print(building.tagName+" failed "+" ".join(condition[1:]))
      #             replace=0
      #       elif condition[1]==" in ":
      #         if condition[3]=="tagName":
      #           if (condition[0]) != (building.tagName.find(condition[2])==-1):
      #             # print(building.tagName+" failed tagName "+" ".join(condition[1:]))
      #             replace=0
      #         else:
      #           if (condition[0]) != (not condition[2] in building.get(condition[3])):
      #             # print(building.tagName+" failed "+" ".join(condition[1:]))
      #             replace=0
      #     if replace:
      #       if replaceClasses[i].names[0] in building.names:
      #         #print(building.tagName)
      #         #replaceClasses[i].printAll()
      #         building.replace(replaceClasses[i].names[0], replaceClasses[i].vals[0])
     
    if not args.just_copy_and_check:
      buildingNameToData.removeDuplicatesRec()
      
    #OUTPUT
    if not args.create_standalone_mod_from_mod and not args.just_copy_and_check and not args.test_run: #done elsewhere by mostly copying their mod file in this case
      modfileName=os.path.dirname(args.output_folder)
      if modfileName=='' or modfileName==".": #should only happen if args.output_folder is a pure foldername in which case 'os.path.dirname' is unessecary anyway
        modfileName=args.output_folder
      with open(modfileName+".mod",'w') as modfile:
        modfile.write(args.scriptDescription)
        prio=""
        if args.load_order_priority:
          prio="!"
        if args.custom_mod_name:
          modName=args.custom_mod_name
        else:
          modName=modfileName
        modfile.write('name="{}{}"\n'.format(prio,modName))
        modfile.write('path="mod/{}"\n'.format(args.output_folder.rstrip(os.sep)))
        modfile.write('tags={\n')
        for tag in args.tags.split(","):
          modfile.write('\t"'+tag+'"\n')
        modfile.write('}\n')
        modfile.write('supported_version="{}"\n'.format(args.game_version))
        if args.picture_file:
          modfile.write('picture="{}"'.format(args.picture_file))


    if not args.different_same_name_vars:
      if args.custom_mod_name:
        outfileBaseName=''.join(e for e in args.custom_mod_name if e.isalnum())+".txt"
      else:
        outfileBaseName="JOINED"+buildingFileNameWithoutPath+".txt"
    else:
      outfileBaseName=buildingFileNameWithoutPath
    if not args.just_copy_and_check and not args.test_run:
      #LOCALISATION OUTPUT
      if not os.path.exists(args.output_folder+"/localisation"):
        os.mkdir(args.output_folder+"/localisation")
      for language in args.languages.split(","):
        if not os.path.exists(args.output_folder+"/localisation/"+language):
          os.mkdir(args.output_folder+"/localisation/"+language)
        with codecs.open(args.output_folder+"/localisation/{}/build_upgraded_{}_l_{}.yml".format(language,outfileBaseName.replace(".txt",""),language),'w', "utf-8") as locOutPutFile:
          locOutPutFile.write(u'\ufeff')
          locOutPutFile.write("l_"+language+":"+"\n")
          locOutPutFile.write(args.scriptDescription)
          for line in locData:
            locOutPutFile.write(" "+line+"\n")
      
 
    if args.test_run:
      continue
    
    #BUILDING OUTPUT
    if not args.different_same_name_vars: #only happens once if that is true.
      for nonHelperFile in mainFileList:
        # print(nonHelperFile)
        origFileContent=readFile(nonHelperFile,argSilent())
        outPutToThisFile=TagList()
        for name,val, comment,separator in buildingNameToData.getAll():
          for nameOrig,valOrig, commentOrig,separatorOrig in origFileContent.getAll():
            # if not isinstance(val, TagList) and not isinstance(valOrig, TagList):
              # print(name+","+comment+","+separator)
              # print(val)
              # print(nameOrig+","+commentOrig+","+separatorOrig+"found")
              # print(valOrig)
            if name==nameOrig and comment==commentOrig and separator==separatorOrig or name==nameOrig+"_direct_build" or name==nameOrig+"_hidden_tree_root":
              outPutToThisFile.add(name,val, comment, separator)
              break
            # if isinstance(val, TagList) and isinstance(valOrig, TagList):
            #   if name==nameOrig :
            #     outPutToThisFile.add(name,val, comment,separator)
            #     break
        startBuildingsOrig, endBuildingsOrig=origFileContent.findFirstAndLastTagList()
        startBuildingsOut, endBuildingsOut=outPutToThisFile.findFirstAndLastTagList()
        with open(args.outPath+os.path.basename(nonHelperFile),'w') as outputFile:
          outputFile.write(args.scriptDescription)
          # print("writing "+os.path.basename(nonHelperFile))
          origFileContent.writeAll(outputFile,args,False,0,startBuildingsOrig)
          outPutToThisFile.writeAll(outputFile,args,False, startBuildingsOut, endBuildingsOut+1)
          origFileContent.writeAll(outputFile,args,False, endBuildingsOrig+1)
    else:
      if args.create_standalone_mod_from_mod:
        outputFileName=args.outPath+prioFile+outfileBaseName
      else:
        outputFileName=args.outPath+prioFile+"build_upgraded_"+outfileBaseName
      lastOutPutFileName=outputFileName
      with open(outputFileName,'w') as outputFile:
        outputFile.write(args.scriptDescription)
        buildingNameToData.writeAll(outputFile,args,len(isHelperFileItList))

      if isHelperFileItList and args.different_same_name_vars:  #reset after doing a file
        varsToValue=TagList(0)
        buildingNameToData=TagList(0)


  if not args.just_copy_and_check and not args.test_run:
    copiedBuildingsFile.close()
    with open(args.copiedBuildingsFileName) as file:
      newCopiedBuilings=[line.strip() for line in file]
    if newCopiedBuilings!=args.copiedBuildings and not args.just_copy_and_check:
      args.copiedBuildings=newCopiedBuilings
  # if lastOutPutFileName and lastOutPutFileName[0]!="." and lastOutPutFileName[0]!=os.sep and lastOutPutFileName[0]!="/":
  #   lastOutPutFileName="./"+lastOutPutFileName
  return lastOutPutFileName
  
def killWindowsBackSlashesWithFire(string):
  return os.path.normpath(string).replace(os.sep,"/")
  
def preprocess(argv):
  args=parse(argv)
  main(args,argv)
  
def main(args, argv):
  args.t0_buildings=args.t0_buildings.split(",")
  
  args.output_folder=os.path.normpath(args.output_folder.strip('"'))
  if args.output_folder[0]=="." and not args.output_folder[1]==".":
    args.output_folder=args.output_folder[1:].lstrip(os.sep)
  args.output_folder+="/"
  
  if not os.path.exists(args.output_folder):
    os.makedirs(args.output_folder)
    
  copiedBuildingsFileFolder=args.output_folder
  # print(copiedBuildingsFileFolder)
  args.copiedBuildingsFileName="/copiedBuildings.txt"
  levelsToCheck=4
  if not args.just_copy_and_check:
    levelsToCheck=1
  level=0
  
  if not args.test_run:
    while 1:
      if level==levelsToCheck:
        if args.just_copy_and_check:
          print("No copiedBuildings.txt file found! This file is created by the main script and is mandatory for the --just_copy_and_check variant! Exiting!")
          return ""
        break
      try: 
        with open(copiedBuildingsFileFolder+args.copiedBuildingsFileName) as file:
          args.copiedBuildings=[line.strip() for line in file]
        break
      except FileNotFoundError:
        if not args.just_copy_and_check:
          args.copiedBuildings=[]
          break
        level+=1
        copiedBuildingsFileFolder+="/.."
    args.copiedBuildingsFileName=copiedBuildingsFileFolder+args.copiedBuildingsFileName
  else:
    args.copiedBuildings=[]
  
    
  if args.create_standalone_mod_from_mod:
    rerunName=os.path.split(os.path.dirname(args.output_folder))[1]+"_rerun.py" #foldername, not path!
    # print(os.path.split(os.path.dirname(args.output_folder))[1])
    # print(os.path.dirname(args.output_folder))
  elif args.just_copy_and_check:
    rerunName=args.output_folder+"/rerun_just_copy_and_check.py"
  else:
    rerunName=args.output_folder+"/rerun.py" 

  if not args.test_run:
    with open(rerunName, 'w') as file:
      file.write("#!/usr/bin/env python\n")
      file.write("# -*- coding: utf-8 -*-\n")
      file.write("import subprocess\n")
      file.write("import os\n")
      file.write("os.chdir(os.path.dirname(os.path.abspath(__file__)))\n")
      if not args.create_standalone_mod_from_mod:
        file.write("os.chdir('..')\n")
        for i in range(level):
          file.write("os.chdir('..')\n")  #script will have been placed is subdir!
        
      callString=os.path.normpath("subprocess.call('python "+__file__+" "+'"'+'" "'.join(argv)+'"'+"', shell=True)\n").replace(os.sep,"/")
      file.write(callString)
      if not args.just_copy_and_check and not args.create_standalone_mod_from_mod:
        file.write("import fnmatch\n")
        file.write("for root, dirnames, filenames in os.walk('.'):\n")
        file.write("\tfor filename in fnmatch.filter(filenames,'rerun_just_copy_and_check.py'):\n")
        file.write("\t\tsubprocess.call('python {}'+{}+'{}', shell=True)\n".format('"',"os.path.join(root,filename)",'"'))
        # file.write("\t\tsubprocess.call('python "+'+"'+'filename'+'"'+"', shell=True)\n")

  if args.create_standalone_mod_from_mod:
    modFileName=args.buildingFileNames[0]
    # print(modFileName)
    with open(modFileName) as modFile:
      modFileCont=[line for line in modFile]
      pathString='path="mod/'+killWindowsBackSlashesWithFire(args.output_folder.lstrip("."))+'"\n'
    for i in range(len(modFileCont)):
      if modFileCont[i][:5].strip()=="path=":
        path=os.path.normpath(modFileCont[i][5:].strip().strip('"')).replace(os.sep,"/")      
        modFileCont[i]=pathString
      if modFileCont[i][:8].strip()=="archive=":
        path=os.path.normpath(modFileCont[i][8:].strip().strip('"')).replace(os.sep,"/")
        import zipfile
        zip_ref = zipfile.ZipFile(path, 'r')
        path=path.replace(".zip","/")
        zip_ref.extractall(path)
        zip_ref.close()
        modFileCont[i]=pathString
      if modFileCont[i][:5].strip()=="name=":
        if args.custom_mod_name:
          modFileCont[i]='name="'+args.custom_mod_name+'"\n'
        else:
          modFileCont[i]=modFileCont[i].strip()[:-1] #remove quote and newline
          modFileCont[i]+='_direct_build"\n'
    if path[:3]=="mod":
      path=path[4:]#hopefully taking away mod and slash, backslash
    path=path.strip()
    # if args.custom_mod_name:
      # newModFileName=args.custom_mod_name+".mod"
    # else:
      # newModFileName=modFileName.replace(".mod","_direct_build.mod")
    newModFileName=os.path.split(os.path.dirname(args.output_folder))[-1]+".mod" #foldername, not path!
    with open(newModFileName,'w') as modFile:
      for line in modFileCont:
        modFile.write(line)
        
    buildingArgs=copy.deepcopy(args)
    buildingArgs.buildingFileNames=[path+"/common/buildings/*.txt"]
    readAndConvert(buildingArgs,1)
    with open(args.copiedBuildingsFileName) as file:
        args.copiedBuildings=[line.strip() for line in file]
    createConvertEvent(args)

    otherFilesArgs=copy.deepcopy(args)
    otherFilesArgs.buildingFileNames=[]    
    otherFilesArgs.just_copy_and_check=True
    otherFilesArgs.join_files=False
    # otherFilesArgs.replacement_file=''
    for root, dirs, files in os.walk(path):
      # if len(files)>0:
      # print(files)
      rootWithoutPath=root.rstrip(".").replace(path,"",1)
      if not os.path.exists(args.output_folder+rootWithoutPath):
        os.mkdir(args.output_folder+rootWithoutPath)
      if not root[-16:]=="common"+os.sep+"buildings":
        for file in files:
          # if file[-4:]==".txt" and rootWithoutPath!="":
          #   # print(rootWithoutPath)
          #   # sys.exit(0)
          #   otherFilesArgs.output_folder=args.output_folder+rootWithoutPath+"/"
          #   otherFilesArgs.buildingFileNames=[root+"/"+file]
          #   readAndConvert(otherFilesArgs,0)
          # else:
            # print(root)
            # print(file)
            copyfile(root+"/"+file, args.output_folder+"/"+rootWithoutPath+"/"+file)
    # print(otherFilesArgs.buildingFileNames)   
    # sys.exit(0)
    #otherFilesArgs.buildingFileNames=path+"/common/scripted_triggers/*"

    
    # readAndConvert(buildingArgs,0)
  else:
    out= readAndConvert(args)
    createConvertEvent(args)
    return out

def createConvertEvent(args):
  if args.custom_mod_name=="":
    print("ERROR: Custom mod name needed for create convert")
    return 1
  simpleModName=''.join(e for e in args.custom_mod_name if e.isalnum())
  onActionTagList=TagList("on_building_complete", TagList("events", TagList("direct_build_{}.1".format(simpleModName),""))).add("on_building_replaced", TagList("events", TagList("direct_build_{}.1".format(simpleModName),"")))
  eventTagList=TagList("namespace", "direct_build_{}".format(simpleModName))
  convertEvent=TagList("id", "direct_build_{}.1".format(simpleModName))
  eventTagList.add("planet_event", convertEvent)
  convertEvent.add("hide_window", "yes")
  convertEvent.add("is_triggered_only","yes")
  triggerOr=TagList()
  convertEvent.add("trigger", TagList("from", TagList("or", triggerOr)))
  immediateSwitch=TagList("trigger", "has_building")
  convertEvent.add("immediate", TagList("from", TagList("switch", immediateSwitch)))
  for building in args.copiedBuildings:
    # if not building.helper:
      triggerOr.add("has_building", building+"_direct_build")
      immediateSwitch.add(building+"_direct_build", TagList("remove_building","yes").add("set_building", building))
  convertPlanetEvent=TagList("id", "direct_build_{}.3".format(simpleModName))
  eventTagList.add("planet_event", convertPlanetEvent)
  convertPlanetEvent.add("hide_window", "yes")
  convertPlanetEvent.add("is_triggered_only","yes")
  convertPlanetEvent.add("immediate", TagList("every_tile", TagList("limit", TagList("has_building","yes")).add("switch", immediateSwitch)))
  convertAllEvent=TagList("id","direct_build_{}.2".format(simpleModName))
  eventTagList.add("country_event", convertAllEvent)
  convertAllEvent.add("hide_window", "yes").add("fire_only_once","yes")
  convertAllEvent.add("immediate", TagList("every_playable_country", TagList("every_owned_planet", TagList("planet_event", TagList("id", "direct_build_{}.3".format(simpleModName))))))

  if not args.test_run:
    if not os.path.exists(args.output_folder+"/common/on_actions/"):
       os.makedirs(args.output_folder+"/common/on_actions")
    if not os.path.exists(args.output_folder+"/events/"):
       os.mkdir(args.output_folder+"/events")
    with open(args.output_folder+"/common/on_actions/direct_build_{}.txt".format(simpleModName),'w') as file:
      onActionTagList.writeAll(file,args)
    with open(args.output_folder+"/events/direct_build_{}.txt".format(simpleModName),'w') as file:
      eventTagList.writeAll(file,args)
  # print(eventTagList)
if __name__ == "__main__":
  preprocess(sys.argv[1:])
  
