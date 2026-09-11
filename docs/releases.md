# How this repo releases

Two long-lived branches. `develop` integrates; `main` is what people install.
`claude plugin marketplace add` clones the default branch, so a commit is
released the moment it reaches `main`: nothing else is required, and nothing
else can hold it back.

## The first release has to be done by hand

GitHub runs `schedule` and `workflow_dispatch` only from the copy of a workflow
on the **default branch**. Until `release.yml` exists on `main`, it is not
registered at all: `gh workflow list` does not show it and a dispatch answers
`404: workflow not found on the default branch`. The release automation cannot
put itself on `main`, because putting it there *is* a release.

So the first promotion is manual: bump the changed plugins, open `develop → main`,
merge it **with a merge commit**. Every release after that is automatic. The same
applies if the workflow is ever renamed: the new filename is unregistered until
it reaches `main`.

## The cadence

`.github/workflows/release.yml` runs daily and asks three questions. All three
must say yes, or it logs why it is holding and exits:

1. **Does `develop` carry content `main` does not?** Measured as a tree diff,
   not a commit count: after a squashed release plus its back-merge, `develop`
   is "ahead" by every commit the squash absorbed while carrying nothing new,
   and a count gate would propose an empty release. Identical trees, no release.
2. **Is the newest tag at least three days old?** This is what makes the cadence
   three days. It is enforced in the job rather than in the cron expression
   because GitHub's schedule has no clean three-day form: `*/3` on day-of-month
   restarts every month, leaving a one-day gap after the 31st and a four-day one
   in February. The age is measured from the **committer date of the commit the
   tag points at**, not from when the tag was created, so a tag applied later to
   an older commit opens the gate sooner than its own age suggests.
3. **Is there no release PR already open?** If there is, it refreshes that one.

`workflow_dispatch` bypasses the three-day gate. It never bypasses the other two:
you cannot release nothing.

## What a release does

- Patch-bumps `plugin.json` for **only** the plugins with changes under
  `plugins/<name>/**`, and commits that to `develop`. Untouched plugins keep
  their version, so `claude plugin update` re-fetches only what moved.
- Opens the `develop → main` pull request with the inventory: which versions
  moved, which PRs are in the batch, the diffstat, the commits.
- Runs the CI suite and enables auto-merge.
- Once merged, tags `vYYYY.MM.DD` and publishes a GitHub Release. `main` is
  only tagged once it is a release point; while `develop` is ahead and no
  release has ever happened, `main` is a baseline and is left alone. Tagging
  it would publish a release containing none of the merged work, and the
  fresh tag would then hold the real first release behind the three-day gate.
- Fast-forwards `develop` back to `main`, so the branches do not drift.

Marketplace tags are CalVer and plugin versions are semver on purpose. The tag
answers *when*; a plugin's version answers *what changed in it*.

## Five couplings that will not announce themselves

**One dispatch promotes; tagging needs a second, until the App token is
configured.** The release pull request auto-merges under `GITHUB_TOKEN`, and a
push made with that token does not trigger workflows, so the `push: main` run
that would tag never starts. The first dispatch leaves `main` promoted and the
versions bumped with no tag; a second runs the tag job against it. The tell is
`gh run list --workflow=Release` showing no `push` event for the merge, only the
dispatch you asked for. Cost two dispatches on 2026-09-05, for `v2026.09.05.1`,
and again on 2026-09-08 and 2026-09-09.

**The same missing event also swallows issue closing**, which is the half nobody
looks for. A squash commit saying `Closes #86` reached `main` with the promotion
on 2026-09-08 and the issue was still open the next day, along with two others;
all three were closed by hand. A keyword in a pull request body would not have
helped either, because that path needs the pull request's base to be the default
branch, and a feature pull request targets `develop`. Put the keyword in the
commit message, then check the issue rather than assuming.

Both of these are the same root cause and have one fix, below.

## Releasing under an App token

The workflow mints an installation token when two secrets are present and falls
back to `GITHUB_TOKEN` when they are not, so the pipeline is unchanged until the
App exists. Creating it is the only manual step left in this repo's release path:

1. **Settings > Developer settings > GitHub Apps > New GitHub App**, owned by the
   same account as the repository. Homepage URL can be the repository. Uncheck
   **Webhook > Active**; nothing here listens to one.
2. Repository permissions: **Contents** read and write (push the tag and the
   back-merge), **Pull requests** read and write (open and merge the promotion),
   **Commit statuses** read and write (post `validate`), **Metadata** read, which
   GitHub adds by itself.
