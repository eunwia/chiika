"""
build_exe.py - Builds a standalone Windows .exe for Chiikawa Study Planner using PyInstaller.
"""

import os
import subprocess
import sys

def build():
    print("[Build] Packaging Chiikawa Study Planner into standalone Windows executable...")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--icon=app_icon.ico",
        "--name=ChiikawaStudyPlanner",
        "--add-data=static;static",
        "--add-data=app_icon.ico;.",
        "--collect-all=customtkinter",
        "app.py"
    ]
    
    subprocess.run(cmd, cwd=project_dir, check=True)
    print("\n[Build] Standalone app generated in: dist/ChiikawaStudyPlanner/ChiikawaStudyPlanner.exe")

if __name__ == "__main__":
    build()
