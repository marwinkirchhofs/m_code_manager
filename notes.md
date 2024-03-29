
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
