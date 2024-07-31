
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
    #     * for ["codemanagers"][codemanager]["templates"], this has to be the 
    #     direct templates location (no "templates" hierarchy level is appended 
    #     to the paths)
    #     * for ["global_config"]["templates"], the codemanager name will be 
    #     appended as a hierarchy level
    # * same precedence for [...]["local_extra_repos"] - but no local repos are 
    # kept at all if none of the two is specified (per codemanager)
    # all fields are "either that or standard" - meaning that for example if 
    # ...["codemanagers"][codemanager]["templates"] is specified, then ALL 
    # templates for that specific codemanager have to be at that location. It's 
    # not that this one AND the standard location would be considered.
    # * all locations in the config file should (or rather have to) be absolute 
    # paths

    __DEFAULT_CONFIG = {
            "global_config": {
                "templates": "",
                "local_extra_repos": ""
            },
            "codemanagers": {
                "example": {
                    "use_symlinks": "",
                    "templates": "",
                    "local_extra_repos": "",
                    "implementation_path": ""
                }
            }
    }

    def __init__(self, codemanager=""):
        if 'APPDATA' in os.environ:
            self.CONFIG_PATH = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:
            self.CONFIG_PATH = os.environ['XDG_CONFIG_HOME']
        else:
            self.CONFIG_PATH = os.path.join(os.environ['HOME'], '.config')
        self.CONFIG_FILE = os.path.join(self.CONFIG_PATH, "m_code_manager", FILE_XDG_CONFIG)
        self.codemanager = codemanager
        self._load()

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

    def get(self, field, codemanager="", prefer_global=True):
        """get a value from the xdg config file, either from the global or from 
        the codemanagers section
        It does "semantic" interpretation, in that it returns the "actually 
        usable values". Example: if field=="templates" and it ends up selecting 
        the global_config templates, and codemanager or self.codemanager is 
        non-empty, the actual return value is:
        os.path.join(...["global_config"]["templates"], codemanager)
        because that is the directory that will actually hold the templates (the 
        path is not extended of course if the "templates" field already comes 
        from a codemanager-specific config field.

        decision logic (global or codemanager config) between codemanager and 
        prefer_global:
        1. prefer_global==True? global section
        2. codemanager!=""? codemanager
        3. self.codemanager
        4. return "" if none of the above yields a result
        Why? Mostly, this module will be used as a class member of CodeManager, 
        but not always. So for some functions it might come in handy to still 
        specify a specific codemanager for which to obtain a certain field.

        :prefer_global: if True, always return 'field' from the global_config 
        (only falling back to 'codemanager' if 'codemanager' is passed and 
        exists in the config)
        :codemanager: see decision logic above
        """
        self._load()
        if not codemanager:
            codemanager = self.codemanager

        if prefer_global:
            if field in self.config["global_config"]:
                if field == "templates" and codemanager:
                    return os.path.join(self.config["global_config"]["templates"], codemanager)
                else:
                    return self.config["global_config"][field]
        if codemanager:
            if field in self.config["codemanagers"][codemanager]:
                return self.config["codemanagers"][codemanager][field]
        return ""

    def set(self, field, value, codemanager="", add=False):
        """set a field, either in the global_config or in the respective 
        codemanager

        :codemanager: see McmConfig.get(), overrides self.codemanager (and 
        defaults to global config if both are empty)
        :add: if True, a non-existing codemanager is added to the config. If 
        False and codemanager not in the "codemanagers" section of the config, 
        raises a KeyError

        :raises: KeyError - either if 'field' does not exist in the default 
        config at all (meaning it is invalid), or if an unknown codemanager 
        argument is passed and add=False
        """
        self._load()
        if not codemanager:
            codemanager = self.codemanager

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
