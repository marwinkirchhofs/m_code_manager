#!/usr/bin/env python3

# TOP-LEVEL SCRIPT PROJECT_CREATE
#
# The script is used to load the language-specific template scripts, call the 
# respective create_project function and pass the given parameters to it

from optparse import OptionParser
import os, sys

# IMPORT LANGUAGE-SPECIFIC SCRIPTS
# add templates path to python's search path
def add_templates_path():
    s_abs_path = os.path.realpath(__file__)
    l_templates_path = s_abs_path.split('/')[:-1] + ["templates"]
    system.path.append( "/".join(l_templates_path) )

# add_templates_path()
from templates import *


############################################################
# "GLOBAL" VARS
############################################################

# TODO: make it syntactically clearer that you can specify multiple aliases for 
# one language (dictionary style, but still easy to edit)
supported_lang_identifiers = "c cpp python".split()


############################################################
# FUNCTION DEFINITIONS
############################################################


def run_code_manager_command(**args):
    """Create a project for the given language -> basically calls the respective 
    run_code_manager_command_* function

    By default, the project is created 

    :language:      The language to create a project for
    :create_dir:    If True, a new top-level project is created whose name is 
    equal to the application name (default: True)
    :args:          language-specific arguments as defined in the respective 
    run_code_manager_command_* functions
    :returns: TODO

    """

#     ##############################
#     # GENERAL ACTIONS
#     ##############################
#     TODO: more or less transfer this code into a general create project 
#     directory method of Code_Manager
#     
#     # PROJECT DIRECTORY
#     # The application directory gets created if not disabled and afterwards it 
#     # is ensured that the application directory (newly created or not) is the 
#     # working directory when calling the language-specific function
#     if create_dir:
#         if not os.path.isdir(app_name):
#             os.mkdir(app_name)
#         os.chdir(app_name)
 
    ##############################
    # LANGUAGE-SPECIFIC PROJECT CREATION
    ##############################
    # First get the respective project generator object, then invoke it

    if args["lang"] == "c":
        pass
    elif args["lang"] == "cpp":
        cm = Cpp_Code_Manager()
    elif args["lang"] == "python":
        cm = Python_Code_Manager()
    elif args["lang"] == "":
        cm = Code_Manager()

    cm.run_code_manager_command(**args)
    
    return 0


############################################################
# MAIN
############################################################

if __name__ == "__main__":
    
    ##############################
    # ARGUMENT PARSING
    ##############################
    # calling syntax/argument order:
    # marwin_code_manager [language] <command> [command_specifier] [... options ...]
    # options are passed using --<option> syntax. there are no options 
    # implemented as of now
    #
    # language          - one of the supported languages. Can also be empty, in 
    # which case one of the non-language depending options is executed
    # command           - one of the available commands for the respective 
    # language
    # command_specifier - some commands have additional specifiers
    
    parser = OptionParser()

    # GLOBAL
    # target
    parser.add_option("--target", "-t",
            dest="target",
            help="specify the local target/project to work on",
            )
#     # language
#     parser.add_option("-l",
#             dest="language",
#             help="""the language for which to build a target; valid options:
# """ + ", ".join(supported_lang_identifiers)
#             )
    # git repo
#     parser.add_option("--git",
#             action="store_true",
#             dest="git",
#             help="if set, a git repo will be created",
#             )
#     # vimspector
#     parser.add_option("--vimspector",
#             action="store_true",
#             dest="vimspector",
#             help="if set, a vimspector config will be created",
#             )
# 
#     # CPP
#     # cuda
#     parser.add_option("--cuda",
#             action="store_true",
#             dest="cuda",
#             help="if set, cuda support will be added to CMakeLists.txt",
#             )
# 
#     # PYTHON
#     # package dir
#     parser.add_option("--py_pkg",
#             dest="py_pkg",
#             help="if set, the corresponding plot will be renewed using \
# plot_template_single_layer",
#             )

    # PARSE ARGS AND OPTIONS
    (options, args) = parser.parse_args()

    if args[0] in supported_lang_identifiers:
        arg_lang = args[0]
        args = args[1:]
    else:
        # arg_lang=="" is equivalent to no language specified
        arg_lang = ""
    arg_command = args[0]
    args = args[1:]
    if len(args) >= 1:
        arg_specifier = args[0]
    else:
        arg_specifier = ""

    dict_args = {
            "lang": arg_lang,
            "command": arg_command,
            "specifier": arg_specifier
            }

    ##############################
    # CHECK REQUIRED ARGUMENTS
    ##############################
    # TODO

    ##############################
    # PROJECT CREATION
    ##############################
    # use the function exit code as the script exit code

    sys.exit( run_code_manager_command(**options.__dict__, **dict_args) )


