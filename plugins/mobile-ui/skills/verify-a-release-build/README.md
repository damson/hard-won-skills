# verify-a-release-build

Runs the release APK before the change that altered it merges. A build task
packages an APK and never starts one, unit tests run on the JVM, and screenshot
goldens render on the debug classpath, so an R8 regression passes every check a
project has and reaches a user as a crash.

The upgrade this came from was green everywhere and shipped a build that died
before its first frame. R8 had stripped the no-argument constructor Room reflects
on to instantiate its generated database, in a WorkManager database the app never
asked for: it arrived under an ads SDK and initialised itself through
`androidx.startup`, so the failure landed in a content provider during application
bind. One keep rule fixed it, and nothing except launching the APK could have found
it.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it looks like in use
and how to reach it.

## Using it

Ask for the outcome, not the technique:

- "bump AGP"
- "turn on R8 optimization"
- "the tests are green, can this merge"
- "why is the release APK suddenly smaller"

It fires on a change that can reach R8: the Android Gradle plugin, the Kotlin or
KSP version, a proguard file or keep rule, a dependency that ships consumer rules.
It stays quiet for a diff that cannot, and says so rather than driving an emulator
for form's sake.

## Example

An AGP bump, green on every check the project had. The comparison is against the
integration branch's own release build, not against the change alone:

```console
$ module=:app; out=${module#:}
$ for d in . ../baseline; do ( cd "$d" && ./gradlew "$module:assembleRelease" ); done
BUILD SUCCESSFUL in 1m 48s
BUILD SUCCESSFUL in 1m 52s
$ for d in . ../baseline; do
>   m="$d/$out/build/outputs/mapping/release/mapping.txt"
>   [ -f "$m" ] && echo "$d: $(grep -cE '^[a-zA-Z].* -> ' "$m") mapped classes"
> done
.: 18492 mapped classes
../baseline: 19104 mapped classes
```

Six hundred classes gone that the release notes did not mention. Reading the
mapping for what survives only by name found a generated database implementation
with no keep rule behind it, and the release APK died before its first frame while
the debug build and every test stayed green.

## What it does

1. Builds the release APK on both the branch and the integration branch, and
   compares sizes **and mapped class counts**, because the count is what says how
   much the plugin changed on its own.
2. Reads `mapping.txt` for everything that survives only by name: `Parcelable`
   `CREATOR` fields, a Room `_Impl` and its constructor, DI holders and entry
   points, enums whose `name` is persisted.
3. Asks before running it, then takes the device offline, because a release build
   carries production ad ids and the live analytics project.
4. Installs and drives the app, waiting for `Displayed` rather than for a command
   to return, and reads logcat for four error classes rather than just `FATAL`.
5. Proves persisted state round-trips, including through `adb root` where `run-as`
   cannot reach a release build's files.
6. Restores the device and states which branches the hand pass did not reach.

## What it will not do

It does not run the production build without being asked. Driving a release build
sends synthetic traffic to someone's ad account and real events to their
dashboards, so the authorisation is part of the procedure rather than a courtesy.

It does not report a green build as coverage. Where there is no device or no
signing config, it says the change is unverified against a shipped artifact.

It is not a size tool. Cutting an APK to fit a transfer ceiling is a separate
job, one that trades device coverage for bytes on purpose and carries its own
verification.

It does not add a keep rule on suspicion. A rule earns its place by being removed
once and the failure being watched, so the next reader knows it is load-bearing.

## The distinction it is built around

A class in `mapping.txt` proves the class survived. It proves nothing about the
class's members, and the constructor Room needs is a member. That gap is why "the
mapping still lists it" reads as safety and is not.
