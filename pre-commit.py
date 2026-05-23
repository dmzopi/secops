#!/usr/bin/env python3
"""Helper script to be used as a pre-commit hook.
   Installs, enables, applies gilleaks for sensitive data lookup in codebase.
   Rejects commit if such data was found.
"""

import os
import sys
import subprocess
import sys
import json
from pathlib import Path
import platform
import tarfile
import zipfile

def gitleaksEnabled():
    """Determine if the pre-commit hook for gitleaks is enabled."""
    out = subprocess.getoutput("git config --bool hooks.gitleaks")
    if out == "false" or out == "":
        return False
    return True

def gitleaksInstall():
    # win32 | darwin | linux
    plat = sys.platform
    if plat in ["darwin","linux"]:
        arch = os.uname().machine
        binary_name = "gitleaks"
    elif plat in ["win32"]:
        plat = "windows"
        arch = platform.machine().lower()
        binary_name = "binary_name.exe"
    else:
        print(f"Platfrom {plat} not supported")
        sys.exit(0)
    if arch in ("x86_64", "amd64"):
        arch = "x64"
    if arch in ("aarch64", "arm64"):
        arch = "arm64"
    if arch in ("x86", "i386", "i686"):
        arch = "x32"
    print(f"Installing gitleaks for: {plat}-{arch}")
    # Fetch url avoiding import requests
    # https://api.github.com/repos/gitleaks/gitleaks/releases/latest
    # https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_darwin_arm64.tar.gz
    # https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_windows_x64.zip
    cmd = ["curl", "-s", "https://api.github.com/repos/gitleaks/gitleaks/releases/latest"]
    data = json.loads(subprocess.check_output(cmd))
    for asset in data["assets"]:
        if plat in asset["name"] and arch in asset["name"]:
            break
    #print(asset)
    url = asset["browser_download_url"]
    print(f"Fetching release {url}")
    file_name = asset["name"]
    binary_path = Path.home() / ".local" / "bin" / binary_name
    subprocess.check_call(["curl", "-L", url, "-o", file_name])
    if os == "windows":
        with zipfile.ZipFile(file_name, "r") as z:
            for name in z.namelist():
                if name.endswith(binary_name):
                    with z.open(name) as f:
                        binary_path.write_bytes(f.read())
                    break
    else:
        with tarfile.open(file_name, "r:gz") as t:
            for m in t.getmembers():
                if m.name.endswith("gitleaks") and m.isfile():
                    f = t.extractfile(m)
                    binary_path.write_bytes(f.read())
                    os.chmod(binary_path, 0o755)
                    break
    Path(file_name).unlink(missing_ok=True)

                

# Execution
print("pre-commit hook running")
if gitleaksEnabled():
    gitleaks_path = Path.home() / ".local" / "bin" / (
        "gitleaks.exe" if os == "windows" else "gitleaks"
    )
    try:
        # ✅ check if installed
        result = subprocess.run(
            [str(gitleaks_path), "version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Gitleaks installed version:", result.stdout.strip())

    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Gitleaks not found. Installing...")
        gitleaksInstall()

    # ✅ ALWAYS run scan
    result = subprocess.run(
        [str(gitleaks_path), "detect", "--redact", "-v"]
    )

    exitCode = result.returncode

    if exitCode == 1:
        RED = "\033[31m"
        RESET = "\033[0m"

        print(f"""{RED}
Warning: COMMIT REJECTED
Gitleaks has detected sensitive information in your changes.

Disable with:
git config hooks.gitleaks false
{RESET}""")

        sys.exit(1)
        RED = "\033[31m"
        RESET = "\033[0m"
        print(f"""Warning: {RED} COMMIT REJECTED {RESET} Gitleaks has detected sensitive information in your changes.\n 
            To disable the gitleaks precommit hook run the following command:\n
            git config hooks.gitleaks false""")
        sys.exit(1)
else:
    print('gitleaks precommit disabled\
     (enable with `git config hooks.gitleaks true`)')

