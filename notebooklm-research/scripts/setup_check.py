#!/usr/bin/env python3
"""
Setup check for notebooklm-research skill.
Verifies: notebooklm-py installed, yt-dlp installed, NotebookLM auth valid.
"""

import os
import subprocess
import sys


def check_package(package: str) -> bool:
    try:
        __import__(package.replace("-", "_"))
        return True
    except ImportError:
        return False


def check_python_module(module: str) -> bool:
    """Check if a Python module is importable."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def check_notebooklm_auth() -> tuple[bool, str]:
    """Check auth by inspecting the storage file directly.
    Avoids notebooklm auth check command which crashes on Windows due to Unicode rendering."""
    import json
    storage_path = os.path.expanduser("~/.notebooklm/storage_state.json")
    if not os.path.exists(storage_path):
        return False, "No storage_state.json found. Run: python -m notebooklm login"
    try:
        with open(storage_path) as f:
            data = json.load(f)
        cookies = data.get("cookies", [])
        key_names = {c["name"] for c in cookies}
        required = {"SID", "SAPISID"}
        missing = required - key_names
        if missing:
            return False, f"Auth cookies missing: {missing}. Re-run: python -m notebooklm login"
        return True, f"authenticated ({len(cookies)} cookies)"
    except Exception as e:
        return False, f"Could not read storage file: {e}"


def main():
    errors = []

    # Check notebooklm-py (importable as 'notebooklm')
    if not check_python_module("notebooklm"):
        errors.append("notebooklm-py not installed. Fix: pip install notebooklm-py")
    else:
        print("[OK] notebooklm-py installed")

    # Check yt-dlp (importable as 'yt_dlp')
    if not check_python_module("yt_dlp"):
        errors.append("yt-dlp not installed. Fix: pip install yt-dlp")
    else:
        print("[OK] yt-dlp installed")

    # If core tools missing, stop here
    if errors:
        print("\n[FAIL] Setup incomplete:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Check NotebookLM auth
    auth_ok, auth_msg = check_notebooklm_auth()
    if auth_ok:
        print("[OK] NotebookLM auth valid")
    else:
        print(f"\n[FAIL] NotebookLM auth failed: {auth_msg}")
        print("  Fix: run `python -m notebooklm login` and complete browser authentication")
        sys.exit(1)

    print("\n[OK] All checks passed. Ready to run notebooklm-research.")


if __name__ == "__main__":
    main()
