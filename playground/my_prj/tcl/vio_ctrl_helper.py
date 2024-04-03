#!/usr/bin/env python3

import re
import json

class VioSignal(object):
    """All the necessary fields for describing a signal that needs to be added 
    to the VIO
    """

    def __init__(self, name="", direction="input",
                 width=1, radix="binary", init=0, index=0):
        """
        radix - can be 'binary', 'hex' or 'decimal' (TODO: distinguish 
        signed/unsigned decimal, and maybe others if there are other radices 
        available for VIO ports)
        """
        self.name = name
        self.direction = direction
        self.width = width
        self.radix = radix
        self.init = init

    @classmethod
    def get_vio_signal_from_str_verilog(cls, s_input):
        """analyse a verilog/systemverilog line of code and look for a vio_ctrl 
        signal definition (not the vio clock). Returns the according vio signal object if it finds 
        a vio signal definition, otherwise 'None'.

        VIO signals need to be defined in the following way in 
        verilog/systemverilog files (for clock look below):
        "logic"/"reg"/"wire" [\[<width_upper>:<width_lower>\]] 
        vio_ctrl_<"in"/"out">_<name>; // radix=<radix> init=<val>
        - no width is automatically interpreted as width = 1.
            - otherwise, width = width_upper - width_lower
            the restriction here is, as is quite visible: No 
            placeholders/parameters/variables in the signal definition. The 
            widths need to be given explicitly (otherwise the line will be 
            ignored).
        - there can be an arbitrary amount of whitespaces in any spot that has 
          a whitespace in the format given (as long as it doesn't affect the 
          syntactical meaning of course)
        - <name> is the user name that the signal will eventually have in 
          vio_ctrl.tcl. It gets specified here
        - radix is the radix for the signal representation in the user vio 
          interface. If no radix is given, the vio will automatically determine 
          the radix for the signal (probably either binary or hex)
        - <val> is the initialization value for the signal that the vio core 
          will set at device initialization. Setting init is optional

        The vio clock needs to have the name vio_ctrl_clk and be present in the 
        module. With that there is no need to match for the clock here, it will 
        always be named the same when generating the vio (so you don't gain 
        information from matching). Just require the user to implement the 
        signal, and if they fail to do so let the synthesis tool complain
        """

        # the pattern of death... it does what is described above for the 
        # arbitrary signal names (not the clock)
        pattern_vio_sig = re.compile(
r'[\s]*(logic|reg|wire)([\s]+\[([\d]+):([\d]+)\][\s]+){0,1}vio_ctrl_(in|out)_([\w]+)[\s]*;([\s]*//[\s]*(radix=([\w]+)[\s]*){0,1}[\s]*(init=([\w]+)){0,1}[\s]*){0,1}'
        )
        # Match the general signal description, return None. 
        mo = pattern_vio_sig.match(s_input)
        if mo:
            # the match group indices are determined by just trying out
            width_upper = mo.group(3)
            width_lower = mo.group(4)
            direction = mo.group(5)
            name = mo.group(6)
            # (if radix and/or init are not given, mo.group({8,9}) exist, but 
            # are None. So no need for any existence check or try/except here)
            radix = mo.group(9).upper()
            init = mo.group(11)
            return VioSignal(name, direction, int(width_upper)-int(width_lower), radix, init)
        else:
            return None

    def print_instantiation(self, probe_index=0):
        """prints the line to be used within a verilog/systemverilog vio ctrl 
        module instantiation (".probe...<probe_index>     (<signal>))

        probe_index: probe index for the given group ('in' or 'out').
        """
        # purely inserting a space for cosmetics, to make sure that in the
        # instantiation the ports are aligned no matter if the direction
        # string would have 2 or 3 letters...
        s_direction_index = f"in{probe_index} " if self.direction == "in" \
                            else f"out{probe_index}"
        # the line is only too long so that the indentation looks good in the 
        # eventual file...
        return f"    .probe_{s_direction_index}             (vio_ctrl_{self.direction}_{self.name}),"


