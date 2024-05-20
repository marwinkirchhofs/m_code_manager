#!/usr/bin/env python3

# TODO: put the include_chapters script into some subdirectory, it's stupid to 
# have that in top level
# TODO: think about making chapter_order some sort of standard file type, 
# probably yaml (or json if that's necessary for some reason, but yaml should be 
# fine, no outdated tcl versions involved here) -> another benefit that would 
# have: You can include ordering for the subsections, and the pyhton parsing 
# becomes a little more standardized

import os
from operator import itemgetter

import code_manager

LANG_IDENTIFIERS = ["latex"]


class TexCodeManager(code_manager.CodeManager):

    PLACEHOLDERS = {
            'DIR_SRC':                      "src",
            'DIR_UTIL':                     "util",
            'FILE_TEX_MAIN_BASE':           "main",
            'FILE_CHAPTER_ORDER':           "chapter_order",
            'FILE_CHAPTERS':                "chapters.tex",
            'FILE_TEX_PACKAGES':            "packages.tex",
            'FILE_TEX_COMMANDS':            "commands.tex",
            'FILE_TEX_COLORS':              "colors.tex",
            'SCRIPT_INCLUDE_CHAPTERS':      "include_chapters.py",
            'EXAMPLE_CHAPTER':              "example",
    }

    def __init__(self):
        # why passing the language to the base class init? See (way too 
        # extensive) comment in python_code_manager
        super().__init__("tex")

    def _command_project(self, name="document", tex_engine="pdflatex",
                         dir_texmk_out="texmk_out", **kwargs):
        '''
        If app_name is not specified, it is assumed to be the project directory name
        empty - don't generate a hello world main.cpp

        :name: name for the created pdf document (<name>.pdf)
        :tex_engine: any valid latexmk tex engine. Is passed to latexmk in the 
        makefile via -<tex_engine>
        '''
        # TODO: git option

        ##############################
        # PROJECT DIRECTORIES
        ##############################

        project_dirs = itemgetter(
                'DIR_SRC', 'DIR_UTIL',
                )(self.PLACEHOLDERS)
        for directory in project_dirs:
            # comments: hdl_code_manager.py
            try:
                os.mkdir(directory)
            except FileExistsError:
                pass

        ##############################
        # TEMPLATES
        ##############################

        # MAKEFILE
        s_target_file = "makefile"
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("makefile", dict_placeholders={
                        "TEX_ENGINE": tex_engine,
                        "DOC_NAME": name,
                        "DIR_TEXMK_OUT": dir_texmk_out,
                        })
            self._write_template(template_out, s_target_file)

        # INCLUDE_CHAPTERS
        s_target_file = self.PLACEHOLDERS["SCRIPT_INCLUDE_CHAPTERS"]
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("include_chapters")
            self._write_template(template_out, s_target_file)

        # MAIN
        s_target_file = self.PLACEHOLDERS["FILE_TEX_MAIN_BASE"] + ".tex"
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("main")
            self._write_template(template_out, s_target_file)

        # UTIL/COMMANDS
        s_target_file = os.path.join(
                self.PLACEHOLDERS["DIR_UTIL"],
                self.PLACEHOLDERS["FILE_TEX_COMMANDS"])
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("commands")
            self._write_template(template_out, s_target_file)

        # UTIL/ACRONYMS
        # TODO

        # UTIL/PACKAGES
        s_target_file = os.path.join(
                self.PLACEHOLDERS["DIR_UTIL"],
                self.PLACEHOLDERS["FILE_TEX_PACKAGES"])
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("packages")
            self._write_template(template_out, s_target_file)

        # UTIL/COLORS
        s_target_file = os.path.join(
                self.PLACEHOLDERS["DIR_UTIL"],
                self.PLACEHOLDERS["FILE_TEX_COLORS"])
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("colors")
            self._write_template(template_out, s_target_file)

        # EXAMPLE CHAPTERS
        s_target_file = self.PLACEHOLDERS["FILE_CHAPTER_ORDER"]
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("chapter_order")
            self._write_template(template_out, s_target_file)

        # EXAMPLE CHAPTER
        s_dir_example_chapter = os.path.join(
                self.PLACEHOLDERS["DIR_SRC"], self.PLACEHOLDERS["EXAMPLE_CHAPTER"])
        try:
            os.mkdir(s_dir_example_chapter)
        except FileExistsError:
            pass

        s_target_file = os.path.join(s_dir_example_chapter,
                                     self.PLACEHOLDERS["EXAMPLE_CHAPTER"] + "_section.tex")
        if self._check_target_edit_allowed(s_target_file):
            template_out = self._load_template("example_section", dict_placeholders={
                        "EXAMPLE_CHAPTER_TITLE": self.PLACEHOLDERS["EXAMPLE_CHAPTER"].capitalize()
                        })
            self._write_template(template_out, s_target_file)
