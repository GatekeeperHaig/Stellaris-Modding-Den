#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os, sys, io

# os.chdir(os.path.dirname(sys.argv[0]))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#default to exporting from English to all other languages and not overwriting pre-existing files
allLanguages = {'braz_por', 'english', 'french', 'german', 'polish', 'russian', 'spanish'}
sourceLanguage = 'english'
targetLanguages = allLanguages  - set([sourceLanguage])
input("This will overwrite all localisations in this folder with the English ones. This executable must be in a 'localisation' folder. Cancel (ctrl-c or closing the window) now if that is not intended (last chance!). Press Enter to continue...")
for dirpath, dirnames, files in os.walk("."):
  for name in files:
    if name.lower().endswith(".yml"):
      for language in targetLanguages:
        outName=name.replace("l_"+sourceLanguage, "l_"+language)
        outfolder=dirpath.replace(sourceLanguage, language)
        if outName!=name:
          if not os.path.exists(outfolder):
            os.makedirs(outfolder)
          with io.open(os.path.join(dirpath,name), 'r', encoding="utf-8") as infile:
            with io.open(os.path.join(outfolder,outName), 'w', encoding="utf-8") as outfile:
              foundHeader=False
              for line in infile:
                if not foundHeader:
                  if "l_"+sourceLanguage in line:
                    foundHeader=True
                    outfile.write(line.replace("l_"+sourceLanguage, "l_"+language))
                  else:
                    outfile.write(line)
input("Completed. Press Enter to continue...")