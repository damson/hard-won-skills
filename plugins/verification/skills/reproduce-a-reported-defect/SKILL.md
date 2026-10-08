---
name: reproduce-a-reported-defect
description: >
  Use when a review hands you a defect you did not find yourself and you are about to
  act on it: an agent or bot review, a human comment, a bug report, a stand-in's
  critical finding. Fires BEFORE editing the code the finding names, and on "fix the
  review's findings", "it says there is a race", "address the critical one". Do NOT
  fire for a defect you watched happen yourself, for a finding you can settle by
  reading one line of the source, or for proving a new guard can fail, which is
  prove-the-check-can-fail.
---

# Reproduce a reported defect

A cold reader is confidently wrong at a predictable rate, and it is wrong in the
same voice it is right in. Severity does not separate them: a finding ranked
critical is a claim about code the reader never ran, and the ones that turn out
to be real and the ones that turn out to be imaginary arrive in identical prose.

Patching on the claim costs twice. A fix for a defect that was never there is a
change nobody can justify later, and it displaces the real finding underneath it.
A fix for a defect that *was* there, applied without reproducing it, leaves you
unable to say whether you fixed the thing or moved it.

The cheap separator is an artifact: build the smallest thing that makes the
claimed failure happen, and let it answer.

## Procedure

1. **Read the claim against the source first, and stop here when the source
   settles it.** A finding that names a line can be checked by opening that line.
   One claimed a string key still carried an old name when the rename had already
   landed; one named an import as duplicated, and it was. Neither needed a test.
   What needs the next step is a claim about *behaviour over time*: an order, a
   race, a bound, a state read at the wrong moment.

2. **Build the probe, not the patch.** A throwaway test that drives the exact
   sequence the finding describes. Keep it outside the suite for now and name it
   as a probe, so a run that leaves it behind does not look like coverage.

3. **Run it and read WHY it failed, never that it failed.** This is the step that
   gets skipped, and skipping it produces a confident wrong answer in both
   directions. A probe that dies because it addressed the wrong element, timed
   out, or could not find a node has told you nothing about the defect: a modal
   sheet composing into a second window made one probe fail with
   `Expected exactly '1' node but found '2'`, which is not the bug and would have
   read as one. Fix the probe until it is testing the claim, then read the result.

4. **Reproduced: fix it, then promote the probe and show it red.** Move the probe
   into the suite under a name that says the behaviour, and run it against the
   unfixed code once so the record shows the guard catching the thing it was
   written for. A test added beside a fix, never seen failing, is the same
   unverified claim one layer down.

   **Where there is no suite to promote it into**, the probe does not get thrown
   away and it does not get left lying in the tree either. Both of those end the
   same way, with the next reader unable to tell whether anything was checked.
   Find out which it is before deciding:

   ```bash
   ls test* tests spec 2>/dev/null; ls **/src/test 2>/dev/null
   grep -rilE '"(test|spec)"\s*:' package.json 2>/dev/null
   grep -rl 'testImplementation\|pytest\|go test' . --include='*.gradle*' \
     --include='*.toml' --include='Makefile' 2>/dev/null | head
   ```

   Nothing found, and the probe ships beside the fix as the project's first test,
   with whatever runner the language gives for free, plus one line in the change
   saying there was nowhere to put it. Where even that is refused, say in the
   change that the fix is unguarded and why, so the gap is a decision somebody
   made rather than an omission nobody noticed.

5. **Not reproduced: reject it with the evidence, never silently.** Quote the line
   that contradicts it. A finding withdrawn against the source is a better record
   than one that quietly disappears, and the reviewer's next reader deserves to
   know which of its findings held.

6. **Say what the probe could not reach.** A probe often proves the mechanism
   while leaving the reachability open: one proved that state was read at the
   wrong moment by injecting into a window a real scrim would have intercepted.
   That is worth fixing and worth saying, because "I proved the bug" and "I proved
   the code reads this at the wrong time" are different sentences.

## When to STOP

- **The finding is about taste, naming or structure.** There is nothing to
  reproduce; answer it as an opinion, with yours.
- **One line of source settles it.** Reading beats building, and step 1 is the
  whole procedure for most findings.
- **The probe needs hardware the environment does not have.** Say the finding is
  unverified here and name what would settle it, rather than reporting it proved
  or disproved.
- **Reproducing it means running something destructive**, against real data, a
  live account or somebody else's environment. Reason it through on the source
  and hand the question over.
- **The fix is smaller than the probe and provably inert** (a duplicate import, an
  unused symbol). Apply it, and say that is why you did not build one.
- **The repository has no suite and adding one is not yours to decide.** Ship the
  fix with the probe's result quoted in the change and say it is unguarded;
  inventing a test framework on the way past a one-line fix is a larger change
  than the one you were asked for.
