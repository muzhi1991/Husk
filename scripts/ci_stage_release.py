#!/usr/bin/env python3
"""Stage pinned, unmodified runtime dependencies for the 3.0 native-layer test build."""
import hashlib, json, os, plistlib, shutil, sys, zipfile
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
IPA = Path(sys.argv[1])
EXPECTED = "112a1ddbb3143ae25e80c18c5b195b6dfa5067d66cbf99d2188fc03f4ab0f61d"
assert hashlib.sha256(IPA.read_bytes()).hexdigest() == EXPECTED, "Official IPA hash mismatch"
DEST = ROOT / "build/release-runtime"
DEST.mkdir(parents=True, exist_ok=True)
resources = {"android-system", "java-runtime", "pc-bios", "vmlinuz-virt", "initramfs-virt", "edk2-aarch64-code.fd", "lineage-efi-vars-seed.fd", "lineage-vdb-seed.qcow2"}
manifest = {}
with zipfile.ZipFile(IPA) as z:
    for entry in z.infolist():
        prefix = "Payload/Husk.app/"
        if not entry.filename.startswith(prefix) or entry.is_dir(): continue
        rel = Path(entry.filename[len(prefix):])
        assert ".." not in rel.parts
        if rel.parts[0] not in resources | {"Frameworks"}: continue
        data = z.read(entry)
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        manifest[str(rel)] = hashlib.sha256(data).hexdigest()
lib = ROOT / "build/ios-arm64/lib"
lib.mkdir(parents=True, exist_ok=True)
shutil.copy2(DEST / "Frameworks/libqemu-aarch64-softmmu.dylib", lib)
project_path = ROOT / "src/app/project.yml"
project = yaml.safe_load(project_path.read_text())
app = project["targets"]["Husk"]
variant = os.environ.get("HUSK_VARIANT", "device")
assert variant in ("device", "vphone", "vphone-baseline")
if variant != "device":
    app["settings"]["base"]["SWIFT_ACTIVE_COMPILATION_CONDITIONS"] = "$(inherited) HUSK_VPHONE_TEST"
if variant == "vphone-baseline":
    app["settings"]["base"]["GCC_PREPROCESSOR_DEFINITIONS"] = ["$(inherited)", "HUSK_HEAP_BASELINE=1"]
for dep in app["dependencies"]:
    old = dep.get("framework", "")
    if old.endswith("libANGLE-shared.dylib"):
        dep["framework"] = "../../build/release-runtime/Frameworks/libANGLE-shared.dylib"
    elif old.endswith("MoltenVK.xcframework"):
        dep["framework"] = "../../build/release-runtime/Frameworks/MoltenVK.framework"
    elif old.endswith("libhuskps4.dylib"):
        dep["framework"] = "../../build/release-runtime/Frameworks/libhuskps4.dylib"
app["preBuildScripts"] = [{"name": "Stage verified 3.0 runtime resources", "basedOnDependencyAnalysis": False,
    "script": "set -eu\nSRC=\"$SRCROOT/../../build/release-runtime\"\nDST=\"$BUILT_PRODUCTS_DIR/$UNLOCALIZED_RESOURCES_FOLDER_PATH\"\nmkdir -p \"$DST\"\n" + "\n".join('ditto \"$SRC/'+n+'\" \"$DST/'+n+'\"' for n in sorted(resources))}]
project_path.write_text(yaml.safe_dump(project, sort_keys=False))
plist_path = ROOT / "src/app/Husk/Info.plist"
info = plistlib.loads(plist_path.read_bytes())
info["CFBundleDisplayName"] = "Husk Heap Test" if variant == "device" else "Husk VM " + variant.removeprefix("vphone").strip("-")
info["CFBundleVersion"] = str(130 + int(os.environ.get("GITHUB_RUN_NUMBER", "0")))
info["HuskExperimentalFix"] = "dart-aligned-cage-vm-map-v1"
info["HuskTestVariant"] = variant
plist_path.write_bytes(plistlib.dumps(info))
(ROOT / "build/runtime-manifest.json").write_text(json.dumps({"source": "Leviidev/Husk release 3.0", "ipa_sha256": EXPECTED, "files": manifest}, indent=2))
print("Staged", len(manifest), "verified runtime files; app and translation layer will be compiled from this fork.")