def parse_verilog_module(s_module_file_name):
    """analyse a verilog module for vio-connected signal definitions (format see 
    VioSignal.get_vio_signal_from_str_verilog).
    Returns: list of VioSignal objects (the clock is not included in the list, 
    it is always named the same)
    """
    with open(s_module_file_name, 'r') as f_in:
        l_lines = f_in.readlines();

    l_vio_ctrl_signals = []
    # counters to hold the indices with which the signals will be connected to 
    # the vio ports -> that's also what the vio_ctrl.tcl will eventually 
    # utilize in order to map vio ports to user signal names and vio-internal 
    # port names.
    counts_vio_ports = {'in': 0, 'out': 0}
    for line in l_lines:
        vio_ctrl_sig = VioSignal.get_vio_signal_from_str_verilog(line)
        if vio_ctrl_sig:
            vio_ctrl_sig.index = counts_vio_ports[vio_ctrl_sig.direction]
            # for the 10000th time, where on earth is the += in python?
            counts_vio_ports[vio_ctrl_sig.direction] =                  \
                        counts_vio_ports[vio_ctrl_sig.direction] + 1
            l_vio_ctrl_signals.append(vio_ctrl_sig)

    return l_vio_ctrl_signals


def process_verilog_module(s_module_file_name)
    """update the vio_ctrl instantiation in a verilog module:
    - find vio_ctrl signal definitions (see parse_verilog_module)
    - write the vio_ctrl signals json file (to be read by vio_ctrl.tcl when 
      loading)
    - edit the verilog module file to hold an up-to-date instantiation of the 
      vio_ctrl ip: Scan the module for an existing instantiation, if you find 
      one, remove that. Insert the new instantiation at the very end of the 
      module (that is, right before 'endmodule')
    """
    # TODO


def generate_vio_ip_instantiation(l_vio_ctrl_signals):
    """
    Returns: A list of strings, representing the lines of verilog code for the 
    vio control core instantiation
    """

    # I know, list plus filter is not necessarily what you should, but these 
    # lists are probably not gonna contain >1e4 entries...
    l_vio_ctrl_signals_in = list(filter(lambda x: x.direction == 'in', l_vio_ctrl_signals))
    l_vio_ctrl_signals_out = list(filter(lambda x: x.direction == 'out', l_vio_ctrl_signals))

    l_lines = [
"module xips_vio_ctrl (",
"    .clk                    (vio_ctrl_clk),"]

    # theoretically you wouldn't have to separate in and out signals here, but 
    # it looks nice in the rtl file
    for index, signal in enumerate(l_vio_ctrl_signals_in):
        l_lines.append(signal.print_instantiation(index))
    for index, signal in enumerate(l_vio_ctrl_signals_out):
        l_lines.append(signal.print_instantiation(index))

    # remove the ',' from the last line of signal connection
    s_last_line = l_lines.pop()
    l_lines.append(s_last_line.replace(',',''))

    l_lines.append(");")

    return l_lines


def write_json_sig_list(l_vio_ctrl_signals, file_name):
    """write a list of vio control signals into a json file, such that it can 
    later easily be picked up vio_ctrl.tcl
    """
    
    # transform the list of VioSignal objects into a list of dictionaries
    l_vio_ctrl_signals_dicts = [l.__dict__ for l in l_vio_ctrl_signals]
    with open(file_name, 'w') as f_out:
        json.dump(l_vio_ctrl_signals_dicts, f_out, indent=4)


if __name__ == "__main__":
    s_file_in = "rtl/top.sv"
    l_vio_ctrl_signals = parse_verilog_module(s_file_in) 
    l_vio_inst_lines = generate_vio_ip_instantiation(l_vio_ctrl_signals)
    for l in l_vio_inst_lines:
        print(l)
    write_json_sig_list(l_vio_ctrl_signals, "vio_ctrl_signals.json")
