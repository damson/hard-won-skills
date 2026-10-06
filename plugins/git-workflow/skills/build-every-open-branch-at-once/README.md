# build-every-open-branch-at-once

Builds one throwaway artefact carrying every open pull request, so a feature
split into reviewable slices can be tried as a whole before the first slice
merges. The combination happens in a worktree that is never pushed, and the
conflicts it hits are resolved as unions rather than by picking a side.

Read [SKILL.md](SKILL.md) for the procedure. This file is why the resolution
rule is the part worth writing down.

## Using it

It fires when somebody wants the whole of a feature that is still in pieces:

- "get me a build with all of that in"
- "can I test it end to end before these land?"
- "what does it look like with every branch together?"
- "build the three open PRs as one APK"

It deliberately does **not** fire on:

- one open pull request, which needs no procedure
- a pure stack where the last child already contains every ancestor: build the
  child
- a request to merge those branches, which is `merge-on-go-ahead` and a decision
  rather than a build
- a request to push, keep, or open a pull request from the result

## Example

Three open branches off `develop`, and somebody asking for one build. The
combination happens on a branch the forge has never seen:

```console
$ base=develop; br=throwaway/combined-build; wt=$HOME/throwaway-combined-build
$ gh pr list --head "$br" --state all --json number --jq '.[].number'
$ git worktree add -B "$br" "$wt" "origin/$base"
Preparing worktree (new branch 'throwaway/combined-build')
$ branches="feat/offline-queue feat/retry-banner feat/queue-settings"
$ for b in $branches; do
>   git -C "$wt" merge --no-edit "origin/$b" && echo "merged $b" || { echo "$b conflicts"; break; }
> done
merged feat/offline-queue
merged feat/retry-banner
Auto-merging app/src/main/res/values/strings.xml
CONFLICT (content): Merge conflict in app/src/main/res/values/strings.xml
feat/queue-settings conflicts
$ git -C "$wt" diff --name-only --diff-filter=U
app/src/main/res/values/strings.xml
app/src/main/java/com/example/SyncState.kt
```

Both files are two additions meeting: a strings file where each branch appended
at the same anchor, and a sealed hierarchy each gave a new case. Keeping both
sides in each, then finishing the merge:

```console
$ git -C "$wt" add -u && git -C "$wt" commit --no-edit
[throwaway/combined-build 4a1c9e2] Merge remote-tracking branch 'origin/feat/queue-settings'
$ git -C "$wt" rev-parse -q --verify MERGE_HEAD >/dev/null && echo "STILL mid-merge" || echo "merge completed"
merge completed
```

Then compile, because the union of two `when` arms only builds if the hierarchy
took both cases, and hand the artefact over named for the question rather than
for a branch, with the three heads it was built from.

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
