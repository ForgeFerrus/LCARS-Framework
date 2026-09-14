@echo off
start /min pythonw -c "import subprocess, sys; subprocess.Popen([sys.executable, r'C:\Users\Forge\MyProject\LCARS-Framework\scripts\autocommit.py', '--watch', '15'])"
