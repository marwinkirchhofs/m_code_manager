#!/usr/bin/env python3

# PYTHON PROJECT_CREATE
#
# Create a python project from the template in this directory

import os, re
import code_manager

LANG_IDENTIFIERS = ["python", "py"]

class PythonCodeManager(code_manager.CodeManager):


    def __init__(self):
        # It might feel confusing, but it appeared to be the most convenient to 
        # manually pass the language name to the base class init:
        # The base class init sets self.TEMPLATES_ABS_PATH, that's what it needs 
        # the language for.
        # Other (inferior) options for passing the language:
        # - always call the constructor with the language, but why would you 
        # call a constructor for a python code manager and at the same moment 
        # tell it that it's for python? Basically you'd have a positional 
        # argument with always the same value, that's not the point.
        # - Determine the language name from the file name, just like 
        # m_code_manager.py does.  But the class then would need code for that 
        # as well, so you would do something like:
        # super().get_lang(__file__)
        # That's just not better, conclusion is to require a random programmer 
        # to pass the language name to the base class init.
        super().__init__("python")


    PLACEHOLDERS = {
    }


    def _command_main(self, name="main", src_dir="", **kwargs):

        s_target_file = name + ".py"

        if src_dir:
            import_src_dir = "import " + src_dir
        else:
            # just passing an empty string here will cause an empty line which 
            # is not ideal (it should just remove the placeholder line. But 
            # currently that would require an update on the replacement engine.
            import_src_dir = ""

        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("main", {
                            "IMPORT_SRC_DIR": import_src_dir,
                            })
            self._write_template(template_out, s_target_file)

        # EXECUTION/READ PERMISSIONS
        os.chmod(s_target_file, (7<<6)+(5<<3)+5)


    def _command_init(self, pkg, **kwargs):

        s_target_file = os.path.join(pkg, "__init__.py")

        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("init")
            self._write_template(template_out, s_target_file)


    def _command_vimspector(self, **kwargs):

        app_name = os.path.dirname(os.path.realpath(__file__))

        # DETERMINE MAIN FILE
        # if main.py exists, pass that as the main file. Otherwise select 
        # <app_name>.py.
        if os.path.isfile("main.py"):
            program_main = "main.py"
        else:
            program_main = app_name + ".py"

        s_target_file = ".vimspector.json"

        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("vimspector", {
                            "APP_NAME": app_name,
                            "PROGRAM_MAIN": program_main,
                            })
            self._write_template(template_out, s_target_file)


    def _command_package(self, name, write_init_file=False, **kwargs):
        """
        """
        # TODO: Currently, it doesn't remove contents of an existing package 
        # directory (although it might add a new init file). Think about if that 
        # is the best behaviour.

        s_init_file = os.path.join(name, "__init__.py")
        
        # check if package directory is existing
        if os.path.isdir(name):
            input_edit_dir = \
                input(f"Package directory '{name}' already exists. Proceed anyway? [y/n]")
            write_init = input_edit_dir == 'y'
#             if input_edit_dir == 'y':
#                 # check for existing init file
#                 write_init = self._check_target_edit_allowed(s_init_file)
#             else:
#                 write_init = False

        # if not existing, create the directory right-away
        else:
            os.mkdir(name)

        if write_init_file:
            self._command_init(name)


