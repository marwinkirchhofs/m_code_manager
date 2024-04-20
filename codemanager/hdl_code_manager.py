#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re
import shutil
import json
import code_manager
from hdl_xilinx_debug_core_manager import XilinxDebugCoreManager
from operator import itemgetter

import inspect

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
    PRJ_DIRS = {                                                \
            'rtl':                  "rtl",                      \
            'simulation':           "sim",                      \
            'testbench':            "tb",                       \
            'constraints':          "constraints",              \
            'scripts':                  "scripts",                      \
            'blockdesign':          "bd",                       \
            'xilinx_ips':           "xips",                     \
            'software':             "sw",                       \
            'xilinx_log':           "hw_build_log",             \
            'hardware_export':      "hw_export",                \
    }
    FILES = {
            'read_sources':         "read_sources.tcl",         \
            'create_project':       "create_project.tcl",       \
            'build_hw':             "build_hw.tcl",             \
            'source_helpers':       "source_helper_scripts.tcl",\
            'manage_xil_prj':       "manage_project.tcl",       \
            'project_config':       "project_config.json",      \
            'manage_builds':        "manage_build_files.bash",  \
            'read_json_var':        "get_json_variable.py",     \
            'make_variables':       "var.make",                 \
            'generate_xilinx_ips':  "generate_xips.tcl",        \
            'xilinx_vio_control':   "vio_ctrl.tcl",             \
            'xilinx_vio_control_config':"vio_ctrl_signals.json",\
            'xilinx_ip_def_user':   "xips_user.tcl",            \
            'xilinx_ip_debug_cores':"xips_debug_cores.tcl",     \
    }


    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        self.xilinx_debug_core_manager = XilinxDebugCoreManager()
        super().__init__("hdl")


