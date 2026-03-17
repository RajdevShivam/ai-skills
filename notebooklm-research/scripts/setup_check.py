#!/usr/bin/env python3
"""
Setup check for notebooklm-research skill.
Verifies: notebooklm-py installed, yt-dlp installed, NotebookLM auth valid.
"""

import subprocess
import sys


def check_package(package: str) -> bool:
    try:
        __import__(package.replace("-", "_"))
        return True
    except ImportError:
        return False


def check_command(cmd: str) -> bool:
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_notebooklm_auth() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["notebooklm", "auth", "check"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "authenticated"
        return False, result.stderr.strip() or result.stdout.strip()
    except FileNotFoundError:
        return False, "notebooklm command not found — is notebooklm-py installed?"
    except subprocess.TimeoutExpired:
        return False, "auth check timed out"


def main():
    errors = []
    warnings = []

    # Check notebooklm-py
    if not check_command("notebooklm"):
        errors.append(
            "notebooklm-py not installed. Fix: pip install notebooklm-py"
        )
    else:
        print("✓ notebooklm-py installed")

    # Check yt-dlp
    if not check_command("yt-dlp"):
        errors.append("yt-dlp not installed. Fix: pip install yt-dlp")
    else:
        print("✓ yt-dlp installed")

    # If core tools missing, stop here
    if errors:
        print("\n❌ Setup incomplete:")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)

    # Check NotebookLM auth
    auth_ok, auth_msg = check_notebooklm_auth()
    if auth_ok:
        print("✓ NotebookLM auth valid")
    else:
        print(f"\n❌ NotebookLM auth failed: {auth_msg}")
        print("  Fix: run `notebooklm login` and complete browser authentication")
        sys.exit(1)

    print("\n✅ All checks passed. Ready to run notebooklm-research.")


if __name__ == "__main__":
    main()
