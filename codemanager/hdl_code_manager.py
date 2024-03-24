#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re
import code_manager
from operator import itemgetter

LANG_IDENTIFIERS = ["hdl"]

class HdlCodeManager(code_manager.CodeManager):


    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("hdl")

        # set variables for hdl project directory structure
        self.PRJ_DIRS = {                                   \
                'rtl':          "rtl",                      \
                'simulation':   "sim",                      \
                'testbench':    "tb",                       \
                'constraints':  "constraints",              \
                'tcl':          "tcl",                      \
                'blockdesign':  "bd",                       \
                'xilinx_ips':   "xips",                     \
                'software':     "sw",                       \
        }

    def _command_project(self, specifier, **args):
        """Creates the skeleton for an hdl project as generic as possible. That 
        mainly is, create the hdl project directory structure and add common 
        build scripts like makefile and vivado project generation script (given 
        that a xilinx project is asked for)

        !!! The method can create a new project, including project directory, or 
        act from within an existing project directory. This is decided on 
        whether or not args["target"] is not specified (which means passing a -t 
        option to m_code_manager or not). !!!

        An existing project will never be deleted. If the user confirms to 
        edit/overwrite an existing directory, that means that the contents will 
        be added to the existing directory (instead of doing nothing). The 
        design guideline is to really only delete files when that is 
        unambiguously confirmed. In this case, if the user really wants an 
        entirely new project, they can easily delete an existing one manually.
        """

        # TODO: only directory creation so far to facilitate developing other 
        # command handlers. IMPLEMENT THE REST!

        # TODO: temporary rtl directory structure. So far, everything gets 
        # dumped into 'rtl' with no subdirectories whatsoever. Works for small 
        # projects, not ideal for larger projects, but that's something to 
        # address later on.

        if "target" in args:
            prj_name = args["target"]
            if self._check_target_edit_allowed(prj_name):
                try:
                    os.mkdir(prj_name)
                except:
                    # no need to handle the exception if the directory prj_name 
                    # exists, that's taken care of and confirmed in 
                    # self._check_target_edit_allowed
                    pass
                os.chdir(prj_name)

        # some directories are omitted here: xips, bd
        # reason: they really only makes sense when the respective feature is 
        # used, and it's less likely/unintended that the user is going to edit 
        # or create things in these directories without going through the 
        # codemanager flow. Let's see how many days it takes until I get proven 
        # wrong about the last sentence (today is the 2024-03-24)...
        project_dirs = itemgetter(
                'rtl', 'constraints', 'simulation', 'testbench', 'tcl')(self.PRJ_DIRS)
        for directory in project_dirs:
            if self._check_target_edit_allowed(directory):
                try:
                    os.mkdir(directory)
                except:
                    # again, if a project directory already exists, that's fine 
                    # (assuming that it's a directory, theoretically could be 
                    # a file as well. but at some point users gotta act 
                    # reasonably, such as not to create files with meaningful 
                    # names and without file extensions)
                    pass