3. **Install** the App on this repository only, then generate a private key.
4. Add one repository **variable** and one repository **secret**:
   `RELEASE_APP_ID` as a variable (the numeric App ID, not the client ID) and
   `RELEASE_APP_PRIVATE_KEY` as a secret (the whole `.pem`, `BEGIN` and `END`
   lines included). The variable, not a secret, because the step that mints the
   token is gated on that value and `secrets` is not an available context in a
   step-level `if`; an App ID is not confidential in any case. Getting this
   backwards leaves the step permanently skipped, which looks exactly like an App
   that was never installed.

Then one dispatch is enough, because the promotion's push raises the event the
`push: main` trigger listens for, and a commit-message closing keyword closes its
issue. The way to confirm it is working is not that a release succeeded, since a
release succeeds either way: it is `gh run list --workflow=Release` showing a
`push` event for the merge commit. Until that line appears, assume the fallback
is still in use and tag with a second dispatch.


**The propose job needs a repository setting that is off by default.** It opens
the release PR with `GITHUB_TOKEN`, which requires *Settings → Actions →
General → "Allow GitHub Actions to create and approve pull requests"*. Off,
the failure (`GitHub Actions is not permitted to create or approve pull
requests`) arrives only at the first real release, after the version bumps
have already been pushed. It cost this repo its first automated run
(2026-09-02); a fork or a re-created repo starts with it off again.

**The required check is matched by name.** Branch protection on `main` requires
a context called `validate`, which is the job id in `ci.yml`. Rename the job and
protection silently stops gating anything: the release still merges, just
unchecked. They move together or not at all.

**The release PR must merge with a merge commit, never a squash.** The
back-merge fast-forwards `develop` to `main`, which only works while `develop`
is an ancestor of `main`. A squash is not the commits it squashed, so it breaks
that relationship and the next back-merge falls back to opening a PR.

A squash is no longer fatal (v2026.09.02 went in as one, and it taught the
tag job to treat identical trees as "promoted" so the release still tags), but
it costs a manual back-merge review and muddies `develop`'s history. The
mechanical guard is a repository ruleset restricting merges into `main` to
merge commits (Settings → Rules, a `pull_request` rule with
`allowed_merge_methods: ["merge"]`); prose warnings do not gate UI buttons.

**The release PR's own CI run is killed by its own merge.** Auto-merge is
enabled the moment the `validate` status is posted, so the pull-request run
starts and the merge lands about a second later; GitHub drops the merge ref
under the running job and records the run as `failure` with zero jobs and no
logs. The timestamps are unambiguous, and they were the only way to tell this
apart from a workflow that was never allowed to start: across the three release
PRs to date the run was created one second **before** the merge and updated
within a second **after** it (#60 merged 01:58:03Z, run 01:58:02Z to
01:58:04Z). Compare a zero-job run's `updated_at` with the PR's `merged_at`
before diagnosing anything else, here or anywhere.

That run gates nothing, which is why the propose job runs the two
validators itself and posts the result as the `validate` status on the same
head commit. Read a release PR's checks, not the Actions tab; and since
2026-09-04 `ci.yml` ignores pull requests into `main` so the phantom row is not
created at all. A hotfix PR into `main` from a branch other than `develop`
therefore needs `validate` from a `workflow_dispatch` run on that branch, which
lands on the same commit and satisfies protection.

## Holding a release

Close the release PR. The next run reopens one when the cadence comes round
again. To hold for longer, disable the workflow in the Actions tab: the gates
have no "paused" state, deliberately, because a paused release is one nobody
remembers to resume.

## The tests, and where they came from

`scripts/validate-skills.sh` is vendored from
[`agent-config-harness`](https://github.com/damson/agent-config-harness), at the
commit named in its header. It began as a copy because the harness was private
then; it stays one now that the harness is public because the copy is what
keeps contribution self-contained: the exact check CI runs sits in the repo,
runnable with zero extra clones and no network. `diff` the two files when the
harness moves.

`scripts/validate-marketplace.py` has no upstream. It checks the wiring the
harness knows nothing about: that `marketplace.json` lists every plugin
directory and no phantom ones, that each `plugin.json` name matches its folder
and carries a semver version, and that the README's per-plugin skill counts and
skill lists still match the tree.

`scripts/validate-shell-blocks.py` has no upstream either. It parses every
fenced shell block in every skill with `bash -n`, which never executes them.
The blocks are what a reader pastes into a terminal, and nothing else here
reads them: an unbalanced quote or an unterminated loop ships green and is
found by whoever tries to follow the step. Angle-bracket placeholders are
substituted before parsing, because `git fetch <url> <branch>` is how these
skills say what to fill in and bash reads `<url>` as a redirect. So it catches
malformed shell, not a badly chosen placeholder.
