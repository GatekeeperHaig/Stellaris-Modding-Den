#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open("copiedBuildings.txt") as file:
  # print(file.read())
  buildings=[line.strip() for line in file]
# print(buildings)

with open("events/z_build_upgraded_autobuild_events.txt") as file:
  fileLines=[line for line in file]

with open("events/z_build_upgraded_autobuild_events.txt",'w') as file:
  for line in fileLines:
    file.write(line)
    for building in buildings:
      if "\t"+building+" =" in line:
        file.write(line.replace(building,building+"_direct_build"))
        break