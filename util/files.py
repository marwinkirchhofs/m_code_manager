
# collection of functions to handle any sort of file manipulations, including 
# file creation, checking if file can be overwritten and everything else that 
# just needs a little more than a call to `os.path.<whatever>`

import os
import shutil


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
