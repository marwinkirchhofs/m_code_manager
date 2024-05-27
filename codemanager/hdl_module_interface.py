#!/usr/bin/env python3

# supported module declaration syntax (whitespaces optional as per language 
# syntax):
#
# (SYSTEM)VERILOG
#
# module <module_name> #(
# ...
#     ) (
# );
#
# module <module_name> (
# );
#
# - no separate line for opening round bracket
# - parameters are optional
#
# VHDL
# TODO

import re

class HdlPort(object):

    PORT_IN         = "in"
    PORT_OUT        = "out"
    PORT_INOUT      = "inout"

    def __init__(self, name, width=1, direction=self.PORT_OUT):
        """
        :direction: one of HdlPort.PORT_* (default: PORT_OUT)
        """
        self.name = name
        self.width = width
        self.direction = direction

    @classmethod
    def from_sv(cls, line):
        """
        :line: line of code (within a module declaration)
        """
        

class HdlModuleInterface(object):

    # distinct between parameterized and parameter-free declaration via the 
    # regex
    # match "module <name> ("
    __re_begin_module_decl_sv_param = \
            re.compile(r'\s*module\s+(\w+)\s*#\(\s*')
    # match "module <name> #("
    __re_begin_module_decl_sv_no_param = \
            re.compile(r'\s*module\s+(\w+)\s*\(\s*')
    # match "    ) ("
    __re_module_decl_sv_param_end = \
            re.compile(r'\s*\)\s*\(\s*')
    # match ");"
    __re_module_decl_sv_end = \
            re.compile(r'\s*\)\s*;\s*')

    def __init__(self, name, ports=[]):
        """
        :ports: list of HdlPort objects
        """
        self.name = name
        self.ports = ports

    @classmethod
    def from_sv(cls, declaration):
        """
        :declaration: can be one of 2 options:
            1. str - file name to SystemVerilog module file
            2. list of str - lines of code that contains a SystemVerilog module 
            declaration
        """

        if isinstance(declaration, str):
            with open(declaration, 'r') as f_in:
                l_lines = f_in.readlines()
        else:
            l_lines = declaration

        in_module_decl = False

        for line in l_lines:
            # check for module declaration begin
            mo = __re_begin_module_decl_sv_no_param.match(line)
            if mo:
                in_module_decl = True
                module_name = mo.group(1)
        
