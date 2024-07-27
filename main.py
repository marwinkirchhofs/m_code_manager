#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# TOP-LEVEL SCRIPT PROJECT_CREATE
#
# The script is used to load the language-specific template scripts, call the 
# respective create_project function and pass the given parameters to it

import argcomplete
from argparse import ArgumentParser
import inspect
from importlib import import_module
import os
import sys
import re


class _CommandOption(object):

    """hold the name of a command option and information on whether it is 
    required or not"""

    def __init__(self, name, required, action='store', default=None):
        self.name = name
        self.required = required
        self.default = default
        self.action = action

    @classmethod
    def from_args(cls, list_args, list_defaults):
        """creates a list of _CommandOption objects from args and defaults 
        iterables as inspect.getfullargspec(...).args/defaults generates them
        (does not do any cleaning of things like a 'self' argument, you have to 
        do that in advance)
        """
        l_options = []
        if not list_args:
            return []
        if not list_defaults:
            num_required_args = len(list_args)
        else:
            num_required_args = len(list_args) - len(list_defaults)
        # for-loop with range(len) here, instead of enumerate, because it looks 
        # as if enumerate causes problems with argparse. Don't know if it really 
        # was enumerate or something else, but the range(len) worked.
        for i in range(len(list_args)):
            required = i < num_required_args
            if required:
                l_options.append(
                    cls(name=list_args[i], required=required))
            else:
                # interpret the default value to determine the action:
                # - for a boolean value, set the action to store_* for the 
                # opposite value (if default is False, passing the argument 
                # should set it to true) - just set the default to align with 
                # the function default
                # - in any other case, set the action to store, and make the 
                # default argument also the default for the store action 
                # (theoretically that wouldn't be necessary, but why not)
                # TODO: this might be extended in the future
                default_val = list_defaults[i-num_required_args]
#                 if type(default_val) == bool:
                if isinstance(default_val, bool):
                    if default_val:
                        action = "store_false"
                        default = True
                    else:
                        action = "store_true"
                        default = False
                else:
                    action = "store"
                    default = default_val
                l_options.append(
                    cls(name=list_args[i], action=action, required=required, default=default))
        return l_options


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

# keep in mind for the future: you need to use realpath on __file__ RIGHT-AWAY, 
# otherwise it doesn't work symlinking the executable (without realpath you get 
# the path of the symlink, not of this script)
s_code_manager_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "codemanager")


def add_codemanager_path():
    sys.path.append(s_code_manager_path)

# from codemanager import *


############################################################
# ARGPARSE SETUP
############################################################

def setup_parser():

    # for enabling autocompletion (via argcomplete), we need some information 
    # from the code managers when creating the parser/subparser tree, which is 
    # structured as a dict:
    # * first-level keys is the official language/project type names
    # * one field 'aliases' -> to be passed to the top-level parser
    # * one field 'subparser' -> subparser for this project type
    # * one field 'commands' -> all the commands that 'subparser' can link to 
    #   (again nice, because you can just pass the list of keys to 'subparser' 
    #   as the available completions)
    #     * one field 'subparser' -> the subparser for this command
    #     * one field 'specifiers' -> the specifiers that are available for that 
    #     command - None if not required (no parser will be created in this case)
    #     * one field 'options' -> that is all the '--<option>' objects, plus 
    #     information whether they are required or not
    # how do we retrieve that? The guidelines that first all of the information 
    # should be automatically available from the codemanager modules, such that 
    # nobody has to edit or know any of the top-level script. Secondly, in general 
    # it should still be sufficient to just define your command handling functions 
    # as '_command_<command>' (without having to give an additional list or 
    # something just for the arg completer to read it) -> no duplicate information
    # * language names: from the code manager file names
    # * aliases: defined out-of-class per code manager file
    # * commands: from all the \*CodeManager classes, filter the dir() list
    # * specifiers: to be decided...
    #     * decorator might not work, because the decorator is only called I guess 
    #     when the function is called itself
    # * options: that is the function arguments which are not 'self' or 
    # 'subcommand' (because that one is a positional command line argument)
    #
    # TODO: how to provide choices for the subcommand option?
    #

    add_codemanager_path()

    D_SUBPARSE_TREE = {}
    L_LANG_IDENTIFIERS_ALL = []

    l_dir_codemanager = os.listdir(s_code_manager_path)
