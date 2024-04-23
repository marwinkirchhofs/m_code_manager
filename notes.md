
### DOCUMENTATION

#### structure
how do you actually structure the documentation? There are different parts and 
different levels of documentation to the project:
* concept of functionality
    * structure of the command line interface
    * capabilities (language-agnostic)
* per-code manager documentation
    * commands and options
    * project structure
* how to add/extend a codemanager -> which parts of the code are there such that 
  you can easily extend it and use the frameworks behind?
    * baseclass CodeManager
    * templates
        * syntax
        * file structure
        * how to interact
* how to contribute
    * how do the internals of the code work (the part that is not obvious from 
      reading the code)
    * which guidelines are there to be followed

The top level readme can only do part 1, the concept of functionality, and tease 
about part 2/link to a respective location.

How about part 2? Two things that come to my mind: Docstrings and argparse help 
messages. Is there a way to combine the two, such that your docstrings are also 
your help messages? The help messages I would maybe define as class variables in 
the respective code managers, which are linked to the command handlers using 
a naming convention (like `COMMAND_<COMMAND>_HELP`)

Part 3 and 4 are things for a github wiki. For part 3 it would be nice if that 
ships with the code itself in a doc that you can build into a pdf. Maybe there 
is a way of using the same text for both. Part 4 is git wiki only, no 
contributing without git anyway.

#### things to later on add to a README
* \*\_CodeManager classes
    * you need to call the baseclass init with the language name as argument (-> 
      that sets the correct self.TEMPLATES_ABS_PATH)
    * command implementation functions in \*\_Code_Manager classes
        * the functions need to have the exact name "_command_<command>"
        * the functions need to comply with the signature (self, specifier, \*\*args)
        * (run_code_manager_command() in Code_Manager is implemented such that 
          passing all of that correctly results in executing the according function, 
          without even having to implement run_code_manager_command() in subclasses)
        * document that \*\*args will always contain the 'target' field (if 
          a target was passed); also, document any other generally applicable 
          fields in the arguments
* new language-specific code managers
    * again, a "how-to-do-it": Implement the code manager module, define the 
      valid language specifiers in the top-level script, make sure the names of 
      the specifiers and of your module align correctly - then just let the 
      top-level `run_code_manager_command` take care of selecting the correct 
      language-specific code manager
* point out which variables you should not edit from within the vivado project, 
  but via the mcm api, because otherwise it messes with variable handling (like 
  top module, part, board_part). Basically for everything that is in 
  project_config.json, this file is supposed to be the root of information.
* naming convention for (third-party) testbenches: tb\_<simulator>\_<sim_top>.sv
  (for example, for verilator: tb_vl_...)
* naming convention for xip definition scripts: xips\_\*.tcl (yes, although are 
  already in a specific IP directory)
* hw build: make it clear that `make build` incorporates handling all xilinx ip, 
  including the vio ctrl core. If you want to run the build from the gui (and if 
  you are using xips at all), you need to first make sure that xips are set up 
  via the make target (or an according vivado-loaded tcl function). Then run 
  synth/impl in whatever way you want from the gui
* command function signatures: for optional arguments, default value 
  convention/requirements
    * If there is no semantic meaning in a default value, then just go for None 
      -> works as well to make an argparse argument optional. The usecase would 
      be if a command (like 'config' in hdl) can handle multiple options, but 
      doesn't necessarily have to do all of those
    * Only if there is a semantic meaning, do True/False or whatever else 
      suitable. The usecase is more of a parameter that you need to decide about 
      the flow, but where a default value makes sense.
    * Pay attention that the argument command (store, store_* etc) depends on 
      the type of default argument that you specify
