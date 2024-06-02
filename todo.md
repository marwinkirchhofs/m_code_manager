
# Bugfix

* hdl
    * verilator lint does not import sv package (error: import from missing 
      package)
    * `make build` stalls (I think in combination with IP runs)
    * read_hdl_sources:
        * tb files only in synthesis fileset
        * also check that really everything from the tb directory gets read

# Wiki

## C++
* project generation

## HDL
* module instantiation
* sv testbench generation

## Latex
* project generation

## Python
* project generation

# Framework

* in `_check_target_edit_allowed`, add an 'a' option to overwrite all files 
  (instead of querying for every file)


# Language Support

### Cpp

#### fixes

#### new language functionality

* gitignore the build directory

### HDL

#### fixes

* xips: when running XIP generation, remove IPs from the project that are 
  actually not described any longer
* build dependencies for makefile (check that again, rtl files etc)
* vio_ctrl features
    * set the radices in vio_ctrl.tcl
    * vio false path constraints
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
* when updating the board_part via the config command, also attempt loading the 
  master constraints file for that new board (and somehow delete the old one)
* turn `read_sources` (tcl) into an `update_sources`, in that it also removes 
  any sources from the project that are not present anymore on the filesystem.  
  At least do that for the sources, constraints and sim filesets (and whatever 
  the name was for the scripts fileset that holds non-constraint tcl files)
    * while you're at that, maybe it's useful/logical to do also include 
      handling IPs here.
* functionality to print the current project configuration
* find a better solution for generating the xips_vio_ctrl description than only 
  via m_code_manager, because now the makefile has to call m_code_manager
* hdl: have `make sim` dynamically revert to whichever simulator is specified in 
  the project config simulator field
* (not exactly sure what I meant by that) update the hw build functions to 
  detect and run all runs that are set up in the vivado project, now that using 
  the `make build` flow that encapsulates it is almost mandatory for building 
  the xips

* make the class file a little more modular (in terms of functions, to increase 
  code readability (talking about project generation)
* check if you can automatically retrieve the part from the board_part
* look into the distribution of the instantiation and testbench generation code 
  between hdl_code_manager and systemverilog_code_manager -> make sure things 
  are intuitive and make sense in combination with a future vhdl support update

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

* testbench
    * full verilator templates: top level testbench which instantiates the DUT 
      and something like an agent for the actual simulation (to separate that 
      from the infrastructure)
        * think about the best way to set up clocks. Maybe it's handy to do that 
          via a separate entity as well (or some config file/header)
        * the goal would be to not having to touch the top level tb file at all 
          (including that re-running the command would update the testbench, and 
          maybe the agent as well, in terms of port definitions)
    * systemverilog
        * xsim commands (both gui and cli) and targets
        * strip port suffixes in the interface class (i_,o_ etc)
* SDK targets: sdk_project, build_sw, program_soc (programming PL and PS)
* support for vivado preferred run configuration (the "design space exploration" 
  you just do in the project, but it should be exportable such that it 
  reproduces)

### Latex

#### fixes

#### new functionality
* yaml-based chapter and subfile structure description

### Python

#### fixes

* python virtual environment support (or rather, just a note on that it does 
  work out of the box with the vimspector config)

#### new functionality


