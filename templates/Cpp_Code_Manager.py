#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re, shutil
import Code_Manager

class Cpp_Code_Manager(Code_Manager.Code_Manager):


    def __init__(self):
        super().__init__("cpp")
        self.language = "cpp"


    def __create_main(self, app_name):

        ##############################
        # PROJECT DIRECTORIES
        ##############################
        
        name_src_dir = "src"
        name_include_dir = "include"

        for name_dir in [name_src_dir, name_include_dir]:
            if not os.path.isdir(name_dir):
                os.mkdir(name_dir)

        ##############################
        # MAIN 
        ##############################

        shutil.copy(f"{self.TEMPLATES_ABS_PATH}/template_main.cpp",
                    f"{name_src_dir}/main.cpp")
        
#         ##############################
#         # READ TEMPLATE FILE
#         ##############################
# 
# #     with open (TEMPLATES_ABS_PATH_ + "/python/template_main.py", "r") as f_in:
# #         template = f_in.readlines()
#         template = self._load_template(
#                 self.TEMPLATES_ABS_PATH + "/template_main.cpp", # TODO: os.path.join()
#                 app_name)
# 
#         ##############################
#         # ADAPT
#         ##############################
#         # basically handle the special template placeholders (indicated by 
#         # '_TT_*_TT_' instead of '_T_*_T_')
# 
#         template_out = template
# 
#         ##############################
#         # WRITE PROJECT FILE
#         ##############################
# 
#         with open ("main.cpp", "w") as f_out:
#             f_out.writelines(template_out)

        return 0


    def __create_cmake(self, app_name, cuda=False):

        ##############################
        # PROJECT DIRECTORIES
        ##############################

        name_debug_dir = "debug"        
        name_release_dir = "release"
        name_maxopt_dir = "maxopt"

        for name_dir in [name_debug_dir, name_release_dir, name_maxopt_dir]:
            if not os.path.isdir(name_dir):
                os.mkdir(name_dir)

        ##############################
        # READ TEMPLATE FILES
        ##############################

        template_cmakelists = self._load_template(
                self.TEMPLATES_ABS_PATH + "/template_cmakelists.txt", app_name
                )

        template_makefile = self._load_template(
                self.TEMPLATES_ABS_PATH + "/template_makefile", app_name
                )

        ##############################
        # ADAPT
        ##############################
        # basically handle the special template placeholders (indicated by 
        # '_TT_*_TT_' instead of '_T_*_T_')

        cmakelists_out = []

        for line in template_cmakelists:

            # SOURCE DIRECTORY
            if re.match(r'.*_TT_CUDA_TT_.*', line):
                if cuda:
                    cmakelists_out.extend([
                        "include(CheckLanguage)\n",
                        "check_language(CUDA)\n",
                        "\n",
                        "if (CMAKE_CUDA_COMPILER)\n",
                        "    message(\"CUDA is supported. Enabling CUDA sources.\")\n",
                        "    enable_language(CUDA)\n",
                        "    add_definitions(-DUSE_CUDA)\n",
                        "    set(CMAKE_CUDA_STANDARD 11)\n",
                        "    set(CUDA_SRCS\n",
                        "    )\n",
                        "\n",
                        "    set(CMAKE_CUDA_FLAGS \"${CMAKE_CUDA_FLAGS} -Xcompiler -Ofast\")\n",
                        "else ()\n",
                        "    message(\"Could not find CUDA support. Disabling CUDA sources.\")\n",
                        "endif ()\n",
                        "\n",
                    ])
                else:
                    pass

            elif re.match(r'.*_TT_ADD_EXECUTABLE_TT_.*', line):
                if cuda:
                    cmakelists_out.extend([
                        "add_executable(${PROJECT_NAME} ${CPP_SRCS} ${CUDA_SRCS})",
                    ])
                else:
                    cmakelists_out.extend([
                        "add_executable(${PROJECT_NAME} ${CPP_SRCS})",
                    ])

            # NOTHING SPECIAL
            # -> copy over the line
            else:
                cmakelists_out.append(line)

        ##############################
        # WRITE PROJECT FILES
        ##############################

        with open ("CMakeLists.txt", "w") as f_out:
            f_out.writelines(cmakelists_out)

        with open ("makefile", "w") as f_out:
            f_out.writelines(template_makefile)

        return 0


    def __create_vimspector(self, app_name):

        ##############################
        # READ TEMPLATE FILE
        ##############################

        template = self._load_template(
                self.TEMPLATES_ABS_PATH + "/template_vimspector.json", app_name, 
                )

        ##############################
        # ADAPT
        ##############################
        # basically handle the special template placeholders (indicated by 
        # '_TT_*_TT_' instead of '_T_*_T_')

        template_out = list(map(
            lambda s: s.replace("_TT_CWD_TT_", f"{os.getcwd()}/debug"), template
            ))

        ##############################
        # WRITE PROJECT FILE
        ##############################

        with open (".vimspector.json", "w") as f_out:
            f_out.writelines(template_out)

        return 0


    def create_project(self, app_name, 
            vimspector=False, git=False, cuda=False,
            **args):
        """Create a cpp project from the template in this directory

        :app_name:  The name for the application -> the main file
        :returns:   TODO

        """

        # LAUNCH FILE CREATION
        self.__create_main(app_name)
        self.__create_cmake(app_name, cuda)
        if vimspector:
            self.__create_vimspector(app_name)
        if git:
            self._create_git(app_name)

        # set up
#         self.__run_cmake()


        return 0
