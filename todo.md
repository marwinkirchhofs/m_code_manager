
# Bugfix

* hdl
    * verilator lint does not import sv package (error: import from missing 
      package)
    * make build stalls (I think in combination with IP runs)
* language aliases don't translate to the code managers

# Language Support

### Cpp

#### fixes

#### new language functionality

* gitignore the build directory

### HDL

#### fixes

* find a better solution for generating the xips_vio_ctrl description than only 
  via m_code_manager, because now the makefile has to call m_code_manager
* build dependencies for makefile (check that again, rtl files etc)
* something for adding sources after creating the project: either a separate 
  invoking of read sources, or a "project update" (which doesn't create an 
  entirely new project if there already is a project)
* think about if it is useful to introduce a 'config' directory that would hold 
  the project config and vio_ctrl config, to not have the json files floating 
  around at top level...
* vio_ctrl features
    * set the radices in vio_ctrl.tcl
    * harden the script with error checks (for example currently you get 
      a python error when there is just no top module set in the project)
    * if no vio ctrl is requested in the project (I would say, if there is no 
      vio_ctrl connection signal declared), then please abort that as a whole.  
      That is, don't generate the IP description file (and remove it if present), 
      don't generate a signal config (and remove it if is present) and don't 
      generate an instantiation (and remove it if it is present)
    * tcl+make command to open the hw manager in the vivado gui with loading the 
      current hw_version files (mainly to connect to the ILA, and the VIO, of 
      whatever might just be loaded onto the chip)
    * vio false path constraints
* xips: when running XIP generation, remove IPs from the project that are 
  actually not described any longer
* when updating the board_part via the config command, also attempt loading the 
  master constraints file for that new board
* functionality to print the current project configuration
* hdl: have `make sim` dynamically reverting to whichever simulator is specified 
  in the project config simulator field
* (not exactly sure what I meant by that) update the hw build functions to 
  detect and run all runs that are set up in the vivado project, now that using 
  the `make build` flow that encapsulates it is almost mandatory for building 
  the xips

* make the class file a little more modular (in terms of functions, to increase 
  code readability
* check if you can automatically retrieve the part from the board_part

#### new functionality

* (don't know if that idea is still applicable/useful) make it possible to 
  "update" a project: for every file that would be written by the project 
  command, instead compare the template to the existing file. If a line with 
  a placeholder that is being passed matches a line in the existing file, 
  replace that line. Leave every other line in the existing file untouched.
* extend the manage hardware file in some way such that it holds a git tag, 
  history entry or something like that, so you can restore the code that led to 
  that bit file
* AXI(lite) interface generator
* code indentation manager
* instantiation generator
      * there is an easy way of doing arbitrary module generation: You 
        completely ignore the pointer. Just give the tool a target module and 
        a destination module. Then, act similar to the vio_ctrl instantiation:
            * in the destination module, look for an existing instantiation. If you 
              don't find one, just create an empty one before 'endmodule'.
                  * if you find an instantiation, stop the pointer at that point.  
                    Register that instantiation as a dictionary (port name -> 
                    connected signal name).  Then, line by line, write the new 
                    instantiation. Whenever a port of the new instantiation appears 
                    in the dictionary, connect the according signal.
                        * also, provide an option to keep the old instantiation 
                          commented out. That makes it easier to reconnect correctly 
                          if port names changed on the module to be instantiated, 
                              but you actually still want to have the same signals 
                              connected. I mean, you COULD do something like even 
                              checking if the overall structure of the ports is the 
                              same, and if so, assume that it's just the names that 
                              changed and connect right-away, but as Jimothy would 
                              say: With every half-decent text editor it's a matter 
                              of seconds to reestablish the connections by pasting 
                              into the new instantiation.

* testbench
    * full verilator templates: top level testbench which instantiates the DUT 
      and something like an agent for the actual simulation (to separate that 
      from the infrastructure)
        * think about the best way to set up clocks. Maybe it's handy to do that 
          via a separate entity as well (or some config file/header)
        * the goal would be to not having to touch the top level tb file at all 
          (including that re-running the command would update the testbench, and 
          maybe the agent as well, in terms of port definitions)
    * same structure in SystemVerilog for other simulators
        * for that you need module instantiation
* xsim commands (both gui and cli)
* SDK targets: sdk_project, build_sw, program_soc (programming PL and PS)
* support for vivado preferred run configuration (the "design space exploration" 
  you just do in the project, but it should be exportable such that it 
  reproduces)

### Python

#### fixes

* python virtual environment support (or rather, just a note on that it does 
  work out of the box with the vimspector config)

#### new functionality


