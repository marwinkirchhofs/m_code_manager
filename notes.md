
#### things to later on add to a README
* command implementation functions in \*\_Code_Manager classes
    * the functions need to have the exact name "_command_<command>"
    * the functions need to comply with the signature (self, specifier, \*\*args)
    * (run_code_manager_command() in Code_Manager is implemented such that 
      passing all of that correctly results in executing the according function, 
      without even having to implement run_code_manager_command() in subclasses)
* new language-specific code managers
    * again, a "how-to-do-it": Implement the code manager module, define the 
      valid language specifiers in the top-level script, make sure the names of 
      the specifiers and of your module align correctly - then just let the 
      top-level `run_code_manager_command` take care of selecting the correct 
      language-specific code manager