#     def _command_project(self, specifier, **args):
    def _command_project(self, command_specifier,
                target=None, part=None, board_part=None, top=None,
                hdl_lib=None, xil_tool=None,
                **kwargs):
        """Creates the skeleton for an hdl project as generic as possible. That 
        mainly is, create the hdl project directory structure and add common 
        build scripts like makefile and vivado project generation script (given 
        that a xilinx project is asked for)

        !!! The method can create a new project, including project directory, or 
        act from within an existing project directory. This is decided on 
        whether or not target is not specified (which means passing a -t 
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
        if not target == None:
            prj_name = target
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
                'scripts', 'xilinx_log', 'hardware_export', 'xilinx_ips'
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
        # BUILD FILE MANAGEMENT
        ##############################

        s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['manage_builds'])
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("manage_build_files", {
                            "DIR_HW_EXPORT": self.PRJ_DIRS['hardware_export'],
                            })
            self._write_template(template_out, s_target_file)

        ##############################
        # PYTHON JSON INTERFACE
        ##############################
        # (makefile helper)

        s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['read_json_var'])
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("get_json_variable", {
                            })
            self._write_template(template_out, s_target_file)

        ##############################
        # SIM MAKEFILE
        ##############################

        s_target_file = os.path.join(self.PRJ_DIRS['simulation'], "makefile")
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("makefile_sim", {
                            "FILE_NAME_MAKE_VAR": self.FILES['make_variables'],
                            })
            self._write_template(template_out, s_target_file)

        # GLOBAL MAKE VARS
        s_target_file = self.FILES['make_variables']
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("make_var", {
                            "FILE_READ_JSON_VAR": self.FILES['read_json_var'],
                            "FILE_PROJECT_CONFIG": self.FILES['project_config'],
                            "DIR_TCL": self.PRJ_DIRS['scripts'],
                            })
            self._write_template(template_out, s_target_file)

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
        if command_specifier == "xilinx":
            # default values for non-passed arguments
            if not part == None:
                part = part
            else:
                part = ""
            if not board_part == None:
#                 board_part = board_part
                board_specs = _BoardSpecs.get_board_specs_obj(board_part)
            else:
#                 board_part = ""
                board_specs = _BoardSpecs("", "")
#             if not top == None:
#                 s_set_top_module = f"set_property top {top} [get_filesets 
#                 sources_1]"
#             else:
#                 s_set_top_module = \
# """# TODO: SPECIFY THE PROJECT TOP MODULE HERE!!!
# # set_property top <top_module> [get_filesets sources_1]"""

            # project generation script
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['create_project'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_create_project", dict( [
                                ("PRJ_NAME", os.path.basename(os.getcwd())),
                                ("DIR_TCL", self.PRJ_DIRS['scripts']),
                                ("TCL_FILE_SOURCE_HELPER_SCRIPTS", self.FILES['source_helpers']),
                                ("TCL_FILE_XILINX_IP_GENERATION", self.FILES['generate_xilinx_ips']),
                                ("SIMULATOR_LANGUAGE", "Mixed"),
                                ("TARGET_LANGUAGE", "Verilog"),
                                ] ))
                self._write_template(template_out, s_target_file)

            # read sources script
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['read_sources'])
            if not hdl_lib == None:
                s_set_vhdl_lib = f"-library {hdl_lib}"
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
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['build_hw'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_build_hw", {
                                "DIR_XILINX_HW_BUILD_LOG": self.PRJ_DIRS['xilinx_log'],
                                "DIR_HW_EXPORT": self.PRJ_DIRS['hardware_export'],
                                "PRJ_NAME": os.path.basename(os.getcwd()),
                                "COMMAND_BUILD_HW": "build_hw",
                                "COMMAND_PROG_FPGA": "program_fpga",
                                "FILE_PROJECT_CONFIG": self.FILES['project_config'],
                                })
                self._write_template(template_out, s_target_file)

            # project management script
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['manage_xil_prj'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_manage_project", {
                                "FILE_PROJECT_CONFIG": self.FILES['project_config'],
                                "COMMAND_UPDATE": "update",
                                })
                self._write_template(template_out, s_target_file)

            # source helper scripts script
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['source_helpers'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_source_helper_scripts", {
                                "DIR_TCL": self.PRJ_DIRS['scripts'],
                                "TCL_FILE_READ_SOURCES": self.FILES['read_sources'],
                                "TCL_FILE_BUILD_HW": self.FILES['build_hw'],
                                "TCL_FILE_XILINX_IP_GENERATION": self.FILES['generate_xilinx_ips'],
                                "TCL_FILE_MANAGE_XIL_PRJ": self.FILES['manage_xil_prj'],
                                })
                self._write_template(template_out, s_target_file)

            # generate xilinx IPs
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['generate_xilinx_ips'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("generate_xips", {
                                "DIR_XIPS": self.PRJ_DIRS['xilinx_ips'],
                                })
                self._write_template(template_out, s_target_file)

            # xilinx IP definition file
            s_target_file = os.path.join(self.PRJ_DIRS['xilinx_ips'], self.FILES['xilinx_ip_def_user'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xips_def_user", {
                                })
                self._write_template(template_out, s_target_file)

            # vio control interface script
            s_target_file = os.path.join(self.PRJ_DIRS['scripts'], self.FILES['xilinx_vio_control'])
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_vio_ctrl", {
                                "DIR_HW_EXPORT": self.PRJ_DIRS['hardware_export'],
                                "INST_XIP_VIO_CTRL": "inst_xip_vio_ctrl",
                                "FILE_VIO_CTRL_SIGNALS_CONFIG": self.FILES['xilinx_vio_control_config'],
                                "FILE_PROJECT_CONFIG": self.FILES['project_config'],
                                })
                self._write_template(template_out, s_target_file)

