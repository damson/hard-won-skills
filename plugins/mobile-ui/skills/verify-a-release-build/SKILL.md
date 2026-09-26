---
name: verify-a-release-build
description: >
  Use after a change that alters what R8 sees or does and before that change merges:
  the Android Gradle plugin, the Kotlin or KSP version, a proguard file or keep rule,
  a dependency that ships consumer rules, or turning optimization on. Fires on "bump
  AGP", "enable R8 optimization", "why is the release APK smaller", "the tests are
  green, can this merge". Owns the step every pipeline skips, which is starting the
  shipped artifact, because a build task packages an APK and never launches one. Do
  NOT fire for a debug build, where none of this applies, for cutting an APK to a
  transfer size ceiling, which android-shrink-apk-to-a-budget owns, or for a diff that
  cannot reach R8's input.
---

# Verify a release build

`assembleRelease` proves an APK **builds**. Nothing in a normal Android pipeline
starts one: unit tests run on the JVM, screenshot goldens render on the debug
classpath, and the release job stops at packaging. So a shrinking or optimization
regression passes every check that exists and arrives as a crash on a user's device.

That is not a hypothetical failure mode. An AGP 8 to 9 upgrade, green on every
check, shipped a release APK that died before its first frame: R8 had stripped the
no-argument constructor Room reflects on to build its generated database
implementation, in a WorkManager database the app never asked for, which arrived
under an ads SDK and initialised itself through `androidx.startup`. One keep rule
fixed it. Nothing but launching the APK could have found it.

## Procedure

### 1. Decide whether the change can reach R8 at all

It can if it touches the plugin, the compiler, the symbol processor, a proguard or
keep-rule file, or any dependency that ships consumer rules. It cannot if it touches
only test sources, documentation, or code behind a flag that is off in release. A
diff that cannot reach R8 does not need any of this; say so rather than driving an
emulator for form's sake.

### 2. Build both APKs and compare them, not just yours

```bash
git worktree add ../baseline <integration-branch>     # its own checkout, not a stash
./gradlew :app:assembleRelease                       # in each, with the project's own
                                                     # exclusions for upload steps
ls -l */app/build/outputs/apk/release/*.apk           # sizes
grep -cE '^[a-zA-Z].* -> ' */app/build/outputs/mapping/release/mapping.txt
```

The size tells you something happened; the **mapped class count** tells you how
much. A plugin upgrade that shakes out 600 more library classes is doing more than
its release notes said, and one of them can be load-bearing. Report sizes the way a
person reads them, in MB, and keep the exact bytes only where the byte is the
evidence.

Name what is in each build. A comparison against an integration branch that has
moved since your branch was cut is still worth making, as long as the difference is
stated: two commits of app code cannot explain a megabyte.

### 3. Read the mapping for what survives only by name

Before installing, ask the mapping about every reflective path the app has. Each of
these is kept by a rule, or not at all:

- `Parcelable` `CREATOR` fields, including every `@Parcelize` type;
- a `RoomDatabase`'s generated `<Name>_Impl` **and its no-argument constructor**,
  which is a separate thing from the class surviving;
- DI graph holders, entry points and generated factories;
- any enum whose `name` is persisted or sent over a wire;
- registries resolved by class name, which `android-shrink-apk-to-a-budget`
  describes failing as an empty list rather than a crash.

A class present in `mapping.txt` proves the class survived. It does not prove its
members did, which is exactly how the Room crash above got through.

### 4. Get authorisation before running it, because a release build is not a toy

A release build carries the **production** configuration: real ad unit ids, the live
crash reporter, the real analytics project. Driving it generates synthetic traffic on
someone's ad account and real events in their dashboards. Ask first, then blunt it:

```bash
adb shell svc data disable && adb shell svc wifi disable
```

Offline still exercises what matters here. An SDK's initialisation is the reflective
part, and it runs whether or not the network answers. Say plainly afterwards that the
filled-request path was not covered.

### 5. Install it and drive the app, not the launcher

```bash
adb install -r app/build/outputs/apk/release/app-release.apk
adb logcat -c
adb shell monkey -p <pkg> -c android.intent.category.LAUNCHER 1
```

`am start` cannot reach an activity that is not exported, and a bare `monkey -p <pkg> 1`
often injects an event that goes nowhere. Wait for `Displayed <pkg>/<activity>` in
logcat rather than for the command to return, then confirm the app is what is resumed
before reading anything off the screen. `android-verify-on-device` owns the driving
technique in full, including locating controls by `uiautomator` bounds instead of
guessing coordinates, and why a capture must be compared against the frame from
before the action.

Cover, at minimum: the first screen, one screen per subsystem the change could reach,
a configuration change on a screen holding parcelled state, and a force-stop and
relaunch. Then read logcat for all of `FATAL EXCEPTION`, `ClassNotFoundException`,
`NoSuchMethodError`, `NoClassDefFoundError` and `BadParcelableException`. A clean
`FATAL` grep alone is not the answer.

### 6. Prove persisted state still round-trips

Optimization renames fields, and code that stores an enum by `name` is one rename
away from silently losing every user's saved choice on upgrade. `run-as` cannot read
a release build's files, but on an emulator `adb root` can:

```bash
adb root && adb shell cat /data/data/<pkg>/shared_prefs/<name>.xml
```

Set the value through the UI, read the file, force-stop, relaunch, and confirm the
app comes back in the state you left it. The second half is what makes the first
mean anything: a value that stopped resolving falls back to the default and stays
there, which looks like nothing happening.

### 7. Restore the device, and say what you did not cover

```bash
adb shell svc data enable && adb shell svc wifi enable
adb shell settings put system accelerometer_rotation 1
adb unroot
adb uninstall <pkg>          # so a later debug install is not blocked by the signature
```

Delete anything pushed to `/sdcard` as well.

Then report the route you drove **and the branches you did not**: a hand pass cannot
reach an error path, another locale or a device configuration you do not have, and
the crash reporter is the net under those.

## When to STOP

- **No emulator or device, or no release signing config.** Report the change as
  unverified against a shipped artifact rather than implying a green build covers it.
- **The owner has not authorised running the production build.** It reaches their ad
  account and their analytics. Ask, do not assume, and do not run it online to be
  thorough.
- **The target is a transfer copy rather than a release**, where bytes are being
  traded against device coverage on purpose: `android-shrink-apk-to-a-budget` owns
  that, including its own verification.
- **A finding needs a keep rule.** Add the rule, then prove it was needed by building
  without it and watching the same failure, so the rule is evidence rather than
  superstition.
- **The app crashes and the integration branch's own release APK crashes too.** That
  is a pre-existing fault, not this change's. Say so, and do not fix it here.
