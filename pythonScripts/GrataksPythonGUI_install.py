#!/usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
import sys


def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install","--user", package])



install("Pillow")
install("googletrans")
install("pyexcel-io")
install("pyexcel-ods")
# install("")
# install("")
# install("")

