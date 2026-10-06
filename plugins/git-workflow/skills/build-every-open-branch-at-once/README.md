# build-every-open-branch-at-once

Builds one throwaway artefact carrying every open pull request, so a feature
split into reviewable slices can be tried as a whole before the first slice
merges. The combination happens in a worktree that is never pushed, and the
conflicts it hits are resolved as unions rather than by picking a side.

Read [SKILL.md](SKILL.md) for the procedure. This file is why the resolution
rule is the part worth writing down.

## Why the conflicts are always additions

Branches cut from one base and built in parallel rarely disagree about logic.
They disagree about lists: both added a string at the same anchor, both gave a
sealed hierarchy a new case, both added an arm to the same `when`. Every one of
those is two additions meeting, and every one of them resolves by keeping both.

Picking a side there succeeds. The merge completes, the build compiles, the
artefact installs, and one of the features it was built to demonstrate is simply
absent. Nobody finds it by reading the diff afterwards, because the diff of a
merge commit shows the resolution rather than what it discarded. In the session
this was extracted from, the same three files conflicted on three separate
rounds, and the resolution was identical every time.

## Why it is never pushed

The commits are guesses. They were made in a minute, against no review, to
answer a question that will be stale by the afternoon. A branch that carries
them looks like any other branch in the forge, and the moment one exists
somebody can open a pull request from it, cut work from it, or merge it, which
puts unreviewed resolutions into the integration branch wearing the authority of
the slices they came from.

Resetting the same worktree each time is what keeps that impossible. It also
makes the next round cheaper than the last, which is the only reason anybody
runs this procedure a third time.
