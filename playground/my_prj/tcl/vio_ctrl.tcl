
# TOP LEVEL VIO CONTROL
# connects to a top level xilinx vio core, which acts as more of a 'prototyping' 
# hardware control interface solution than a memory mapped axi interface.
#
# quick usage:
# after sourcing the script, make sure to run mcm_vio_init. That opens the 
# hardware manager, detects the vio core, connects to it and sets up the vio 
# object. It also links the probes file to the vio and sets up the user-defined 
# radices for interacting with vio signals (soon).
# After that, you can operate any signal by using the mcm_vio_read/write 
# functions. Everything else on top of that, like resetting and printing the 
# system status, is built on top of that.
#

package require json



proc _vio_ctrl_get_port_direction {user_signal_name} {
    global vio_ctrl_signals

    foreach signal $vio_ctrl_signals {
        if {[dict get $signal "name"] eq $user_signal_name} {
            return [dict get $signal "direction"]
        }
    }
    return ""
}


proc _vio_ctrl_get_port_name {user_signal_name} {
    global vio_ctrl_signals
    global d_debug_core_vio_ctrl

    # find the port index in the list of vio signals that originates from 
    # analysing the top-level rtl file
    foreach signal $vio_ctrl_signals {
        if {[dict get $signal "name"] == $user_signal_name} {
            set port_index [dict get $signal "index"]
            set direction [string toupper [dict get $signal "direction"]]
            break
        }
    }

    # find the port number in the dictionary that comes from the 
    # vivado-generated probes file
    set port_name_vio_ctrl ""
    foreach debug_pin [dict get $d_debug_core_vio_ctrl "pins"] {
        if {                                                            \
                [dict get $debug_pin direction] eq $direction &&        \
                [dict get $debug_pin portIndex] eq $port_index} {
            set port_name_vio_ctrl [dict get [lindex [dict get $debug_pin "nets"] 0] "name"]
            break
        }
    }

    return $port_name_vio_ctrl
}


proc mcm_vio_read {port_name} {
    global vio_gt_interface
    global vio_port_direction_identifiers

    set port_name_vio_ctrl [_vio_ctrl_get_port_name $port_name]
    set port_direction [_vio_ctrl_get_port_direction $port_name]
    set port_direction_specifier [dict get $vio_port_direction_identifiers $port_direction]

    if {$port_direction eq "in"} {
        # if it is a vio input port, the value at the ip tcl object might not be 
        # up-to-date yet
        refresh_hw_vio $vio_gt_interface
    }
    set read_val [get_property $port_direction_specifier [                     \
                    get_hw_probes $port_name_vio_ctrl -of_objects $vio_gt_interface]]
    return $read_val
}


proc mcm_vio_write {port_name value} {
    global vio_gt_interface
    global vio_ports_write

    set port_name_vio_ctrl [_vio_ctrl_get_port_name $port_name]

    startgroup
    # assign output value to port
    set_property OUTPUT_VALUE $value [get_hw_probes $port_name_vio_ctrl -of_objects $vio_gt_interface]
    # commit port to hardware
    commit_hw_vio [get_hw_probes $port_name_vio_ctrl -of_objects $vio_gt_interface]
    endgroup
}

############################################################
# SCRIPT SETUP
############################################################

set dir_hw_export hw_export
set name_vio_gt_interface inst_xip_vio_ctrl
# TODO: find a generic way to determine the hw device, or to set it in the 
# project config
set name_hw_device xc7a35t_0

