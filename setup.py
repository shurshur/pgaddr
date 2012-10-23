#!/usr/bin/python

from distutils.core import setup
import py2exe
options = {
    "bundle_files": 1,
    "compressed": 1,
    "optimize": 2,
    "dist_dir": ".",
    "dll_excludes": ['w9xpopen.exe']
}

setup(console=['pgaddr.py'],
    options={"py2exe": options},
    zipfile = None,
)

import shutil
shutil.rmtree("build")
