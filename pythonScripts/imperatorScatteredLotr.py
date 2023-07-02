#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from stellarisTxtRead import *
import custom_difficulty_files as cdf
import imperatorFile
import copy
import xlsxwriter
from random import randint,uniform,choice,choices
from locList import LocList


class LoadedFileContents (imperatorFile.LoadedFileContents):
  def __init__(self): #will really just load them, no changes yet
    super().__init__()
    self.countryProps=TagList(0)
    self.countryProps.readFile("setup/countries/countries.txt",encoding='utf-8-sig')
    self.codeOnAction=TagList(0)
    self.codeOnAction.readFile("common/on_action/00_specific_from_code.txt",encoding='utf-8-sig')
    self.monthlyCountryOnAction=TagList(0)
    self.monthlyCountryOnAction.readFile("common/on_action/00_monthly_country.txt",encoding='utf-8-sig')
    self.yearlyCountryOnAction=TagList(0)
    self.yearlyCountryOnAction.readFile("common/on_action/00_yearly_country.txt",encoding='utf-8-sig')
    self.yearlyProvOnAction=TagList(0)
    self.yearlyProvOnAction.readFile("common/on_action/00_yearly_province.txt",encoding='utf-8-sig')
    self.yearly_character=TagList(0)
    self.yearly_character.readFile("common/on_action/00_yearly_character.txt",encoding='utf-8-sig')
    self.lotr_other_decisions=TagList(0)
    self.lotr_other_decisions.readFile("decisions/lotr_other_decisions.txt",encoding='utf-8-sig')
    self.BR_rings=TagList(0)
    self.BR_rings.readFile("common/traits/BR_rings.txt",encoding='utf-8-sig')
    self.BR_racial=TagList(0)
    self.BR_racial.readFile("common/traits/BR_racial.txt",encoding='utf-8-sig')
    self.BR_bloodlines=TagList(0)
    self.BR_bloodlines.readFile("common/traits/BR_bloodlines.txt",encoding='utf-8-sig')
    self.lotr_from_events_province=TagList(0)
    self.lotr_from_events_province.readFile("common/modifiers/lotr_from_events_province.txt",encoding='utf-8-sig')

class ProcessedFileData (imperatorFile.ProcessedFileData):
  def __init__(self, loadedFileContents):
    super().__init__(loadedFileContents)
    self.countryCapitals={}
    self.stateToCountry={}
    self.extraCountryDef={}

    for name,vals in self.countries.getNameVal(True):
      if vals:
        self.countryCapitals[name]=vals.get("capital")
    self.countryCapitals["BLC"]="3699"
    self.countryCapitals["OOM"]="3754"
    self.countryCapitals["FEL"]="2401"
    self.countryCapitals["MUM"]="2966"
    self.countryCapitals["TUL"]="2400"
    self.countryCapitals["NYK"]="2074"
    self.countryCapitals["LBN"]="1328"
    self.countryCapitals["PEL"]="1303"
    self.countryCapitals["NUR"]="1148" #avoid double nurn
    self.extraCountryDef["PEL"]=("despotic_monarchy","gondorian","iluvatarism")
    self.countryCapitals["ITH"]="1200"
    self.extraCountryDef["ITH"]=("despotic_monarchy","lesser_dunedain","iluvatarism")
    self.countryCapitals["ANA"]="2582"
    self.extraCountryDef["ANA"]=("despotic_monarchy","black_numenorean","melkorism")
    self.countryCapitals["MIT"]="1164"
    self.extraCountryDef["MIT"]=("despotic_monarchy","dunedain","iluvatarism")
    self.countryCapitals["ATE"]="1605"
    self.extraCountryDef["ATE"]=("despotic_monarchy","dunedain","iluvatarism")
    self.countryCapitals["PIN"]="2245"
    self.extraCountryDef["PIN"]=("despotic_monarchy","dunedain","iluvatarism")
    self.countryCapitals["EDH"]="1437"
    self.extraCountryDef["EDH"]=("despotic_monarchy","sindar","iluvatarism")
    self.countryCapitals["BUC"]="2167"
    self.extraCountryDef["BUC"]=("hobbit_mayordom_republic","hobbit","iluvatarism")
    self.countryCapitals["TOO"]="1623"
    self.extraCountryDef["TOO"]=("hobbit_mayordom_republic","hobbit","iluvatarism")
    self.countryCapitals["UIL"]="1091"
    self.extraCountryDef["UIL"]=("tribal_kingdom","lossoth","iluvatarism")
    self.countryCapitals["DUA"]="3256"
    self.extraCountryDef["DUA"]=("tribal_kingdom","lossoth","iluvatarism")
    self.countryCapitals["ANG"]="1035"
    self.extraCountryDef["ANG"]=("despotic_monarchy","angmarim","melkorism")
    self.countryCapitals["ETD"]="304"
    self.extraCountryDef["ETD"]=("despotic_monarchy","eotheod","iluvatarism")
    self.countryCapitals["GWT"]="1663"
    self.countryCapitals["THA"]="1612"
    self.extraCountryDef["THA"]=("despotic_monarchy","arnorian","iluvatarism")

    for key,val in self.countryCapitals.items():
      area=self.provinceToArea[val]
      if area in self.stateToCountry.keys():
        print(f"Two countries share same capital state: {area}, {key}, {self.stateToCountry[area]}")
      self.stateToCountry[area]=key

    self.cultureToGroup={}
    self.cultureGroupToCulture={}
    self.cultureToNum={}
    self.cultureToReligion={"black_numenorean":(0,1),"corsairs":(0,1)}
    self.cultureToGovernment={}
    self.cultureGroupToReligion={"amrun_group":(0.1,0.9),"banadunaim_group":(0.1,0.9),"barangil_group":(0.1,0.9),"breelander_group":(0.9,0.1),"dwarf_group":(0.9,0.1),"easterling_group":(0.1,0.9),"edain_group":(1,0),"edain_mixed_group":(0.9,0.1),"eotheod_group":(0.9,0.1),"forodwaith_group":(0.5,0.5),"haldadian_group":(0.8,0.2),"halfling_group":(1,0),"haradrim_group":(0.1,0.9),"harondorian_group":(0.5,0.5),"mirkwoodmen_group":(0.9,0.1),"noldor_group":(0.9,0.1),"orcs_group":(0,1),"teleri_group":(0.9,0.1),"vanyar_group":(0.9,0.1),"yopi_group":(0.5,0.5),} #iluvatarism,melkorism chances (there is enough ritualist already!)
    self.cultureGroupToGovernment={"amrun_group":(0.1,0.9,0),"banadunaim_group":(0.7,0.2,0.1),"barangil_group":(0.1,0.9,0),"breelander_group":(0.3,0,0.7),"dwarf_group":(0.9,0.1,0),"easterling_group":(0.1,0.9,0),"edain_group":(0.9,0,0.1),"edain_mixed_group":(0.9,0,0.1),"eotheod_group":(0.7,0.1,0.2),"forodwaith_group":(0.1,0.9,0),"haldadian_group":(0.2,0.7,0.1),"halfling_group":(0.4,0,0.6),"haradrim_group":(0.1,0.9,0),"harondorian_group":(0.5,0.5,0),"mirkwoodmen_group":(0.7,0,0.3),"noldor_group":(0.9,0.1,0),"orcs_group":(0.5,0.5,0),"teleri_group":(0.9,0.1,0),"vanyar_group":(0.9,0.1,0),"yopi_group":(0.4,0.5,0.1),} #monarchy, tribal, domocracy
    self.cultureGroupToNum={}
    for fileName in os.listdir("common/cultures/"):
      if fileName.startswith("00_") or fileName=="maia.txt" or fileName=="monsters.txt":
        continue
      content=TagList()
      content.readFile("common/cultures/"+fileName,encoding='utf-8-sig')
      cultures=content.vals[0].get("culture").names
      self.cultureGroupToCulture[content.names[0]]=cultures
      for c in cultures:
        self.cultureToGroup[c]=content.names[0]
        self.cultureToNum[c]=0
      self.cultureGroupToNum[content.names[0]]=0
    for cultureGroup, religion in self.cultureGroupToReligion.items():
      for culture in self.cultureGroupToCulture[cultureGroup]:
        if not culture in self.cultureToReligion:
          self.cultureToReligion[culture]=religion
    for cultureGroup, gov in self.cultureGroupToGovernment.items():
      for culture in self.cultureGroupToCulture[cultureGroup]:
        if not culture in self.cultureToGovernment:
          self.cultureToGovernment[culture]=gov
    # print(f'self.cultureToReligion = "{self.cultureToReligion}"')
      # print(f'cultures = "{cultures}"')
    # print(f'cultureToGroup = "{self.cultureToGroup}"')

