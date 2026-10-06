---
name: hand-over-a-test-build
description: >
  Use when someone asks for a build to try themselves: "get me an apk", "build me
  something to test", "can I have a debug build", or after fixing something they
  reported and the confirmation has to come from their hands. Owns the two steps
  that get skipped, which are integrating the branches the fixes actually live on
  and proving each one is inside the artifact before it is sent. Do NOT fire for a
  release or store upload, for driving the app yourself (android-verify-on-device
  owns that), or for a build that only has to compile in CI.
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
git worktree add --detach ../build-handover origin/<integration-branch>
git -c user.name=t -c user.email=t@t merge --no-edit origin/<branch-a> origin/<branch-b>
```

Detached and never pushed. This is a throwaway integration, not a proposal about
how those branches should land, and pushing it would turn one into the other.

A conflict here is a finding, not an obstacle: two fixes that cannot sit together
is something the author needs to know before either merges.

### 2. Run the suite on the combination

Each branch was green alone. The combination is a tree nothing has tested, and it
is what you are about to send. Run the project's own test task over it and read
the count, not the exit code: a suite that silently ran nothing also exits 0.

### 3. Prove each change is inside the artifact

This is the step the skill exists for. For every fix the handover claims to
carry, find something in the compiled output that exists only because of it.

**Read the compiled classes, not the packaged archive.** Searching a `.dex` for a
symbol is the obvious move and it fails quietly: the strings are encoded, a
release build has renamed them, and a search that finds nothing looks exactly
like a search of the wrong file. The intermediates still hold real class files:

```bash
R=app/build/intermediates/classes/debug/transformDebugClassesWithAsm/dirs
javap -p -cp "$R" <the.class.you.changed> | grep <the member you added>
```

The path differs between plugin versions, so locate it rather than pasting it:
`find app/build/intermediates -name '<Something>.class' | head -1`.

For a change with no new member, a constant for instance, disassemble the method
and read the value: `javap -c -p -cp "$R" <class>` shows `iconst_0` where the
source used to push a different one. For a change to a resource or an asset, list
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
- **Two branches conflict.** Report the conflict and which files, and ask which
  should win rather than resolving it inside a throwaway nobody will review.
- **Nothing in the compiled output distinguishes the fix.** A pure comment or
  documentation change has no signature, so say that it cannot be shown to be
  present rather than implying it was checked.
- **The build needs signing material you do not have.** Report it as unbuildable
  rather than switching variant quietly: a debug build handed over as though it
  were the release one is the failure this whole skill is about.
- **The handover is a release build after a change that reached the shrinker.**
  Packaging it is not the check that matters there, and `verify-a-release-build`
  owns the one that is: starting the shipped artifact before it goes anywhere.
