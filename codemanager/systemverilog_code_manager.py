#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re
import code_manager
import hdl_code_manager

LANG_IDENTIFIERS = ["systemverilog", "sv"]

class SystemverilogCodeManager(code_manager.CodeManager):

    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("systemverilog")
        self.hdl_code_manager = hdl_code_manager.HdlCodeManager()


    def _command_module(self, specifier, **args):

        # TODO: placeholder
        print(f"creating a module using {self.TEMPLATES_ABS_PATH}/template_project")


    def run_code_manager_command(self, command, specifier, **args):

        # "pass-through" hdl code manager commands, such that the systemverilog 
        # code manager can be used with any command that the hdl code manager 
        # has as well (not particularly necessary, but it's a nice convenience 
        # feature)
        try:
            fun_command = getattr(self, '_command_' + command)
        except:
            fun_command = getattr(self.hdl_code_manager, '_command_' + command)
        fun_command(specifier, **args)
#         print("Please implement this function for each language-specific Code_Manager!")
        
