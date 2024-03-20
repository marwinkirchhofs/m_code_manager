#!/usr/bin/env python3

# PROJECT CREATOR
# This class is meant as a superclass for language-specific project creators.  
# The main reason is (kinda stupid): It's neat to have _TEMPLATES_ABS_PATH as a 
# variable accessible to all language-specific functions. As python doesn't have 
# global variables, initiating this during the import via the __init__.py 
# doesn't help the function within imported modules. So make everything classes, 
# have the subclasses calling this super-constructor which sets up the necessary 
# variable. Straightforward, huh?

import os, re, shutil
from git import Repo


class Code_Manager():
    """Superclass for all language-specific Code_Manager classes.
    The main reason is to set up _TEMPLATES_ABS_PATH as a class variable such 
    that all language-specific functions have access...
    """

    def __init__(self, lang="generic"):
        # default value for language: CodeManager.__init__() only needs the 
        # language for determining the correct template directory. Might not 
        # matter too much in the end for non-language commands because these 
        # could end up not needing templates.  But it's more convenient to use 
        # a dummy than to not set the template directory at all, and who knows 
        # when it turns out to be needed.

        # _TEMPLATES_ABS_PATH path private for the class to let all called 
        # methods know where to find the templates
        s_class_file_path = os.path.realpath(__file__)
        l_templates_path = s_class_file_path.split('/')[:-1]
        s_templates_path = "/".join(l_templates_path)
        self.TEMPLATES_ABS_PATH = os.path.join(s_templates_path, lang)
        pass

    
    def _get_str_src_dir(self, pkg_dir):
        """Get a string for the source directory name
        The source directory (if it shall be created) can be given as string or 
        bool. Functions deeper in the call stack need a string. So, if src_dir 
        is a str, nothing needs to be done, if it's a bool (and True), it 
        defaults to "src"

        :src_dir: bool or str; indicate the source directory
        :returns: a string represenation
        """
        if isinstance( pkg_dir, str ):
            return pkg_dir
        elif isinstance( pkg_dir, bool ):
            return "src"
        else:
            # TODO: make this an error
            return -1

    def __replace_template_string(self, str_in, app_name, pkg_dir=""):
        """Replace the template strings in 'str_in' with the respective variable 
        as demonstrated below. The function is mainly meant to be used in a map 
        call within _load_template.

        _T_APP_NAME_T_      -> app_name
        _TC_APP_NAME_TC_    -> app_name.upper()
        _T_SRC_DIR_T_       -> src_dir
        _TC_SRC_DIR_TC_     -> src_dir.upper()
    
        :str_in: TODO
        :app_name: TODO
        :src_dir: TODO
        :returns: TODO

        """
        # TODO: if we know that this is useful, replace it by a dictionary. Or 
        # two dictionaries, a global one for all languages and then a second 
        # language-specific one. In this case, we can make this function a 
        # global one...
        str_out = str_in
        str_out = str_out.replace("_T_APP_NAME_T_", app_name)
        str_out = str_out.replace("_TC_APP_NAME_TC_", app_name.upper())
        if pkg_dir:
            str_out = str_out.replace("_T_SRC_DIR_T_", pkg_dir)
            str_out = str_out.replace("_TC_SRC_DIR_TC_", pkg_dir.upper())

        return str_out


    def _load_template(self, f_template, app_name, pkg_dir=""):
        """loads the respective template file and correctly replaces all 
        placeholders according to the parameters

        :f_template: TODO
        :returns: TODO

        """
        # TODO: for e.g. the python __init__ file we might need identifiers if a 
        # placeholder shall be inserted in caps or not since there we have the same 
        # placeholder in caps and small...

        ##############################
        # READ FILE
        ##############################
        
        with open(f_template, "r") as f_in:
            l_lines = f_in.readlines()

        ##############################
        # PROCESS
        ##############################
        # -> parameterize the placeholders

        l_lines = list(map(
            lambda s: self.__replace_template_string(s, app_name, pkg_dir),
            l_lines ))

        return l_lines


    def _command_git(self, specifier, **args):
        """Create a git repo and copy the respective gitignore template

        :app_name: TODO
        :returns: TODO

        """

        print("Fake-initiating a git repo")
#         # CREATE REPO
#         repo = Repo.init()
#         assert not repo.bare
# 
#         # COPY GITIGNORE
#         shutil.copy(f"{self.TEMPLATES_ABS_PATH}/template_gitignore",
#                     ".gitignore")


    def run_code_manager_command(self, command, specifier, **args):

        # call the respective _command_<command> class member function from the 
        # <command> argument
        # `getattr` is used to obtain a function object from a string.  
        # Hopefully that helps with extendability later on, because then the 
        # only thing you have to do is to implement the actual function that you 
        # want to have (with the right exact name and signature), and the link 
        # from passing the argument to calling this function works 
        # automatically.
        fun_command = getattr(self, '_command_' + command)
        fun_command(specifier, **args)
#         print("Please implement this function for each language-specific Code_Manager!")
        

        
