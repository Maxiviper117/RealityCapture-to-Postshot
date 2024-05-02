import sys
import os
# when developing, prefer local kapture to the one installed on the system
CWD_PATH = os.getcwd()
# check the presence of kapture directory in cwd to be sure its not the installed version
if os.path.isdir(os.path.join(CWD_PATH, 'kapture')):
    # workaround for sibling import
    sys.path.insert(0, CWD_PATH)