def main():
  output_folder="../wotrScatteredRealms/"
  gamePath=os.path.expanduser("~")+"/.steam/debian-installation/steamapps/common/ImperatorRome/game/"

  unitSetup = imperatorFile.UnitSetup()
  for unit in unitSetup.units:
    if not unit.name in ["troll_infantry","mumakil"]: #legion only units excluded
      unit.attackFactor=1
      unit.armorFactor=1
      unit.moraleFactor=1
      unit.AP=False

  for unit in unitSetup.units:
    d=unit.assemble(unitSetup)
    fileName=unit.name
    if unit.name=="warelephant":
      fileName="warelephants"
    cdf.outputToFolderAndFile(d , output_folder+"common/units", f"army_{fileName}.txt" ,2,".",encoding="utf-8-sig")

  loadedFileContents = LoadedFileContents()
  processedFileData = ProcessedFileData(loadedFileContents)

  for name,vals in processedFileData.countries.getNameVal(True):
    cap=processedFileData.countryCapitals[name]
    area=processedFileData.provinceToArea[cap]
    vals.set("capital", cap)
    try: vals.remove("poptype_rights") 
    except: pass
    try: vals.remove("monarchy_religious_laws") 
    except: pass
    provinces=copy.deepcopy(loadedFileContents.areas.get(area).get("provinces"))
    provinces.bracketLevel=4
    # print(f'vals.get("own_control_core") = "{vars(vals.get("own_control_core"))}"')
    # print(f'loadedFileContents.areas.get(area).get("provinces") = "{vars(loadedFileContents.areas.get(area).get("provinces"))}"')
    # print(f'provinces = "{vars(provinces)}"')
    if len(vals.get("own_control_core").names)>25:
      vals.set("is_antagonist","yes")
      # print(f'name = "{name}"')
    vals.set("own_control_core", provinces)
    # vals.set("own_control_core", TagList().add(cap))
  tech=processedFileData.countries.get("TAR").get("technology")
  for country,extra in processedFileData.extraCountryDef.items():
    newCountry=processedFileData.countries.addReturn(country)
    cap=processedFileData.countryCapitals[country]
    area=processedFileData.provinceToArea[cap]
    provinces=copy.deepcopy(loadedFileContents.areas.get(area).get("provinces"))
    newCountry.add("government",extra[0])
    newCountry.add("diplomatic_stance","trading_stance")
    newCountry.add("primary_culture",extra[1])
    newCountry.add("religion",extra[2])
    newCountry.add("technology",tech)
    newCountry.add("centralization",50)
    newCountry.add("capital", cap)
    if country in ["ATE", "ANA","EDH", "ETD"]:
      newCountry.add("is_antagonist","yes")
    else:
      newCountry.add("is_antagonist","no")
    newCountry.add("own_control_core", provinces)
    provinces.bracketLevel=4
  loadedFileContents.countries.set("trade", TagList())
  loadedFileContents.countries.set("diplomacy", TagList())
  for name,val in loadedFileContents.countries.get("provinces").getNameVal(True):
    for k,i in val.getNameVal(True):
      if k!="modifier":
        val.remove(k)
  loadedFileContents.countryProps.add("")
  loadedFileContents.countryProps.addComment("scattered realms")
  countNewCountries=0
  # start_index = 1   #  it can start either at 0 or at 1
  with open("localization/english/countries_l_english.yml",encoding='utf-8-sig') as f:
    countryLocs=[line for line in f]
  countryLocs[-1]+="\n"
  countryLocs.append("#####SCATTERED REALMS#######\n")
  for area, region in processedFileData.areaToRegion.items():
    if not area in processedFileData.stateToCountry.keys():
      provinces=copy.deepcopy(loadedFileContents.areas.get(area).get("provinces"))
      anyArctic=False
      for p in provinces.names:
        terrain=loadedFileContents.provinces.get(p).get("terrain").strip('"')
        if terrain == "arctic":
          anyArctic=True
          break
      if anyArctic:
        continue

      tag="Z"+xlsxwriter.utility.xl_col_to_name(countNewCountries+26)
      while tag in processedFileData.countryCapitals.keys():
        countNewCountries+=1
        tag="Z"+xlsxwriter.utility.xl_col_to_name(countNewCountries+26)
      f=f"setup/countries/scattered/{tag}.txt"
      countryLocs.append(f' {tag}:0 "{processedFileData.areaNames[area]}"'+"\n")
      newCountry=processedFileData.countries.addReturn(tag)
      loadedFileContents.countryProps.add(tag, f)
      processedFileData.stateToCountry[area]=tag
      props=TagList()
      props.addReturn("color","= hsv").add(str(round(uniform(0,1),2))).add(str(round(uniform(0.5,1),2))).add(str(round(uniform(0.5,1),2)))
      # props.addReturn("color","= rgb").add(str(randint(100,255))).add(str(randint(100,255))).add(str(randint(100,255)))
      props.add("gender_equality","no")
      props.add("ship_names",TagList())
      cdf.outputToFolderAndFile(props , "setup/countries/scattered", f"{tag}.txt" ,3,output_folder,False,encoding="utf-8-sig")
      maxPops=-1
      for p in provinces.names:
        numPops=computePopNum(loadedFileContents.provinces.get(p))
        if numPops>maxPops:
          cap=p
          maxPops=numPops

      p=loadedFileContents.provinces.get(cap)
      culture=p.get("culture").strip('"')
      # try:
      if culture in processedFileData.cultureToGovernment:
        cultureGroup=processedFileData.cultureToGroup[culture]
        if cultureGroup in ["amrun_group","haldadian_group","yopi_group","easterling_group","haradrim_group"]: #there are just too many of these
          if uniform(0, 1)>0.5:
            # print(f'culture = "{culture}"')
            culture="beasts" #will be determined randomly later
      # except KeyError:
        # print(f'culture = "{culture}"')
        # pass
      # print(f'p = "{p}"')
      if culture in processedFileData.cultureToGovernment:
        newCountry.add("government",choices(["despotic_monarchy","tribal_kingdom","oligarchic_republic"],processedFileData.cultureToGovernment[culture])[0]) #randomize with bias depending on culture
      newCountry.add("diplomatic_stance","trading_stance")
      newCountry.add("primary_culture",culture)
      newCountry.add("religion",p.get("religion"))
      newCountry.add("technology",tech)
      newCountry.add("centralization",50)
      newCountry.add("capital",cap)
      processedFileData.countryCapitals[tag]=cap
      newCountry.add("is_antagonist","no")
      newCountry.add("own_control_core",provinces)
      countNewCountries+=1
    # print(f'vals = "{vals}"')
  os.makedirs(output_folder+"/localization/english", exist_ok=True)
  with open(output_folder+"/localization/english/countries_l_english.yml","w",encoding='utf-8-sig') as f:
    for line in countryLocs:
      f.write(line)

  for p,v in loadedFileContents.provinces.getNameVal(True):
    v.removeAny("nobles")
    v.removeAny("citizen")
    v.removeAny("freemen")
    v.removeAny("slaves")
    v.removeAny("tribesmen")
    v.removeAny("port_building")
    v.removeAny("fortress_building")
    v.set("province_rank","settlement") #todo: what about leftover treasures?


  for name,val in processedFileData.countries.getNameVal(True):
    cap=processedFileData.countryCapitals[name]
    loadedFileContents.provinces.get(cap).add("nobles", TagList("amount",2))
    loadedFileContents.provinces.get(cap).add("citizen", TagList("amount",6))
    loadedFileContents.provinces.get(cap).is_capital=True
    culture=val.get("primary_culture").strip('"')
    if culture!="beasts" and culture!="spider":
      cultureGroup=processedFileData.cultureToGroup[culture]
      if cultureGroup!="orcs_group": #increase number of orcs a bit
        processedFileData.cultureToNum[culture]+=1
        processedFileData.cultureGroupToNum[cultureGroup]+=1
  processedFileData.cultureToNum["lossoth"]+=100 #placed manually near arctic
  processedFileData.cultureGroupToNum["forodwaith_group"]+=4 #lossoth placed manually near arctic
  cultureList=list(processedFileData.cultureToNum.keys())
  cultureWeightList=[1/((x+1)**2+processedFileData.cultureGroupToNum[processedFileData.cultureToGroup[k]]) for k,x in processedFileData.cultureToNum.items()]
  for name,val in processedFileData.countries.getNameVal(True):
    culture=val.get("primary_culture").strip('"')
    cap=processedFileData.countryCapitals[name]
    area=processedFileData.provinceToArea[cap]
    if culture=="beasts" or culture=="spider":
      if area in ["goldladwen_area", "forovirkain_area","talath_oiohelka_area","sarch_nia_linquelie_area"]:
        newCulture="lossoth"
      else:
        newCulture=choices(cultureList, cultureWeightList)[0]
        # print(f'newCulture = "{newCulture}"')
        processedFileData.cultureToNum[newCulture]+=1
        processedFileData.cultureGroupToNum[processedFileData.cultureToGroup[newCulture]]+=1
        cultureWeightList=[1/((x+1)**2+processedFileData.cultureGroupToNum[processedFileData.cultureToGroup[k]]) for k,x in processedFileData.cultureToNum.items()]
      newReligion=choices(["iluvatarism","melkorism"],processedFileData.cultureToReligion[newCulture])[0]
      val.add("government",choices(["despotic_monarchy","tribal_kingdom","oligarchic_republic"],processedFileData.cultureToGovernment[newCulture])[0]) #randomize with bias depending on culture
      val.set("primary_culture",newCulture)
      val.set("religion",newReligion)
      # cap=processedFileData.countryCapitals[country]
      provinces=val.get("own_control_core").names
      for p in provinces:
        loadedFileContents.provinces.get(p).set("culture", newCulture)
        loadedFileContents.provinces.get(p).set("religion", newReligion)
  # print(f'processedFileData.cultureToNum = "{processedFileData.cultureToNum}"')
  # print(f'processedFileData.cultureGroupToNum = "{processedFileData.cultureGroupToNum}"')

  for area, region in processedFileData.areaToRegion.items():
    if not area in processedFileData.stateToCountry.keys():
      continue
    tag=processedFileData.stateToCountry[area]
    culture = processedFileData.countries.get(tag).get("primary_culture")
    gov = processedFileData.countries.get(tag).get("government")
    is_tribal = "tribal" in gov
    if is_tribal:
      popChoices=["tribesmen" for _ in range(5)]+["slaves" for _ in range(2)]
    else:
      popChoices=["freemen" for _ in range(5)]+["slaves" for _ in range(2)]+["citizen" for _ in range(1)]
    provinces=processedFileData.areaToProvince[area]
    if culture.strip('"')!="lossoth":
      for p in provinces:
        if loadedFileContents.provinces.get(p).get("terrain").strip('"')=="arctic":
          loadedFileContents.provinces.get(p).set("terrain",'plains')
    if culture.strip('"')=="nurnim":
      for p in provinces:
        if loadedFileContents.provinces.get(p).get("terrain").strip('"')=="wasteland":
          loadedFileContents.provinces.get(p).set("terrain",'steppe')
    # provinces=[p for p in processedFileData.areaToProvince[area] if loadedFileContents.provinces.get(p).get("terrain").strip('"')!="arctic"]
    numPops=50-len(provinces)-8
    baseCiv=5
    if not is_tribal:
      baseCiv+=15
    for p in provinces:
      pp=loadedFileContents.provinces.get(p)
      pp.add("slaves", TagList("amount",1)) #base slaves to avoid levy messup
      pp.set("culture", culture)
      pp.set("religion", processedFileData.countries.get(tag).get("religion"))
      if not hasattr(pp, "is_capital"):
        pp.set("civilization_value", baseCiv)
      else:
        pp.set("civilization_value", baseCiv+15)
    def addPop(p, type):
      try:
        pops=int(p.get(type).get("amount"))
        p.get(type).set("amount",pops+1)
      except ValueError:
        pops=0
        p.add(type, TagList("amount",1))
    for _ in range(numPops):
      p=loadedFileContents.provinces.get(choice(provinces))
      addPop(p, choice(popChoices))

  def removeComment(t):
    if type(t)==TagList:
      for i in range(len(t.comments)):
        t.comments[i]=""
  def empty(t):
    return t[0]=='' and t[1]=='' and t[2]==''

  processedFileData.countryListsUpdate()


  loadedFileContents.provinces.applyOnAllLevel(removeComment)
  loadedFileContents.provinces.deleteOnLowestLevel(empty)


  for i in range(len(loadedFileContents.provinces.names)):
    j=loadedFileContents.provinces.names[i]
    jj=int(j)

    culture=loadedFileContents.provinces.vals[i].get("culture").strip('"')
    terrain=loadedFileContents.provinces.vals[i].get("terrain").strip('"')
    is_impassable=(terrain=='impassable_terrain')
    if j in processedFileData.provinceNames:
      loadedFileContents.provinces.comments[i]="#"+processedFileData.provinceNames[ j]


    if j in processedFileData.ownerCountry:
      loadedFileContents.provinces.comments[i]+=f" ({processedFileData.ownerCountry[j]})"

      if culture=="beasts":
        loadedFileContents.provinces.vals[i].set("culture", f'"{processedFileData.countryCulture[processedFileData.ownerCountry[j]]}"')
        print(f"{j} owned but beast culture")
      if j in processedFileData.uninhabitable:
        print(f"{j} owned but uninhabitable")
    else:
      if j in processedFileData.uninhabitable:
        loadedFileContents.provinces.comments[i]+=" (uninhabitable)"
      else:
        if is_impassable and not processedFileData.provinceNames[j].startswith("River"):
          loadedFileContents.provinces.comments[i]+=" (impassable)"
        elif jj in processedFileData.impassable_terrain_list:
          # setTerrain(i, "riverine_terrain")
          loadedFileContents.provinces.comments[i]+=" (impassable river)"
        elif int(j) in processedFileData.river_provinces:
          loadedFileContents.provinces.comments[i]+=" (river)"
          # setTerrain(i, "riverine_terrain")
        elif int(j) in processedFileData.lake_provinces:
          loadedFileContents.provinces.comments[i]+=" (lake)"
          # setTerrain(i, "ocean")
        elif int(j) in processedFileData.allWaterProvinces:
          loadedFileContents.provinces.comments[i]+=" (sea)"
        else:
          loadedFileContents.provinces.comments[i]+=" (unowned)"
      loadedFileContents.provinces.vals[i].set("civilization_value", 0)


    if j in processedFileData.provinceToArea:
      loadedFileContents.provinces.comments[i]+=f" ({processedFileData.provinceToArea[j]})"
    if j in processedFileData.provinceToRegion:
      loadedFileContents.provinces.comments[i]+=f" ({processedFileData.provinceToRegion[j]})"



  for v in loadedFileContents.countries.get("family").get("families").vals:
    if type(v)==TagList:
      v.forceMultiLineOutput = True


  ##### removing on actions ####
  for i in [1,2,3,6,7]:
    loadedFileContents.codeOnAction.get("on_game_initialized").get("events").remove(f"br_pops.{i}")
    loadedFileContents.monthlyCountryOnAction.get("monthly_country_pulse").get("events").remove(f"br_pops.{i}")
  for i in [1,3]:
    loadedFileContents.monthlyCountryOnAction.get("monthly_country_pulse").get("events").remove(f"lotr_war_events.{i}")
  for i in [2,3,4,5,8,10,11]:
    loadedFileContents.monthlyCountryOnAction.get("monthly_country_pulse").get("events").remove(f"lotr_storyline_events.{i}")
  for i in [2,102]:
    loadedFileContents.monthlyCountryOnAction.get("monthly_country_pulse").get("events").remove(f"lotr_sacrifice_events.{i}")
  for i in range(1,6):
    loadedFileContents.codeOnAction.get("on_game_initialized").get("events").remove(f"br_truce.{i}")
    loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("events").remove(f"br_truce.{i}")
  for i in [1,4,5,6,7]:
    loadedFileContents.codeOnAction.get("on_game_initialized").get("events").remove(f"lotr_startup.{i}")
  loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("events").remove(f"lotr_startup.7")
  loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("events").remove(f"br_sauron.4")
  for i in [5,6,7]:
    loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("events").remove(f"lotr_maintenance.{i}")
  loadedFileContents.monthlyCountryOnAction.get("monthly_country_pulse").get("events").remove(f"lotr_maintenance.2")
  for i in [1,2,3,4,6]:
    loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("events").remove(f"lotr_migration_events.{i}")
  loadedFileContents.codeOnAction.get("on_game_initialized").get("effect").remove("lotr_ancient_glory_init_effect")
  loadedFileContents.codeOnAction.get("on_game_initialized").get("effect").remove("lotr_tiny_country_ai_setup")
  loadedFileContents.codeOnAction.get("on_game_initialized").get("effect").remove("lotr_fleet_init")
  loadedFileContents.codeOnAction.get("on_game_initialized").get("effect").add("set_global_variable","lotr_one_ring_allow_ai")
  for action in ["on_military_annex","on_diplomatic_annex"]:
    eff=loadedFileContents.codeOnAction.get(action).get("effect")
    eff.addReturnFront("every_character").add("limit", (TagList("has_trait", "nazgul"))).addReturn("random_country").add("limit", (TagList("country_culture_group", "orcs_group"))).addReturn("prev").add("move_country","prev")
  loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("effect").remove("lotr_gondor_vassal_update")
  i=loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("on_actions").names.index("corsair_raid_events_pulse")
  loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("on_actions").removeIndex(i-1)
  loadedFileContents.yearlyCountryOnAction.get("yearly_country_pulse").get("on_actions").removeIndex(i-1)
  i=loadedFileContents.yearlyProvOnAction.get("yearly_province_pulse").get("on_actions").names.index("lotr_assimilation_pulse")
  loadedFileContents.yearlyProvOnAction.get("yearly_province_pulse").get("on_actions").removeIndex(i-1)
  loadedFileContents.yearlyProvOnAction.get("yearly_province_pulse").get("on_actions").removeIndex(i-1)
  tmp=loadedFileContents.yearly_character.get("yearly_character_pulse").get("random_events")
  for name, val in tmp.getNameVal(True):
    if type(val)==str and "sauron" in val:
      tmp.removeNameVal(name,val)
  cdf.outputToFolderAndFile(loadedFileContents.codeOnAction , "common/on_action/", "00_specific_from_code.txt" ,3,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.monthlyCountryOnAction , "common/on_action/", "00_monthly_country.txt" ,3,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.yearlyCountryOnAction , "common/on_action/", "00_yearly_country.txt" ,3,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.yearlyProvOnAction , "common/on_action/", "00_yearly_province.txt" ,3,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.yearly_character , "common/on_action/", "yearly_character_pulse.txt" ,3,output_folder,False,encoding="utf-8-sig")

  ##### removing decisions ####
  cdf.outputToFolderAndFile(TagList().addComment("cleared") , "decisions", "BR_mechanics.txt" ,2,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(TagList().addComment("cleared") , "decisions", "00_gondor_decisions.txt" ,2,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(TagList().addComment("cleared") , "decisions", "BR_rangers_of_the_north.txt" ,2,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(TagList().addComment("cleared") , "decisions", "00_gondor_decisions.txt" ,2,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(TagList().addComment("cleared") , "decisions", "BR_melkor_rulers.txt" ,2,output_folder,False,encoding="utf-8-sig") #normal conversion re-enabled
  for d in ["lotr_rohan_break_gondor_decision","lotr_restore_rohan_decision","lotr_restore_gondor_decision","lotr_force_ranger_subjects_decision","lotr_satrapy_break_gondor_decision","lotr_attack_melkor_vassals","lotr_protect_the_free_people", "lotr_orc_conquest_decision"]:
    loadedFileContents.lotr_other_decisions.get("country_decisions").remove(d)
  for d in ["release_dorw_decision","release_dale_decision","release_gondor_decision","release_dol_amorth_decision","release_rohan_decision"]:
    loadedFileContents.lotr_other_decisions.get("country_decisions").remove(d)
  cdf.outputToFolderAndFile(loadedFileContents.lotr_other_decisions , "decisions", "lotr_other_decisions.txt" ,2,output_folder,False,encoding="utf-8-sig")

  ##### removing op traits ######
  for name,val in loadedFileContents.BR_rings.getNameVal(True):
    if not "one_ring" in name:
      for n,_ in val.getNameVal(True):
        if n in ["charisma", "finesse", "zeal","martial","health","country"]:
          val.remove(n)
  for name,val in loadedFileContents.BR_racial.getNameVal(True):
    if name!="restored_sauron":
      for n,_ in val.getNameVal(True):
        if n in ["charisma", "finesse", "zeal","martial","country","monthly_character_popularity","unit","character_loyalty"]:
          val.remove(n)
  for name,val in loadedFileContents.BR_bloodlines.getNameVal(True):
    for n,_ in val.getNameVal(True):
      if n in ["charisma", "finesse", "zeal","martial","country","monthly_character_popularity","unit","character_loyalty"]:
        val.remove(n)
  cdf.outputToFolderAndFile(loadedFileContents.BR_rings , "common/traits/", "BR_rings.txt" ,0,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.BR_racial , "common/traits/", "BR_racial.txt" ,0,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.BR_bloodlines , "common/traits/", "BR_bloodlines.txt" ,0,output_folder,False,encoding="utf-8-sig")

  ##### removing modifiers ######
  for name,val in loadedFileContents.lotr_from_events_province.getNameVal(True):
    if name in ["minas_anor_modifier","minas_anor_corrupted_modifier","supplied_from_the_rear","minas_ithil_modifier","black_gate_modifier","orthanc_modifier","helms_deep_modifier","argonath_modifier","umbar_harbour_modifier","seaward_modifier","island_fortress_modifier","osgiliath_modifier","caras_galadhon_modifier","lothlorien_from_moria_modifier","mithlond_harbour_modifier","imladris_modifier","elostirion_modifier","arestirion_modifier","ivrostirion_modifier","amon_lind_modifier","dale_modifier","esgaroth_modifier","erebor_modifier","iron_hills_modifier","moria_west_gate_modifier","fanuidhol_modifier","durins_tower_modifier","moria_east_gate_modifier","barad_dur_modifier","barad_dur_foundations_modifier","dol_guldur_modifier","carn_dum_modifier",]:
      val.clear()
      val.add("local_defensive",0.01) #make sure they still have an icon
    elif name in ["elven_forests_modifier","woodmen_forests_modifier","dwarven_hills_modifier","dwarven_mountain_modifier","dwarven_halls_modifier","goblin_hills_mountain_caves_modifier","elven_steppes_modifier","elven_dessert_modifier","other_steppes_modifier","other_dessert_modifier","hobbit_holes_modifier","stuffed_hobbit_holes_modifier"]: #NOT "forodwaith_arctic_modifier",,"uruk_orc_vulcanic_modifier"
      for n,v in val.getNameVal(True):
        if n == "local_population_growth" or n == "local_population_capacity_modifier":
          val.remove(n)
  cdf.outputToFolderAndFile(loadedFileContents.lotr_from_events_province , "common/modifiers/", "lotr_from_events_province.txt" ,0,output_folder,False,encoding="utf-8-sig")

  ##### remove OP character stats #####
  for fileName in os.listdir("setup/characters/"):
    if fileName.startswith("00_") or fileName=="_CHARACTER IDS LIST_.txt":
      continue
    charFile=TagList(0)
    charFile.readFile("setup/characters/"+fileName,encoding='utf-8-sig')
    if len(charFile.names)==0:
      charFile.addComment("empty")
    for _,countryVal in charFile.getNameVal(True):
      for charId,char in countryVal.getNameVal(True):
        if type(char)==TagList:
          for attribute,_ in char.getNameVal(True):
            if attribute in ["no_stats", "add_martial","add_charisma","add_finesse","add_zeal","add_gold"]:
              char.remove(attribute)
    cdf.outputToFolderAndFile(charFile , "setup/characters", fileName ,2,output_folder,False,encoding="utf-8-sig")




  cdf.outputToFolderAndFile(loadedFileContents.provinces , "setup/provinces", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  cdf.outputToFolderAndFile(loadedFileContents.countries , "setup/main", "00_default.txt" ,4,output_folder,False)
  cdf.outputToFolderAndFile(loadedFileContents.countryProps , "setup/countries", "countries.txt" ,2,output_folder,False,encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(loadedFileContents.treasures , "setup/main", "lotr_treasures.txt" ,2,output_folder,False)

### undoing disabling assimilation #####
  buildings=TagList(0)
  buildings.readFile("common/buildings/lotr_buildings.txt",encoding='utf-8-sig')
  for b in ["theathre_building"]:
    buildings.get(b).replaceName("local_pop_conversion_speed","local_pop_assimilation_speed")
    buildings.get(b).get("modification_display").replace("1","local_pop_assimilation_speed")
  for b in ["commerce_building","local_forum_building"]:
    buildings.get(b).replaceName("local_pop_conversion_speed_modifier","local_pop_assimilation_speed_modifier")
    buildings.get(b).get("modification_display").replace("1","local_pop_assimilation_speed_modifier")
  cdf.outputToFolderAndFile(buildings , "common/buildings/", "lotr_buildings.txt" ,2,output_folder,False,encoding="utf-8-sig")
  policies=TagList(0)
  policies.readFile("common/governor_policies/00_default.txt",encoding='utf-8-sig')
  tmp=policies.get("cultural_assimilation").get("ai_will_do")
  for i,(name,val) in enumerate(tmp.getNameVal()):
    if type(val)==TagList and val.getAnywhere("has_culture_group"):
      tmp.removeIndex(i)
  cdf.outputToFolderAndFile(policies , "common/governor_policies/", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  gw=TagList(0)
  gw.readFile("common/great_work_effects/00_default.txt",encoding='utf-8-sig')
  tmp=gw.get("gw_effect_culture_expansion").get("great_work_tier_effect_modifiers")
  for i in range(1,5):
    tmp2=tmp.get(f"gw_effect_culture_expansion_tier_{i}").get("country_modifier")
    tmp2.set("global_pop_conversion_speed_modifier",round(0.1*i,2))
    tmp2.add("global_pop_assimilation_speed_modifier",round(0.1*i,2))
  cdf.outputToFolderAndFile(gw , "common/great_work_effects/", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  inv=TagList(0)
  inv.readFile("common/inventions/00_civic_inventions.txt",encoding='utf-8-sig')
  inv.get("civic_2").get("assimilate_pop_cost_modifier_inv_1").get("modifier").addUnique("global_pop_assimilation_speed_modifier",0.1)
  cdf.outputToFolderAndFile(inv , "common/inventions/", "00_civic_inventions.txt" ,2,output_folder,False,encoding="utf-8-sig")
  laws=TagList(0)
  laws.readFile("common/laws/00_monarchy.txt",encoding='utf-8-sig')
  tmp=laws.get("monarchy_religious_laws")
  p=laws.addReturn("placeholder")
  p.addReturn("potential").add("always","no")
  p.add("age_of_the_orc",tmp.get("age_of_the_orc"))
  tmp.get("potential").clear()
  tmp.get("potential").add("is_monarchy","yes")
  tmp.get("religious_tolerance_monarchy").clear()
  tmp.get("religious_integration_efforts").get("allow").clear()
  tmp.get("religious_integration_efforts").get("allow").add("invention","omen_power_inv_4")
  tmp.remove("age_of_the_orc")
  tmp2=tmp.addReturn("monarchy_religious_mandate_military")
  tmp2.addReturn("allow").add("invention","omen_power_inv_4")
  tmp2.addReturn("modifier").add("global_pop_assimilation_speed","0.25").add("global_pop_assimilation_speed_modifier",0.3)
  cdf.outputToFolderAndFile(laws , "common/laws/", "00_monarchy.txt" ,2,output_folder,False,encoding="utf-8-sig")
  laws=TagList(0)
  laws.readFile("common/laws/00_tribal.txt",encoding='utf-8-sig')
  laws.get("tribal_decentralized_laws").get("tribal_decentralized_laws_2").get("modifier").replaceName("global_pop_conversion_speed_modifier","global_pop_assimilation_speed_modifier")
  laws.get("tribal_super_centralized_laws").get("potential").remove("NOT")
  cdf.outputToFolderAndFile(laws , "common/laws/", "00_tribal.txt" ,2,output_folder,False,encoding="utf-8-sig")
  hardcoded=TagList(0)
  hardcoded.readFile("common/modifiers/00_hardcoded.txt",encoding='utf-8-sig')
  hardcoded.get("roads_in_province").addUnique("local_pop_assimilation_speed_modifier",0.025)
  cdf.outputToFolderAndFile(hardcoded , "common/modifiers/", "00_hardcoded.txt" ,2,output_folder,False,encoding="utf-8-sig")
  for pop in ["tribesmen","slaves","nobles","freemen","citizen"]:
    tmp=TagList(0)
    tmp.readFile(f"common/pop_types/{pop}.txt",encoding='utf-8-sig')
    if pop in ["nobles","tribesmen"]:
      tmp.get(pop).set("assimilate",0.6)
    else:
      tmp.get(pop).set("assimilate",0.4)
    cdf.outputToFolderAndFile(tmp , "common/pop_types/", f"{pop}.txt" ,2,output_folder,False,encoding="utf-8-sig")

  ###undoing enslavement changes ###
  govs = TagList(0)
  govs.readFile("common/governments/00_default.txt",encoding='utf-8-sig')
  for _,gov in govs.getNameVal(True):
    gov.get("base").remove("enslavement_efficiency")
  cdf.outputToFolderAndFile(govs , "common/governments/", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  heritages = TagList(0)
  heritages.readFile("common/heritage/00_country_specific.txt",encoding='utf-8-sig')
  heritages.get("sauron_heritage").get("modifier").remove("enslavement_efficiency")
  cdf.outputToFolderAndFile(heritages , "common/heritage/", "00_country_specific.txt" ,2,output_folder,False,encoding="utf-8-sig")
  heritages = TagList(0)
  heritages.readFile("common/heritage/01_groups.txt",encoding='utf-8-sig')
  heritages.get("orcish_heritage").get("modifier").remove("enslavement_efficiency")
  cdf.outputToFolderAndFile(heritages , "common/heritage/", "01_groups.txt" ,2,output_folder,False,encoding="utf-8-sig")
  trads = TagList(0)
  trads.readFile("common/military_traditions/00_barbarian.txt",encoding='utf-8-sig')
  trads.get("barbarian_philosophy").get("barbarian_infantry_path_5").get("modifier").set("enslavement_efficiency",0.2)
  trads.get("barbarian_philosophy").get("barbarian_infantry_path_5").get("allow").clear()
  cdf.outputToFolderAndFile(trads , "common/military_traditions/", "00_barbarian.txt" ,2,output_folder,False,encoding="utf-8-sig")
  trads = TagList(0)
  trads.readFile("common/military_traditions/00_easterling.txt",encoding='utf-8-sig')
  trads.get("easterling_philosophy").get("easterling_infantry_path_4").get("modifier").set("enslavement_efficiency",0.2)
  trads.get("easterling_philosophy").get("easterling_infantry_path_4").get("allow").clear()
  cdf.outputToFolderAndFile(trads , "common/military_traditions/", "00_easterling.txt" ,2,output_folder,False,encoding="utf-8-sig")

  #nerfing imba trade goods
  goods = TagList(0)
  goods.readFile("common/trade_goods/00_default.txt",encoding='utf-8-sig')
  goods.get("gems").set("gold",1.5)
  cdf.outputToFolderAndFile(goods , "common/trade_goods/", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  goods = TagList(0)
  goods.readFile("common/trade_goods/LOTR_trade_goods.txt",encoding='utf-8-sig')
  goods.get("mithril").set("gold",2)
  cdf.outputToFolderAndFile(goods , "common/trade_goods/", "LOTR_trade_goods.txt" ,2,output_folder,False,encoding="utf-8-sig")

  ###### remove sauron saruman extra aggressive ###
  ai = TagList(0)
  ai.readFile("common/ai_plan_goals/BR_ai_goals.txt",encoding='utf-8-sig')
  ai.remove("is_mordor_aimod")
  ai.remove("is_isengard_aimod")
  tmp=ai.addReturn("is_orc_tribe_aimod")
  tmp.addComment("Tribes are normally less aggressive than monarchies. Offset this for orcs")
  tmp.addReturn("trigger").add("country_culture_group","orcs_group").add("is_tribal","yes")
  tmp.add("aggressive",50)
  cdf.outputToFolderAndFile(ai , "common/ai_plan_goals/", "BR_ai_goals.txt" ,2,output_folder,False,encoding="utf-8-sig")


  ##### allow normal subject stuff ####
  subjects = TagList(0)
  subjects.readFile("common/subject_types/00_default.txt",encoding='utf-8-sig')
  for name,val in subjects.getNameVal(True):
    allow=val.get("allow")
    if allow.getAnywhere("country_culture_group"):
      for i,(n,v) in reversed(list(enumerate(allow.getNameVal(True)))):
        if n in ["NOT","OR"] and v .getAnywhere("country_culture_group"):
          allow.removeIndex(i)
        if n == "scope:future_overlord" and v .getAnywhere("country_culture_group"):
          for ii,(nn,vv) in reversed(list(enumerate(v.getNameVal(True)))):
            if nn in ["NOT","OR"] and vv.getAnywhere("country_culture_group"):
              v.removeIndex(ii)
  cdf.outputToFolderAndFile(subjects , "common/subject_types/", "00_default.txt" ,0,output_folder,False,encoding="utf-8-sig")

  #### allow resettlement for all ####
  cultDec = TagList(0)
  cultDec.readFile("culture_decisions/lotr_culture_decisions.txt",encoding='utf-8-sig')
  cultDec.get("culture_decisions").get("lotr_forced_resettlement_cultural_decision").get("potential").get("scope:target_culture").remove("OR")
  cdf.outputToFolderAndFile(cultDec , "culture_decisions/", "lotr_culture_decisions.txt" ,2,output_folder,False,encoding="utf-8-sig")

  #### reenable normal character conversion ####
  charDec = TagList(0)
  charDec.readFile(gamePath+"common/character_interactions/convert_religion.txt",encoding='utf-8-sig')
  cdf.outputToFolderAndFile(charDec , "common/character_interactions/", "convert_religion.txt" ,2,output_folder,False,encoding="utf-8-sig")

  #### reenable normal country conversion ####


  locClass=LocList()
  locClass.limitLanguage(["en"])
  defaultDec = TagList(0)
  defaultDec.readFile("decisions/religious_conversion.txt",encoding='utf-8-sig')
  template=defaultDec.get("country_decisions").get("convert_to_eastern_animism")
  dec = TagList(0)
  dec2=dec.addReturn("country_decisions")
  dec2.add("convert_to_eastern_animism", template)
  for rel in ["iluvatarism","melkorism"]:
    def replaceReligion(t):
      if type(t)==TagList:
        if len(t.vals)==1 and t.vals[0]=="eastern_animism":
          t.vals[0]=rel
    content=copy.deepcopy(template)
    template.applyOnAllLevel(replaceReligion)
    name=f"convert_to_{rel}"
    dec2.add(name, template)
    locClass.addEntry(name, f"Convert to {rel}")
    locClass.addEntry("desc_"+name, f"Worship of {rel} have become an important part of the [COUNTRY.GetAdjective] religious ceremonies lately, and we have seen old rituals and traditions flourish in addition to our [COUNTRY.GetReligion.GetName] faith. Maybe it is time to put aside some of these newer ideas and revert back to our ancient heritage?")
  locClass.writeToMod(output_folder,"lotr_scattered_realms_extras","z")
  cdf.outputToFolderAndFile(dec , "decisions/", "religious_conversion.txt" ,2,output_folder,False,encoding="utf-8-sig")


  ##### some help for poor saruman #####

  events = TagList(0)
  events.readFile("events/LOTR_storyline_events.txt",encoding='utf-8-sig')
  saruman=events.get("lotr_storyline_events.1").get("option")
  saruman.addReturn("every_character").add("set_character_religion", "melkorism")
  saruman.remove("change_law")
  saruman.addReturn("every_owned_province").addReturn("define_pop").add("type","citizen").add("culture","urukhai").add("religion","melkorism")
  cdf.outputToFolderAndFile(events , "events/", "LOTR_storyline_events.txt" ,2,output_folder,False,encoding="utf-8-sig")

def computePopNum(province):
  num=0
  poptypes = ["nobles","citizen","freemen","slaves","tribesmen"]
  for name,val in province.getNameVal(True):
    if name in poptypes:
      num+=int(val.get("amount"))
  return num

if __name__ == "__main__":
  main()

