
# collection of functions to handle any sort of file manipulations, including 
# file creation, checking if file can be overwritten and everything else that 
# just needs a little more than a call to `os.path.<whatever>`

import os
import shutil
from pathlib import Path


def __check_existing_target(target):
    # TODO: return the target type, if it exists. Then this method returns 
    # a type, while the usually called _check_target_edit_allowed returns 
    # a simple bool
    target_type = ""
    if os.path.exists(target):
        if os.path.isdir(target):
            target_type = "directory"
        elif os.path.isfile(target):
            target_type = "file"
        elif os.path.islink(target):
            target_type = "link"
        else:
            target_type = "other"
    return target_type


def create_dir(path):
    """practically `mkdir -p path`
    :path: may or may not have a trailing path separator, no difference
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)


def create_file_path(path):
    """for the given path, creates the full directory hierarchy if it doesn't 
    exist
    :path: (relative) path of arbitrary depth with or without file name 
    (terminating '/' distinguishes between whether or not path contains a file 
    name)
    """
    path_dir = os.path.dirname(path)
    create_dir(path_dir)


def check_target_edit_allowed(target):
    """Check if the file/directory/link that is specified by target exists.  
    If it does, ask for confirmation to edit or overwrite it.
    In favour of a boolean return value, the function does not return any 
    information on the type of the target if the target is found te be 
    existing.  If you need that, instead of a general "yes, do whatever you 
    want to with this target", then revert to the manual os.path.is* 
    methods.

    Returns True if target is safe to be edited (meaning that it either 
    doesn't exist or that the user confirmed that it can be overwritten)
    """

    target_type = __check_existing_target(target)
    if target_type:
        input_overwrite = input(
f"""Target {target_type} '{target}' exists. How to proceed?
b - backup the existing target to {target}.bak, then edit/overwrite
y - edit/overwrite existing target without backup
n - don't edit/overwrite the target\n""")
        if input_overwrite == 'b':
            target_backup = target + ".bak"
            if os.path.exists(target_backup):
                input_write_backup = input(
f"""Target backup {target_backup} already exists.
y - overwrite
n - don't overwrite, aborts writing {target} entirely""")
            else:
                input_write_backup = 'y'
            if input_write_backup == 'y':
                if target_type == "directory":
                    shutil.copytree(target, target_backup,
                                    symlinks=True, ignore_dangling_symlinks=True,
                                    dirs_exist_ok=True)
                else:
                    # TODO: this might fail if the target is a symlink, 
                    # instead of a file. First step was only to separate 
                    # files and directories
                    shutil.copy(target, target_backup)
                print(f"{target} backed up")
                return True
            else:
                print(f"Existing backup left untouched. {target} won't be edited...")
                return False
        if input_overwrite == 'y':
            return True
        else:
            print("The target won't be edited")
            return False
    else:
        return True


def get_num_hierarchy_levels(path: str, strip_filename=True) -> int:
    """gets the (actual) number of hierarchy steps(!) in a path - meaning it 
    doesn't differ between directory up and down, both just count as one step 
    (look into EXAMPLES).
    internally uses pathlib, which removes any "meaningless" parts from the path 
    (like './')

    :path: a path string
    :strip_filename: don't count the last part of the path (which is considered 
    a file name). Only set this option to False if path is a directory.

    EXAMPLES:
    | path                              | strip_filename==True  | strip_filename==False
    | ---                               | ---                   |
    | "./here/there/./file.xml.bak"     | 2                     | 3
    | "here"                            | 0                     | 1
    | "here/"                           | 0                     | 1
    | "/here"                           | 1                     | 2
    | "./here"                          | 0                     | 1
    | "../here/there/./file.xml.bak"    | 3(!)                  | 4(!)
    """
    path_obj = Path(path)
    if strip_filename:
        return len(path_obj.parts) - 1
    else:
        return len(path_obj.parts)
