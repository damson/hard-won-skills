---
name: prove-a-procedure-on-a-fixture
description: >
  Use before claiming that a documented procedure's commands work — a skill, a
  runbook, a README whose steps a reader pastes into a terminal. Fires on "this
  handles renames and deletions", "the block is paste-and-run", "the step is
  fixed", and on answering any review finding about embedded shell. Do NOT fire
  for prose that ships no commands, for a check or a test (that is
  `prove-the-check-can-fail`), or where CI already runs the procedure on every
  push, which is a stronger proof than a fixture.
---

# Prove a procedure on a fixture

Documentation that ships commands is untested code with a readership. Nothing
compiles it, no suite runs it, and its failures are silent in the worst
direction: a step that errors is discovered immediately, while a step that
answers *confidently and wrongly* is followed. Reading it is not verification.
The reader is not going to read it; they are going to run it.

A fixture is cheap, and it is the only thing that separates a procedure that
works from one that reads as though it does.

## Procedure

1. **List the cases the text claims to handle, in its own words.** Quote the
   claim. "Classifies every dirty path" is a list: modified, deleted, renamed,
   untracked, already-landed. A claim you cannot turn into cases is too vague to
   verify, and that is itself the finding.

2. **Add the awkward cases the prose implies but never names.** These are where
   confident wrongness lives, and each one is a real defect found this way:

   | Shape | What it breaks |
   |---|---|
   | a path containing a space | quoting, and any `read` that splits on it |
   | a path beginning with `-` | every command that parses it as an option |
   | a symlink | tools that follow it and compare the wrong thing |
   | a binary file | line-based logic that reports zero differences |
   | a mode-only change | byte comparisons that call it unchanged |
   | an empty result | loops that treat "nothing" as "done" |

3. **Build one throwaway fixture holding all of them**, outside the tree you are
   working in, and say where it is. One fixture, not one per case: cases
   interact, and the interactions are half the defects.

4. **Run the published commands verbatim.** Extract them from the document
   rather than retyping, substitute only the fill-ins the document declares, and
   change nothing else. A command you adjusted to make work is a command the
   reader cannot run.

   Extracting rather than retyping is the whole of this step. Retyping silently
   repairs what you are trying to test — a fixture that passes because you fixed
   a placeholder on the way in has proved nothing about the published text.

   ```bash
   # Pull block $BLOCK out of the document as it stands, then substitute into a
   # SECOND file, so the two can be compared. Nothing is retyped.
   awk -v want="$BLOCK" \
     '/^```bash$/ {n++; next} /^```$/ {inb=0} n==want && !seen {inb=1; seen=1} inb' \
     SKILL.md > raw.sh
   sed "s|<owner>/<repo>|$REPO|g" raw.sh > block.sh

   diff raw.sh block.sh     # must show ONLY the fill-ins you declared
   bash block.sh
   ```

   The `diff` is the guard on the extraction itself. Anything in that output
   beyond the substitutions you declared is an edit you made without meaning to,
   which is the failure this step exists to prevent. Diffing against a
   re-extraction instead would compare the wrong block the moment there is more
   than one, and quietly pass.

5. **Assert a verdict per case, and read them.** Every case names its expected
   answer before the run. A run you interpret afterwards will agree with
   whatever you already believed.

6. **Run the superseded version too, and record what it answered.** This is the
   step that turns a plausible fix into a demonstrated one, and it fails often
   enough to be worth the minute: a first attempt frequently gets the right
   answer for the wrong reason, and the old and new rules agree. When they
   agree, you have not reproduced the defect and do not yet know it was real.

7. **Re-run against the text as published**, after the merge, not against your
   working copy. The two differ whenever a squash, a rebase or a review round
   touched the block.

8. **Delete the fixture and say so.** A rescue or a migration procedure verified
   against debris left by the last run is verified against nothing.

## Sharp edges

- **A fixture that passes first time usually tested the wrong thing.** Step 6
  is the check on the fixture itself: if the superseded version also passes, the
  fixture does not contain the case the finding described.
- **"Cannot construct the case" is a result, not a skip.** Report the claim as
  unproven. A hazard nobody can reach is worth knowing about; a hazard you
  quietly assumed away is not.
- **The counterfactual belongs in the write-up.** "Fixed the parsing" invites
  the reviewer to re-derive it. "Under the old rule this printed LANDED over a
  modified file" cannot be argued with.

## When to STOP

- **The procedure needs a credential, a paid service or a device** a fixture
  cannot stand in for. Say which step is unverified rather than verifying the
  cheap half and reporting the whole.
- **The claim is about judgement, not behaviour** — when to escalate, whose
  call a merge is. There is nothing to run; review it as prose.
- **CI already executes the procedure on every push.** That is continuous proof
  and a fixture adds nothing; point at the job instead.
- **The fixture would need production data.** Construct the shape by hand or
  report it unproven; never copy real rows into a throwaway repository to make
  a documentation check convenient.
