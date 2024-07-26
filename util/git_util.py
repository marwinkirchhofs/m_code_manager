
import os
import subprocess
import json
import shutil

ABS_PATH_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
FILE_GIT_UTIL = os.path.join(ABS_PATH_FILE_DIR, "git_util.bash")
FILE_NAME_SUBMODULE_EXT_FILES = "destinations.json"

FILE_MCM_SUBMODULE_CONFIG = "submodules.json"
GIT_REPO_PREFIX_HTTP = "https://github.com/marwinkirchhofs/m_code_manager"
GIT_REPO_PREFIX_SSH = "git@github.com:marwinkirchhofs/m_code_manager"

# match the constants in git_util.bash
REPO_OLDER          = "old"
REPO_UP_TO_DATE     = "up-to-date"

# structure MCM_VERSION_CONFIG
# {
#     use_ssh: <True/False>,
#     <module>: {
#         reference: <reference>,
#         remote: <remote>,
#         path: <path>
#     }
# }
# all fields are optional, methods will fallback if a certain module or 
# sub-field is not present
# design decision to not separate the file into user-added repos and mcm-added 
# repos. Sometimes you just have to trust people that they won't ruin absolutely 
# everything they could. There is a command to add all mcm-caused subrepos to 
# the file, with the standard reference, if they're not there already. That's 
# got to be enough for when you messed up and don't manage to restore it with 
# git.

# TODO: if you want this to be somewhat clean and readable, you have to do 
# everything with SubmoduleConfig objects. AND the big deal is: SubmoduleConfig 
# should mirror the mcm version config entries. And the class should be what 
# provides the API to the mcm version config file. Yes, that's extra effort. But 
# it would be logical and maintainable, so let's do it.


class Submodule(object):
    """hold some elementary information on git submodules, just to pass multiple 
    of them around in a more convenient way
    """

    def __init__(self, name, reference="", path="", remote=""):
        self.name = name
        self.path = path
        self.reference = reference
        self.remote = remote

    def __dict__(self):
        d = {
            self.name: {
                "reference": self.reference,
                "remote": self.remote,
                "path": self.path,
            }
        }
        return d

    @classmethod
    def from_dict(cls, name, d_config):

        if "reference" in d_config:
            reference = d_config["reference"]
        else:
            reference = ""
        if "path" in d_config:
            path = d_config["path"]
        else:
            path = ""
        if "remote" in d_config:
            remote = d_config["remote"]
        else:
            remote = ""

        obj = cls(name, reference, path, remote)

        return obj


class SubmoduleConfig(object):
    """API to FILE_MCM_SUBMODULE_CONFIG
    The idea is to channel as much as possible through Submodule objects. The 
    translation between dict, json, and Submodule is handled by this class and 
    by the Submodule class.
    """

    def __init__(self, config={}):
        self.config = config

    def __contains__(self, key):
        self._load()
        if isinstance(key, Submodule):
            return key.name in self.config
        else:
            return key in self.config

    def _load(self):
        if os.path.isfile(FILE_MCM_SUBMODULE_CONFIG):
            with open(FILE_MCM_SUBMODULE_CONFIG, 'r') as f_in:
                d_submodules = json.load(f_in)
            self.config = d_submodules
        else:
            self.config = {}

    def _write(self):
        with open(FILE_MCM_SUBMODULE_CONFIG, 'w') as f_out:
            json.dump(self.config, f_out, indent=4)

    def add(self, submodule: Submodule, overwrite=False):
        """Explicitly meant to add a submodule. If the submodule is already 
        present in the current config, it will only be added if overwrite==True.  
        Otherwise the function returns without doing anything.
        Note that the submodule is only added to the config. No git action is 
        performed, because it's not the responsibility of this class.
        """
        self._load()

        if submodule in self and not overwrite:
            raise KeyError(
f"""Submodule {submodule.name} already exists in the config and won't be 
overwritten.""")

        self.config.update(dict(submodule))
        self._write()

    def set(self, submodule_name, path="", reference="", remote=""):
        """Set one or multiple fields in a given submodule config. Only operates 
        on existing submodules in a config.

        raises: KeyError if the submodule is not present in the config
        """
        self._load()
        if submodule_name not in self:
            raise KeyError(
f"""Submodule {submodule_name} is not present in the submodule config""")

        if path:
            self.config[submodule_name]["path"] = path
        if reference:
            self.config[submodule_name]["reference"] = reference
        if remote:
            self.config[submodule_name]["remote"] = remote
        self._write()

    def get(self, submodule_name, field=""):
        """either get the submodule object corresponding to submodule_name, as 
        it is described in FILE_MCM_SUBMODULE_CONFIG, or get one field of that 
        submodule.
        :field: if set (aka if it evaluates to True), return that specific field 
        of the submodule object. If not, return the submodule object
        """

        self._load()
        if submodule_name not in self:
            raise KeyError(
f"""Submodule {submodule_name} is not present in the submodule config""")

        if field:
            if field in self.config[submodule_name]:
                return self.config[submodule_name][field]
            else:
                return ""
        else:
            submodule = Submodule.from_dict(submodule_name, self.config[submodule_name])
            return submodule

    def get_use_ssh(self):
        self._load()
        if "use_ssh" in self.config:
            return self.config["use_ssh"] == "true"
        else:
            return False

    def set_use_ssh(self, val):
        self._load()
        self.config["use_ssh"] = val


