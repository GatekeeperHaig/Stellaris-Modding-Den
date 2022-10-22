#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
import custom_difficulty_files as cdf
import math
import yaml
from yaml.loader import SafeLoader
from locList import LocList
from random import randint
from PIL import Image
from copy import copy
import pickle
import random
from imperatorFile import getProvinceToPixels





def main():




 
  portLocators=TagList(0)
  portLocators.readFile("gfx/map/map_object_data/port_locators.txt",encoding='utf-8-sig')

 

  sea_of_rhun=list(range(3500,3505+1))
  Haragaer=list(range(4744,4894+1))
  EdgeSee=list(range(5478,5499+1))
  Belegaer=list(range(5500,5687+1))
  river_provinces = list(range(4895,4988+1))
  allSeas=sea_of_rhun+Haragaer+EdgeSee+Belegaer+river_provinces

  uninhabitable = set(map(str,list(range(4969,4988+1))+list(range(5453,5459+1))+list([552,2616,3765,577,564,563,576,575,604,605,606,607,608,602,603,2696,2697,2698,2607,2604,2605,3402,3403,3404,476,475,478,479,2961,2960,2959,2954,2955,2984,2985,2986,540,539,538,537,536,535,547,546,545,544,543,542,2617,594,595,596,597,94,27,95,91,92,581,582,2046,2045,2044,87,85,89,88,83,82,80,2375,2376,7,3,17,23,48,1965,583,584,585,586,587,588,589,590,2997,2998,3000,3001,2988,2991,2989,2992,2994,3003,2990,2995,2996,2993,3002,579,578,2048,2049,2050,2051,2052,2053,593,3142,3143,3146,3144,3145,3147,3148,3149,3150,51,2378,2377,3638,3639,3678,3679,3680,3681,3682,3683,3684,3685,3686,3687,3688,3689,3690,3691,3692,3693,3694,3593,3709,3719,3611,3613,3612,3653,3654,3656,3660,3718,3626,3659,3706,3607,3608,3609,3740,3741,3742,3743,3744,3745,3746,3747,3787,3781,3779,3778,3777,3784,3793,3794,3792,3790,3789,3791,3775,3776,3771,3795,3797,2730,2731,2732,2733,2739,2737,2741,2735,2740,2742,2745,2744,2743,3860,3862,3863,3864,3865,3866,3874,3867,3881,3871,3869,3552,3553,3880,3879,3868,3872,3873,3870,3554,2738,2750,2749,2748,2747,2746,2751,3875,2729,2769,2728,3582,3581,3580,3643,3637,3904,3909,3910,3937,3938,3939,5215,5217,5218,5174,5176,5291,5292,5293,5306,5307,5308,5309,5310,5311,5312,5313,5314,5315,5317,5318,5319,5320,5321,5322,5323,5324,5326,5327,5328,5329,5330,5331,5332,5333,5334,5336,5337,5338,5339,5340,5341,5342,5343,5344,5345,5348,5386,5387,5388,5389,5390,5433,5434,5435,5399,5400,5401,5378,5379,5375,5274,5275,5276,5277,5278,5281,5279,5282,5283,5406,5429,5430,5297,5298,5299,5437,5024,5025,5443,5444,5445,5446,5447,5448,5449,5450,5451,5067,5463,5396,5395,5409,5280,5462,5466,5284,5286,5287,5294,5296,5452,5410,5411,5412,5216,5252,5285,5288,5060,5273])))

  with open("map_data/ports.csv",'r') as file:
    portsFile=[line.strip().split(";") for line in file if len(line.split(";"))>1 and not line.startswith("#")]
  portsDict=dict()
  portsNewDict=dict()
  for line in portsFile[1:-1]:
    portsDict[line[0]]=line[1:]
  # print(f'portsDict = "{portsDict}"')
  portsFile[-1][0]="end"
  portsFile[-1][1]="end"

  provinceToPixels, pixelToProvince, xM, yM = getProvinceToPixels()
  locs=portLocators.get("game_object_locator").get("instances")
  for loc in locs.vals:
    i=loc.get("id")
    if not i in portsDict:
      position=[int(float(a)) for a in loc.get("position").names]
      waterI=pixelToProvince[position[0]*yM+position[2]]
      # if waterI not in allSeas:
      #   found=False
      #   for ii in [-1,1]:
      #     if found==False:
      #       for jj in [-1,1]:
      #         waterI=pixelToProvince[(position[0]+ii)*yM+position[2]+jj]
      #         if waterI in allSeas:
      #           print(f'waterI = "{waterI}"')
      #           found=True
      #           break
      if waterI in Haragaer+Belegaer+river_provinces+sea_of_rhun:
        # if waterI in [4876,4875,4877,4873,4874]: #tiny lakes
          # continue
        # print(f'i = "{i}"')
        portsNewDict[i]=[str(waterI),str(position[0]),str(position[2]),' #added by script']
      # elif waterI in EdgeSee+sea_of_rhun:
      #   print(f'edge or rhun = "{i}"')
      # if not waterI in allSeas:
      #   print(f'none = "{i}":{waterI}')
  portsFile=portsFile[:-1]+[[i]+portsNewDict[i] for i in portsNewDict.keys()]+portsFile[-1:]
  # print(f'portsFile = "{portsFile}"')
  with open("map_data/ports.csv",'w') as file:
    for line in portsFile:
      file.write(";".join(line)+"\n")

  with open("coastal.txt",'w') as file:
    file.write(" ".join(portsDict.keys()))

      # port_building = 5


  # provinceFile=TagList(0)
  # provinceFile.readFile("setup/provinces/00_default.txt",encoding='utf-8-sig')

  # for i in range(len(provinceFile.names)):
  #   j=provinceFile.names[i]
  #   if j in portsDict:
  #     if provinceFile.vals[i].count("port_building")==0:
  #       provinceFile.vals[i].add("port_building",1)

  # output_folder="."
  # cdf.outputToFolderAndFile(provinceFile , "setup/provinces", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")

  
  # cdf.outputToFolderAndFile(provinceFile , "setup/provinces", "00_default.txt" ,2,output_folder,False,encoding="utf-8-sig")
  # cdf.outputToFolderAndFile(countryFile , "setup/main", "00_default.txt" ,4,output_folder,False)
  # cdf.outputToFolderAndFile(treasureFile , "setup/main", "lotr_treasures.txt" ,2,output_folder,False)
  # cdf.outputToFolderAndFile(newClimate , "map_data", "climate.txt" ,4,output_folder,encoding="utf-8")
  # cdf.outputToFolderAndFile(terrainFile , "common/province_terrain", "00_province_terrain.txt" ,2,output_folder,False,encoding="utf-8-sig")

  

if __name__ == "__main__":
  main()

