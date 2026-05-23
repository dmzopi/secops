#!/usr/bin/env python3
"""Helper script to be used as a pre-commit hook."""
import os
import sys
import subprocess
import sys
import json
import tarfile
from pathlib import Path

def gitleaksEnabled():
    """Determine if the pre-commit hook for gitleaks is enabled."""
    out = subprocess.getoutput("git config --bool hooks.gitleaks")
    if out == "false" or out == "":
        return False
    return True

def gitleaksInstall():
    # win32 | darwin | linux
    platform = sys.platform
    # arm64 | 
    arch = os.uname().machine
    #gitleaks_relaese = 
    print(f"Installing gitleaks for: {platform}-{arch}")
    # Fetch dowload url, avoid importing requests
    # https://api.github.com/repos/gitleaks/gitleaks/releases/latest
    # https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_darwin_arm64.tar.gz
    cmd = ["curl", "-s", "https://api.github.com/repos/gitleaks/gitleaks/releases/latest"]
    data = json.loads(subprocess.check_output(cmd))
    for asset in data["assets"]:
        if platform in asset["name"] and arch in asset["name"]:
            break
    #print(asset)
    url = asset["browser_download_url"]
    print(f"Fetching release {url}")
    file_name = asset["name"]
    binary_path = Path.home() / ".local" / "bin" / "gitleaks"
    subprocess.check_call(["curl", "-L", url, "-o", file_name])
    with tarfile.open(file_name, "r:gz") as t:
        for m in t.getmembers():
            if m.name.endswith("gitleaks") and m.isfile():
                f = t.extractfile(m)
                binary_path.write_bytes(f.read())
                os.chmod(binary_path, 0o755)
                break

# Execution
print("pre-commit hook running")
if gitleaksEnabled():
    try:
        output = subprocess.check_output(["gitleaks", "version"], text=True)
        print("Gitleaks installed version:", output.strip())
    except FileNotFoundError:
        gitleaksInstall()
    exitCode = os.WEXITSTATUS(os.system('gitleaks detect --redact -v'))
    if exitCode == 1:
        RED = "\033[31m"
        RESET = "\033[0m"
        print(f"""Warning: {RED} COMMIT REJECTED {RESET} Gitleaks has detected sensitive information in your changes.\n 
            To disable the gitleaks precommit hook run the following command:\n
            git config hooks.gitleaks false""")
        sys.exit(1)
else:
    print('gitleaks precommit disabled\
     (enable with `git config hooks.gitleaks true`)')

