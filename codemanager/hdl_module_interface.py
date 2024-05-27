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

    # TODO: maybe it's more logical to inherit from this class in sv/vhdl code 
    # managers

    PORT_IN         = "input"
    PORT_OUT        = "output"
    PORT_INOUT      = "inout"

    # the re can not detect signal width in certain cases, but it should still 
    # correctly detect the port name and direction:
    # - multi-dimensional array
    # - parameterized (non-digit) width
    # - unpacked arrays
    #
    # setup for detecting multi-dimensional array in the future: the RE matches 
    # an arbitrary number of width declarations ('[...:...]'), both for packed 
    # and unpacked. The width per dimension can be retrieved by findall on the 
    # respective match groups

    # TODO: due to the ()* groups, the re accepts wrong syntax like '[N-1:0' 
    # - no problem if things are coded correctly, but it would be nice to fix 
    # that

    # match [PAR-1:0][3:1]...
    __re_sig_multi_dim_sv = r'((\[[\w+\+\-\*\/]+:[\w+\+\-\*\/]+\])\s*)*'
    # put it together for full line
    __re_port_decl_sv = \
        re.compile(r'\s*(input|output|inout)\s+(logic|reg|wire){0,1}\s+'
                   + __re_sig_multi_dim_sv + r'(\w+)\s*' + __re_sig_multi_dim_sv
                   + r',{0,1}\s*')

    def __init__(self, name, width=1, direction=PORT_OUT):
        """
        :direction: one of HdlPort.PORT_* (default: PORT_OUT)
        """
        self.name = name
        self.width = width
        self.direction = direction

    @classmethod
    def __from_port_decl_mo(cls, match_obj, lang="sv"):
        """
        :match_obj: match object retrieved by __re_port_decl_*
        :lang: sv or vhdl
        """
        if lang == "sv":
            if not match_obj:
                return None
            name = match_obj.group(5)
            direction = match_obj.group(1)

            # TODO: couldn't you do this more elegant, with the port types as 
            # a dictionary and then access to PORT_* with @property?
            if not (direction == cls.PORT_IN or
                    direction == cls.PORT_OUT or
                    direction == cls.PORT_INOUT):
                raise Exception(f"Invalid signal direction: {direction}")

            # TODO: handle the width, as soon as you have a suitable data 
            # structure for that
            return cls(name, width=-1, direction=direction)

        else:
            raise Exception(f"Support for {lang} port declaration match objects "
                            "not implemented")

    @classmethod
    def from_sv(cls, line):
        """
        :line: line of code (within a module declaration)
        """
        match_obj = cls.__re_port_decl_sv.match(line)
        return cls.__from_port_decl_mo(match_obj, "sv")


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
        """assumes that only one module is declared in declaration. (If there 
        are multiple, the first one is detected)

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

        in_ports_decl = False
        in_param_decl = False

        for line in l_lines:
            if not in_ports_decl and not in_param_decl:
                # check for module declaration begin (first non-parameterized 
                # module, then parameterized module)
                mo = cls.__re_begin_module_decl_sv_no_param.match(line)
                if mo:
                    in_ports_decl = True
                    module_name = mo.group(1)
                    l_module_ports = []

                mo = cls.__re_begin_module_decl_sv_param.match(line)
                if mo:
                    in_param_decl = True
                    module_name = mo.group(1)
                    l_module_ports = []

            elif in_param_decl:
                mo = cls.__re_module_decl_sv_param_end.match(line)
                if mo:
                    in_param_decl = False
                    in_ports_decl = True

            else:
                mo = cls.__re_module_decl_sv_end.match(line)
                if mo:
                    # if module declaration end detected, finish reading and 
                    # return
                    in_ports_decl = False
                    return cls(module_name, l_module_ports)
                else:
                    # if no module declaration detected, detect ports in line
                    port = HdlPort.from_sv(line)
                    if port:
                        l_module_ports.append(port)

        # return None if no module declaration was detected
        return None

