#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, os
import math
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np





def main():
  
  # tiersArmor=[0,1,2,3,4,5]
  # for i in range(len(tiersArmor)):
  #   tiersArmor[i]=float(tiersArmor[i])/5.0*4.0+1
  tiersArch=range(1,6)
  tiersArmor=range(1,6)
  #tiersArch=np.linspace(1, 5)
  archpart=0.3
  bsMin=40
  bsMax=560
  # order=[3,0,2,1,4] #alphabetical
  order=[0,1,2,3,4]
  order=[0,2,4,4] #station

  shipsizes=[1,2,4,8,16]
  shipsizes=[6,6,12,12,16] #station
  maxArmor=70
  givenValues=[[[1
  ,1.5,5],[0.6,0.655,0.9]],[[1,2,5],[0.55,0.705,0.925]],[[1,3,5],[0.5,0.82,0.95]],[[1,4,5],[0.45,0.91,0.975]],[[1,4.5,5],[0.4,0.95,1]]]
  armors=[]
  archs=[]
  shipI=-1
  p1=plt.figure()
  p1=p1.add_subplot(111)
  p2=plt.figure()
  p2=p2.add_subplot(111)
  for x,y in givenValues:
    shipI+=1
    if len(x)==2:
      f=interp1d(x,y, kind='linear')
    else:
      f=interp1d(x,y, kind='quadratic')
    # plt.plot(tiersArch,f(tiersArch))
    armors.append(f(tiersArmor))
    archs.append(f(tiersArch))
    armors[-1]=[int(round(a*(1-archpart)*maxArmor*shipsizes[shipI])) for a in armors[-1]]
    archs[-1]=[int(round(a*(archpart)*maxArmor*shipsizes[shipI])) for a in archs[-1]]
    # p1.plot([1,2,3,4,5,6],armors[-1])
    # p2.plot(tiersArch,archs[-1])
  print("ARMOR")
  for i in order:
    for val in armors[i]:
      print(val)
  print("ARCHS")
  for i in order:
    for val in archs[i]:
      print(val)
  # plt.show()

 
if __name__ == "__main__":
  main()