
import os
import subprocess
import json

ABS_PATH_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_GIT_UTIL = os.path.join(ABS_PATH_FILE_DIR, "git_util.bash")

FILE_MCM_VERSION_CONFIG = "mcm_version_config.json"


class GitUtil(object):

    """Utility for handling git repo tasks within m_code_manager. Not sure if an 
    object would have been necessary, but I feel it might come in handy at some 
    point.
    Still, 95% of what the class effectively does is providing an interface to 
    the bash git util bash scripting.
    """

    def __init__(self):
        pass

    def _run_git_action(self, command, args):
        """Call a specified action on FILE_GIT_UTIL
        :returns: TODO
        """
        # subprocess.check_output used over os.system to retrieve stdout, 
        # instead of only the exit code. text=True activates encoding for all 
        # streams, otherwise input and output is in bytes. strip removes 
        # trailing newline that `echo` adds in bash
        return subprocess.check_output([FILE_GIT_UTIL, command] + args, text=True).strip()

    def get_requested_repo_reference(self, submodule):
        """Query the mcm config json to determine if a specific git 
        commit/branch/tag for the given submodule is specified
        """
        # TODO: you'll need some mechanism for specifying a different remote for 
        # standard submodule repos, probably in the same config file. Either 
        # retrieve that here as well, or export that to a separate function.

        with open(FILE_MCM_VERSION_CONFIG, 'r') as f_in:
            d_mcm_version_config = json.load(f_in)
        if submodule in d_mcm_version_config:
            return d_mcm_version_config[submodule]
        else:
            return None

    def update_submodule(self, submodule):
        pass

    def test(self, args):
        return self._run_git_action("test", args)
