---
name: android-shrink-apk-to-a-budget
description: >
  Use when an Android APK has to fit a hard size ceiling that is not negotiable: an
  upload or attachment cap, a chat or ticket limit, a distribution channel's maximum,
  a tester on metered data. Fires on "make it smaller", "reduce it until it fits",
  "why is this APK 200MB", "it is too big to send". Owns the order the cuts are made
  in and the measurement that tells you where the bytes actually are, because the
  obvious measurement reports the wrong number and the largest single win is usually
  invisible in it. Do NOT fire for production size policy, where the trade-offs are a
  product decision rather than a transfer problem, or to diagnose which keep rules are
  redundant, which is keep-rule analysis rather than a size ceiling.
---

# Shrink an Android APK to a budget

A size ceiling is arithmetic, so the first move is never a lever, it is a
measurement. Cutting before measuring spends twenty minute builds on the third
largest item while the largest is padding that one flag removes.

## Procedure

### 1. Measure the composition, and distrust the easy tool

`unzip -l` reports **uncompressed** sizes, and the error is uneven: native libraries
are usually stored uncompressed, so they read true, while dex and resources read far
larger than they contribute. That reorders the ranking, which is the one thing you
are reading the list for. `unzip -v` reports compressed sizes, but its columns shift
on names containing spaces, which silently drops entries from an `awk` sum.

Read it with a parser instead, and always compare the total against the file.
Python 3 ships with macOS and every mainstream Linux; without it, `unzip -v` plus
`stat` gives the same two numbers, taking care that its columns shift on names
containing spaces:

```bash
python3 - <<'PY'
import zipfile, collections, os, sys
p = sys.argv[1] if len(sys.argv) > 1 else "app/build/outputs/apk/debug/app-debug.apk"
z = zipfile.ZipFile(p); agg = collections.Counter()
for i in z.infolist():
    n = i.filename
    k = ("lib/" if n.startswith("lib/")
         else "dex" if n.startswith("classes") and n.endswith(".dex")
         else "res/" if n.startswith("res/")
         else "assets/" if n.startswith("assets/")
         else n.split("/")[0] + "/" if "/" in n else n)
    agg[k] += i.compress_size
tot = sum(agg.values()); disk = os.path.getsize(p)
print("file on disk:  %.2f MB" % (disk / 1048576))
print("entries total: %.2f MB" % (tot / 1048576))
print("PADDING:       %.2f MB" % ((disk - tot) / 1048576))
for k, v in agg.most_common(8):
    print("  %7.2f MB  %s" % (v / 1048576, k))
PY
```

**A large `PADDING` line is the finding.** Uncompressed native libraries have to
start on page boundaries, and on a 16KB page target that padding runs to tens of
percent of the file. It is invisible to every per entry listing because it belongs
to no entry.

### 2. Cut in yield order, not in the order the levers occur to you

Each of these belongs behind a Gradle property so that CI and everyone else's
build are untouched:

```kotlin
val isSmall = providers.gradleProperty("smallApk").isPresent
```

1. **Reclaim the padding.** `packaging { jniLibs { useLegacyPackaging = true } }`
   compresses the `.so` files, which removes the alignment requirement and the
   padding with it. Cost: the installer extracts the libraries, so installs are
   slower and the on device footprint is larger. Nothing about the running app
   changes. This is routinely the single largest win and the cheapest.
2. **Drop the ABIs nobody will run.** `defaultConfig { ndk { abiFilters += "arm64-v8a" } }`.
   Cost: it will no longer install on an x86 emulator or a 32 bit device, so say
   so when handing it over, and check what you are about to verify it on.
3. **Exclude SDKs that survive R8 by their own keep rules.** Some AARs ship
   `consumer-rules.pro` holding their whole package, so no rule you write shrinks
   them; keep rules are additive and there is no un-keep. Excluding the dependency
   from the variant is the only lever:
   ```kotlin
   configurations.configureEach { exclude(group = "com.example.sdk") }
   ```
   plus `-dontwarn com.example.sdk.**` for the references left behind. Verify the
   flows that use them are genuinely unreachable in this build. To find which
   rules are doing the holding, read each dependency's `consumer-rules.pro` out
   of its unpacked AAR; where an `r8-analyzer` skill is installed it does that
   analysis for you.
4. **Minify and shrink resources**, with keep rules no broader than they must be.
   A blanket `-keep class com.vendor.** { *; }` pins an entire SDK: narrowing one
   such rule is worth more than any number of `-dontwarn` lines.
5. **Strip locales, densities and orphaned assets.**
   ```kotlin
   androidResources {
       localeFilters += "en"
       ignoreAssetsPatterns += listOf("models", "*.tflite")
   }
   ```
   Model files and data blobs belonging to a native library you removed in step 3
   are pure waste; grep the asset names against what is left.

### 3. Re-measure after every build

Levers interact. Resource shrinking after a dependency exclusion removes more than
it would have before, and a keep rule narrowed after minification is already on
changes nothing. One build, one measurement, before choosing the next lever.

## Reflection-resolved registries break silently

R8 removes anything reached only by name. A preview or component registry, a
`ServiceLoader`, a DI graph built by codegen, a serializer looked up from a class
name: all of them survive compilation, survive install, survive launch, and then
produce an **empty list** rather than a crash.

Keep the generated holder and the root it hangs from explicitly, then prove the
list is populated by opening the screen that renders it. A clean logcat is not
evidence here; an empty screen is the failure mode.

## Verify before handing it over

Installing and launching proves almost nothing about a build this heavily cut.

1. Launch, and read logcat for `UnsatisfiedLinkError`, `ClassNotFoundException`
   and `NoClassDefFoundError`, not only `FATAL`.
2. Open one screen per stripped native library. A library removed in step 3 fails
   at the moment something calls it, which is usually several taps in.
3. Open the screen backed by any reflection-resolved registry and count the rows.
4. **Calibrate slowness before reporting it.** Time a stock system app's cold
   launch with `am start -W` on the same device. An emulator that takes 16 seconds
   to open Settings will make any build look like it regressed, and an ANR dialog
   there is evidence about the emulator.

State the ABI restriction, the stripped functionality and the stubbed behaviour
whenever the artifact leaves your hands. A smaller APK that quietly lost a feature
is worse than a large one.

## When to STOP

- **The floor is above the ceiling.** Sum dex and native after the free cuts. If
  that already exceeds the budget, further cutting removes features, which is the
  user's call: show the arithmetic and ask, rather than grinding builds.
- **The target is a production or release artifact.** These levers trade
  correctness and device coverage for bytes and are meant for transfer copies.
- **The question is which keep rules are redundant or mutually subsuming.** That
  is keep-rule analysis, a different job from hitting a ceiling; an `r8-analyzer`
  skill covers it where one is installed.
- **A lever would strip something a component on screen uses.** Check before
  removing, not after; the failure arrives on a tap, far from the build.
