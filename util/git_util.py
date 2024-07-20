
import os

ABS_PATH_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_GIT_UTIL = os.path.join(ABS_PATH_FILE_DIR, "git_util.bash")


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
        os.system(f"{FILE_GIT_UTIL} {command} {args}")
        pass

    def get_requested_repo_reference(submodule):
        """Query the mcm config json to determine if a specific git 
        commit/branch/tag for the given submodule is specified
        """
        # TODO
        pass
