#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re
import shutil
import code_manager
from operator import itemgetter

LANG_IDENTIFIERS = ["hdl"]

class _BoardSpecs():

    PATH_CONSTRAINT_FILES = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), os.pardir,
            "templates", "hdl", "constraints")

    def __init__(self, xilinx_board_specifier, constraints_file_name):
        self.xilinx_board_specifier = xilinx_board_specifier
        self.constraints_file_name = constraints_file_name
        self.constraints_file_realpath = os.path.join(
                    self.PATH_CONSTRAINT_FILES, self.constraints_file_name)
    

    @classmethod
    def get_board_specs_obj(cls, xilinx_board_specifier, constraints_file_name=None):
        """If no constraints_file_name is given, the function tries to obtain the 
        correct one from a set of predefined constraint file name formats (such 
        as digilent). The idea: For every board, you need the xilinx board 
        specifier (for setting the part in the project) and the master 
        constraints file name (for copying that one into the project if it is 
        available). One could now
        - let the user pass both the board specs and the constraints file as 
          options, but basically that's passing the same information twice
        - set up all supported boards manually as tupels here; tedious and 
          potentially unneccessary, because:
        For digilent boards for instance, the master constraints file from their 
        website seem to follow a fixed naming convention (as of 2024-03-26...).  
        So basically if you just bulk-download them, you should be able to 
        derive the correct constraints file from the board specifier. (note that 
        the constraints files are not included in the xilinx board parts. The 
        XMLs have something that looks similar, but that is actually the pin 
        connections for standard IPs like an I2C core)

        conclusion: whenever adding support for boards from a new vendor, check 
        if they have a naming convention, and if so add that to 
        __find_constraints_file.
        """
        if not constraints_file_name:
            constraints_file_name = cls.__find_constraints_file(xilinx_board_specifier)
        
        if not constraints_file_name:
            raise Exception(
f"No matching constraints file could be found for board specifier '{xilinx_board_specifier}'")
        else:
            return cls(xilinx_board_specifier, constraints_file_name)


    @classmethod
    def __find_constraints_file(cls, xilinx_board_specifier):
        """find the constraints file for a given board specifier, by checking 
        known constraints file formats and the respective directories
        """

        # TODO: For the time being, the template file directory is hardcoded to:
        # <root>/templates/hdl/constraints
        # Maybe it's nice if in the feature that can somehow be parameterised or 
        # configured, but that'll do it for now.
        l_constraint_files = os.listdir(cls.PATH_CONSTRAINT_FILES)

        # DIGILENT
        # digilent naming convention: arty-a7-35 -> Arty-A7-35-Master.xdc
        # the simple solution: append "-master.xdc" and do a case-insensitive 
        # match
        xdc_file_name_lower_case = xilinx_board_specifier + "-master.xdc"
        pattern = re.compile(xdc_file_name_lower_case, re.IGNORECASE)
        match_fun = lambda x: pattern.match(x)
        # (might not be the prime usage of an iterator to straight-up compress 
        # it into a list, but it does the trick here)
        l_matches = list(filter(pattern.match, l_constraint_files))
        if l_matches:
            # classic, take the first list element, because if the list has more 
            # than one element, you have already messed up anyways
            return l_matches[0]

        # TODO: as a fallback, provide an option to custom implement tupels with 
        # prepared constraints files

        # not found?
        return None


class HdlCodeManager(code_manager.CodeManager):

    # set variables for hdl project directory structure
    PRJ_DIRS = {                                       \
            'rtl':              "rtl",                      \
            'simulation':       "sim",                      \
            'testbench':        "tb",                       \
            'constraints':      "constraints",              \
            'tcl':              "tcl",                      \
            'blockdesign':      "bd",                       \
            'xilinx_ips':       "xips",                     \
            'software':         "sw",                       \
            'xilinx_log':       "hw_build_log",             \
            'hardware_export':  "hw_export",                \
    }
    TCL_FILES = {
            'read_sources':     "read_sources.tcl",         \
            'generate_xips':    "generate_xips.tcl",        \
            'create_project':   "create_project.tcl",       \
            'build_hw':         "build_hw.tcl",             \
            'source_helpers':   "source_helper_scripts.tcl",\
    }

    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("hdl")


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
                'rtl', 'constraints', 'simulation', 'testbench',
                'tcl', 'xilinx_log', 'hardware_export',
                )(self.PRJ_DIRS)
        for directory in project_dirs:
            # it's not necessary to run a 'file allowed to be edited' check here, 
            # since os.mkdir never deletes anything. It only throws an exception 
            # if the directory exists.
            try:
                os.mkdir(directory)
            except:
                # again, if a project directory already exists, that's fine 
                # (assuming that it's a directory, theoretically could be 
                # a file as well. but at some point users gotta act 
                # reasonably, such as not to create files with meaningful 
                # names and without file extensions)
                pass
    
        ############################################################
        # SCRIPTING
        ############################################################

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
            if not args['board_part'] == None:
                board_part = args["board_part"]
                board_specs = _BoardSpecs.get_board_specs_obj(args['board_part'])
                set_board_part = "true"
            else:
                board_part = "_no_board_"
                board_specs = _BoardSpecs("_no_board_specified_", "")
                set_board_part = "false"
            if not args['top'] == None:
                s_set_top_module = f"set_property top {args['top']} [get_filesets sources_1]"
            else:
                s_set_top_module = \
