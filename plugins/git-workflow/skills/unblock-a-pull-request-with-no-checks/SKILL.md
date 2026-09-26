---
name: unblock-a-pull-request-with-no-checks
description: >
  Use when a pull request cannot merge because its required checks never ran at
  all, rather than having run and failed: a merge box reading BLOCKED with an
  empty checks list, a pull request opened by Actions or another bot, "the
  checks never started", "it has been pending for hours". Separates the three
  causes that look identical from the outside, takes the one that is safe to
  force, and names the durable fix, because the ones that recur recur every
  cycle. Do NOT fire when a check has reported red (that is its log's job), when
  one is merely still running (that is await-pr-checks), or when the repository
  requires no checks at all and nothing is actually blocked.
---

# Unblock a pull request with no checks

A check that failed and a check that never existed look the same in a merge box
and opposite in every other way. The first is a verdict; the second is silence,
and silence cannot be waited out. A pull request in that state stays unmergeable
for as long as anyone is patient, which on one repository was three separate
pull requests over two weeks, each losing a worktree and a commit to the same
rediscovery.

## Procedure

1. **Count what reported on the head SHA, and take the SHA from the pull
   request.** The rollup a UI or `gh pr checks` renders answers for whatever head
   it last saw, and it renders an empty list and a passing list the same shade of
   quiet. A remote-tracking ref is no better: it answers for the last time you
   fetched, and for a pull request from a fork it does not exist at all.

   ```bash
   repo=owner/name                               # fill these two in
   pr=123

   if ! command -v gh >/dev/null 2>&1 || ! gh auth status >/dev/null 2>&1
     then echo "gh missing or unauthenticated: nothing below ran, and an empty"
          echo "answer from it is not evidence that the checks are missing"
     else
       sha=$(gh pr view "$pr" --repo "$repo" --json headRefOid --jq .headRefOid)
       runs=$(gh api "repos/$repo/commits/$sha/check-runs" --jq '.check_runs | length')
       stat=$(gh api "repos/$repo/commits/$sha/statuses" --jq 'length')
       echo "head $sha: $runs check run(s), $stat commit status(es)"
   fi
   ```

   **Both numbers, because they are separate registers.** The check-runs endpoint
   does not return legacy commit statuses, so a repository whose gate is posted as
   a status counts zero through the first call and sends this diagnosis down a
   branch that does not apply to it. Either number above zero means this skill is
   the wrong one: something reported, so judge it.

   The `gh` guard is there because an unavailable tool and an empty checks list
   produce the same silence, one step apart, and this whole procedure is built on
   telling those two apart.

2. **Read what the base actually requires.** Zero checks only blocks where
   something is required, and requirements live in two places that can each be
   empty while the other gates:

   ```bash
   base=develop                                  # the branch this pull request targets

   gh api "repos/$repo/rules/branches/$base" \
     --jq '[.[] | select(.type=="required_status_checks")
            | .parameters.required_status_checks[].context]'
   gh api "repos/$repo/branches/$base/protection" \
     --jq '.required_status_checks.contexts'
   ```

   A base with no classic protection answers the second call `404 Branch not
   protected`. That is an answer, nothing is required there, not a call to
   retry.

   Empty in both, and the pull request is blocked by something else: stop here
   and read the merge box's own reason rather than pushing commits at it.

3. **Name the cause before touching anything.** Four produce an empty checks
   list, and only one of them is safe to fix by force:

   | Cause | Tell | Fix |
   |---|---|---|
   | The pull request was opened by automation | `author` is an app or bot, and no `pull_request` run exists for the head at all | Step 4, then step 6 |
   | A run started and died before its jobs | a run exists with `total_count: 0` jobs, actor is a real login | Its own diagnosis; forcing checks hides it |
   | Every workflow is path-filtered past this diff | runs exist for other commits, none for this one, and the workflow files carry `paths:` | Fix the requirement, not the pull request: a required check must not be path-filtered |
   | A run exists and is waiting for a maintainer to approve it | a run for this head with status `action_required` or `waiting`, usually a fork or a first-time contributor | Approve it. A commit raises another run that waits the same way |

   ```bash
   gh pr view "$pr" --repo "$repo" --json author,headRefOid \
     --jq '{author: .author.login, head: .headRefOid}'
   gh run list --repo "$repo" --commit "$sha" \
     --json databaseId,event,status,conclusion
   ```

   A pull request GitHub attributes to Actions raises no `pull_request` events,
   by design, so the workflows that would report never start. Nothing is
   waiting, nothing is queued, and nothing will change on its own.

   **The fourth cause is the one that looks like the first and is its opposite.**
   An approval-gated run does exist, and it is waiting on a person rather than on
   an event, so the empty checks list resolves the moment somebody approves it and
   an empty commit only adds a second run in the same queue. The two are told
   apart by the run list, not by the checks list, which is why step 1's count is
   a screen rather than a diagnosis:

   ```bash
   gh run list --repo "$repo" --commit "$sha" \
     --json status,conclusion,event \
     --jq '[.[] | select(.status == "action_required" or .status == "waiting")] | length'
   ```

   Above zero, stop and ask for an approval.

4. **Unblock it with one commit from a person.** A push attributed to a human
   identity raises the `synchronize` event the pull request never had:

   ```bash
   branch=$(gh pr view "$pr" --repo "$repo" --json headRefName --jq .headRefName)

   git commit --allow-empty -m "Let the required checks run on this pull request"
   git push origin "HEAD:refs/heads/$branch"
   ```

   Say in the message why an empty commit exists, or the next reader deletes it
   as noise. Then wait out the checks properly, by name and at the new SHA.

5. **Do not reach for the alternatives first.** Closing and reopening the pull
   request raises no runs either; re-running from the Actions tab reproduces a
   run that never started; and an administrative merge past the requirement
   ships code no check has ever seen, which is the one outcome worse than the
   block.

6. **Fix the cause, or it returns next cycle.** Automation that opens pull
   requests should open them as a person: a fine-grained token with contents and
   pull-request write, used for the push as well as the opening, because a later
   refresh is attributed to whoever pushed. Check for that token before the work
   that produces the pull request, not at the push, so a missing one costs
   nothing. Where the automation cannot hold a token, say in its own output that
   its pull requests need a commit before they can merge.

## When to STOP

- **A check has reported red.** This skill has nothing to say about it: read the
  failing step's log.
- **Checks exist and are still running.** Waiting is the answer, and doing it
  without mistaking silence for success is `await-pr-checks`.
- **The base requires nothing.** Zero checks blocks nothing; the merge box is
  refusing for another reason, and pushing commits will not reveal it.
- **A run exists with zero jobs and a human actor.** That is a startup failure
  wearing this disguise, and forcing a fresh run buries the evidence.
- **A run exists and is waiting for approval.** Nothing here is broken and a
  commit does not help: it needs a maintainer, and that is a message rather than
  a push.
- **The pull request is blocked by a review requirement**, not a check.
  Commits do not satisfy reviewers.
