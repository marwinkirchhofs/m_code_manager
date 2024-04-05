
today:
* vio_ctrl
    * integrate the new files as a template in the build flow (and presumably 
      make it a class that the code manager can easily import)
        * I guess integrating also means invoking that script whenever you do 
          a hardware build? Think about when you want to invoke it, maybe there 
          is a drawback to doing that automatically
    * complete the ltx import into vio_ctrl.tcl
        * also come up with something that sets all the radices, if they are 
          given
* build dependencies for makefile
* think about if it is useful to introduce a 'config' directory that would hold 
  the project config and vio_ctrl config, to not have the json files floating 
  around at top level...
* functionality to print the current project configuration
* re-integrate the hdl templates
    * implement systemverilog/hdl command handling functions in that particular 
      order:
        * path towards creating the simplest project in the world and making it 
          run on fpga
            * [x] create project
                * [x] directory structure
                * [x] basic tcl build scripts (create project, read sources, 
                  build hardware)
                * [x] makefile with targets (project, build, build_hw (included 
                  in build), program_fpga (preliminary just use the last vivado 
                  build, and using the vivado hw programming api))
                * [x] program_fpga implementation 
            * [x] create sv module
            * [x] create constraints - fetch the master constraints for a given 
              part/board from some default constraint file location (hardcode 
              that for now, later on you would make that something to put in 
              a config file, or even more elegant download it from some web 
              source)
        * [ ] create sv module instantiation
        * [ ] create sv testbench (you need the instantiation for that)
        * [ ] more advanced makefile targets
            * [ ] vivado simulation
            * [x] export hardware
            * [ ] SDK targets: sdk_project, build_sw, program_soc (programming 
              PL and PS)
            * [x] build Xilinx IPs 
        * [ ] support setting up multiple vivado synthesis/implementation runs 
          (just to the point where you can export it to a project such that it 
          can be restored, the trying out you do locally)
        * [x] verilator simulation support 

tomorrow:
* xip generation: extend the script such that it removes IPs from the project 
  for which there is no description given anymore
* implement a way to set the parser options in the language-respective classes, 
  and then load that dynamically in m_code_manager in more or less the same way 
  than language specifiers
* automate vio ctrl IP
  the guideline idea here would be: In what is indicated as the top module in 
  the project config, identify the signals to be vio controlled (naming 
  convention?).  This list is the root of everything.
    * from the top level file (as it is configured), identify the signals to be 
      controlled via a naming convention (something like vio_ctrl_write/read_\*)
        * don't forget about the clock, that one needs a unique name
    * python script to parse the top level rtl file, then generate and update 
      the vio ctrl ip
        * export a json list with all vio-connected signals:
            * extracted signal name (without the prefix) for usage as the 'user 
              space' name in the vio ctrl script
            * port direction
            * index (port number at the vio)
            * width
            * what to do with initial values? maybe allow setting those via 
              a comment in the rtl file
        * update xips/xips_vio_ctrl.tcl according to what you exported
        * instantiate in the top level module file (you can just process the 
          file)
    * vio_ctrl.tcl:
        * parse the control signal json file and the vivado-generated ltx file 
          to set up dictionaries, matching the port number to both the user name 
          (rtl-derived) and the cryptic vio port name (from the ltx file)
        * instead of single getters and setters, we will have a generic getter 
          and setter that just takes as an argument the signal name
        * (maybe, for convenience, add a way of printing the signal 
          configuration: the signals with their user space names, port 
          directions and radices)
    * we still need a way to set the radices. I would say: in vio_ctrl.tcl, you 
      can still have the user prepare a dictionary with signal names and 
      radices. Then one routine during initiation just checks the available 
      signals for matches with that dictionary, and if there is a match, it sets 
      the radix. The signal names are deterministic because they are fully 
      derived from the rtl, so the only thing the user has to do is to ensure 
      that the names in the radix dictionary and in the top level rtl match.
    * do something about necessary false path constraints. Maybe we could use 
      the same idea as for the radices, require a specific command format in the 
      rtl file.
* clean up the legacy code in {,python,cpp}code_manager -> either set good TODOs, 
  or remove what is not used anymore

some day:
* split up the hdl command function into private subfunctions per script (unless 
  it really doesn't make sense, but just to make the code readable)
* check if you can automatically retrieve the part from the board_part
* extend the manage hardware file in some way such that it holds a git tag, 
  history entry or something like that, so you can restore the code that led to 
  that bit file
* make it possible to "update" a project: for every file that would be written 
  by the project command, instead compare the template to the existing file. If 
  a line with a placeholder that is being passed matches a line in the existing 
  file, replace that line. Leave every other line in the existing file 
  untouched.
* check how shell/bash completion can be supported from within the python 
  project (if that is even possible, it might be that that's a different shell 
  config file that gets written or added during an installation procedure)
* check if it is possibleto automatically generate a bash help functionality in 
  git style (if you call -h after some comments, you get help and possible 
  options for that comment).
    * If that works, the ultimate elegance (and a considerable overkill) would 
      be if command handling methods could be implemented even more generic: 
      With a piece of code in the class init or wherever, maybe some function 
      object pushing around, that would allow to still conveniently implement 
      the function, but also define a description text that then automatically 
      shows up when invoking the command line help

# TODO

## Project Structure/Functionality
* refine into "mcm" (Marwin code manager) -> such that it can not only create 
  projects, but also add things to existing projects
  -> what would the user interface look like? Would it still be option-based, or 
  do you rather go sub-program calling like ```mcm python vimspector``` to 
      generate the vimspector config file (and complain if it is already there)?

### Misc
* how to do the git update for the HDL support? Merge the unfinished HDL 
  templates and then do the functionality update, or do the functionality update 
  and rebase the HDL feat branch? -> guess the second, the HDL support is mostly 
  templates and those are not really affected
* make a list of project requirements
    * think about which options you want to have parameterizable (e.g. a code 
      style engine)
* what is important to facilitate others contributing (for example adding 
  support for new languages/adding a new workflow)?

## Language Support
* HDL
    * refine the hdl templates according to the new experiences
        * top-level RTL that instantiates a block design, not top-level bd
        * dict-based IP creation flow
        * VIO-based control interface
    * implement missing parts (thus more or less everything) of the missing hdl
      option
    * think about an instantiator for RTL modules (how do you handle the path to 
      look for modules?)
* add HDL functionality
    * AXI(lite) interface generator
    * code indentation manager
