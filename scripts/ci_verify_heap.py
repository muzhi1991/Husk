#!/usr/bin/env python3
import hashlib, json, plistlib, subprocess, sys, zipfile
from pathlib import Path
with zipfile.ZipFile(sys.argv[1]) as z:
    prefix = "Payload/Husk.app/"
    info = plistlib.loads(z.read(prefix + "Info.plist"))
    assert info["HuskExperimentalFix"] == "dart-aligned-cage-vm-map-v1"
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    assert info["HuskBuildCommit"].startswith(commit)
    has_patch = b"aligned cage vm_map kr=" in z.read(prefix + "Husk")
    assert has_patch == (info.get("HuskTestVariant") != "vphone-baseline"), "Wrong compiled variant"
    manifest = json.loads(Path("build/runtime-manifest.json").read_text())
    for name, sha in manifest["files"].items():
        if name.startswith("Frameworks/"): continue  # codesign changes Mach-O bytes
        assert hashlib.sha256(z.read(prefix + name)).hexdigest() == sha, name
    print("Verified compiled patch, source identity and unchanged guest resources", info["HuskBuildCommit"])
