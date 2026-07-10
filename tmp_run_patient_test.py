import os
import subprocess
import sys

python = r"C:\Users\MOUANGA\sghl\.venv\Scripts\python.exe"
cmd = [python, "manage.py", "test", "accounts.tests.PatientRegistrationTests.test_inscription_patient", "--verbosity=2"]
print("CMD:", cmd)
proc = subprocess.run(cmd, capture_output=True, text=True)
print("RETURNCODE:", proc.returncode)
print("STDOUT:\n", proc.stdout)
print("STDERR:\n", proc.stderr)
