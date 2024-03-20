
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
