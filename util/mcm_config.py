
import os
import json

FILE_XDG_CONFIG = "config.json"


class McmConfig(object):
    """interface to the XDG m_code_manager config file
    """

    # things to go into the system-wide config file
    # * whether to copy or symlink external files (maybe per codemanager type)?
    # * additional template repos (because you don't specify those per project) 
    # - also per codemanager
    # * path for local fallback clones of remote repos - not per codemanager
    # * path for templates - again per codemanager (where not specified, falls 
    # back to standard location?)
    # * whether or not to keep local fallback clones of remote repos? - per 
    # codemanager - speaking of local copies: make sure that you don't 
    # compromise repo portability, stuff still has to point to the remotes such 
    # that you can clone the repo on a different machine.
    #
    # (design choice: system-wide ssh does not happen. It doesn't hurt 
    # contributors to do that per project, you can easily switch that, and 
    # systemwide I'll turn off at some point anyway if it happens too often that 
    # I just want a quick project)
    # 
    # .config/m_code_manager/config.json
    # {
    #     "global_config": {
    #         "templates": <path>,
    #         "local_extra_repos": <path>
    #     },
    #     "codemanagers": {
    #         <codemanager>: {
    #             "use_symlinks": <bool>,
    #             "templates" : <path>,
    #             "local_extra_repos": <path>,
    #
    #         }
    #     }
    # }
    # 
    # * for any field: empty string is the same as not specified
    # * ["codemanagers"][codemanager]["templates"] overrides ["global_config"]
    # ["templates"] -> if none is specified (for a given codemanager),
    # `/usr/local/share/m_code_manager/templates`
    # * same precedence for [...]["local_extra_repos"] - but no local repos are 
    # kept at all if none of the two is specified (per codemanager)

    __DEFAULT_CONFIG = {
            "global_config": {
                "templates": "",
                "local_extra_repos": ""
            },
            "codemanagers": {
                "example": {
                    "use_symlinks": "",
                    "templates": "",
                    "local_extra_repos": ""
                }
            }
    }

    def __init__(self):
        if 'APPDATA' in os.environ:
            self.CONFIG_PATH = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:
            self.CONFIG_PATH = os.environ['XDG_CONFIG_HOME']
        else:
            self.CONFIG_PATH = os.path.join(os.environ['HOME'], '.config')
        self.CONFIG_FILE = os.path.join(self.CONFIG_PATH, FILE_XDG_CONFIG)

    # redirect 'in' to codemanagers, because that is the dynamic part of the 
    # config file
    def __contains__(self, key):
        self._load()
        return key in self.config["codemanagers"]

    def _load(self):
        if os.path.isfile(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f_in:
                self.config = json.load(f_in)
        else:
            self.config = {}

    def _write(self):
        with open(self.CONFIG_FILE, 'w') as f_out:
            json.dump(self.config, f_out, indent=4)

    def get(self, field, codemanager, prefer_global=True):
        """get a value from the xdg config file, either from the global or from 
        the codemanagers section

        :prefer_global: if True, always return 'field' from the global_config 
        (only falling back to 'codemanager' if 'codemanager' is passed and 
        exists in the config)
        :codemanager: if passed, get 'field' for this codemanager. Otherwise, 
        get 'field' from the global section (unless prefer_global==True)
        """
        self._load()
        if prefer_global or not codemanager:
            if field in self.config["global_config"]:
                return field
        if codemanager:
            if field in self.config["codemanagers"][codemanager]:
                return self.config["codemanagers"][codemanager]
        return ""

    def set(self, field, value, codemanager, add=False):
        """set a field, either in the global_config or in the respective 
        codemanager

        :codemanager: a codemanager that
        :add: if True, a non-existing codemanager is added to the config. If 
        False and codemanager not in the "codemanagers" section of the config, 
        raises a KeyError

        :raises: KeyError - either if 'field' does not exist in the default 
        config at all (meaning it is invalid), or if an unknown codemanager 
        argument is passed and add=False
        """
        self._load()
        if codemanager:
            if codemanager not in self.config["codemanagers"]:
                if not add:
                    raise KeyError(
f"""Codemanager {codemanager} is unknown to the m_code_manager config file and 
will not be added. You may add it manually""")
                else:
                    self.config["codemanagers"].update(
                            {codemanager: {
                                field: value
                            }})
            else:
                self.config["codemanagers"][codemanager][field] = value
        else:
            if field in self.__DEFAULT_CONFIG["global_config"]:
                self.config["global_config"][field] = value
            else:
                raise KeyError(f"Field {field} is an invalid global_config field")
        self._write()

    def write_default_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            self._write()
        else:
            print(f"Config file {self.CONFIG_FILE} already exists. Not overwriting...")
