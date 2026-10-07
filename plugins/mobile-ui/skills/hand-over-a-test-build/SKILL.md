---
name: hand-over-a-test-build
description: >
  Use when someone asks for a build to try themselves: "get me an apk", "build me
  something to test", "can I have a debug build", or after fixing something they
  reported and the confirmation has to come from their hands. Owns the two steps
  that get skipped, which are integrating the branches the fixes actually live on
  and proving each one is inside the artifact before it is sent. Do NOT fire for a
  release or store upload, for driving the app yourself (android-verify-on-device
  owns that), for a build that only has to compile in CI, or for combining open
  branches to see what the whole of a feature looks like, which stops at the build
  and is build-every-open-branch-at-once rather than a handover.
---

# Hand over a test build

A build handed to someone is a claim: *this contains the fix you reported*. The
claim is usually made from the fact that a build command exited 0, and that is
not the same statement. Two ways it is false:

- **The fix is on a branch the build did not include.** Work in flight sits on
  one branch per fix, and the person testing wants all of them at once. Building
  the integration branch gives them a build with none of it.
- **The build was served from cache.** Gradle will report success in five
  seconds and produce the artifact it made before your change. Nothing in the log
  says which one you are holding.

## Procedure

### 1. Ask which branches, then integrate them somewhere disposable

List what is open and unmerged, and merge every branch the handover is meant to
carry onto the integration branch in a worktree that exists for this and nothing
else:

```bash
base=develop                          # the integration branch
wt=$HOME/build-handover               # outside the repository

git fetch origin --prune
git worktree add --detach "$wt" "origin/$base" 2>/dev/null \
  || git -C "$wt" reset --hard "origin/$base"

for b in feat/one feat/two; do        # the branches the fixes live on
  git -C "$wt" -c user.name=t -c user.email=t@t merge --no-edit "origin/$b" \
    || { echo "$b conflicts: resolve it before merging the next"; break; }
done
```

Detached and never pushed. This is a throwaway integration, not a proposal about
how those branches should land, and pushing it would turn one into the other.

**Where several branches have to go in, the combination is its own procedure.**
`build-every-open-branch-at-once` owns the merge order, the conflicts parallel
branches produce and how they resolve, and it is worth reading before doing this
by hand with more than two. Where that plugin is not installed, the loop above is
the whole of it.

A conflict is not an obstacle on its own. Two branches that each appended to the
same list resolve by keeping both sides, and that is the common case. A conflict
inside logic both sides genuinely changed is the finding: two fixes that cannot
sit together is something the author needs before either merges.

### 2. Run the suite on the combination, then build the thing you will send

Each branch was green alone. The combination is a tree nothing has tested, and it
is what you are about to send. Run the project's own test task over it and read
the count, not the exit code: a suite that silently ran nothing also exits 0.

**A test task does not produce an installable artifact.** Assemble the variant
the handover is for, and find the file rather than predicting its path:

```bash
module=:app                                   # fill these two in
variant=Debug

( cd "$wt" && ./gradlew "$module:assemble$variant" )

apk=$(find "$wt" -path '*/outputs/apk/*' -name '*.apk' -newermt '-10 minutes' \
        | head -1)
[ -n "$apk" ] || { echo "assembled nothing: do not hand anything over"; }
echo "$apk"
```

The `-newermt` is the check that matters. A stale artifact from an earlier round
sits at exactly the path a fresh one would, and sending it is the failure this
step exists to prevent.

### 3. Prove each change is inside the artifact

This is the step the skill exists for. For every fix the handover claims to
carry, find something in the compiled output that exists only because of it.

**Read the compiled classes, not the packaged archive.** Searching a `.dex` for a
symbol is the obvious move and it fails quietly: the strings are encoded, a
release build has renamed them, and a search that finds nothing looks exactly
like a search of the wrong file. The intermediates still hold real class files:

The path differs between plugin versions and between modules, so derive the
classpath root from a class file you know changed rather than pasting a path:

```bash
cls=MyChangedThing.class                      # the compiled name, not the source
pkg=com/example/ui                            # its package, as directories

hit=$(find "$wt" -path '*/intermediates/*' -path "*/$pkg/$cls" | head -1)
[ -n "$hit" ] || { echo "no class file for $cls: nothing to read"; }
R=${hit%/$pkg/$cls}                           # strip the package back off

javap -p -cp "$R" "$(echo "$pkg" | tr / .).${cls%.class}" | grep theMemberYouAdded
```

`R` is computed from where the class actually landed, so a module that is not
`app` and a variant that is not debug both work. Pasting a fixed intermediates
path is how this step reads a different module's output and reports on it.

For a change with no new member, a constant for instance, disassemble the method
and read the value: `javap -c -p -cp "$R"` on the same class shows `iconst_0`
where the source used to push a different one. For a change to a resource or an asset, list
the archive and compare the entry.

An artifact whose timestamp predates your last edit is a cached one. Check that
too, and rebuild from clean if it is.

### 4. Send it, and say what is not in it

Name, in the message, the things a tester would otherwise assume:

- which commit, and which branches were merged in on top;
- which variant, because a debug build and a release build fail differently and
  only one of them has been through the shrinker;
- anything version-relevant that is **not** in it, such as a dependency bump that
  is still open on its own branch;
- what to actually do to see the fix, in one line per fix.

An artifact arriving with no instructions gets tested for the thing the tester
already had in mind, which is rarely the thing that changed.

### 5. Keep the worktree until the verdict

They will come back with a question, and rebuilding the same combination from
scratch to answer it wastes the integration you already made. Remove it once the
branches merge.

## When to STOP

- **The fixes are already merged.** Build the integration branch and say so; the
  merging is a separate decision and inventing an integration hides it.
- **Two branches conflict inside logic both of them changed.** Report it and
  which files, rather than choosing a winner inside a throwaway nobody will
  review. Two additions meeting in one list are not this case and resolve by
  keeping both.
- **Nothing in the compiled output distinguishes the fix.** A pure comment or
  documentation change has no signature, so say that it cannot be shown to be
  present rather than implying it was checked.
- **The build needs signing material you do not have.** Report it as unbuildable
  rather than switching variant quietly: a debug build handed over as though it
  were the release one is the failure this whole skill is about.
- **The handover is a release build after a change that reached the shrinker.**
  Packaging it is not the check that matters there, and `verify-a-release-build`
  owns the one that is: starting the shipped artifact before it goes anywhere.
