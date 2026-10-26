# Experimental Dart heap alignment build

Based on upstream 3.0 (cffaf8b). Source patch uses vm_map alignment rather than oversized temporary reservations and accepts Dart's 8 GiB minus page-size request. This is an unverified iPhone fix.

GitHub Actions compiles the app, translation layer, extensions and Rust pairing library. Unchanged QEMU/ANGLE/MoltenVK/PS4 libraries and Android fonts/runtime resources come from the public upstream 3.0 IPA, pinned to SHA-256 112a1ddbb3143ae25e80c18c5b195b6dfa5067d66cbf99d2188fc03f4ab0f61d. This avoids rebuilding unrelated large dependencies. Staging modifies the generated project inputs only inside CI; it does not alter upstream runtime payloads. Build logs and manifests record provenance.

The IPA is ad-hoc signed for re-signing by SideStore. No Apple credentials are uploaded. Test artifacts are retained for 7 days. No user APK, app data or private crash report is included in this repository.

Local macOS mapping tests passed; that is not proof that a constrained iPhone process can allocate the region. vphone tests must record the actual JIT route and whether the new fallback executed. A vphone success is not a physical iPhone 13 acceptance result.

CI also emits separately labelled vphone and vphone-baseline builds. Only those builds allow a guarded MAP_JIT execution probe on iOS 27; device builds keep the upstream JIT policy. The baseline excludes the heap fix. In either VM build, the app-specific preference husk.qa.forceCompressedFallback enables TL_MM_MAX_GIB=5 to reproduce the original large reservation failure without changing the virtual machine configuration. This fault injection is not a measured phone limit.
