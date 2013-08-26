import os
import sys

from distutils.core import setup
from distutils.sysconfig import get_python_lib

setup(
    name = "mediawiki_parser",
    url = "https://github.com/ucarbehlul/mediawiki-parser",
    description = "A parser for parsing mediawiki text with support to replacing templates",
    author = "Various",
    license = "GPL",
    requires = ["pijnu"],
    packages = ["mediawiki_parser"]
)