# parse vio signal description json file and vivado-generated debug probes file 
# (which in fact is also json)
set vio_ctrl_signals [::json::json2dict [read [open vio_ctrl_signals.json r]]]
set vio_ltx_data [::json::json2dict [read [open [glob hw_export/latest/*.ltx] r]]]

# general comment about the many times that we have interchanging 'lindex' and 
# 'dict get' in this script: I don't know where it went wrong, if the ltx format 
# is not "exactly" json, or if there is a reason for multiple one-element lists.  
# As of now (2024-04) the code is tested with vivado 2019.1. It might as well 
# break with different vivado versions.
# (here, vio_ltx_data[0] only says "ltx_root", vio_ltx_data[1] is where the 
# information is
set debug_cores [dict get [lindex [dict get [lindex $vio_ltx_data 1] ltx_data] 0] debug_cores]

# find the element in debug_cores that describes the vio_ctrl instance. That is 
# exactly the one whose name is "inst_xip_vio_ctrl". Theoretically, you could 
# use 'lmap' here to filter the list. However, at least for Vivado 2019.1 the 
# tcl version (8.5) is too old for that (>=8.6), so we go the conservative 
# iterate and break way
set d_debug_core_vio_ctrl ""
foreach core $debug_cores {
    if {[dict get $core "name"] eq "inst_xip_vio_ctrl"} {
        set d_debug_core_vio_ctrl $core
        break
    }
}

# Reading from the vio is done via querying a property. Depending on if it is an 
# input or an output to the vio ip, that property is either named 'INPUT_VALUE' 
# or 'OUTPUT_VALUE'. Hence this dictionary, just for convenience in converting 
# that.
set vio_port_direction_identifiers [dict create                                 \
    in                              "INPUT_VALUE"                               \
    out                             "OUTPUT_VALUE"                              \
]


##############################
# SYSTEM
##############################


# LOOPBACK CONSTANTS
# TODO: support these kind of dicts in the getter/setter methods
set dict_switches_status [dict create                                           \
    "1000"                          0                                           \
    "0100"                          1                                           \
    "0010"                          2                                           \
    "0001"                          3                                           \
]


############################################################
# VIO INITIALIZATION
############################################################

# get the latest *.ltx file that has been exported (via manage_hw.bash) to
# $dir_hw_export
proc _mcm_vio_get_config_probes_file {} {
    global dir_hw_export

    set d_project_config [::json::json2dict                                     \
                        [read [open project_config.json r]]]
    set hw_build_name [dict get $d_project_config hw_version]
    set hw_build_path [file join $dir_hw_export $hw_build_name]

    set probes_file [lindex [                                            \
                glob [file join $hw_build_patwitchessw *.ltx]] 0 ]
    return $probes_file
}

proc mcm_vio_set_probes_file {{probes_file ""}} {
    global name_hw_device

    if {$probes_file eq ""} {
        # no probes file specified -> use the latest exported one
        set probes_file [_mcm_vio_get_config_probes_file]
    }

    set_property PROBES.FILE        $probes_file [get_hw_devices $name_hw_device]
    set_property FULL_PROBES.FILE   $probes_file [get_hw_devices $name_hw_device]
    refresh_hw_device [lindex [get_hw_devices $name_hw_device] 0]
}


############################################################
# API
############################################################

##############################
# GENERAL
##############################

# detect VIO and assign to global variable
proc mcm_vio_detect {} {
    global vio_gt_interface
    global name_hw_device
    global name_vio_gt_interface

    set vio_gt_interface [get_hw_vios                                           \
                -of_objects [get_hw_devices $name_hw_device]                    \
                -filter CELL_NAME=~$name_vio_gt_interface]
}


# initialize the VIO connection
# * set up probes file (the newest one that is exported, if none passed)
# * detect vio
# * set port radices
proc mcm_vio_init {{probes_file ""}} {
    global vio_gt_interface
    global vio_ports_write
    global vio_ports_read

    # INITIALIZE VIO OBJECT
    mcm_vio_set_probes_file $probes_file
    mcm_vio_detect

    # SET PORT RADICES
    # TODO
#     # write ports
#     set_property OUTPUT_VALUE_RADIX UNSIGNED [                                  \
#             get_hw_probes [dict get $vio_ports_write counter]                   \
#             -of_objects $vio_gt_interface]
#     # read ports
#     set_property INPUT_VALUE_RADIX HEX [                                        \
#             get_hw_probes [dict get $vio_ports_read switches]                   \
#             -of_objects $vio_gt_interface]
}

##############################
# RESET
##############################

# system reset
# TODO
# proc mcm_vio_sys_reset {} {
#     _mcm_vio_write sys_reset 1
#     _mcm_vio_write sys_reset 0
# }

##############################
# HIGH-LEVEL FUNCTIONALITY
##############################

# --- EXAMPLE ---
proc mcm_vio_print_status {} {
    # GATHER STATUS
    set sig [mcm_vio_get sig]
    set counter [mcm_vio_get counter]

    # PRINT STATUS
    puts "-------------------------------------------------------------"
    puts "SYSTEM STATUS"
    # <signal>
    puts "SIGNAL:         $signal"
    puts "-------------------------------------------------------------"
}

# --- EXAMPLE ---
proc mcm_vio_perform_operation {} {

    # trigger measurement
    mcm_vio_set sig 1

    # wait for hardware processing (10ms)
    after 10

    # check status
    set status [mcm_vio_get sig]

    puts "signal value: $status"
}

# --- EXAMPLE ---
# initialize system to operation mode defaults
proc mcm_vio_set_defaults {{mode ""}} {

    # -------------------- #
    # (non-mode dependent default values here)
    # -------------------- #

    switch $mode {
        "standard" {
            # -------------------- #
            # (mode dependent default values here)
            # -------------------- #
            mcm_vio_set sig 0
        }
        default {
            puts "Please specify one of the supported modes:"
            puts "standard"
        }
    }
    mcm_vio_sys_reset
}