class GitUtil(object):
    """Utility for handling git repo tasks within m_code_manager. Not sure if an 
    object would have been necessary, but I feel it might come in handy at some 
    point.
    Still, the majority of what the class effectively does is providing an 
    interface to the bash git util bash scripting.

    As a design decision, Submodule objects are only handled within this class 
    (and its member objects), but the external class API relies on string 
    parameters.
    """

    BASH_API = {
            "update_submodule":         "update_submodule",
            "reset_submodule":          "reset_submodule",
            "check_scripts_version":    "check_scripts_version",
    }

    # Why pass lang? The idea is that methods like update_submodule should not 
    # need the codemanager as an argument, because when calling it, the 
    # codemanager is effectively known. One way for that is to have CodeManager 
    # objects owning a GitUtil object. CodeManager objects already get the lang, 
    # so it is no extra effort to pass it to the GitUtil object at generation 
    # time.
    def __init__(self, lang="generic"):
        self.lang = lang
        self.submodule_config = SubmoduleConfig()

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

    def get_remote_repo(self, submodule_name: str, use_ssh=False):
        """return the url of the remote repo for the given submodule_name
        * does differentiate between http url (for standard use -> just clone) and 
        ssh url (for development -> basically for me)
        * if a non-empty "remote" is specified in the mcm version config file, 
        it always takes precedence

        note that use_ssh=False can't overwrite use_ssh from 
        FILE_MCM_SUBMODULE_CONFIG (and vice versa, it's an or, not an and)
        """

        try:
            submodule = self.submodule_config.get(submodule_name)
        except KeyError:
            submodule = Submodule(submodule_name)

        if submodule.remote:
            return submodule.remote

        if self.submodule_config.get_use_ssh() or use_ssh:
            git_repo_prefix = GIT_REPO_PREFIX_SSH
        else:
            git_repo_prefix = GIT_REPO_PREFIX_HTTP
        return "-".join([git_repo_prefix, submodule_name, self.lang]) + ".git"

    def get_reference(self, submodule_name: str):
        """Query the mcm config json to determine if a specific git 
        commit/branch/tag for the given submodule is specified
        """
        try:
            return self.submodule_config.get(submodule_name, "reference")
        except KeyError:
            return ""

    def get_path(self, submodule_name: str):
        """Query the mcm config json to determine if a specific git 
        commit/branch/tag for the given submodule is specified
        """

        try:
            return self.submodule_config.get(submodule_name, "path")
        except KeyError:
            return ""

    def update_submodule(self, submodule_name: str, ssh=False, reset=False, add=False):
        """update (or pull) the submodule according to FILE_MCM_SUBMODULE_CONFIG
        if a reference is specified for the submodule, pull that reference, 
        regardless of what the current project repo's .gitmodules is pointing 
        to.
        The remote url will always be set according to FILE_MCM_SUBMODULE_CONFIG 
        (meaning default if not specified differently there) and the `ssh` 
        argument. The url in an existing repo will be overwritten.
        !!! If add==False, the submodule has to exist in 
        FILE_MCM_SUBMODULE_CONFIG !!! If add==True, the submodule is silently 
        added to FILE_MCM_SUBMODULE_CONFIG, and then pulled.

        :reset: if set, resets to the status currently pointed to in the 
        project's .gitmodules - ignores any config other config
        :add: add the submodule to the project if it is not specified in 
        FILE_MCMFILE_MCM_SUBMODULE_CONFIG yet. Method fails if submodule is not 
        present and `add` is False
        """

        # you have to pay attention that none of the args you pass to 
        # _run_git_action is empty (except for possibly reference), because bash 
        # doesn't recognize empty strings as arguments, but instead just drops 
        # them.  Thus everything else would shift and the argument numbers would 
        # be incorrect.

        if submodule_name not in self.submodule_config:
            if add:
                submodule = Submodule(submodule_name)
                self.add_submodule_config(submodule)
            else:
                raise KeyError(
f"""submodule {submodule_name} is not present in the project and can not be 
updated without adding it""")
        else:
            submodule = self.submodule_config.get(submodule_name)

        path = submodule.path
        if not path:
            path = submodule_name
        remote = self.get_remote_repo(submodule_name, ssh)
        # (reference can be empty because it is the last argument to the bash 
        # script)
        reference = submodule.reference

        if reset:
            self._run_git_action(command=self.BASH_API["reset_submodule"],
                                 args=[path, "overwrite"])
        else:
            self._run_git_action(command=self.BASH_API["update_submodule"],
                                 args=[submodule_name, path, remote, reference])

    def handle_submodule_external_files(self, submodule_name, symlink=False):
        """

        structure FILE_NAME_SUBMODULE_EXT_FILES
        {
            <file_name>: {
                destination: <destination>,
                [destination_name: <name>]
            },
            ...
        }
        All files need to reside in 'submodule/external_files'.
        * file_name needs to be the exact name of the file within that directory
        * destination needs to be a directory, relative from the project top-level 
        directory
        * destination_name is optional: what the file will be named in 
        destination_name. If field not given, the file just keeps its name

        The submodule needs to be present and checked out. No (git) action will 
        be performed on the submodule or FILE_MCM_SUBMODULE_CONFIG.

        :symlink: symlink external files in submodules, instead of copying 
        (files that reside in the subrepo but eventually need to be in 
        a different location in the project). Symlinking is considered the 
        'developer' option, because it immediately allows for pushing back 
        changes, but introduces the potential problem of relative symlinks 
        within the git repo
        :submodule_path: path to the submodule. It needs to be checked out and 
        ready to work with! Path can be relative, absolute is suggested as per 
        usual
        """

        path = self.get_path(submodule_name)
        if not path:
            path = submodule_name

        file_ext_files_config = os.path.join(
                path, "external_files", FILE_NAME_SUBMODULE_EXT_FILES)
        if os.path.isfile(file_ext_files_config):
            with open(file_ext_files_config, 'r') as f_in:
                config_files_ext = json.load(f_in)

            for ext_file_name, file_config in config_files_ext.items():

                path_src = os.path.join(path, "external_files", ext_file_name)

                if "destination_name" in file_config:
                    dest_name = file_config['destination_name']
                else:
                    dest_name = ext_file_name

                path_dest = os.path.join(file_config["destination"], dest_name)

                if symlink:
                    os.symlink(path_src, path_dest)
                else:
                    shutil.copy(path_src, path_dest)

    def handle_submodules(self, submodule_names: list, symlink=False, ssh=False, add=True):
        """handle a list of submodules: update (and pull if not present yet), 
        and if the module contains "external_files.json", symlink or copy all 
        files to their correct locations

        :symlink: see GitUtil.handle_submodule_external_files
        :ssh: cause all standard submodules to use ssh remotes, instead of 
        https. Honestly, at this point, I wouldn't know in which situation you 
        would use that, but we shall see.
        :add: add any submodule to the project that it is not specified yet (see 
        GitUtil.update_submodule)
        :submodules: list of str
        """
        # TODO: provide the option to skip external file handling (leaving any 
        # present stuff untouched) if the submodule is up-to-date

        for submodule_name in submodule_names:
            self.update_submodule(submodule_name, ssh=ssh, add=add)
            self.handle_submodule_external_files(submodule_name, symlink=symlink)

    def check_scripts_version(self):
        """determine if the scripts repo is older than the currently used 
        version of this (self.lang) codemanager

        returns: the echo string from the corresponding bash function, which if 
        nothing goes wrong is either git_util.REPO_OLDER or 
        git_util.REPO_UP_TO_DATE
        """
        return self._run_git_action(command=self.BASH_API["check_scripts_version"],
                                    args=[self.lang])

    def add_submodule_config(self, submodule_name, path="", reference="", remote=""):
        """
        raises: KeyError if a submodule of that name already exists in 
        FILE_MCM_SUBMODULE_CONFIG
        """
        submodule = Submodule(submodule_name, path=path, reference=reference, remote=remote)
        self.submodule_config.add(submodule)

    def test(self):
        args = ["here", "", "there"]
        print(self._run_git_action("test", args))


if __name__ == "__main__":
    gu = GitUtil()
    gu.test()
