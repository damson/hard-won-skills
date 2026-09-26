# unblock-a-pull-request-with-no-checks

Tells a pull request whose checks **failed** from one whose checks **never
existed**, and unblocks the second without hiding the two problems that wear the
same disguise.

Read [SKILL.md](SKILL.md) for the procedure. This file is why it exists.

## Silence is not a verdict

A merge box reading BLOCKED with an empty checks list looks like patience is the
answer. It is not: where the required checks were never raised, nothing is
queued and nothing arrives. One repository hit this three times in two weeks,
losing a worktree and a commit to the same rediscovery each time, because the
state reads as pending rather than as broken.

Four causes produce that empty list and only one is safe to force, so the skill
names the cause before it acts:

| Cause | What it needs |
|---|---|
| Actions opened the pull request, so no `pull_request` event was raised | one empty commit from a person, which is the only case a commit repairs |
| A run started and died before its jobs | its own diagnosis; forcing a fresh run buries the evidence |
| Every workflow is path-filtered past this diff | fixing the requirement, because a required check must never be path-filtered |
| A run is held for a maintainer's approval | that maintainer. A commit only queues a second run behind it |

## Using it

It fires when a merge is blocked and the thing blocking it never reported:

- "the checks never started on this PR"
- "it has been pending for hours and nothing is queued"
- "the merge box says blocked but there are no checks"
- "CI did not pick up the bot's pull request"
- a pull request opened by Actions, Dependabot or a release workflow, with an
  empty checks list

It deliberately does **not** fire on:

- a check that reported red, which is its log's job
- a check that is still running, which is `await-pr-checks`
- a base that requires nothing, where zero checks blocks nothing and the merge
  box is refusing for another reason
- a blocking review, because commits do not satisfy reviewers

## Example

A release workflow opened a pull request whose two required checks were missing.
The whole diagnosis, with the head read from the pull request rather than a local
ref and both registers counted, because a gate posted as a commit status is
invisible to the check-runs endpoint:

```console
$ repo=acme/widgets
$ pr=482
$ sha=$(gh pr view "$pr" --repo "$repo" --json headRefOid --jq .headRefOid)
$ gh api "repos/$repo/commits/$sha/check-runs" --jq '.check_runs | length'
0
$ gh api "repos/$repo/commits/$sha/statuses" --jq 'length'
0
$ base=$(gh pr view "$pr" --repo "$repo" --json baseRefName --jq .baseRefName)
$ gh api "repos/$repo/branches/$base/protection" --jq '.required_status_checks.contexts'
["validate","codecov/project"]
$ gh pr view "$pr" --repo "$repo" --json author --jq .author.login
github-actions
$ gh run list --repo "$repo" --commit "$sha" --json status \
    --jq '[.[] | select(.status == "action_required" or .status == "waiting")] | length'
0
```

An app author, nothing required missing, no run at all and none awaiting
approval: the first row of the table, and the only one a commit repairs. One
empty commit raised the `synchronize` event the pull request never had, and both
checks ran.

Had that last count come back above zero, the answer would have been the
opposite. A run was already waiting on a maintainer, and a commit would only have
queued a second one behind it.

## The fix that stops it recurring

Automation that opens pull requests should open them as a person, with a
fine-grained token used for the push as well as the opening: a refresh is
attributed to whoever pushed, so a mixed setup leaves checks pointing at an
older commit, which is worse than none at all.
