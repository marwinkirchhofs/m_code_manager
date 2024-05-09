import os
import re

pkg_dir = os.path.dirname(os.path.realpath(__file__))
pkg_name = os.path.basename(pkg_dir)
# import all python modules in the package
# filter directory for every file that ends with '.py' and that has at least one 
# alphanumeric character before the dot
for s_module_file in filter(
            lambda s: re.match(r'\w+\.py', s), os.listdir(pkg_dir)):
    # prevent self-import
    if not s_module_file == "__init__.py":
        exec(f"import {pkg_name}.{s_module_file[:-3]}")
