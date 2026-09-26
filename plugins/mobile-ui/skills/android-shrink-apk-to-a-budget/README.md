# android-shrink-apk-to-a-budget

Cuts an Android APK down to a size that is not negotiable: an upload cap, an
attachment limit, a channel maximum, a tester on metered data. The work is
ordinary, and the trap is that the obvious measurement reports the wrong number,
so the first three levers get spent on the third largest item while the largest
sits unnoticed.

`unzip -l` reports uncompressed sizes. The file on disk can be half again the sum
of everything inside it, because uncompressed native libraries start on page
boundaries and the padding between them belongs to no entry. One flag reclaims
it, and it is routinely worth more than minification and dependency surgery put
together.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it looks like in
use and how to reach it.

## Using it

Ask for the outcome, not the technique:

- "reduce it until it fits"
- "this APK is 200MB, make it smaller"
- "too big to send, can you trim it"
- "why is the debug build this size"

It fires on a size ceiling, not on a passing wish for a smaller app. It stays
quiet for production size policy, where the trade-offs are a product decision
rather than a transfer problem.

## What it does

1. Measures the composition with a parser rather than a listing, and reports the
   padding as its own line, because that line is usually the finding.
2. Applies the levers in yield order: reclaim padding, drop unused ABIs, exclude
   SDKs that survive R8 through their own consumer keep rules, minify and shrink
   resources, strip locales and orphaned assets.
3. Puts every lever behind a Gradle property, so CI and everyone else's build are
   untouched.
4. Re-measures between builds, because the levers interact.
5. Verifies on a device by opening a screen per stripped library, and calibrates
   any slowness against a system app before calling it a regression.

## What it will not do

It stops rather than grinding when the floor is above the ceiling: when dex plus
native already exceed the budget, the next cut removes features, and that is the
user's call to make with the arithmetic in front of them.

It does not diagnose which keep rules are redundant or mutually subsuming. That
is `r8-analyzer`, and this skill points at it rather than duplicating it.

It is not a release tool. Every lever here trades device coverage or on-device
footprint for bytes, which is the right trade for a copy you are handing to one
person and the wrong one for the build in the store.

## The failure it is built around

R8 removes anything reached only by name. A component registry, a `ServiceLoader`,
a serializer looked up from a class name: each compiles, installs, launches and
then renders an empty list. There is no crash and nothing in logcat. The skill
treats a populated screen, not a clean log, as the evidence that a reflective
registry survived.