# match every string that ends with 'code_manager.py' and either/or
# - has only alphanumeric characters in front of that (at least one character), 
# terminated by a '_'
# - is exactly "code_manager.py"
    f_match_codemanager_modules = lambda s: re.match(r'(\w+_|)code_manager\.py', s)

    # we basically cycle through the hierarchy twice:
    # - First one is file-name driven, to collect all the information that we 
    # need for the parsers (we need all language specifiers and aliases for the 
    # top level parser, therefore we need one full cycle before creating the 
    # parse)
    # - Secondly: Create and set up the parsers using the collected information
    for s_codemanager_module_file in filter(f_match_codemanager_modules, l_dir_codemanager):
        # remove the '.py' ending from the filename
        s_codemanager_module = s_codemanager_module_file[:-3]
        # extract language name from codemanager file name
        # (returns empty list for the code_manager base class module)
        mo_lang = re.findall(r'(\w*)_code_manager', s_codemanager_module)

        if mo_lang:
            s_lang = mo_lang[0]

            # retrieve language identifiers
            exec(f"from {s_codemanager_module} import LANG_IDENTIFIERS")
            cm_module = import_module(s_codemanager_module)
            cm_class = getattr(cm_module, f"{s_lang.capitalize()}CodeManager")

            # retrieve commands
            # (I assume it would've been possible to filter for commands and if 
            # so get only the command name in one step, instead of first 
            # filtering and then removing the '_command_' prefix from the filter 
            # results. But should be good enough...)
            cm_commands = [s.replace('_command_','') for s in list(filter(
                        lambda x: re.match(r'_command_[\w]+', x), dir(cm_class)))]

            L_LANG_IDENTIFIERS_ALL.extend(cm_module.LANG_IDENTIFIERS)
            D_SUBPARSE_TREE[s_lang] = {
                    'aliases': cm_module.LANG_IDENTIFIERS,
                    'commands': {},
                    'subparser': None,
                    }

            for command in cm_commands:
                # RETRIEVE THE OPTIONS FOR A COMMAND:
                # the inspect module can give you the args (and their defaults) 
                # for a function object. defaults is a sparse list, it only has 
                # as many elements as the function has defaults (no empty 
                # positions). But the order is the same, so you can just take 
                # the difference in length, count, and then you know which ones 
                # have a default.
                # Options that have a default are treated as optional, options 
                # without a default are treated as required.

                # get command handler options and defaults
                fun_command_handler = getattr(cm_class, f"_command_{command}")
                fun_args = inspect.getfullargspec(fun_command_handler).args
                fun_arg_defaults = inspect.getfullargspec(fun_command_handler).defaults
                # filter: eliminate the 'self' argument and a potential 
                # 'subcommand' argument
                fun_args_filtered = [arg for arg in fun_args
                                     if not arg=='self' and not arg=='subcommand']

                d_subcommands = {}
                try:
                    index = fun_args.index("subcommand") - 1
                    l_subcommand_names = fun_arg_defaults[index]
                    # if a subcommand was given, remove that entry from 
                    # the option defaults, because passing the list/tuple with 
                    # that entry to _CommandOption.from_args would mess up the 
                    # alignment between args and defaults
                    fun_arg_defaults = fun_arg_defaults[:index] + fun_arg_defaults[index+1:]

                    for subcommand in l_subcommand_names:
                        s_subcommand_description_var = \
                                f"SUBCOMMAND_DESC_{command.upper()}_{subcommand.upper()}"
                        if s_subcommand_description_var in dir(cm_class):
                            subcommand_description = getattr(cm_class, s_subcommand_description_var)
                        else:
                            subcommand_description = ""
                        d_subcommands[subcommand] = subcommand_description
                except:
                    pass

                # retrieve command description (if present)
                s_command_description_var = f"COMMAND_DESC_{command.upper()}"
                if s_command_description_var in dir(cm_class):
                    command_description = getattr(cm_class, s_command_description_var)
                else:
                    command_description = ""
                D_SUBPARSE_TREE[s_lang]['commands'][command] = {
                    'subcommand': d_subcommands,
                    'description': command_description,
                    'options': _CommandOption.from_args(fun_args_filtered, fun_arg_defaults)
                    }

    # SECOND CYCLE - CREATE PARSERS
    parser_top_level = ArgumentParser(prog='m_code_manager')
    subparser_lang = parser_top_level.add_subparsers(dest="lang", required=True)
    # TODO: think about if you really want all language aliases in the arg 
    # completion

    for lang, lang_item in D_SUBPARSE_TREE.items():
        # TODO: what about help messages?
        parser_lang = subparser_lang.add_parser(lang, aliases=lang_item['aliases'])
        lang_item['subparser'] = parser_lang.add_subparsers(
                        dest="command", required=True)

        for command, command_item in lang_item['commands'].items():
            # TODO: what to do with help messages, where to generate those? Is 
            # there a way to get the function docstring?
            parser_command = lang_item['subparser'].add_parser(
                    command, help="help message", description=command_item['description'])

            # how the program allows subcommands: Command handler can 
            # have an argument 'subcommand=[...]'. In that case, add an 
            # additional hierarchy level of subparsers. For every specifier, we 
            # add a separate parser to l_parsers_lowest_level. If no 
            # subcommand is given, we still need that list, just that we 
            # only fill it with one element (the command parser, so we don't add 
            # the last hierarchy layer at all).
            if command_item['subcommand']:
                subparser_subcommands = parser_command.add_subparsers(
                            dest="subcommand", required=True)
                l_parsers_lowest_level = []

                for subcommand, subcommand_desc in command_item['subcommand'].items():
                    l_parsers_lowest_level.append(
                            subparser_subcommands.add_parser(
                                subcommand, description=subcommand_desc))
            else:
                l_parsers_lowest_level = [parser_command]

            # the options to a command are independent of the command specifier 
            # -> we just add the same options to every parser for this command, 
            # may it be just one without specifier, or all of the specifier 
            # parsers. Bit of duplication, but it does exactly what we want.
            for parser in l_parsers_lowest_level:
                for option in command_item['options']:
                    if option.required:
                        parser.add_argument(
                                '--'+option.name, action=option.action, required=True)
                    else:
                        parser.add_argument(
                                '--'+option.name, action=option.action, default=option.default)

    # enable autocompletion
    argcomplete.autocomplete(parser_top_level)

    return parser_top_level, D_SUBPARSE_TREE

