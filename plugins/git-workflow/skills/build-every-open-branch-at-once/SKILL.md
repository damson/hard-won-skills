---
name: build-every-open-branch-at-once
description: >
  Use when a feature is split across several open pull requests and somebody
  wants to try the whole of it before any of them land: "get me a build", "can I
  test it end to end", "what does it look like with all of that in". Produces one
  throwaway build carrying every open branch, resolved in a worktree that is never
  pushed. NOT for merging those branches (that is merge-on-go-ahead), NOT for a
  stack where each child already contains its parent, NOT for building one branch,
  which needs no procedure, and NOT for packaging a build somebody will judge a
  fix by, where the combination is one step of a longer handover that
  hand-over-a-test-build owns.
---

# Build every open branch at once

A feature cut into reviewable slices cannot be tried until the last slice
merges, which is the wrong order: the slices are open *because* nobody has
decided yet, and the decision wants the thing in a hand.

The build that answers it is a throwaway. Its value is that it exists for an
hour; its danger is that it looks exactly like a branch worth keeping, and the
resolutions inside it are guesses nobody reviewed.

## Procedure

1. **Make the combination somewhere that cannot be pushed by accident.** A
   worktree of its own, on a branch nothing has ever opened a pull request for,
   reset to the integration branch and reused every time:

   ```bash
   base=develop                                  # the integration branch
   br=throwaway/combined-build                   # fill these three in
   wt=$HOME/throwaway-combined-build             # OUTSIDE the repository

   git fetch origin --prune

   # the forge is the check here, not the branch name: a name that once had a
   # pull request can be pushed to again, and the push looks reviewed
   if [ -n "$(gh pr list --head "$br" --state all --json number --jq '.[].number')" ]
     then echo "$br has carried a pull request before: choose another name"
   elif git -C "$wt" rev-parse --git-dir >/dev/null 2>&1
     then git -C "$wt" checkout -q -B "$br" "origin/$base"    # reuse, from round two on
          git -C "$wt" reset --hard "origin/$base"
     else git worktree add -B "$br" "$wt" "origin/$base"      # first round
   fi
   ```

   **The first branch of that `if` is the one worth reading.** `reset --hard`
   against a worktree that does not exist yet fails, and on a later round a bare
   reset does not say which branch it is resetting, so the same command either
   errors or lands the combination on whatever that worktree was last left on.
   `worktree add -B` creates the branch and the checkout together; `checkout -B`
   re-points it on every round after.

   Never the primary checkout, and never a branch that has a pull request. The
   commits this makes are resolutions nobody reviewed, and a push would put
   them in front of a reviewer as though somebody had.

2. **Merge in the order the stack implies**, parents before children, and
   independent branches in any order after them. A child that already contains
   its parent is merged once, as the child.

   **One at a time, and in the worktree.** A merge that stops at a conflict
   leaves the tree mid-merge, and the next iteration of a loop refuses or
   compounds it; a `git merge` without `-C "$wt"` merges into whatever the
   primary checkout has checked out, which is the one thing step 1 exists to
   prevent.

   ```bash
   branches="feat/one feat/two feat/three"       # parents before children

   for b in $branches; do
     if git -C "$wt" merge --no-edit "origin/$b"
       then echo "merged $b"
       else echo "$b conflicts: resolve it with step 3, then continue from here"
            break
     fi
   done
   ```

   The `break` is deliberate. Stopping on the first conflict is what makes step 3
   a resolution of one merge rather than an archaeology of three.

3. **Expect the conflicts in the same places every time, and resolve them as a
   union.** Branches built in parallel off one base conflict where each
   *appended* to a shared list rather than where either edited the other's
   work:

   - a translations or strings file, where both added entries at the same
     anchor;
   - a sealed hierarchy or enum that each branch gave a new case;
   - a `when` over that hierarchy, which each branch gave a new arm;
   - a registry, module or dependency list.

   In all of them both sides are additions and the resolution is **keep both,
   in either order**, never one side. Taking a side here is the failure that
   produces a build missing a feature its branch was merged for, and it is
   invisible afterwards because the merge succeeded.

   ```bash
   git -C "$wt" diff --name-only --diff-filter=U     # what is actually conflicted

   # edit each one to carry both sides, then finish THIS merge before the next
   git -C "$wt" add -u                               # every path you resolved
   git -C "$wt" commit --no-edit

   # the only answer to "is this merge finished"
   git -C "$wt" rev-parse -q --verify MERGE_HEAD >/dev/null \
     && echo "STILL mid-merge" || echo "merge completed"
   ```

   **Completing the merge is a step, not an implication.** A resolved working
   tree with nothing committed is still a merge in progress: the next `git merge`
   refuses, and `MERGE_HEAD` survives long enough that a later reader cannot tell
   which round they are in. Then go back to step 2 and continue from the branch
   after the one that conflicted.

4. **Compile before believing the resolution.** A union merge of two `when`
   arms compiles only if the hierarchy got both cases, and that is exactly the
   pair most likely to have been resolved separately in two hunks.

5. **Build, install, and say what it is.** Name the artefact for the question it
   answers rather than for a branch, because the branch set is what makes it
   true and the branch set changes hourly. Hand it over with the list of what
   is in it and the heads they were at.

6. **Leave the worktree dirty and unpushed.** Reset it next time rather than
   tidying it now: a clean throwaway invites someone to branch from it.

## When to STOP

- **One pull request.** Build that branch; there is nothing to combine.
- **The build is a handover rather than an answer to "what does all of it look
  like".** Somebody judging a fix by it needs the suite run on the combination
  and each change shown to be inside the artifact, which is a longer procedure
  that this one is the first step of. `hand-over-a-test-build` owns it where that
  plugin is installed; where it is not, this still builds the combination and the
  rest is yours.
- **A pure stack**, where the last child already contains every ancestor. Build
  the child.
- **A conflict inside logic both sides genuinely changed**, rather than two
  additions to one list. That is a real design collision between two open pull
  requests and it is worth more than a test build: report it, because it is
  going to happen again at merge time in front of a reviewer.
- **The combination does not compile and the fix is not obvious.** Say which two
  branches disagree. A throwaway build is not worth debugging an integration
  nobody has asked for yet.
- **Somebody asks to push it, keep it, or open a pull request from it.** It is
  resolutions nobody reviewed. The branches merge on their own go-aheads, in
  their own order, through whatever gate the repository runs.
