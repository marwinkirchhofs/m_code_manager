
Example: HDL
* 'scripts' a git subrepo -> needs to not be templated
* how to deal with things like makefiles?
  Some things are part of the scripting environment, but they need to be 
  templates. Keep the amount of templates as small as possible, like the 
  `var.make` and that's it.
    * Problem with makefiles: they have to be in their specific directory, but 
      they should be part of the scripts subdirectory because repo.
        * Possible solution: after fetching the subrepo, symlink the makefiles.  
          Don't copy, because then you can't push changes back to the repo. Also, 
          in the repo, give the makefiles a non-makefile name to prevent them 
          from execution in that directory.
          TODO: does symlinking persist across git push/clone?
        
* how to do version management between main tool and scripts?
    * should differentiate between 'stable' and 'experimental' version of 
      scripts -> use a config to check local against a certain git branch
    * what if m_code_manager got updated?
        * one possibility: whenever you run mcm, it checks for the present 
          subrepos. If the subrepos are older than the current mcm version, it 
          queries you to update them.
          Downside with that: There's a good chance that a part of mcm got 
          updated that doesn't belong to the current type of project (update to 
          c++ part while you're working in hdl).
            * Solution: every codemanager would need its own subrepo...
* how to do project portability? Basically a project needs to hold the exact 
  commit of the scripts repo that it was on. If the scripts got updated, the 
  project might otherwise break if you clone it and it fetches the scripts 
  subrepo from the newest commit

# Ideas

* allow the user to point to their own codemanager/template/asset repos in an 
  mcm config file -> those then will be treated just like my "official" 
  language-specific repos


# Git Structure Proposals

## "Excessive"

would consist of the following repos:
* m_code_manager
* one repo per codemanager
* one subrepo 'templates' per codemanager
* one subrepo 'scripts' (or maybe 'assets', because makefiles would also be in 
  there I think) per codemanager
    * actually, on that note, does it work to symlink a makefile and does that 
      persist across git repos (if the path is relative, not absolute)? Because 
      in that case you could immediately push back changes to the makefiles, 
      instead of copying the makefiles. Maybe make that an option in mcm, with 
      the standard being that the makefile is just copied, because that is what 
      you would want for standard project flow. Symlink in a git repo just feels 
      like it asks for breaking at some point.

## "Less Excessive"

everything like "Excessive", except that 'templates' are integrated into the 
respective codemanager repo

# Example - HDL

| file | type | comment |
| --- | --- | --- |
| makefile                          | asset* | copy/symlink |
| sim/makefile                      | asset* | copy/symlink |
| project_config                    | asset* | see below|
| var.make                          | asset* | copy/symlink |
| scripts/create_sim_scripts.bash   | asset | |
| scripts/generate_xips.tcl         | asset | |
| scripts/vio_ctrl.tcl              | asset* | see below |
| scripts/read_sources.tcl          | asset | |
| scripts/source_helper_scripts.tcl | asset | |
| scripts/manage_project.tcl        | asset | |
| scripts/get_json_variable.py      | asset | |
| scripts/manage_build_files.bash   | asset | |
| scripts/build_hw.tcl              | asset | |
| scripts/create_project.tcl        | asset | |
| rtl/top                           | template | |
| tb/axi                            | axi_simlib | see below |
| tb/{util_pkg,ifc_rst}             | util_simlib or template | |
| tb/{tb_,ifc_,agent_}              | template* | see below |

a general remark on assets: they do rely on the names for the project 
directories being consistent. So either you REALLY enforce those names, or you 
do good version control to make sure that codemanager and assets expect the same 
    directory names (or create them respectively), or you need a central place 
    that holds the directory names and which is managed by the codemanager.
* could a central directory naming config also be part of the project_config, 
  but then of a sort of "system"-section? I don't really like that idea because 
  the user is supposed to interact with that file constantly. A solution could 
  be a second top level json config file, something like 
  "project_constants.json"
    * in that case, make.var should also draw from that second json config file 
      for consistency

* scripts/vio_ctrl.tcl: Most of it is an asset/framework, but a part is supposed 
  to be user-edited - Idea: Split it up into two files. The asset part stays 
  constant, and then a user file with an example in the same way as the 
  xips_user.tcl scripts, which then needs to source the vio framework script.  
  Think about where you would place that user file. I would like to implement 
  the 'scripts' directory as a "user don't touch" directory (also for gitignore 
  reasons!!).  But then the user vio ctrl file needs to go somewhere else, maybe 
  something like a 'user_scripts' directory?
    * And then, secondly, how to get the user script example there?
        * for the sake of repo consistency, seems better to keep it in the 
          scripts repo, instead of going templates directory. Also with 
          makefiles, we'll have that problem of files being in the assets repo 
          which eventually need to be somewhere else
        * how to deal with overwriting in case the scripts are updated in an 
          existing project? I would say silently don't overwrite an existing 
          user vio ctrl script, and implement an explicit mcm command that can 
          bring you back the example file
* project_config: in fact, it could be generated by the codemanager. However, if 
  you add a field, that normally is in conjunction with the assets, not with the 
  codemanager. Therefore the standard project_config should count as an asset 
  (and be a default-valued json file). Then when downloading copy it into the 
  correct place just like the makefiles - or maybe, especially in the case here, 
  update an existing json config
* interaction module tb and util_simlib: The module templates are definitely 
  templates, while the util_simlib has the character of an asset. Problem: The 
  templates use the util_simlib for reset. So you at least have to ensure 
  version consistency. The alternative would be to treat the util_simlib as 
  a template, although it practically is not. But it basically solve all 
  problems before they occur, so currently I'm gravitating into that direction.  
  Little downside would be though that you can not just update it (e.g. a hotfix 
  somewhere) and then fetch and you're good. So maybe long run a separate repo 
  with version dependency management causes overhead to implement, but is 
  better.

think about supporting more subrepos, motivation: The axi simulation framework 
is clearly an asset, it doesn't depend on anything and is not a template.  
However, in terms of code dependency management it doesn't really make sense to 
put it into the same repo as the script assets, because they have nothing to do 
with each other. Also, how would you do that with directories? Scripts works 
nicely, you just clone the subdirectory into your project. With the axi 
framework, you can do the same in the tb directory if the axi package is its own 
repo. I guess, it's decided...
-> Create an implementation that is not hard-coded to only an 'assets' subrepo, 
but that gives a convenient way for including other subrepos. Question: How do 
you do dependency management (and things like notifying about new versions)?  
There might be dependencies between codemanager, templates and assets. But it 
might very well not be the case for e.g. the axi traffic gen. Guess the way to 
go is: For the first iteration, don't do any version dependency management for 
any non-standard subrepo. Either it becomes too much of a problem at some point, 
or it doesn't. But I mean, you can leave some power to the user.
