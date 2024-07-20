#!/usr/bin/env python3

# PROJECT CREATOR
# This class is meant as a superclass for language-specific project creators.  
# The main reason is (kinda stupid): It's neat to have TEMPLATES_ABS_PATH as a 
# variable accessible to all language-specific functions. As python doesn't have 
# global variables, initiating this during the import via the __init__.py 
# doesn't help the function within imported modules. So make everything classes, 
# have the subclasses calling this super-constructor which sets up the necessary 
# variable. Straightforward, huh?

import os
import re
import shutil
from git import Repo

LANG_IDENTIFIERS = []

class CodeManager():
    """Superclass for all language-specific Code_Manager classes.
    The main reason is to set up TEMPLATES_ABS_PATH as a class variable such 
    that all language-specific functions have access...
    """

    def __init__(self, lang="generic"):
        # default value for language: CodeManager.__init__() only needs the 
        # language for determining the correct templates subdirectory. Might not 
        # matter too much in the end for non-language commands because these 
        # could end up not needing templates.  But it's more convenient to use 
        # a dummy than to not set the template directory at all, and who knows 
        # when it turns out to be needed.

        # TEMPLATES_ABS_PATH path private for the class to let all called 
        # methods know where to find the templates
        s_project_root = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), os.pardir)
#         s_class_file_path = os.path.realpath(__file__)
#         l_templates_path = s_class_file_path.split('/')[:-1]
        self.TEMPLATES_ABS_PATH = os.path.join(s_project_root, "templates", lang)

    
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

    def __replace_template_string(self, str_in, dict_placeholders):
        # TODO: make this generic: pass **args, which are keyword arguments for 
        # how to replace a specific template placeholder. Let's suppose 
        # something like 'target=my_var' was passed as the keyword argument, 
        # then what should happen:
        # _T_TARGET_T_      -> my_var
        # therefore, for EVERY distinct placeholder that you want to use in the 
        # template, you need to pass a keyword argument
        # placeholders: _T_<PLACEHOLDER>_T_
        #   by convention, placeholders in the templates are written in capitals, 
        #   but the keyword arguments to the functions are lowercase. Might seem 
        #   a bit unintuitive, but capitals are way more readable in templates, 
        #   and arguments in capitals would mess with python naming conventions.
        """TODO Replace the template strings in 'str_in' with the respective variable 
        as demonstrated below. The function is mainly meant to be used in a map 
        call within _load_template.
        """

        str_out = str_in
        # find all placeholders in the input string
        l_template_matches = re.findall(r'_T_[A-Z_]+_T_', str_in)
        
        for s_placeholder_full in l_template_matches:
            # remove the leading and trailing '_T_' from the placeholders
            s_placeholder_extracted = s_placeholder_full[3:-3]
            # (interesting side fact here: it's significantly faster to search 
            # for the key and conditionally retrieve the value this way (and 
            # even looks like implemented as O(1) in input size and key index), 
            # than using a dictionary.items() for-loop, which theoretically 
            # saves one lookup)
            if s_placeholder_extracted in dict_placeholders:
                str_out = str_out.replace(
                            s_placeholder_full, dict_placeholders[s_placeholder_extracted])
            else:
                print(f"\
Found unspecified placeholder {s_placeholder_extracted} in template input line:\n{str_in}")
        
        return str_out


    def _write_template(self, l_template_out, s_target_file):
        """Write the target file with the content that was obtained from loading 
        and parameterising a template. This method is practically an alias to 
        the python-native file writing API, makes the code look a little more 
        intuitive.

        l_template_out: the lines to be written to f_target as a list of strings
        """
        with open (s_target_file, 'w') as f_out:
                f_out.writelines(l_template_out)
    

    def __check_existing_target(self, target):
        # TODO: return the target type, if it exists. Then this method returns 
        # a type, while the usually called _check_target_edit_allowed returns 
        # a simple bool
        target_type = ""
        if os.path.exists(target):
            if os.path.isdir(target):
                target_type = "directory"
            elif os.path.isfile(target):
                target_type = "file"
            elif os.path.islink(target):
                target_type = "link"
            else:
                target_type = "other"
        return target_type


    def _check_target_edit_allowed(self, target):
        """Check if the file/directory/link that is specified by target exists.  
        If it does, ask for confirmation to edit or overwrite it.
        In favour of a boolean return value, the function does not return any 
        information on the type of the target if the target is found te be 
        existing.  If you need that, instead of a general "yes, do whatever you 
        want to with this target", then revert to the manual os.path.is* 
        methods.

        Returns True if target is safe to be edited (meaning that it either 
        doesn't exist or that the user confirmed that it can be overwritten)
        """

        target_type = self.__check_existing_target(target)
        if target_type:
            input_overwrite = input(
f"""Target {target_type} '{target}' exists. How to proceed?
b - backup the existing target to {target}.bak, then edit/overwrite
y - edit/overwrite existing target without backup
n - don't edit/overwrite the target\n""")
            if input_overwrite == 'b':
                target_backup = target + ".bak"
                if os.path.exists(target_backup):
                    input_write_backup = input (
f"""Target backup {target_backup} already exists.
y - overwrite
n - don't overwrite, aborts writing {target} entirely""")
                else:
                    input_write_backup = 'y'
                if input_write_backup == 'y':
                    if target_type == "directory":
                        shutil.copytree(target, target_backup,
                                        symlinks=True, ignore_dangling_symlinks=True,
                                        dirs_exist_ok=True)
                    else:
                        # TODO: this might fail if the target is a symlink, 
                        # instead of a file. First step was only to separate 
                        # files and directories
                        shutil.copy(target, target_backup)
                    print(f"{target} backed up")
                    return True
                else:
                    print(f"Existing backup left untouched. {target} won't be edited...")
                    return False
            if input_overwrite == 'y':
                return True
            else:
                print("The target won't be edited")
                return False
        else:
            return True
            


    def _load_template(self, template_identifier, dict_placeholders={}):
        """loads the respective template file and replaces all placeholders:
        The main placeholders are supplied by self.PLACEHOLDERS. Any other 
        placeholders (probably dynamic runtime ones) can be supplied via 
        dict_placeholders.

        :f_template: TODO
        :returns: TODO

        """
        # TODO: might very well be suitable to integrate writing the target file 
        # into this method. Currently, that's two function calls for the command 
        # handlers. It used to be like that such that the command handler could 
        # replace any "non-standard" placeholders in the template. But since 
        # that now works generically, there shouldn't be any need anymore to do 
        # that. Probably best call: Make that an option to this function with 
        # default true, and complain if the option is true and no target file 
        # was passed.

        # merge self.PLACEHOLDERS and dict_placeholders (try/except in case 
        # self.PLACEHOLDERS was not specified)
        try:
            dict_placeholders_all = {**self.PLACEHOLDERS, **dict_placeholders}
        except:
            dict_placeholders_all = dict_placeholders

        ##############################
        # READ FILE
        ##############################
        
        f_template = os.path.join(
                self.TEMPLATES_ABS_PATH, "template_" + template_identifier)
        with open(f_template, "r") as f_in:
            l_lines = f_in.readlines()

        ##############################
        # PROCESS
        ##############################
        # -> parameterize the placeholders

        l_lines = list(map(
            lambda s: self.__replace_template_string(s, dict_placeholders_all),
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


    def run_code_manager_command(self, command, **args):

        # call the respective _command_<command> class member function from the 
        # <command> argument
        # `getattr` is used to obtain a function object from a string.  
        # Hopefully that helps with extendability later on, because then the 
        # only thing you have to do is to implement the actual function that you 
        # want to have (with the right exact name and signature), and the link 
        # from passing the argument to calling this function works 
        # automatically.
        fun_command = getattr(self, '_command_' + command)
        fun_command(**args)
#         print("Please implement this function for each language-specific Code_Manager!")
        

        
