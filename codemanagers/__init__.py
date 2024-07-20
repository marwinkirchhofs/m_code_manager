# Add this directory to the search path for imports
import sys, os
s_init_file_path = os.path.realpath(__file__)
l_templates_path = s_init_file_path.split('/')[:-1]
_TEMPLATES_ABS_PATH_ = "/".join(l_templates_path)
sys.path.append( _TEMPLATES_ABS_PATH_ )

from code_manager import CodeManager
# from cpp_code_manager import CppCodeManager
# from python_code_manager import PythonCodeManager
