---
name: merge-on-go-ahead
description: >
  Use when the user authorises merging pull requests they name: "merge #4",
  "12 and 13 are ready", "land 21 and 22", or a bare "go ahead" in a thread
  about one identified PR. Owns only the merge itself: it confirms the authorisation covers
  this PR at its current head, checks the gates the repo actually enforces,
  merges in the repo's own convention, orders a set that shares a file and
  stops after each of its merges for a refresh, and waits out the
  recomputation before touching a dependent PR. Do NOT fire without an authorisation
  naming the PRs, on a promotion to the branch people install from (that is
  a release), or to decide WHETHER something should merge.
---

# Merge on a go-ahead

Merging is the one step in a pull request's life that cannot be undone quietly.
Every neighbouring procedure stops at this line on purpose: a checks watcher
authorises reporting, not merging, and a review loop answers findings and hands
the button back. This skill picks up exactly there, and it starts by proving the
permission still applies rather than assuming the last one carried forward.

The failure it prevents is not a broken merge. It is a *correct-looking* one:
the right button pressed on a PR whose head moved after the go-ahead, or in a
merge style the repo forbids, or while a review sits unanswered.

## Procedure

1. **Bind the authorisation to a PR and a commit.** Write down which numbers
   were named, then pin each head:

   ```bash
   gh pr view <n> --json number,headRefOid,baseRefName,isDraft,mergeable,mergeStateStatus
   # one line per authorised PR, kept for step 7; a single `head` variable is
   # overwritten by the next PR and then matches the wrong one
   gh pr view <n> --json number,headRefOid --jq '[.number, .headRefOid] | @tsv' >> authorised.tsv
   ```

   An authorisation is per pull request and per head. It does not roll forward
   to a sibling PR, to the next one in a stack, or to a new commit pushed after
   it was given, however small. If the head moved, the go-ahead was for
   something the reader no longer sees; say so and ask again. A PR with a row
   in `stopped.tsv` (step 2) is pinned only when its head differs from that
   row's latest SHA, and only after the user has seen the change since it
   (`gh api repos/<owner>/<repo>/compare/<stopped sha>...<head sha>`); a head
   that still equals it was never refreshed, so refuse.

2. **When the authorised PRs share a file, find it and order them before the
   first merge.** With the authorised numbers in place of these:

   ```bash
   d=$(mktemp -d); ok=1
   for n in 12 13 14; do
     gh pr diff "$n" --name-only > "$d/$n" || { echo "cannot read #$n"; ok=0; }
   done
   [ "$ok" = 1 ] && cat "$d"/* | sort | uniq -d; rm -rf "$d"
   ```

   A failed read stops the procedure, since a missing list compares as no
   overlap. Order the whole set by dependency whatever the output: a PR whose
   base is another's head, or whose branch contains another's commits, lands
   after that one. Where there is output, among PRs free to go in either
   order, land the widest edit to the shared files first (additions plus
   deletions in those files, per `gh pr view <n> --json files`), so each later
   PR meets a base that already says the most. The set and its shared files
   are fixed here and this step does not run again.

   Where there is output, every merge changes the base under the PRs still
   open that touch a shared file, and a go-ahead covers a head, not what it
   becomes on a new base. So **after each merge, once step 10 has reported
   it, stop**: for each authorised PR still open that touches a shared file,
   record its head and name it:

   ```bash
   gh pr view <n> --json number,headRefOid --jq '[.number, .headRefOid] | @tsv' >> stopped.tsv
   ```

   Say each needs refreshing against the new base, a review at the refreshed
   head, and a new go-ahead before it merges; step 1 enforces it. The refresh
   is not this skill's job; whoever does it keeps both sides' lines wherever
   both PRs only added to the shared files, keeping one copy of a line both
   added identically, and reads those files against what both meant, since two
   edits can merge cleanly and still be wrong together (two PRs that each
   raised a count from 10 to 11 merge to 11, where 12 may have been meant).
   Once the set's last PR has merged, read the shared files against what
   landed: a count or list that several PRs each edit is where the result goes
   wrong, and a statement that stays true beats a maintained tally.

3. **Confirm the gates the repo enforces, not the ones you remember.** Read the
   required contexts rather than eyeballing a checks list:

   ```bash
   gh api repos/<owner>/<repo>/branches/<base>/protection \
     --jq '.required_status_checks.contexts'
   gh api repos/<owner>/<repo>/rules/branches/<base>          # rules in force here
   ```

   Two sources, because either can be empty while the other gates. A branch
   with no classic protection answers the first call with `404 Branch not
   protected`, which is an answer (nothing is required here), not a failure to
   route around. The second is the one to trust for rulesets: a repository-wide
   listing tells you a ruleset exists, while this endpoint tells you which
   rules apply to *this* base, with their parameters.

   Judge each check by `status` and `conclusion` per the checks-watching
   discipline (`await-pr-checks` covers it, including the reruns and the
   unpinned reads). Counting the word "fail" in a rendered checks list is not
   judging it: job names contain that word on purpose, and a suite whose whole
   point is a must-fail case reports itself as one.

4. **Confirm the review gate is answered, not merely present.** Where the repo
   requires a review before merge, an automated one that posted findings still
   needs the reply that dispositions them (`pr-comment-loop` owns that loop).
   A merge on top of an unanswered review erases the finding and the record of
   why it was ignored, in one action.

