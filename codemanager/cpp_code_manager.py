#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os
import re
import shutil
from operator import itemgetter

import code_manager

LANG_IDENTIFIERS = ["cpp", "c++"]

class CppCodeManager(code_manager.CodeManager):

    PLACEHOLDERS = {
            'DIR_BUILD':                    "build",
            'DIR_SRC':                      "src",
            'DIR_INCLUDE':                  "include",
            'DIR_DEBUG':                    "debug",
            'DIR_RELEASE':                  "release",
            'DIR_MAXOPT':                   "maxopt",
            'FILE_MAKE_VARIABLES':          "var.make",
    }


    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("cpp")


    def _command_main(self, **kwargs):

        ##############################
        # PROJECT DIRECTORIES
        ##############################
        
        project_dirs = itemgetter(
                'DIR_SRC', 'DIR_INCLUDE',
                )(self.PLACEHOLDERS)
        for directory in project_dirs:
            # comments: hdl_code_manager.py
            try:
                os.mkdir(directory)
            except:
                pass

        s_target_file = os.path.join(
                    self.PLACEHOLDERS['DIR_SRC'], "main.cpp")
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("main")
            self._write_template(template_out, s_target_file)


    def _command_project(self, app_name="", enable_cuda=False, empty=False,
                                enable_vimspector=False, **kwargs):
        '''
        If app_name is not specified, it is assumed to be the project directory name
        empty - don't generate a hello world main.cpp
        '''
        # TODO: git option

        ##############################
        # PROJECT DIRECTORIES
        ##############################

        try:
            os.mkdir(self.PLACEHOLDERS['DIR_BUILD'])
        except:
            pass

        project_dirs = itemgetter(
                'DIR_DEBUG', 'DIR_RELEASE', 'DIR_MAXOPT',
                )(self.PLACEHOLDERS)
        for directory in project_dirs:
            # comments: hdl_code_manager.py
            try:
                os.mkdir(os.path.join(self.PLACEHOLDERS['DIR_BUILD'], directory))
            except:
                pass

        if not app_name:
            app_name = os.path.basename(os.getcwd())

        ##############################
        # TEMPLATES
        ##############################

        # MAKEFILE
        s_target_file = "makefile"
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("makefile", dict_placeholders={
                        "APP_NAME": app_name,
                        })
            self._write_template(template_out, s_target_file)

        # MAKEFILE VARIABLES
        s_target_file = self.PLACEHOLDERS["FILE_MAKE_VARIABLES"]
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("make_var", dict_placeholders={
                        "APP_NAME": app_name,
                        })
            self._write_template(template_out, s_target_file)

        # CMAKELISTS
        if enable_cuda:
            s_enable_cuda = \
"""include(CheckLanguage)
"check_language(CUDA)
"
"if (CMAKE_CUDA_COMPILER)
"    message(\"CUDA is supported. Enabling CUDA sources.\")
"    enable_language(CUDA)
"    add_definitions(-DUSE_CUDA)
"    set(CMAKE_CUDA_STANDARD 11)
"    set(CUDA_SRCS
"    )
"
"    set(CMAKE_CUDA_FLAGS \"${CMAKE_CUDA_FLAGS} -Xcompiler -Ofast\")
"else ()
"    message(\"Could not find CUDA support. Disabling CUDA sources.\")
"endif ()"""
            
            s_add_executable = "add_executable(${PROJECT_NAME} ${CPP_SRCS} ${CUDA_SRCS})"

        else:
            s_enable_cuda = ""
            s_add_executable = "add_executable(${PROJECT_NAME} ${CPP_SRCS})"

        s_target_file = "CMakeLists.txt"
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("cmakelists", dict_placeholders={
                        "APP_NAME": app_name,
                        "CUDA": s_enable_cuda,
                        "ADD_EXECUTABLE": s_add_executable,
                        })
            self._write_template(template_out, s_target_file)

        # MAIN
        if not empty:
            self._command_main()

        # VIMSPECTOR
        if enable_vimspector:
            self._command_vimspector(app_name)

        # GITIGNORE
        self._command_gitignore()


    def _command_vimspector(self, app_name="", **kwargs):

        if not app_name:
            app_name = os.path.basename(os.getcwd())

        s_target_file = ".vimspector.json"

        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("vimspector", {
                            "APP_NAME": app_name,
                            })
            self._write_template(template_out, s_target_file)


    def _command_gitignore(self, **kwargs):

        s_target_file = ".gitignore"

        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("gitignore")
            self._write_template(template_out, s_target_file)


#         template_out = list(map(
#             lambda s: s.replace("_TT_CWD_TT_", f"{os.getcwd()}/debug"), template
#             ))

