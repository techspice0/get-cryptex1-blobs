#!/usr/bin/env python3
"""
collect_blob_config.py
-----------------------
Creates or modifies SHSH blob config files.
Cryptex is requested only for iOS 16+.
Supports multiple configs named by version/build.
"""

import os
import re
import subprocess
import shutil

def ask(prompt, optional=False):
    while True:
        v = input(prompt).strip()
        if v or optional:
            return v
        print("This field cannot be empty.\n")

def yesno(prompt, default=False):
    v = input(prompt).strip().lower()
    if not v:
        return default
    return v.startswith("y")

def ios_major(version):
    try:
        return int(version.split(".")[0])
    except Exception:
        return None

def download_buildmanifest(url, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    internal = "AssetData/boot/BuildManifest.plist"
    dest = os.path.join(target_dir, "BuildManifest.plist")

    subprocess.run(["pzb", "-g", internal, url], check=True)

    if os.path.exists("BuildManifest.plist"):
        shutil.move("BuildManifest.plist", dest)
    else:
        raise RuntimeError("BuildManifest.plist not found after pzb run")

def main():
    print("=== SHSH Blob Config Generator ===\n")

    nickname = ask("Device nickname: ").replace(" ", "-")
    device = ask("Device identifier (e.g. iPhone11,8): ")
    ecid = ask("ECID: ")

    ios_version = ask("iOS version (e.g. 16.7.1): ")
    build_id = ask("Build ID (optional, for betas): ", optional=True)

    major = ios_major(ios_version)

    device_dir = os.path.join("blobs", nickname)
    os.makedirs(device_dir, exist_ok=True)

    print("\nRestore type:")
    print("1) OTA  2) Update  3) Erase  4) ALL")
    rtmap = {"1": "ota", "2": "update", "3": "erase", "4": "all"}
    restore_type = rtmap[ask("Choice: ")]

    ota_url = ""
    if restore_type in ("ota", "all"):
        ota_url = ask("OTA URL: ")
        download_buildmanifest(ota_url, device_dir)

    apnonce = ask("APNonce: ")
    generator = ask("Generator: ")

    cryptex_nonce = cryptex_seed = ""
    if major and major >= 16:
        cryptex_seed = ask("Cryptex1 Seed: ")
        cryptex_nonce = ask("Entangled Cryptex1 Nonce: ")

    cellular = yesno("Cellular device? (y/n): ")
    bbsnum = ask("Baseband SNUM: ") if cellular else "N/A"

    safe_ecid = ecid.replace(":", "")
    suffix = build_id if build_id else ios_version
    filename = f"{device}-{safe_ecid}-{suffix}.mkdn"
    path = os.path.join(device_dir, filename)

    with open(path, "w") as f:
        f.write(f"""# SHSH Blob Configuration

## Device
- **Device ID:** `{device}`
- **ECID:** `{ecid}`
- **iOS Version:** `{ios_version}`
- **Build ID:** `{build_id}`

## Restore
- **Restore Type:** `{restore_type}`
- **OTA URL:** `{ota_url}`

## Security
- **APNonce:** `{apnonce}`
- **Generator:** `{generator}`
- **Cryptex1 Seed:** `{cryptex_seed}`
- **Entangled Cryptex1 Nonce:** `{cryptex_nonce}`

## Baseband
- **Cellular:** `{cellular}`
- **Baseband SNUM:** `{bbsnum}`
""")

    print(f"\nConfig saved to: {path}")

if __name__ == "__main__":
    main()
