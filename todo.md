# Bugfix

* hdl
    * verilator lint does not import sv package (error: import from missing 
      package)
    * `make build` stalls (I think in combination with IP runs)
    * read_hdl_sources:
        * tb files only in synthesis fileset
        * also check that really everything from the tb directory gets read
* `make xip_ctrl` is broken in playground my_prj (could also be incompatibility 
  between current version and generated scripts)
* axi_sim_pkg test_rand_read_write: @(posedge if_axi.cb) before starting 
  operation
    * reason: if somebody before waited on the clk, but not on the cb, then the 
      cb event is still active and you get an awvalid assertion and deassertion 
      at the same moment

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

* questa sim: if there is an elaborate.do in the xilinx export, fetch the libs 
  from that (probably awk in the create_sim_scripts.bash) and add them to the 
  run_sim.do
    * unless there is a way of deterministacilly fetching all the precompiled 
      libs that a certain IP needs
    * option to disable vopt entirely (for small designs for instance)

* get_json_variable fails if variable doesn't exist, but for things like sim 
  verbosity and sim args there should be default values
    * on that note, also introduce some sort of value check: vsim compile 
      fails if verbosity is an empty string for example, it has to be an 
      integer (also print_test_start is not imported)
* in testbench template, fix the function names for the function names from 
  util_pkg
    * also replace $finish with $stop
    * and insert the top tb timeout
* vivado project creation fails if no xdc file is present (and no part set), 
  shouldn't be the case either. Maybe default to a different part, you can 
  edit that later
     * on that note, the hdl config command needs auto-completion for part 
       and board_part
* also, since you have now splitted that: The sim makefile shouldn't 
  unconditionally link to the xilinx IP generation (after all, if you don't 
  check for project type, it's pure luck that XIL_TOOL is even defined).  That 
  should depend both on the project type and on if there are any IPs presentor 
  a Xilinx project at all.
* constraints path
* testbench generation: in testbench, seems like importing the agent package is 
  hardcoded to 'top', instead of templated - same for the interface
* xip questa integration: copy generated .mem files into the questa directory 
  (and yes, I still have no idea what to do if there are files of the same name, 
  but they are literally called from within the RTL, doesn't look like I can do 
  anything to resolve conflicts)
* place simulation wavefile in a subdirectory sim/wave/simulator, instead of in 
  sim/simulator -> that way you can gitignore everything in the sim directory 
  except for makefile and wave
    * check at which points in the flow you have to check-create those 
      directories
* in generated example testbench agent, wait_timeout_cycles -> 
  wait_timeout_cycles_ev
* questasim: after sourcing the exported xip bash script, remove the optimized 
  library to save disk space
* modelsim/questa: ensure compile order - rtl packages first (which means that 
  they can't contain interfaces, let's see when that becomes a problem), then 
  interfaces, then tb (aka simulation) packages, then everything else
    * rename agent_<module>, containing `<module>_sim_pkg` to both 
      `agent_<module>_pkg`
    -> works hard-coded in the thesis project, gonna be in the git restructure 
    update
* axi_sim_pkg print64/256 etc.: depending on the AXI_ADDR_WIDTH, select the 
  correct function for printing (and maybe do a demux helper function)
* testbench generation fails if top module has no ports
* xips: when running XIP generation, remove IPs from the project that are 
  actually not described any longer
* add a convenient way for fetching constraints file from the given project 
  config
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

* think about exporting the verbosity into a generated header that you include 
  in the top level testbench. Advantage: You don't have to recompile if you only 
  change the verbosity

#### new functionality

* for questa simulation: think about appending a vopt step to the compilation
    * it gets executed anyway, but now it's in simulation which you don't want
    * it forms one compile unit, so that should discover invalid references and 
      that kind of stuff
    * the necessary variables should already be there, like the libs.
* testbench generation: support structs and interfaces as ports
* generated testbench: add an "emergency stop" -> fork that just stops after 
  a parameterizable amount of time, in case something else hangs up
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
        * clocking block for generated top module interface
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


