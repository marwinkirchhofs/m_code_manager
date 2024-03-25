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
        self.TCL_FILE_READ_SOURCES = "read_sources.tcl"
        self.TCL_FILE_XILINX_IP_GENERATION = "generate_xips.tcl"    # TODO
        self.TCL_FILE_CREATE_PROJECT = "create_project.tcl"

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

        ##############################
        # PROJECT DIRECTORY
        ##############################
        if not args['target'] == None:
            prj_name = args['target']
            if self._check_target_edit_allowed(prj_name):
                try:
                    os.mkdir(prj_name)
                except:
                    # no need to handle the exception if the directory prj_name 
                    # exists, that's taken care of and confirmed in 
                    # self._check_target_edit_allowed
                    pass
                os.chdir(prj_name)

        ##############################
        # SUBDIRECTORIES
        ##############################
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
    
        ##############################
        # TCL SCRIPTS
        ##############################
        # * generate project script - generates or updates the vivado/vitis 
        # project
        # * helpers
        #     * helper_read_sources - functions to read source files of any 
        #     type (rtl, constraints, software)
        #     * helper_build_project - synthesis and implementation

        # XILINX PROJECT
        if specifier == "xilinx":
            # default values for non-passed arguments
            if not args['part'] == None:
                part = args["part"]
            else:
                part = ""
        
            if not args['top'] == None:
                s_set_top_module = f"set_property top {args['top']} [get_filesets sources_1]"
            else:
                s_set_top_module = \
"""# TODO: SPECIFY THE PROJECT TOP MODULE HERE!!!
# set_property top <top_module> [get_filesets sources_1]"""

            # project generation script
            s_target_file = os.path.join(self.PRJ_DIRS['tcl'], self.TCL_FILE_CREATE_PROJECT)
            template_out = self._load_template("xilinx_create_project", dict( [
                            ("DIR_TCL", self.PRJ_DIRS['tcl']),
                            ("TCL_FILE_READ_SOURCES", self.TCL_FILE_READ_SOURCES),
                            ("TCL_FILE_XILINX_IP_GENERATION", self.TCL_FILE_XILINX_IP_GENERATION),
                            ("PART", part),
                            ("SET_TOP_MODULE", s_set_top_module),
                            ("SIMULATOR_LANGUAGE", "Mixed"),
                            ("TARGET_LANGUAGE", "SystemVerilog"),
                            ] ))
            self._write_template(template_out, s_target_file)

            # read sources script
            s_target_file = os.path.join(self.PRJ_DIRS['tcl'], self.TCL_FILE_READ_SOURCES)
            if not args['hdl_lib'] == None:
                s_set_vhdl_lib = f"-library {args['hdl_lib']}"
            else:
                s_set_vhdl_lib = ""
            template_out = self._load_template("xilinx_read_sources", {
                            "DIR_RTL": self.PRJ_DIRS['rtl'],
                            "DIR_TB": self.PRJ_DIRS['testbench'],
                            "DIR_CONSTRAINTS": self.PRJ_DIRS['constraints'],
                            "HDL_LIB": s_set_vhdl_lib,
                            })
            self._write_template(template_out, s_target_file)

        elif specifier == "":
            print("You must specify a project platform (xilinx or others)")
        else:
            print(f"Project platform '{specifier}' unknown")


