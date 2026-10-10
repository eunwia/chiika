"""
create_desktop_shortcut.py - Creates a Windows Desktop shortcut with Chiikawa app icon.
"""

import os
import subprocess
import sys

def create_shortcut():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    app_py = os.path.join(project_dir, "app.py")
    icon_path = os.path.join(project_dir, "app_icon.ico")
    shortcut_path = os.path.join(desktop, "Chiikawa Study Planner.lnk")

    # Find pythonw.exe (windowed Python, no console window!)
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    # PowerShell script to create the .lnk file
    ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{pythonw}'
$Shortcut.Arguments = '"{app_py}"'
$Shortcut.WorkingDirectory = '{project_dir}'
$Shortcut.IconLocation = '{icon_path}, 0'
$Shortcut.Description = 'Chiikawa Study Planner'
$Shortcut.Save()
"""
    ps_file = os.path.join(project_dir, "_make_shortcut.ps1")
    with open(ps_file, "w", encoding="utf-8") as f:
        f.write(ps_script)

    try:
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], check=True)
        print(f"[OK] Desktop shortcut created at: {shortcut_path}")
    finally:
        if os.path.exists(ps_file):
            os.remove(ps_file)

if __name__ == "__main__":
    create_shortcut()
