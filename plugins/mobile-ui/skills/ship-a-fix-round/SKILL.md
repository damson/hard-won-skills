---
name: ship-a-fix-round
description: >
  Use when a user reports on-device findings against an Android build and
  expects fixes and a new APK back: "X is broken, fix it", a list of UI
  complaints from a test session, a bug with repro steps on hardware. Owns the
  whole round: root cause, fail-proofed fix, goldens, the repo's full gate,
  focused commits, the PR brought up to date, a fresh build handed over, CI
  watched on the pushed commit. Do NOT fire for a change nobody reported, for
  a non-Android build (the diagnostics here are adb's), or to skip the parts
  a round already verified.
---

# Ship a fix round

A device-testing report is a batch, and the batch is the unit of work: the
user is waiting for one build that answers every finding, not a trickle of
half-verified edits. The failure this prevents is the round that looks done,
fixes pushed and checks green, while a finding was quietly narrowed, a golden
silently regenerated, or the build handed over predates the last fix.

## Procedure

1. **Root-cause every finding before fixing any.** Read the code path, then
   reproduce: on the emulator when the claim is visual or gestural, in a JVM
   test when a test can hold it. Write down, per finding, what is wrong and
   why; a finding that cannot be reproduced is reported as such, with what was
   tried, never silently dropped. If the emulator misbehaves, read the ANR
   trace's main-thread stack (`adb shell cat /data/anr/<latest>` after
   `adb root`): app frames mean the app, pure renderer or system frames mean
   the emulator, so cold-boot it instead of debugging the app on it.

2. **Fix minimally, and prove each check can fail.** New behaviour gets a
   test; a test born green is then defeated (invert the guard, break the
   constant) and must go red, then restored. A test that passes both ways
   holds nothing.

3. **Re-record goldens only when pixels changed, and look at them.** List the
   changed files and confirm the set matches the change. A golden that moved
   outside the touched area is a finding, not noise. Read the images; a file
   size is not evidence of what is in one.

4. **Run the repo's full pre-push gate**, the exact command its README states
   (grep the README for it rather than reciting one; a repo that states none
   gets its test and lint tasks, and the report says the gate was assembled,
   not found). Capture the verdict as `cmd > log 2>&1; rc=$?`, because a pipeline
   reports its last command, not the gate.

5. **Commit per concern and bring the PR up to date.** One focused commit per
   fix, high-level messages; append a round note to the PR body saying what
   this round changed and why.

6. **Hand the user the build.** Assemble the debug APK, name the file by
   short SHA and round, and send it through the session's file hand-off (the
   send-file tool where the harness has one, an attached path where it does
   not). The round is not delivered while the fix exists only in git.

7. **Watch CI pinned to the pushed commit's full SHA.** A branch-level or
   rollup answer can describe the previous head. Report terminal verdicts per
   check, then per finding: fixed, deferred with a reason, or not reproducible
   with what was tried, and say plainly which claims only hardware can settle.

## When to STOP

- **A finding needs hardware the session lacks:** a camera position, a real
  inset, a finger. Fix what can be held by tests, ship the round, and name
  the unverified claim instead of stretching an emulator result over it.
- **The user's requirement shifted mid-round** ("that was not what I meant").
  Re-anchor, rendering the candidate interpretations if words have failed
  twice, before writing more code.
- **The same fix has failed twice.** The third attempt is a different root
  cause's problem; go back to step 1 rather than stacking another patch.
- **The gate is red for something this round did not touch.** Report it;
  fixing a stranger's breakage inside a fix round buries both changes.
