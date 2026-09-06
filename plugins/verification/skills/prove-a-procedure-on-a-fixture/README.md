# prove-a-procedure-on-a-fixture

Verifies that a documented procedure's commands do what the surrounding prose
says, by building a throwaway fixture that holds every case the text claims to
handle and running the published commands against it. Documentation that ships
commands is untested code with a readership: nothing compiles it, no suite runs
it, and the reader is going to run it rather than read it.

Read [SKILL.md](SKILL.md) for the procedure. This file is why the counterfactual
is a required step rather than a nicety.

## Using it

Reach for it when a document promises behaviour:

- "this handles renames and deletions"
- "the block is paste-and-run"
- "fixed the parsing" on a review finding about embedded shell
- before merging a change to a runbook whose steps someone will follow

It does not fire for prose that ships no commands, for a check or a test, which
is a different discipline, or where CI already runs the procedure on every push,
which is a stronger proof than any fixture.

## Why the old rule gets run too

A fix that is never compared against what it replaced is a claim, and the claim
is wrong more often than it feels. In the session this was extracted from, a
classifier was rewritten to compare symlinks by target rather than by content.
The first fixture retargeted a link and the rewritten rule answered correctly,
which looked like proof and was not: the superseded rule answered correctly too,
because following a link to a different file usually finds different bytes. The
defect only appeared once the fixture pointed the link at a file whose contents
were exactly the old target's name, at which point the old rule reported the
retargeted link as unchanged and offered it for deletion.

The lesson is not about symlinks. A fixture that passes on the first attempt has
usually failed to contain the case, and running the superseded version is the
cheapest way to find that out.

## Example

A skill claims to classify every uncommitted path in a working tree. The claim
names five cases; the awkward shapes it implies add four more.

One fixture holds all nine: a modified file, a deleted one, a rename, an
untracked file already on the branch, a genuinely new one, a path containing a
space, a path beginning with a dash, a changed binary, and a file whose only
change is its mode. Each case is given its expected verdict in advance.

The published loop is extracted from the document rather than retyped, and run
with only the declared fill-ins substituted. Three cases come back wrong, and
one of them is wrong in the direction that destroys work: a modified file is
reported as already landed, because the status format quotes and reshapes paths
the loop assumed were plain, and the resulting path matches nothing.

Each fix is then run beside the rule it replaces, so the write-up says what the
old rule answered rather than that the new one looks better. The fixture is
deleted, and the report says so.

## Related

- `prove-the-check-can-fail` (this plugin): the mirror image, for a check rather
  than a procedure. That one mutates the subject until the check goes red; this
  one runs the procedure until its own answers can be read.
- `diagnose-a-lying-signal` (this plugin): for when the disagreement is with a
  status surface rather than with a documented step.
- `validate-skill-against-real-project` (agent-config): the complement, running
  a skill against a real repository instead of a constructed one, which finds
  what a fixture's tidiness hides.
