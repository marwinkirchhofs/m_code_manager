
import os
import subprocess
import json

ABS_PATH_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_GIT_UTIL = os.path.join(ABS_PATH_FILE_DIR, "git_util.bash")

FILE_MCM_VERSION_CONFIG = "mcm_version_config.json"
GIT_REPO_PREFIX_HTTP = "https://github.com/marwinkirchhofs/m_code_manager"
GIT_REPO_PREFIX_SSH = "git@github.com:marwinkirchhofs/m_code_manager"

# structure MCM_VERSION_CONFIG
# {
#     use_ssh: <True/False>,
#     <module>: {
#         reference: <reference>,
#         remote: <remote>
#     }
# }
# all fields are optional, methods will fallback if a certain module or 
# sub-field is not present


class GitUtil(object):
    """Utility for handling git repo tasks within m_code_manager. Not sure if an 
    object would have been necessary, but I feel it might come in handy at some 
    point.
    Still, 95% of what the class effectively does is providing an interface to 
    the bash git util bash scripting.
    """

    # todo list
    # * overwrite (and check) the remote of an existing subrepo, in case a user 
    # switches to a fork or between ssh and https (bash function:
    # `git -C <submodule> remote get-url/set-url origin`
    # -> check the url, if it's not what it is supposed to be, change it and 
    # then I guess run an update
    # * python equivalents to bash functions:
    #     * check repo (scripts) againts codemanager commit
    # * handle a list of submodules: per submodule, pull if it is not there, 
    # maybe update it if it is there, and most importantly: move or symlink any 
    # content of the subrepo that belongs somewhere else (and think about if you 
    # want to do that in bash or in python)

    BASH_API = {
            "update_submodule": "update_submodule",
    }


    # Why pass lang? The idea is that methods like update_submodule should not 
    # need the codemanager as an argument, because when calling it, the 
    # codemanager is effectively known. One way for that is to have CodeManager 
    # objects owning a GitUtil object. CodeManager objects already get the lang, 
    # so it is no extra effort to pass it to the GitUtil object at generation 
    # time.
    def __init__(self, lang="generic"):
        self.lang = lang

    def _run_git_action(self, command, args):
        """Call a specified action on FILE_GIT_UTIL
        :returns: TODO
        """
        # subprocess.check_output used over os.system to retrieve stdout, 
        # instead of only the exit code. text=True activates encoding for all 
        # streams, otherwise input and output is in bytes. strip removes 
        # trailing newline that `echo` adds in bash
        # TODO: I don't know if you want to explicitly add 'bash' to the args, 
        # or if that's exactly what you don't want to do in terms of operating 
        # system compatibility. But also let's be honest, on Linux systems the 
        # worst thing that can happen from adding it is no difference to not 
        # adding it, and this whole thing practically is already 
        # Linux-targetting (unix best case)
        return subprocess.check_output(["bash", FILE_GIT_UTIL, command] + args, text=True).strip()

    # return the url of the remote repo for the given submodule
    # * does differentiate between http url (for standard use -> just clone) and 
    # ssh url (for development -> basically for me)
    # * if a non-empty "remote" is specified in the mcm version config file, 
    # this url is always used and overwrites every other option
    # 
    # note that use_ssh=False can't overwrite config_use_ssh (and vice versa, 
    # it's an or, not an and)
    def get_remote_repo(self, submodule, use_ssh=False):
        with open(FILE_MCM_VERSION_CONFIG, 'r') as f_in:
            d_mcm_version_config = json.load(f_in)

        if (submodule in d_mcm_version_config) and ("remote" in d_mcm_version_config[submodule]):
            if d_mcm_version_config[submodule]["remote"]:
                return d_mcm_version_config[submodule]["remote"]

        if "use_ssh" in d_mcm_version_config:
            # conservative approach: only an exact True match activates ssh, 
            # everything else is a False
            # ("true" is what python json spits out for a True bool)
            config_use_ssh = d_mcm_version_config["use_ssh"] == "true"
        
        if use_ssh or config_use_ssh:
            git_repo_prefix = GIT_REPO_PREFIX_SSH
        else:
            git_repo_prefix = GIT_REPO_PREFIX_HTTP
        return "-".join([git_repo_prefix, submodule, self.lang]) + ".git"

    def get_requested_repo_reference(self, submodule):
        """Query the mcm config json to determine if a specific git 
        commit/branch/tag for the given submodule is specified
        """
        # TODO: you'll need some mechanism for specifying a different remote for 
        # standard submodule repos, probably in the same config file. Either 
        # retrieve that here as well, or export that to a separate function.

        with open(FILE_MCM_VERSION_CONFIG, 'r') as f_in:
            d_mcm_version_config = json.load(f_in)

        if      submodule in d_mcm_version_config and \
                "reference" in d_mcm_version_config[submodule]:
            return d_mcm_version_config[submodule]["reference"]
        else:
            return None

    # update (or pull) the submodule according to FILE_MCM_VERSION_CONFIG
    # if a reference is specified for the submodule, pull that reference, 
    # regardless of what the current project repo is pointing to.
    # If the submodule is already initialized (thus a remote is already set up), 
    # the remote will not be overwritten.
    # TODO: we need a way to overwrite the remote, in case for example a user 
    # switches to a fork
    #
    # ssh is possibly set by an xdg config file which is read at program start 
    # (and a hidden option, because nobody except for developers needs to know 
    # about it)
    #
    # :reset: if set, resets to the status currently pointed to in the project's 
    # .gitmodules - ignores any config other config
    def update_submodule(self, submodule, path="", ssh=False, reset=False):
        
        # you have to pay attention that none of the args you pass to 
        # _run_git_action is empty (except for possibly reference), because bash 
        # doesn't recognize empty strings as arguments, but instead just drops 
        # them.  Thus everything else would shift and the argument numbers would 
        # be incorrect.
        if not path:
            path = submodule
        remote = self.get_remote_repo(submodule, ssh)
        reference = self.get_requested_repo_reference(submodule)
    
        if reset:
            self._run_git_action(command=self.BASH_API["reset_submodule"],
                                args=[path, "overwrite"])
        else:
            self._run_git_action(command=self.BASH_API["update_submodule"],
                                args=[submodule, path, remote, reference])

    def test(self):
        args = ["here", "", "there"]
        print(self._run_git_action("test", args))

if __name__ == "__main__":
    gu = GitUtil()
    gu.test()
