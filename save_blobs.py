#!/usr/bin/env python3
"""
save_blobs.py
-------------
Saves blobs to blobs/<nickname>/shsh/ using --save-path.
Understands versioned configs and skips Cryptex on iOS 15 and below.
"""

import os
import re
import subprocess
import sys

# -------------------- Helpers --------------------

def extract(contents, key):
    m = re.search(rf"\*\*{re.escape(key)}:\*\*\s*`(.*?)`", contents)
    return m.group(1) if m else None

def ios_major(version):
    try:
        return int(version.split(".")[0])
    except Exception:
        return 0

def run_tsschecker(cmd):
    print("\n=== Running tsschecker ===")
    print("Command:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print("ERROR: 'tsschecker' not found.")
        sys.exit(1)

# -------------------- Main --------------------

def main():
    print("=== SHSH Blob Saver ===\n")

    cfg_path = input(
        "Enter path to .mkdn config "
        "(e.g., blobs/iphone-xr-black/iPhone11,8-ECID-17.0.mkdn): "
    ).strip()

    if not cfg_path or not os.path.exists(cfg_path):
        print("Config file not found.")
        return

    device_folder = os.path.dirname(cfg_path)
    contents = open(cfg_path, "r").read()

    device = extract(contents, "Device ID")
    ecid = extract(contents, "ECID")
    ios_version = extract(contents, "iOS Version")
    restore_type = extract(contents, "Restore Type")
    apnonce = extract(contents, "APNonce")
    generator = extract(contents, "Generator")
    cryptex_nonce = extract(contents, "Entangled Cryptex1 Nonce")
    cryptex_seed = extract(contents, "Cryptex1 Seed")
    cellular = extract(contents, "Cellular")
    bbsnum = extract(contents, "Baseband SNUM")

    major = ios_major(ios_version)

    shsh_root = os.path.join(device_folder, "shsh")
    manifest_file = os.path.join(device_folder, "BuildManifest.plist")

    modes = ["update", "erase", "ota"] if restore_type == "all" else [restore_type]

    for mode in modes:
        outdir = os.path.join(shsh_root, f"{ios_version}-{mode}")
        os.makedirs(outdir, exist_ok=True)

        cmd = [
            "tsschecker",
            "-d", device,
            "-s",
            "-e", ecid,
            "-g", generator,
            "--apnonce", apnonce,
            "--save-path", outdir
        ]

        # Cryptex only for iOS 16+
        if major > 15:
            if cryptex_seed and cryptex_seed != "N/A":
                cmd += ["-x", cryptex_seed]
            if cryptex_nonce and cryptex_nonce != "N/A":
                cmd += ["-t", cryptex_nonce]

        if mode == "ota":
            if not os.path.exists(manifest_file):
                print("Skipping OTA: BuildManifest.plist not found in", device_folder)
                continue
            cmd += ["-m", manifest_file, "-o"]
        elif mode == "update":
            cmd += ["-i", ios_version, "-u"]
        elif mode == "erase":
            cmd += ["-i", ios_version, "-E"]

        if cellular and cellular.lower() in ("no", "false", "n"):
            cmd.append("-b")
        elif bbsnum and bbsnum != "N/A":
            cmd += ["-c", bbsnum]

        run_tsschecker(cmd)

    print("\nDone. All files are in:", device_folder)

# --------------------

if __name__ == "__main__":
    main()
