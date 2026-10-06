---
name: build-every-open-branch-at-once
description: >
  Use when a feature is split across several open pull requests and somebody
  wants to try the whole of it before any of them land — "get me a build",
  "can I test it end to end", "what does it look like with all of that in".
  Produces one throwaway build carrying every open branch, resolved in a
  worktree that is never pushed. NOT for merging those branches (that is
  merge-on-go-ahead), NOT for a stack where each child already contains its
  parent, and NOT for building one branch, which needs no procedure.
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
   worktree of its own, reset to the integration branch, reused every time:

   ```bash
   git fetch origin --prune
   git -C <throwaway-worktree> reset --hard origin/<integration-branch>
   ```

   Never the primary checkout, and never a branch that has a pull request. The
   commits this makes are resolutions nobody reviewed, and a push would put
   them in front of a reviewer as though somebody had.

2. **Merge in the order the stack implies**, parents before children, and
   independent branches in any order after them. A child that already contains
   its parent is merged once, as the child.

   ```bash
   for b in <branches-in-order>; do git merge --no-edit "origin/$b"; done
   ```

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
   git diff --name-only --diff-filter=U        # what is actually conflicted
   ```

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
