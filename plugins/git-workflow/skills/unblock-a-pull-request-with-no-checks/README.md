# unblock-a-pull-request-with-no-checks

Tells a pull request whose checks **failed** from one whose checks **never
existed**, and unblocks the second without hiding the two problems that wear the
same disguise.

Read [SKILL.md](SKILL.md) for the procedure. This file is why it exists.

## Silence is not a verdict

A merge box reading BLOCKED with an empty checks list looks like patience is the
answer. It is not: where the required checks were never raised, nothing is
queued and nothing arrives, however long anyone waits.

The common cause is an automated pull request. A pull request GitHub attributes
to Actions raises no `pull_request` events, so the workflows that would report
never start, and a repository that requires two checks has just produced a pull
request that can never satisfy it. One repository hit this three times across
two weeks, each time losing a worktree and a commit to the same rediscovery,
because the state reads as pending rather than as broken.

## What it refuses to do

Three other causes produce the same empty list, and forcing checks onto them
destroys the evidence:

- a run that started and died before any job, which has a real actor and a real
  run record with zero jobs;
- a diff that misses every workflow's `paths:` filter, where the fix is the
  requirement rather than the pull request, because a required check that is
  path-filtered will be pending forever on every unrelated change;
- a run held for a maintainer's approval, which a fork or a first-time
  contributor produces. That one is the opposite of the automation case: it is
  waiting on a person, and a commit only puts a second run in the same queue.

So the skill identifies the cause first and only then takes the one action that
is safe: a single empty commit from a human identity, which raises the
`synchronize` event the pull request never had.

## The fix that stops it recurring

Automation that opens pull requests should open them as a person, with a
fine-grained token used for the push as well as the opening: a refresh is
attributed to whoever pushed, so a mixed setup leaves checks pointing at an
older commit, which is worse than none at all.
