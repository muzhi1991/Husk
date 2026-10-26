# Flutter compatibility probe

An independently authored, offline fixture for system-font discovery and startup.
No custom fonts, network requests, application data, or third-party app content.
The validation workflow creates a stock Android Flutter project with Flutter
3.35.7 (adc901062556672b4138e18a4dc62a4be8f4b3c2), replaces lib/main.dart with
this file, and builds an arm64 release APK. Check visible Latin and Chinese text,
the increment button and forward/back navigation. Log markers are supplementary;
first-frame submission alone is not a visual acceptance result.
