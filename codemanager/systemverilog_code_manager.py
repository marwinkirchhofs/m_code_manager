#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os
import code_manager
import hdl_code_manager

LANG_IDENTIFIERS = ["systemverilog", "sv"]


class SystemverilogCodeManager(code_manager.CodeManager):

    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("systemverilog")
#       Why the additional hdl code manager?
#       It's handy if generic hdl stuff is also accessible with sv/systemverilog 
#       as the language specifier. So normally you would just inherit 
#       systemverilog_code_manager from hdl_code_manager, and there you are.  
#       Problem: If the hdl codemanager methods need templates, those would be 
#       in the hdl templates directory.  But self.TEMPLATES_ABS_PATH would point 
#       to systemverilog. Best I could come up with is the additional internal 
#       hdl code manager with a pass-through of hdl code  manager commands (see 
#       run_code_manager_command). Creating soft links from the systemverilog 
#       directory into the hdl directory is against all rules of portability.
        self.hdl_code_manager = hdl_code_manager.HdlCodeManager()

    def _command_module(self, specifier, **args):

        # check if module directory exists. if it doesn't, abort straight-away?
        if not os.path.isdir(self.hdl_code_manager.PRJ_DIRS['rtl']):
            print(f"Project rtl directory '{self.hdl_code_manager.PRJ_DIRS['rtl']}' "
                  "could not be found found. A potential reason is that you are not in "
                  "the project top-level directory. No file will be touched")
            return

        s_module = args["target"]
        s_target_file = os.path.join(
                self.hdl_code_manager.PRJ_DIRS['rtl'], s_module + ".sv")
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("module", {"MODULE": s_module})
            self._write_template(template_out, s_target_file)

    def _command_inst(self, specifier, **args):
        print(f"creating an instantiation of systemverilog module f{args['target']}")

    def _command_testbench(self, specifier, **args):
        print(f"creating a testbench for systemverilog module f{args['target']}")

    def run_code_manager_command(self, command, specifier, **args):

        # "pass-through" hdl code manager commands, such that the systemverilog 
        # code manager can be used with any command that the hdl code manager 
        # has as well (not particularly necessary, but it's a nice convenience 
        # feature)
        try:
            fun_command = getattr(self, '_command_' + command)
        except AttributeError:
            fun_command = getattr(self.hdl_code_manager, '_command_' + command)
        fun_command(specifier, **args)
