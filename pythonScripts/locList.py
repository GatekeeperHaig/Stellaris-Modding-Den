#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from googletrans import Translator
import re


class LocList:
  def __init__(self, translateRest=False):
    self.languages=["braz_por","english","french","german","polish","russian","spanish"]
    self.languageCodes=["pt","en","fr", "de","pl","ru", "es"]
    self.entries=[]
    self.dicts=dict()
    self.translateRest=translateRest
    for languageCode in self.languageCodes:
      self.dicts[languageCode]=dict()

  def addLoc(self, id, loc, language="en"):
    if language=="all":
      for k,d in self.dicts.items():
        d[id]=loc
    else:
      self.dicts[language][id]=loc
  def addEntry(self, gameLocId, string):
    # if not isinstance(stringOrList,str):
      self.entries.append([gameLocId, string])
    # else:
      # self.entries.append([gameLocId, [stringOrList]])
  def append(self, gameLocId, string):
    self.addEntry(gameLocId,string)
  def write(self,fileName, language, yml=True):
    if len(language)==2:
      languageCode=language
      language=self.languages[self.languageCodes.index(language)]
    else:
      languageCode=self.languageCodes[self.languages.index(language)]
    if self.translateRest:
      translator=Translator()

    localDict=self.dicts[languageCode]
    for englishKey, englishLoc in self.dicts["en"].items():
      # print(self.translateRest)
      if not englishKey in localDict:
        if self.translateRest:
          localDict[englishKey]=translator.translate(text=englishLoc, src="en", dest=languageCode).text
        else:
          localDict[englishKey]=englishLoc

    with io.open(fileName,'w', encoding="utf-8") as file:
      if yml:
        file.write(u'\ufeff')
        file.write("l_"+language+':\n')
      for entry in self.entries:
        if yml:
          file.write(" "+entry[0]+':0 "')
        # for loc in entry[1]:
        awaitingVar=False
        for loc in re.split("(@| |\.|,|:|§|\)|\\n)",entry[1]):
          if loc=="":
            continue
          if loc[0]=="@":
            awaitingVar=True
            # file.write(localDict[loc[1:]])
          elif awaitingVar:
            try:
              file.write(localDict[loc])
              awaitingVar=False
            except:
              print(entry[1])
              print(loc)
              raise
          else:
            file.write(loc)
        if yml:
          file.write('"')
        file.write("\n")