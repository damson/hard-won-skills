# ship-a-fix-round

For the moment someone hands back a list of findings from testing a build on a
real device. The batch is the unit of work: they are waiting for one build that
answers every finding, not a trickle of half-verified edits. This owns the whole
round, from root cause to the APK in their hands.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it does and how
to reach it.

## Using it

It fires on the shape of the report, not on a command:

- "X is broken on my phone, fix it"
- a list of UI complaints from a test session
- a bug with repro steps on hardware

It stays quiet for a change nobody reported, for a non-Android build, since the
diagnostics here are adb's, and for the parts of a round already verified.

## The failure it prevents

A round that looks finished. Fixes pushed, checks green, and underneath it a
finding quietly narrowed until it passed, a golden regenerated without anyone
looking at the image, or a build handed over that predates the last fix. Every
one of those reads as done.

## What it insists on

- **Root-cause every finding before fixing any**, and report the ones that will
  not reproduce, with what was tried, rather than dropping them silently.
- **A test born green is defeated before it is trusted.** Invert the guard,
  watch it go red, restore. A test that passes both ways holds nothing.
- **Look at the goldens.** A file size is not evidence of what is in an image,
  and a golden that moved outside the touched area is a finding.
- **Read the gate's exit status, not its pipeline's.** Redirect rather than pipe,
  and set `pipefail` as well, because the gate the repo documents may be a
  pipeline itself and a gate ending in `tee` otherwise reports the status of
  `tee`: a red build read as green.
- **Watch CI against the pushed commit's full SHA.** A branch-level or rollup
  answer can describe the previous head.
- **The round is not delivered while the fix exists only in git.** The build goes
  to the user, named by short SHA and round.

## Example

A tester comes back from twenty minutes on a Pixel with four things: a sheet that
opens behind the navigation bar, a label that truncates in German, a crash on
rotate, and a suspicion that a button "feels slow". One build is expected back
answering all four.

Step 1 refuses to fix anything yet. Three reproduce. The crash does not, and the
emulator stops drawing while chasing it, so the newest ANR trace is read rather
than guessed at: its main-thread stack is all renderer frames, which means the
emulator rather than the app, so it is cold-booted instead of the app being
debugged on it. The crash then reproduces, and it is a stale window inset read
during a configuration change.

Step 2 fixes each cause and writes a test per fix. Every one of those tests is
then deliberately broken, watched go red, and restored. The truncation test is
the one that matters here: it passed before the fix as well, because it asserted
on a string the layout never measured, and only defeating it exposed that.

Step 3 re-records two goldens, and the verify task is run afterwards rather than
trusted: it reports success having made 0 comparisons, because the baselines were
written under a different task name. A count of zero is a failure however green
the run looked, and the goldens are only accepted once the count is real.

Step 4 finds the gate in the repo's own README and captures it with `pipefail`
set. The gate ends in a `tee`, so without that line it would have reported the
status of `tee` and called a red build green.

Step 6 is where the round would otherwise have shipped a lie. The assemble task
is taken from the README, and the artifact that comes out is checked against the
timestamp of the last commit:

```bash
ref=$(mktemp)
touch -t "$(git log -1 --format=%cd --date=format:%Y%m%d%H%M.%S)" "$ref"
apk=$(find . -name '*.apk' -newer "$ref" | head -1); rm -f "$ref"
[ -n "$apk" ] || { echo "no APK newer than the last fix: it did not rebuild"; exit 1; }
```

The first run finds nothing, because the build had been skipped by a cache. The
file that would have been handed over was the previous round's, with the right
name and the right short SHA and none of the four fixes in it.

The user gets one APK, and a report naming three findings fixed, one deferred
with its reason, and the "feels slow" claim as unsettled: nothing on an emulator
can answer it.

## Related

- `android-verify-on-device` (this plugin): the single-claim version, for when
  one behaviour needs a real device rather than a whole round.
- `android-screenshot-baseline-verify` (this plugin): the golden step in
  isolation, including the task that reports PASSED while comparing nothing.
- `render-the-candidates` (verification plugin, if installed): what step 2 of
  the STOP list reaches for when the requirement itself keeps moving.
