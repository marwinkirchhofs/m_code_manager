
today:
* check if you can automatically retrieve the part from the board_part
* split up the hdl command function into private subfunctions per script (unless 
  it really doesn't make sense, but just to make the code readable)
* re-integrate the hdl templates
    * implement systemverilog/hdl command handling functions in that particular 
      order:
        * path towards creating the simplest project in the world and making it 
          run on fpga
            * [ ] create project
                * [x] directory structure
                * [x] basic tcl build scripts (create project, read sources, 
                  build hardware)
                * [x] makefile with targets (project, build, build_hw (included 
                  in build), program_fpga (preliminary just use the last vivado 
                  build, and using the vivado hw programming api))
                * [ ] program_fpga implementation 
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
            * [ ] export hardware
            * [ ] program fpga from last exported hardware, instead of last 
              vivado build
            * [ ] SDK targets: sdk_project, build_sw, program_soc (programming 
              PL and PS)
            * [ ] build Xilinx IPs 
        * [ ] support setting up multiple vivado synthesis/implementation runs
        * [ ] verilator simulation support 

tomorrow:
* implement a way to set the parser options in the language-respective classes, 
  and then load that dynamically in m_code_manager in more or less the same way 
  than language specifiers
* clean up the legacy code in {,python,cpp}code_manager -> either set good TODOs, 
  or remove what is not used anymore

some day:
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
