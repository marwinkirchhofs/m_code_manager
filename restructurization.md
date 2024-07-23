# Roadmap

## Get it to work
* [ ] Preliminary
    * [x] Be sure about how to correctly to add a subrepo to a project.
    * [ ] API for fetching specific commits or versions of a repo, and also for 
          getting the one that a repo is currently at (and its timestamp)
    * [x] check if I can do all the git repos in my git with according prefixing 
      (like 'm_code_manager/<repo>' or if I need a separate git account for that)
* [ ] Repo Creation
    * [ ] actually add functionality to mcm itself to add a codemanager, because 
          manually creating 3 git repos and the respective directories is a bit 
          finnicky
    * [x] one repo per codemanager
    * [x] per codemanager: one repo for scripts, one for templates
* [ ] Others
    * [ ] pretty sure you'll need some sort of xdg config file 
    * [ ] mechanism to get the timestamp of the commit that mcm itself is on 
    * [ ] update the auto-completion: it also needs to check for functions 
          available through GitUtil - that's safe, because every codemanager has 
          a GitUtil, so if the codemanager doesn't have the command itself, it 
          can fall through to git_util
* [ ] Repo Integration
    * [ ] figure out where the templates repos should go. /opt? Needs to be 
      somewhere where you have write permissions, or can obtain some. Would that 
      be /etc?
        * most likely that location will also be used for local mirrors of extra 
          repos (see below for sim util and sim axi)
    * [ ] mechanism to check if a certain repo is already cloned, if so if the 
      current commit is the newest one, or older than a specified 
      commit/version/branch. If it is older, query for updating
        * that mechanism needs to be fail-safe for the case that you're not 
          online
            * it would make sense if that could fall back to a local repo 
              - imagine you just want to generate a testbench, but you can't 
                because the sim util pkg is only in an online repo, that'd be 
                stupid
            * you need some way of specifying which repos to keep local mirrors 
              of, from which you can clone if you're offline (and which you 
              update every time you clone from online)
        * [ ] as we have seen, this mechanism needs an automatic fall back to 
          local mirrors, before it aborts - it also needs to update the local 
          mirror every time it actually clones from the remote repo
    * [ ] handler for arbitrarily cloning a git into a certain spot (and adding 
      it as a subrepo to the current project, including registering the commit 
      in the mcm git status file)
    * [ ] handler for scripts repo (which makes use of the "clone an arbitrary 
      git repo into a certain spot" handler)
        * [ ] download the repo
        * [ ] symlink (and later on copy) every file from the 'assets' subrepo 
          (or whatever that will be called) to the according location in the 
          project
            * which rises the question: where do you specify that destination 
              location? I feel: config file within the assets directory could be 
              a good call. Alternative would be hardcoding into mcm, but then 
              first it's hardcoded, and second you'd have messed up 
              responsibilites across different git repos (mcm is not responsible 
              for where to place files, because it might not even know which 
                  files are there)
    * [ ] project needs a sort of 'm_code_manager config file', with the main 
      purpose to specify specifc commits/versions/branches of the extra repos 
      that you want to use (the actual current commit is tracked by git itself, 
      so this would be more of a read config file for when you add something)
* [ ] Codemanagers
    * [ ] mechanism to specify, per codemanager, in a global data structure 
      which command depends on which subrepos. The repo checker is then only 
      triggered on repos that the current command actually needs. (Make it so 
      that you also give the repos globally, so something like a table/dict at 
      the beginning of the file of repos and commands. Then m_code_manager can 
      handle everything repo-related, and the actual commands can rely on the 
      repo being there in the way that the user wants it to)
    * [ ] hard-code that every project in whatever language is a git repo
    * [ ] HDL
        * [ ] command to update the extra repos (sim utils, axi
        * [ ] split up vio_ctrl.tcl, such that one of them goes into a "user 
          don't touch" scripts directory and provides the framework, and that 
          the other resides in "user_scripts"
        * [ ] make project_config an asset
            * on that note, think about if it should really fail if a field can 
              not be found, or if it is ok to silently assume that field is 
              supposed to be there and create it. It's not that the user 
              accesses the field, so unless I screwed up the programming, the 
              error source is the user removing a field, not the tool adding an 
              undesired field.

## Make it usable
* [ ] Find and implement a way for the user to make changes to a submodule

# Notes

Example: HDL
* 'scripts' a git subrepo -> needs to not be templated
* how to deal with things like makefiles?
  Some things are part of the scripting environment, but they need to be 
  templates. Keep the amount of templates as small as possible, like the 
  `var.make` and that's it.
    * Problem with makefiles: they have to be in their specific directory, but 
      they should be part of the scripts subdirectory because repo.
        * Possible solution: after fetching the subrepo, symlink the makefiles 
          (make sure the symlinks use relative paths, in order to make it work 
          across git repos). Don't copy, because then you can't push changes 
          back to the repo. Also, in the repo, give the makefiles a non-makefile 
          name to prevent them from execution in that directory.
          There should be an option to copy the makefile, instead of symlinking, 
          for everyone who's not intending to push back changes. I say: That 
          goes into a system-wide mcm config file in a later phase. Up until 
          that point, you do symlinking, once the config file is there, the 
          default behavior changes to copying
        
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
          Addition: It might be a good idea to check per functionality, because 
          if you're just instantiating a module, why would you care about the 
              subrepos at all? I mean, yeah, of course there could've been 
              a change in project structure, but not very likely, to be honest.  
              I say: At the top of every code manager, define a global data 
              structure that defines which command actually depends on the 
              script or another subrepo. Then in m_code_manager, only check for 
              subrepo versions if it is required by the command. This way the 
              code manager has control over the check, but only needs to 
              implement a minimum of additional code.
* how to do project portability? Basically a project needs to hold the exact 
  commit of the scripts repo that it was on. If the scripts got updated, the 
  project might otherwise break if you clone it and it fetches the scripts 
  subrepo from the newest commit

* for the mcm/subrepo version control file: Do you want to integrate that into 
  project_config, or make it an additional yaml/json file (probably hidden) that 
  goes into the top-level directory? I say: additional json file (you could do 
  yaml, but you're already using json, so less library dependencies).  
  Explicitly include it into tracking in the project git, even if hidden files 
  are otherwise not tracked. If user deletes it and doesn't have a copy in the 
  git, their problem.

## Altering Submodules
Problem if a user changes something in a submodule, let's say scripts: The 
changes don't persist when you push you project, because they would need to be 
pushed somewhere with the subrepo. For the time being, it is what it is. Long 
run, I think the only thing you can do is that the tool has to create their own 
fork of the submodule.

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
  regardless of the name, it will be cloned to 'scripts' in the project

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
I say: too complicated. Use hardcoded directory names and rely on inter-repo 
version control (if a directory name changed, integrate that in a changelog).

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
    * maybe it's neat for the assets/scripts to have a hidden subdirectory for 
      things that are just there because they are assets - like makefiles, 
      project_config etc. Looks cleaner
* interaction module tb and util_simlib: The module templates are definitely 
  templates, while the util_simlib has the character of an asset. Problem: The 
  templates use the util_simlib for reset. So you at least have to ensure 
  version consistency. The alternative would be to treat the util_simlib as 
  a template, although it practically is not. But it basically solve all 
  problems before they occur, so currently I'm gravitating into that direction.  
  Little downside would be though that you can not just update it (e.g. a hotfix 
  somewhere) and then fetch and you're good. So maybe long run a separate repo 
  with version dependency management causes overhead to implement, but is 
  better. I say: It is a separate repo.

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
I say: It's ok to not do dependency management with the standard subrepos.  
However, you definitely should include the git commits/versions in the hidden 
mcm version config json, and provide a command to update these subrepos to the 
newest or any other commit/version.