############################################################
# FUNCTION DEFINITIONS
############################################################


def run_code_manager_command(subparse_tree, **args):
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

    # resolve potential LANG_IDENTIFIER to "code-manager name" language
    if args["lang"] == "":
        lang = ""
    else:
        if args['lang'] in subparse_tree:
            # the keys of subparse_tree are the main language identifiers as 
            # retrieved from the *_code_manager.py file names
            lang = args['lang']
        else:
            # check all subparse_tree["args['lang']"]['aliases'] -> the aliases 
            # are exactly the LANGUAGE_IDENTIFIERS as specified in the code 
            # manager files
            fun_match_language_identifier = lambda d: args['lang'] in d['aliases']
            # item[0/1]: key and value of the subparse_tree elements
            lang = [item[0] for item in subparse_tree.items() if fun_match_language_identifier(item[1])][0]

    ##############################
    # LANGUAGE-SPECIFIC PROJECT CREATION
    ##############################
    # First get the respective project generator object, then invoke it

    if lang == "":
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
        cm_module = import_module(f"{lang}_code_manager")
        cm_class = getattr(cm_module, f"{lang.capitalize()}CodeManager")

    cm = cm_class()

    cm.run_code_manager_command(**args)

    return 0


############################################################
# MAIN
############################################################

def main():
    parser, subparse_tree = setup_parser()
    args = parser.parse_args()
    run_code_manager_command(subparse_tree, **vars(args))


if __name__ == "__main__":
    main()
