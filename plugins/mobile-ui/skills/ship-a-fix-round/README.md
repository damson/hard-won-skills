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
- **Read the gate's exit status, not its pipeline's.** `cmd > log 2>&1; rc=$?`,
  because a pipeline reports its last command.
- **Watch CI against the pushed commit's full SHA.** A branch-level or rollup
  answer can describe the previous head.
- **The round is not delivered while the fix exists only in git.** The build goes
  to the user, named by short SHA and round.

## Related

- `android-verify-on-device` (this plugin): the single-claim version, for when
  one behaviour needs a real device rather than a whole round.
- `android-screenshot-baseline-verify` (this plugin): the golden step in
  isolation, including the task that reports PASSED while comparing nothing.
- `render-the-candidates` (verification plugin, if installed): what step 2 of
  the STOP list reaches for when the requirement itself keeps moving.
