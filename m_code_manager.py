#!/usr/bin/env python3

# TOP-LEVEL SCRIPT PROJECT_CREATE
#
# The script is used to load the language-specific template scripts, call the 
# respective create_project function and pass the given parameters to it

from optparse import OptionParser
from importlib import import_module
import os
import sys
import re

# IMPORT LANGUAGE-SPECIFIC SCRIPTS
# Why is the codemanager directory added to the path here, although it is not 
# immediately imported? Two reasons: First, the according codemanager is 
# imported dynamically run_code_manager_command, so it has to be accessible to 
# python. On that same note, the dynamic module import is preferred over 
# a package import because that avoids loading unnecessary code (and you always 
# only need one of the specific code managers per program call). Second reason, 
# the language-specific code managers all have to import the CodeManager class.  
# Therefore this one needs to be accessible in any scenario, and here is the 
# central spot to do that.
s_code_manager_path = os.path.realpath(os.path.join(
                os.path.dirname(__file__), "codemanager"))
def add_codemanager_path():
#     s_abs_path = os.path.realpath(__file__)
#     l_code_manager_path = s_abs_path.split('/')[:-1] + ["codemanager"]
#     system.path.append( "/".join(l_code_manager_path) )
    sys.path.append(s_code_manager_path)

# from codemanager import *


############################################################
# "GLOBAL" VARS
############################################################

# import supported language identifiers from the 'codemanager' package module 
# files
# why import them here manually, instead of using the __init__.py? We want to 
# import all the language specifiers for comparing against the command line 
# arguments, but then we only want to import the code manager that we actually 
# need (don't do wildcard import). Setting that up as a package import would 
# either mean that you import all code managers, or that you would import none 
# of them, which feels very counterintuitive when you are actually importing 
# a package called 'codemanager'. Therefore import the language identifiers "by 
# hand", and then do the package explicitly
#
# The imports are done globally to have everything in the global namespace that 
# is accessible to the __main__ method

add_codemanager_path()

D_LANG_IDENTIFIERS = {}
l_dir_codemanager = os.listdir(s_code_manager_path)
# match every string that ends with 'code_manager.py' and either/or
# - has only alphanumeric characters in front of that (at least one character), 
# terminated by a '_'
# - is exactly "code_manager.py"
f_match_codemanager_modules = lambda s: re.match(r'(\w+_|)code_manager\.py', s)

for s_codemanager_module_file in filter(f_match_codemanager_modules, l_dir_codemanager):
    # remove the '.py' ending from the filename
    s_codemanager_module = s_codemanager_module_file[:-3]
    # extract language name from codemanager file name
    # (returns empty list for the code_manager base class module)
    mo_lang = re.findall(r'(\w*)_code_manager', s_codemanager_module)

    if mo_lang:
        s_lang = mo_lang[0]
        exec(f"from {s_codemanager_module} import LANG_IDENTIFIERS")
        D_LANG_IDENTIFIERS[s_lang] = LANG_IDENTIFIERS


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

    if args["lang"] == "":
        cm_module = import_module("code_manager")
        cm_class = getattr(cm_module, "CodeManager")
    else:
        # automatically instantiate the correct language-specific code manager 
        # from the args['lang'] parameter
        # why so complicated? In general, getattr is what we want, because it 
        # can give us any attribute of an object referenced by a string. Yes, 
        # a function is an attribute as well, it turns out. Problem: There is no 
        # parent object here to the Code_Manager classes (unless we change the 
        # entire import logic to importing modules instead of classes 
        # right-away...). So first step import the module (again, sort of), 
        # referenced by a string, then import the class as an attribute of that 
        # module, referenced by the same string (because class and module have 
        # the same name in this case). Then call the constructor (which is not 
        # exactly the __init__, referencing the __init__ doesn't work)
        cm_module = import_module(f"{args['lang']}_code_manager")
        cm_class = getattr(cm_module, f"{args['lang'].capitalize()}CodeManager")

    cm = cm_class()

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

    arg_lang = ""
    for s_lang, l_identifiers in D_LANG_IDENTIFIERS.items():
        if args[0] in l_identifiers:
            arg_lang = s_lang
            args = args[1:]
            break

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

    add_codemanager_path()
    sys.exit( run_code_manager_command(**options.__dict__, **dict_args) )


