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

1. **Count the check runs on the head SHA, and get the SHA from the git ref.**
   The rollup a UI or `gh pr checks` renders answers for whatever head it last
   saw, and it renders an empty list and a passing list the same shade of quiet.

   ```bash
   sha=$(git rev-parse "origin/<branch>")
   gh api "repos/<owner>/<repo>/commits/$sha/check-runs" --jq '.check_runs | length'
   ```

   A number greater than zero means this skill is the wrong one: the checks
   exist, so judge them.

2. **Read what the base actually requires.** Zero checks only blocks where
   something is required, and requirements live in two places that can each be
   empty while the other gates:

   ```bash
   gh api "repos/<owner>/<repo>/rules/branches/<base>" \
     --jq '[.[] | select(.type=="required_status_checks")
            | .parameters.required_status_checks[].context]'
   gh api "repos/<owner>/<repo>/branches/<base>/protection" \
     --jq '.required_status_checks.contexts'
   ```

   Empty in both, and the pull request is blocked by something else: stop here
   and read the merge box's own reason rather than pushing commits at it.

3. **Name the cause before touching anything.** Three produce an empty checks
   list, and only one of them is safe to fix by force:

   | Cause | Tell | Fix |
   |---|---|---|
   | The pull request was opened by automation | `author` is an app or bot, and no `pull_request` run exists for the head at all | Step 4, then step 6 |
   | A run started and died before its jobs | a run exists with `total_count: 0` jobs, actor is a real login | Its own diagnosis; forcing checks hides it |
   | Every workflow is path-filtered past this diff | runs exist for other commits, none for this one, and the workflow files carry `paths:` | Fix the requirement, not the pull request: a required check must not be path-filtered |

   ```bash
   gh pr view <n> --json author,headRefOid --jq '{author: .author.login, head: .headRefOid}'
   gh run list --commit "$sha" --json databaseId,event,status,conclusion
   ```

   A pull request GitHub attributes to Actions raises no `pull_request` events,
   by design, so the workflows that would report never start. Nothing is
   waiting, nothing is queued, and nothing will change on its own.

4. **Unblock it with one commit from a person.** A push attributed to a human
   identity raises the `synchronize` event the pull request never had:

   ```bash
   git commit --allow-empty -m "Let the required checks run on this pull request"
   git push origin HEAD:refs/heads/<branch>
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
- **The pull request is blocked by a review requirement**, not a check.
  Commits do not satisfy reviewers.