#             # vio control xip example definition
#             s_target_file = os.path.join(self.PRJ_DIRS['xilinx_ips'], self.FILES['xilinx_ip_debug_cores'])
#             if self._check_target_edit_allowed(s_target_file):
#                 template_out = self._load_template("xips_vio_ctrl", {
#                                 "DIR_HW_EXPORT": self.PRJ_DIRS['hardware_export'],
#                                 "INST_XIP_VIO_CTRL": "inst_xip_vio_ctrl",
#                                 "FILE_VIO_CTRL_SIGNALS_CONFIG": self.FILES['xilinx_vio_control_config'],
#                                 "FILE_PROJECT_CONFIG": self.FILES['project_config'],
#                                 })
#                 self._write_template(template_out, s_target_file)

            ##############################
            # MAKEFILE
            ##############################
            # default xil_tool to vivado
            if xil_tool == None:
                xil_tool = "vivado"
            s_target_file = "makefile"
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("xilinx_makefile", {
                                "TCL_FILE_SOURCE_HELPER_SCRIPTS": self.FILES['source_helpers'],
                                "XILINX_TOOL": xil_tool,
                                "PRJ_NAME": os.path.basename(os.getcwd()),
                                "DIR_TCL": self.PRJ_DIRS['scripts'],
                                "DIR_SIM": self.PRJ_DIRS['simulation'],
                                "DIR_RTL": self.PRJ_DIRS['rtl'],
                                "TCL_FILE_CREATE_PROJECT": self.FILES['create_project'],
                                "TCL_FILE_BUILD_HW": self.FILES['build_hw'],
                                "TCL_FILE_GENERATE_XIPS": self.FILES['generate_xilinx_ips'],
                                "TCL_FILE_VIO_CTRL": self.FILES['xilinx_vio_control'],
                                "FILE_XIP_VIO_CTRL": self.FILES['xilinx_ip_debug_cores'],
                                "FILE_READ_JSON_VAR": self.FILES['read_json_var'],
                                "FILE_MANAGE_HW_BUILDS": self.FILES['manage_builds'],
                                "FILE_PROJECT_CONFIG": self.FILES['project_config'],
                                "COMMAND_PROG_FPGA": "program_fpga",
                                })
                self._write_template(template_out, s_target_file)

            ##############################
            # CONSTRAINTS FILE
            ##############################
            # TODO: implement something that processes a master constraints file, 
            # in the sense that it splits it up in timing and physical 
            # constraints - and make that a selectable option, because some 
            # people don't like splitting up makefiles
            if board_specs.constraints_file_name:
                s_target_file = os.path.join(
                            self.PRJ_DIRS['constraints'], board_specs.constraints_file_name)
                if self._check_target_edit_allowed(s_target_file):
                    shutil.copy2(board_specs.constraints_file_realpath,
                                    self.PRJ_DIRS['constraints'])

            ##############################
            # PROJECT CONFIG FILE
            ##############################
            # holds project variables that might be used by multiple tools, and 
            # thus are handy to have one central spot
            # About that idea: Some of the variables in here, like part and 
            # board_part, are actually only used by the vivado project, they 
            # would not be necessary to have in the json file. Also managing 
            # that introduces overhead, because you always have to update the 
            # json file AND the vivado project. And you either need to make 
            # clear that adapting the json file doesn't change the vivado 
            # project - or you need to implement checks between json and vivado 
            # project in the build functions, which is probably what is gonna 
            # happen...
            # Anyway, for some variables it actually makes sense:
            # - hw_target: programming the fpga doesn't need to open a vivado 
            # project, it only fetches the bitstream and whatever it needs.
            # - sim_top: third-party simulators...
            # conclusion: Yes, the project_config file does do actual work in 
            # some situations, and for the rest I justify the overhead with the 
            # fact that it gives you a quick overview on every project variable 
            # that has somewhat of a dynamic character to it.
            if not top == None:
                s_top_module = ""
            else:
                s_top_module = top
            s_target_file = self.FILES['project_config']
            if self._check_target_edit_allowed(s_target_file):
                d_config = {
                    "part": part,
                    "board_part": board_specs.xilinx_board_specifier,
                    "top": s_top_module,
                    "sim_top": s_top_module,
                    "simulator": "xsim",
                    "hw_version": "latest",
                    }
                with open(self.FILES['project_config'], 'w') as f_out:
                    json.dump(d_config, f_out, indent=4)

        elif command_specifier == "":
            print("You must specify a project platform (xilinx or others)")
        else:
            print(f"Project platform '{command_specifier}' unknown")


    def _get_project_config(self):
        """return the contents of the project config json file as a dict
        """
        # (quickly, why do we use json instead of yaml? Answer: it works with 
        # the tcl packages in older vivado versions (namely 2019.1 in the test 
        # case), yaml doesnt. program_fpga makes use of the tcl yaml package, 
        # where in older versions importing a yaml script as a tcl dict didn't 
        # work straightforward when tested. json however, being the older format, 
        # did, so we go with that)
        with open(self.FILES['project_config'], 'r') as f_in:
            d_config = json.load(f_in)
        return d_config