"""# TODO: SPECIFY THE PROJECT TOP MODULE HERE!!!
# set_property top <top_module> [get_filesets sources_1]"""

            # project generation script
            s_target_file = os.path.join(self.PRJ_DIRS['tcl'], self.TCL_FILES['create_project'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_create_project", dict( [
                                ("PRJ_NAME", os.path.basename(os.getcwd())),
                                ("DIR_TCL", self.PRJ_DIRS['tcl']),
                                ("TCL_FILE_SOURCE_HELPER_SCRIPTS", self.TCL_FILES['source_helpers']),
                                ("TCL_FILE_XILINX_IP_GENERATION", self.TCL_FILES['generate_xips']),
                                ("PART", part),
                                ("SET_BOARD_PART", set_board_part),
                                ("BOARD_PART", board_specs.xilinx_board_specifier),
                                ("SET_TOP_MODULE", s_set_top_module),
                                ("SIMULATOR_LANGUAGE", "Mixed"),
                                ("TARGET_LANGUAGE", "Verilog"),
                                ] ))
                self._write_template(template_out, s_target_file)

            # read sources script
            s_target_file = os.path.join(self.PRJ_DIRS['tcl'], self.TCL_FILES['read_sources'])
            if not args['hdl_lib'] == None:
                s_set_vhdl_lib = f"-library {args['hdl_lib']}"
            else:
                s_set_vhdl_lib = ""
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_read_sources", {
                                "DIR_RTL": self.PRJ_DIRS['rtl'],
                                "DIR_TB": self.PRJ_DIRS['testbench'],
                                "DIR_CONSTRAINTS": self.PRJ_DIRS['constraints'],
                                "HDL_LIB": s_set_vhdl_lib,
                                })
                self._write_template(template_out, s_target_file)

            # hardware build helpers script
            # DIR_XILINX_LOG
            s_target_file = os.path.join(self.PRJ_DIRS['tcl'], self.TCL_FILES['build_hw'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_build_hw", {
                                "DIR_XILINX_HW_BUILD_LOG": self.PRJ_DIRS['xilinx_log'],
                                "DIR_HW_EXPORT": self.PRJ_DIRS['hardware_export'],
                                "PRJ_NAME": os.path.basename(os.getcwd()),
                                "COMMAND_BUILD_HW": "build_hw",
                                "COMMAND_PROG_FPGA": "program_fpga",
                                })
                self._write_template(template_out, s_target_file)

            # source helper scripts script
            s_target_file = os.path.join(self.PRJ_DIRS['tcl'], self.TCL_FILES['source_helpers'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_source_helper_scripts", {
                                "DIR_TCL": self.PRJ_DIRS['tcl'],
                                "TCL_FILE_READ_SOURCES": self.TCL_FILES['read_sources'],
                                "TCL_FILE_BUILD_HW": self.TCL_FILES['build_hw'],
                                "TCL_FILE_XILINX_IP_GENERATION": self.TCL_FILES['generate_xips'],
                                })
                self._write_template(template_out, s_target_file)

            ##############################
            # MAKEFILE
            ##############################
            # XILINX_TOOL (vivado or vitis)
            # TCL_FILE_CREATE_PROJECT
            # DIR_TCL
            # TCL_FILE_BUILD_HW
            # default xil_tool to vivado
            if not args['xil_tool'] == None:
                xil_tool = args['xil_tool']
            else:
                xil_tool = "vivado"
            s_target_file = "makefile"
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_makefile", {
                                "TCL_FILE_SOURCE_HELPER_SCRIPTS": self.TCL_FILES['source_helpers'],
                                "XILINX_TOOL": xil_tool,
                                "PRJ_NAME": os.path.basename(os.getcwd()),
                                "DIR_TCL": self.PRJ_DIRS['tcl'],
                                "TCL_FILE_CREATE_PROJECT": self.TCL_FILES['create_project'],
                                "TCL_FILE_BUILD_HW": self.TCL_FILES['build_hw'],
                                "COMMAND_PROG_FPGA": "program_fpga",
                                })
                self._write_template(template_out, s_target_file)

            ##############################
            # CONSTRAINTS FILE
            ##############################
            # TODO: implement something that processes a master constraints file, 
            # in the sense that it splits it up in timing and physical 
            # constraints
            if board_specs.constraints_file_name:
                s_target_file = os.path.join(
                            self.PRJ_DIRS['constraints'], board_specs.constraints_file_name)
                if self._check_target_edit_allowed(s_target_file):
                    shutil.copy2(board_specs.constraints_file_realpath,
                                    self.PRJ_DIRS['constraints'])


        elif specifier == "":
            print("You must specify a project platform (xilinx or others)")
        else:
            print(f"Project platform '{specifier}' unknown")



