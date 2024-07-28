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

# why absolute and not relative import? Relative only works within subpackages 
# (if you want to "cross" the top level it gives you an "import beyond 
# top-level" error). Since m_code_manager itself is not really supposed to be 
# a package (at least in my understanding, maybe "python-ish" way it is), I'd 
# rather use an absolute import. Still requires m_code_manager to be in 
# PYTHONPATH!! (so either install location or env variable). Also, with an 
# absolute import everybody can immediately see where in the directory structure 
# to look for GitUtil, with relative you need to know things by heart.
from m_code_manager.util.git_util import GitUtil
from m_code_manager.util.git_util import SubmoduleConfig

LANG_IDENTIFIERS = []

# todo: check all types of references


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
        self.git_util = GitUtil(lang)
        if not hasattr(self, 'submodules'):
            self.submodules = ["scripts"]

    def _get_str_src_dir(self, pkg_dir):
        """Get a string for the source directory name
        The source directory (if it shall be created) can be given as string or 
        bool. Functions deeper in the call stack need a string. So, if src_dir 
        is a str, nothing needs to be done, if it's a bool (and True), it 
        defaults to "src"

        :src_dir: bool or str; indicate the source directory
        :returns: a string represenation
        """
        if isinstance(pkg_dir, str):
            return pkg_dir
        elif isinstance(pkg_dir, bool):
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
        with open(s_target_file, 'w') as f_out:
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
                    input_write_backup = input(
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
        except AttributeError:
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
            l_lines))

        return l_lines

    # high-level git API
    # `mcm <lang> git <command>
    # -> that actually differs from the command structure from codemanagers in 
    # that it adds one layer. But you need the codemanager info for the 
    # standard repos and their paths, so you can't just go `mcm git ...`. And 
    # hopefully it's feasible to set up the argparse a little different for 
    # everything that is defined within code_manager.py. If not, you can 
    # fallback to `mcm <lang> git_<command>`. Bit uglier, but does the job.
    # submodule to include into the project are always specified by either the 
    # standard ones for the codemanager (specified in the <codemanager>.py) or 
    # the mcm version config. No passing from the command line
    # * handle/update submodule(s) - optionally pass the name of the submodule 
    # to work on
    # * check submodule(s) - sort of a dry-run; check for all or the given 
    # submodule what an update would do with the current configuration, without 
    # actually doing anything
    # * add a submodule (will for example be used by hdl project command, to 
    # add the vendor tool-specific scripts depending on the vendor project flow)
    # * add all mcm-required submodules for a given codemanager, if they aren't 
    # present anymore in the version (yes, then again, e.g. for hdl how do you 
    # pass if it's xilinx or lattice, but either that's an argument, or that's 
    # user's problem)
    #
    # remark: as opposed to in git_util.py, in this class an argument 
    # 'submodule' is a string (over there it's a Submodule object, strings are 
    # called 'submodule_name'). That's because this class here is basically 
    # unaware of Submodule objects, so there is no ambiguity and 'submodule' is 
    # intuitive.

    # how does a code_manager specify which (standard-path) submodules it needs?
    # * every CodeManager has self.submodules, which is a list of strings with 
    # submodule names.
    #     * by design choice, self.submodules only contains module names, but 
    #     no paths or references. paths or references must be set in 
    #     a system-wide local xdg config file (FUTURE).
    #     Reason: If I myself write the code_manager, than I'll use the 
    #     standard submodule path anyways. If someone else adds a code_manager, 
    #     including their scripts or whatever repos, I don't want code that 
    #     could be merged into the mainline to hard-point to something else 
    #     than the "official" submodule repos. So if you merge back a fork, you 
    #     have to add the corresponding submodule repos to the standard remote 
    #     as well. Still, with a system-wide config, the paths will be correct 
    #     when creating a repo across all your system, and once added, the path 
    #     persists in the submodule config, so it will be correct when cloning 
    #     the project on a new system.
    #     * how is self.submodules set? CodeManager() (which always needs to be 
    #     called by an inheriting class) sets `self.submodules = ['scripts']`, 
    #     if it is not set already. That means:
    #         * whenever you set self.submodules in an inheriting class, this will 
    #         persist (regardless of whether you do that before or after calling 
    #         the super-constructor)
    #         * still the default behavior is 'scripts' as the only submodule
    # * for dynamically adding submodules: favorably do so in _command_project, 
    # which supposingly every code_manager is going to have, by calling 
    # _command_git_add_submodule

    def _command_git_update(self, submodule=None, no_add=False, reset=False, **kwargs,):
        """
        :no_add: if True, submodules will not be added to the project if they 
        are not specified yet in the submodule config file. Default is to 
        silently add them.
        :submodule: (optional) name of a submodule to work on. If not passed, 
        all currently present submodules, and all submodules in self.submodules, 
        will be considered.
        :reset: instead of "updating", reset to the status tracked by the 
        parent directory
        """
        if submodule:
            # TODO: once xdg config file is implemented, draw symlink from 
            # there
            self.git_util.handle_submodules([submodule], symlink=True, reset=reset)
        else:
            # add self.submodules -> ensures that all the desired modules to 
            # add/update are in the submodule config file
            for submodule in self.submodules:
                try:
                    self.git_util.add_submodule_config(submodule)
                except KeyError:
                    pass

            # TODO: once xdg config file is implemented, draw symlink from 
            # there
            self.git_util.handle_submodules(symlink=True, reset=reset)

    def _command_git_check(self, submodule="", **kwargs):
        update_list = self.git_util.check_updates(submodule)
        if submodule:
            if update_list:
                print(f"Submodule '{submodule}' can be updated")
            else:
                print(f"Submodule '{submodule}' is up-to-date")
        else:
            if update_list:
                print(f"The following configured submodules can be updated: {update_list}")
            else:
                print("All configured submodules are up-to-date")

    def _command_git_add_submodule(self, name, path="", init=True, **kwargs):
        """adds a submodule (optionally with path) to the mcm version config 
        file. If desired, initializes and checks out the submodule.

        :init: set up and checkout the submodule: add as a submodule to the 
        top-level repo, init the submodule and checkout the latest HEAD. You 
        might want to disable this option if you first want to specify 
        a reference in the mcm version config file, before actually checking 
        out anything (in that case run _command_git_update(...) afterwards 
        manually). !Note that with init==False, the submodule will not even be 
        added to the project git repo, it will really only be added to the mcm 
        version config file!
        """
        submodule = SubmoduleConfig(name, path)
        self.git_util.add_submodule(submodule)
        if init:
            self.git_util.handle_submodules(submodule)

    def _command_git_init(self, **kwargs):
        """Create a git repo in the current directory
        """
        # (gitingores go into scripts, because what they are connected to the 
        # closest is artifacts that are generated by the scripts. Plus 
        # gitignores are not templates)
        self.git_util.init()

    def run_code_manager_command(self, command, **args):

        # call the respective _command_<command> class member function from the 
        # <command> argument
        # `getattr` is used to obtain a function object from a string.  
        # Hopefully that helps with extendability later on, because then the 
        # only thing you have to do is to implement the actual function that you 
        # want to have (with the right exact name and signature), and the link 
        # from passing the argument to calling this function works 
        # automatically.

        # TODO: determine if the command depends on any git submodule. If it 
        # does, check if newer data for that subrepo is available

        # TODO: if the command is 'project', enforce creating the directory and 
        # the git repo before you actually call the code_manager's 
        # _command_project, and change into the just created project directory.  
        # Basically, that also means that any _command_project can not act from 
        # within a project, but that everything you'd do within an existing 
        # project needs separate commands.

        fun_command = getattr(self, '_command_' + command)
        fun_command(**args)
