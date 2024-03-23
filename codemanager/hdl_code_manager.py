#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re
import code_manager

LANG_IDENTIFIERS = ["hdl"]

class HdlCodeManager(code_manager.CodeManager):


    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("hdl")


    def _command_project(self, specifier, **args):

        # TODO: placeholder
        print(f"creating a project using {self.TEMPLATES_ABS_PATH}/template_project")
