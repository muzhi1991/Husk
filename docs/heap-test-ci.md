# Experimental Dart heap alignment build

Based on upstream 3.0 (cffaf8b). Source patch uses vm_map alignment rather than oversized temporary reservations and accepts Dart's 8 GiB minus page-size request. This is an unverified iPhone fix.

GitHub Actions compiles the app, translation layer, extensions and Rust pairing library. Unchanged QEMU/ANGLE/MoltenVK/PS4 libraries and Android fonts/runtime resources come from the public upstream 3.0 IPA, pinned to SHA-256 112a1ddbb3143ae25e80c18c5b195b6dfa5067d66cbf99d2188fc03f4ab0f61d. This avoids rebuilding unrelated large dependencies. Staging modifies the generated project inputs only inside CI; it does not alter upstream runtime payloads. Build logs and manifests record provenance.

The IPA is ad-hoc signed for re-signing by SideStore. No Apple credentials are uploaded. Test artifacts are retained for 7 days. No user APK, app data or private crash report is included in this repository.

Local macOS mapping tests passed; that is not proof that a constrained iPhone process can allocate the region. vphone tests must record the actual JIT route and whether the new fallback executed. A vphone success is not a physical iPhone 13 acceptance result.

CI also emits separately labelled vphone and vphone-baseline builds. Only those builds allow a guarded MAP_JIT execution probe on iOS 27; device builds keep the upstream JIT policy. The baseline excludes the heap fix. In either VM build, the app-specific preference husk.qa.forceCompressedFallback enables TL_MM_MAX_GIB=5 to reproduce the original large reservation failure without changing the virtual machine configuration. This fault injection is not a measured phone limit.

## Validation status (2026-10-26)

GitHub Actions run 40272635684 built and verified all three variants successfully. The research VM accepted installation and the test app's guarded MAP_JIT probe returned failure: the kernel granted an executable mapping, but the generated-code probe faulted. The upstream JIT policy blocks the standard build before APK execution, and the VM-only probe does not resolve that underlying execution restriction. See the open upstream vphone issue https://github.com/Lakr233/vphone-cli/issues/603 for related research-guest JIT limitations (different tested system version).

No end-to-end Flutter success is claimed. The forced reservation comparison cannot reach the heap initialization until JIT works. The device IPA is an experimental heap candidate, not a verified fix. Do not use a vphone artifact as the physical-device candidate.

## Device diagnostic follow-up

The first vm_map candidate failed on iPhone 13 with KERN_NO_SPACE. This follow-up logs large virtual regions and holes, then attempts the same aligned 4 GiB reservation with MALLOC tags to distinguish allocation-range selection from capacity. All requests remain ANYWHERE and PROT_NONE. If they fail, temporary aligned 1 GiB probes are released immediately and never returned to Dart. Host tests are not evidence of iOS success. Only the device variant is built for this round.

## Segmented reservation candidate

If aligned whole-cage allocations fail, reserve four adjacent 1 GiB entries. Only the first entry uses ANYWHERE with 4 GiB alignment; following entries use FIXED without OVERWRITE, so collisions fail. Roll back partial reservations and return a cage only when all 4 GiB are owned. Diagnostic-only size probes are immediately released. Host interposition verifies both complete-cage commit at both ends and partial rollback; this does not establish iOS compatibility.