#     def _command_config(self, specifier, **args):
    def _command_config(self, 
                top=None, sim_top=None, part=None, board_part=None,
                hw_version=None, simulator=None, xil_tool=False, vio_top=None,
                no_xil_update=False,
                **kwargs):
        """update the project config file (self.FILES['project_config']) 
        with the specified parameters
        """

        # the goal: automatically update the config for all non-None arguments
        # problem: 1. how to get the arguments 2. there might be arguments that 
        # refer to this function, but are not project config parameters
        # solution: We use inspect.getargvalues(), which in combination with 
        # pointing to this function as the current frame gives us a list of the 
        # defined function arguments and the ones that are actually passed.  
        # Problem: 'values' uses locals() in the backend, which apparently 
        # somehow is recursive (at least here), so 'values' itself would contain 
        # 'values', endlessly. Since it also contains 'self' and friend, we have 
        # to filter 'values' anyway, then we just incorporate the information 
        # from 'rgas'. We filter that for arguments that:
        # - appear in 'args'
        # - are not 'self'
        # - are not None
        # - are not in the list of non_config_arguments that we define
        non_config_arguments = ['no_xil_update']

        # meaning of xil_project_parameters: those are the ones that play a role 
        # in the xilinx project. So if one of those gets passed, we need to call 
        # the respective API to update the xilinx project.
        xil_project_parameters = ["part", "board_part", "top"]

        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)

        def fun_filter_args(raw_item):
            key, value = raw_item
            if not key in args or key == 'self': return False
            if not value: return False
            if key in non_config_arguments: return False
            return True

        config_args = dict(filter(fun_filter_args, values.items()))

        d_config = self._get_project_config()
        update_xil_project = False
        # update config where necessary
        for key, value in config_args.items():
            # catch the case that for some reason the key doesn't exist yet in 
            # the config (shouldn't happen, but might happen)
            try:
                if not d_config[key] == value:
                    d_config[key] = value
                    # only update xilinx project if the key value has actually 
                    # changed
                    if key in xil_project_parameters:
                        update_xil_project = True
            except:
                d_config[key] = value
                if key in xil_project_parameters:
                    update_xil_project = True

        with open(self.FILES['project_config'], 'w') as f_out:
            json.dump(d_config, f_out, indent=4)
    
        # update the vivado project if necessary
        # TODO: maybe there is a more elegant way to select the xilinx tool, but 
        # for now it's good enough to default to vivado
        if not no_xil_update and update_xil_project:
            if not xil_tool:
                xil_tool = "vivado"
            s_tcl_manage_prj = os.path.join(
                        self.PRJ_DIRS['scripts'], self.FILES['manage_xil_prj'])
            os.system(f"{xil_tool} -mode batch -source {s_tcl_manage_prj}")


    def _command_testbench(self, target, simulator=None, **kwargs):
        """generate a testbench with an optional parameter to use the template 
        for a specific simulator
        """

        # TODO: selecting UVM as the simulator would also go in here
        if simulator == None:
            # default to a generic (systemverilog) testbench
            simulator = "generic"
        else:
            simulator = simulator
        # TODO: check how often you end up trying to pass the top module using 
        # --top or --sim_top, instead of target. If that happens, think about 
        # supporting whichever one of the two here as well
        if target == None:
            print(
"""No target module specified ('-t <target>')! The testbench name needs to align 
with the top module name that it tests in order for the simulation make flow to 
work, so a target name is required. Aborting...""")
            return
        else:
            module_name = target

        if simulator == 'verilator':

            s_target_file = os.path.join(
                    self.PRJ_DIRS['testbench'], "tb_vl_" + module_name + ".cpp")
            if self._check_target_edit_allowed(s_target_file):
                template_out = self._load_template("testbench_verilator", {
                                "MODULE_NAME": module_name,
                                })
                self._write_template(template_out, s_target_file)

        else:
            print(f"Simulator/Testbench flow {simulator} is not implemented or supported yet")
    

    def _command_xip_ctrl(self, target=None, **kwargs):
        """invoke XilinxDebugCoreManager to generate vio ctrl IP core target files, 
        based on a set of vio-connection signals.

        If no target (-t <target>) is specified, the top level module is 
        retrieved from the project config json file, and that file is analysed 
        for generating the vio ctrl IP. A different module can be specified by 
        passing -t <target> (module name, not file name). Then the file for that 
        module is needs to be found in the project's RTL directory.
        """
        # TODO: retrieving the top level module file is currently hardcoded to 
        # systemverilog. Be a little more inclusive...

        if not target == None:
            target_module = target
        else:
            d_config = self._get_project_config()
            target_module = d_config['top']

        l_rtl_files = os.listdir(self.PRJ_DIRS['rtl'])
        # look for the file in the list of rtl files that matches the 
        # <target_module>.sv. Theoretically, it looks for all files and takes 
        # the first one. But if there is more than one match, then the root of 
        # error is not my sloppy coding.
        f_match_target_module = lambda x: re.match(target_module + "\.sv", x)
        s_target_module_file = [
                i for i in l_rtl_files if bool(f_match_target_module(i))][0]
        s_target_module_path = os.path.join(self.PRJ_DIRS['rtl'], s_target_module_file)

        self.xilinx_debug_core_manager.process_module(
                s_target_module_path,
                s_xip_declaration_file_name=os.path.join(
                    self.PRJ_DIRS['xilinx_ips'], self.FILES['xilinx_ip_debug_cores']),
                s_json_file_name_signals=self.FILES['xilinx_vio_control_config']
                                                     )
