#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, io,math
from cgm_automation_files import *

def main():

  os.chdir(os.path.dirname(__file__))

  createEffectDecisionStuff()
  automatedCreationAutobuildAPI(resources)
  #return
  automatedCreationAutobuildAPI(resources,"alphamod",["../NOTES/api files/cgm_api_files/alphamod/"])


if __name__ == "__main__":
  main()
