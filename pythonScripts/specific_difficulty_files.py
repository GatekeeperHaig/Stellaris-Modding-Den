#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io
from stellarisTxtRead import *
from copy import deepcopy
from googletrans import Translator
import re
from locList import LocList
from custom_difficulty_files import *

def main():

  locList=LocList()

  testEventFile=TagList("namespace", "sd_test")
  testEvent=TagList("id", "sd_test.0")
  testEventFile.add("country_event", testEvent)
  testEvent.add("is_triggered_only","yes")
  immediate=TagList()
  testEvent.add("immediate", immediate)
  everyCountry=TagList("limit", TagList("has_communications","prev"))
  immediate.add("set_variable", TagList("which", "sd_count").add("value", 0))
  immediate.add("every_country",everyCountry)

  testEvent.add("option", TagList("name", "sd_UP").add("hidden_effect", TagList("change_variable", TagList("which", "sd_orig").add("value", -10)).add("country_event", TagList("id", "sd_test.0"))).add("trigger", TagList("check_variable",TagList("which", "sd_orig").add("value", 0,"",">"))))

  everyCountry.add("prev", TagList("set_variable", TagList("which", "sd_check").add("value", "sd_orig")))
  for i in range(10):
    everyCountry.add("if", TagList("limit", TagList("prev", TagList("check_variable", TagList("which", "sd_count").add("value", "sd_check")))).add("save_global_event_target_as", "sd_test_target_{!s}".format(i)))
    everyCountry.add("prev", TagList("change_variable", TagList("which", "sd_check").add("value", "1")))
    testEvent.add("option", TagList("name", "sd_option_{!s}".format(i)).add("trigger", TagList("check_variable",TagList("which", "sd_count").add("value", "sd_orig_{!s}".format(i),"",">"))))
    locList.addEntry("sd_option_{!s}".format(i), "[sd_test_target_{!s}.GetName]".format(i))
    immediate.add("set_variable", TagList("which", "sd_orig_{!s}".format(i)).add("value", "sd_orig"))
    immediate.add("change_variable", TagList("which", "sd_orig_{!s}".format(i)).add("value", i))
  i+=1
  immediate.add("set_variable", TagList("which", "sd_orig_{!s}".format(i)).add("value", "sd_orig"))
  immediate.add("change_variable", TagList("which", "sd_orig_{!s}".format(i)).add("value", i))

  everyCountry.add("prev", TagList("change_variable", TagList("which", "sd_count").add("value", 1)))
  testEvent.add("option", TagList("name", "sd_DOWN").add("hidden_effect", TagList("change_variable",  TagList("which", "sd_orig").add("value", 10)).add("country_event", TagList("id", "sd_test.0"))).add("trigger", TagList("check_variable",TagList("which", "sd_count").add("value", "sd_orig_{!s}".format(i),"",">"))))


  outputToFolderAndFile(testEventFile, "events", "sd_test.txt", level=2, modFolder="../gratak_mods/specific_difficulty")
  # print(testEventFile)

  for language in locList.languages:
    outFolderLoc="../gratak_mods/specific_difficulty/localisation/"+language
    if not os.path.exists(outFolderLoc):
      os.makedirs(outFolderLoc)
    locList.write(outFolderLoc+"/sd_l_"+language+".yml",language)


if __name__ == "__main__":
  main()