5. **Look the merge method up. Do not carry it between repos.**

   ```bash
   gh api repos/<owner>/<repo> --jq '{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge}'
   gh api repos/<owner>/<repo>/rules/branches/<base> > rules.json
   # every rule that narrows the choice, not just the first one
   jq '[.[] | select(.type == "pull_request") | .parameters.allowed_merge_methods] | add' rules.json
   jq 'any(.[]; .type == "required_linear_history")' rules.json    # true rules out --merge
   grep -rniE "squash|rebase|merge commit" CONTRIBUTING* docs/ .github/ 2>/dev/null | head
   ```

   The answers are not the same question. The repository flags say what is
   *permitted anywhere*; the rules say what is *allowed on this base*, and
   several can apply at once, so intersect them rather than reading the first.
   A `required_linear_history` rule removes `--merge` whatever the merge-method
   list says. What is left is narrowed by what the project says it prefers, and
   `rebase` is a real answer there, not only `squash` and `merge`.

   Repos that allow several are the dangerous ones: allowed is not preferred,
   and the preference is usually written down. A project can also want
   different methods for different bases, most often a squash into the
   integration branch and a merge commit for the promotion, because a squash
   is not the commits it squashed and breaks the ancestry the next step relies
   on.

6. **Deal with anything stacked on this PR before merging it.** A child whose
   base is this branch does not follow the parent through the merge; it is left
   pointing at a branch nobody will push to again, and its checks keep running
   against it. Retarget the children first, or delete the parent branch as part
   of the merge if that is what retargets them on this host. Polling a child's
   mergeability does not repair a stale base, and `branch-hygiene` owns the
   full post-merge sequence.

7. **Merge one at a time, in the stated method, bound to the authorised head.**
   Let the merge command own the line it runs on: some tool wrappers classify a
   chained merge differently from a bare one, and a merge refused halfway
   through a compound command is harder to reason about than one that simply
   ran.

   ```bash
   head=$(awk -v n=<n> '$(1) == n { h = $(2) } END { print h }' authorised.tsv)   # this PR's latest pin
   [ -n "$head" ] || { echo "no pin recorded for #<n>"; exit 1; }
   gh pr merge <n> --squash --match-head-commit "$head"        # --merge or --rebase, per step 5
   ```

   `--match-head-commit` is step 1's pin made mechanical: if anything was
   pushed between the go-ahead and this command, the merge is refused instead
   of quietly landing a commit nobody authorised. An empty value is not a pin:
   `gh` drops the flag when it is blank, so a PR with no row in the file would
   merge whatever head it has now, and the guard stops there instead. A PR
   authorised again after a push has two rows, and the latest is the go-ahead
   that counts.

8. **Between dependent merges, wait for the recomputation, and do not read a
   failure as an answer.** Where step 2 stopped the set, it stays stopped;
   otherwise, after a parent lands, a child's `mergeable` reads `UNKNOWN`
   until the host recomputes it, and `UNKNOWN` is not `false`. A bare
   command substitution in the loop test turns a failed API call into an empty
   string, which is also not `UNKNOWN`, so the loop exits on the error:

   ```bash
   for _ in $(seq 1 24); do
     state=$(gh pr view <child> --json mergeable --jq .mergeable) || state=
     [ -n "$state" ] && [ "$state" != "UNKNOWN" ] && break
     sleep 5
   done
   [ -n "$state" ] && [ "$state" != "UNKNOWN" ] || { echo "mergeability never settled"; exit 1; }
   ```

   Acting on the interim value either merges something the host has not
   finished judging, or abandons a PR that was fine two seconds later.

9. **Prove it landed with the merge commit, not the branch tip.** A squash
   produces a commit that is not the branch's commits, so asking whether the
   *head* is an ancestor of the base answers "not merged" for work that is
   fully merged. The merge commit the host recorded is on the base, so ask
   about that one:

   ```bash
   git fetch --prune
   mc=$(gh pr view <n> --json mergeCommit --jq .mergeCommit.oid)
   git merge-base --is-ancestor "$mc" origin/<base> && echo landed
   ```

   Where no merge commit is recorded (a PR closed and applied by hand), fall
   back to content. The branch may be gone by then, so capture the paths before
   merging and read the head back from the ref the host keeps:

   ```bash
   # before the merge
   git diff --name-only origin/<base>...origin/<branch> > paths.txt

   # after it, against the authorised head rather than a branch that may not exist
   git fetch origin "refs/pull/<n>/head:refs/pr/<n>"
   git diff --stat origin/<base> "refs/pr/<n>" -- $(cat paths.txt)
   ```

   Empty output means those paths are identical on the base. Read it the same
   day: once another PR touches one of them, a difference stops saying anything
   about this one.

10. **Report per PR, naming the method**: `#12 squashed into develop, #13
   squashed, both branches deleted`. Cleaning up the merged branches and their
   worktrees is its own procedure (`branch-hygiene`); a promotion to the branch
   people install from is a release cycle, not a merge, and belongs to
   `close-the-release-cycle`.

## When to STOP

- **No authorisation names this PR.** "Looks good", an approving review, or a
  go-ahead given for a different PR is not one. Report the PR as ready and stop.
- **The head moved after the authorisation.** Re-ask against the new commit
  rather than deciding the change was too small to matter.
- **A required check is missing rather than failing.** Absent and passing look
  identical in a summary and are opposites; treat missing as pending.
- **A review posted findings that have no reply.** Answer them first, or hand
  back; merging closes the thread by force.
- **The authorised PRs share a file and one has just merged.** The rest wait
  for a refresh and a new go-ahead, as step 2 says.
- **The repo allows several merge methods and states no preference.** Ask which
  one. Guessing here is the one mistake in this procedure that rewrites history
  for everybody.
- **The base is the branch people install from.** That is a promotion with
  steps after the merge (tag, floating tag, back-merge) and a different owner.
- **The merge is refused for a reason you did not diagnose** (protection, a
  queue, a conflict). Report the refusal with its message; retrying a blocked
  merge with a different flag is how a rule gets worked around instead of read.
