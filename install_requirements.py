import sys
import subprocess
import env

subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", f"{env.base_path}/requirements.txt"])
