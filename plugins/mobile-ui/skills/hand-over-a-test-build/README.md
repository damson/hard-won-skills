# hand-over-a-test-build

Produces a build someone else can install and try, from the branches the fixes
are actually on, and proves each fix is inside it before sending.

Handing over a build is a claim that it contains what the person reported. That
claim is usually made from a build command exiting 0, which says something else
entirely. A fix in flight lives on its own branch, so a build of the integration
branch carries none of them; and Gradle will hand back a cached artifact in five
seconds with nothing in the log to say which one it is.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it looks like in
use and how to reach it.

## Using it

Ask for the outcome, not the technique:

- "get me an apk"
- "build me something to test"
- "can I have a debug build with both fixes"
- "I want to check that on my phone"

It fires when the build is for someone else to run. It stays out of the way when
the build only has to compile, and it does not drive the app itself.

## What it does

1. Merges the named branches onto the integration branch in a detached worktree
   that is never pushed, because a throwaway integration is not a proposal about
   how those branches should land.
2. Runs the suite over the combination, which is a tree nothing has tested even
   when every branch was green alone.
3. Proves each fix is in the compiled output, reading the class files rather than
   the packaged archive.
4. Sends it with what a tester would otherwise assume: the commit, the variant,
   what is deliberately absent, and one line per fix on how to see it.
5. Keeps the worktree until the verdict comes back.

## Example

Two fixes reported by one tester, each on its own open branch, and a request for
something to try. The combination goes in a detached worktree, the suite runs on
it, and the variant gets assembled because a test task produces nothing
installable:

```console
$ git worktree add --detach "$wt" origin/develop
$ for n in 318 322; do
>   git -C "$wt" fetch -q origin "refs/pull/$n/head:refs/pr/$n"
>   git -C "$wt" merge --no-edit "refs/pr/$n" || break
> done
$ ( cd "$wt" && ./gradlew :app:testDebugUnitTest :app:assembleDebug )
BUILD SUCCESSFUL in 2m 14s
412 tests completed
$ find "$wt" -path '*/outputs/apk/*' -name '*.apk' -newermt '-10 minutes' | head -1
/Users/me/build-handover/app/build/outputs/apk/debug/app-debug.apk
```

Then the step the skill exists for, once per fix, against the class files rather
than the packaged archive:

```console
$ hit=$(find "$wt" -path '*/intermediates/*' -path '*/com/example/sync/RetryBanner.class' | head -1)
$ R=${hit%/com/example/sync/RetryBanner.class}
$ javap -p -cp "$R" com.example.sync.RetryBanner | grep retryAfterSeconds
  private final int retryAfterSeconds;
```

The member exists only because of #322, so that fix is demonstrably in the
artifact. #318 changed a constant and has no new member, so its value gets read
out of the disassembled method instead. The handover then says the commit, the
variant, how to see each fix, and that the offline queue work on a third open
branch is deliberately not in it.

## What it will not do

It does not push the integration, and it does not choose a winner quietly where
two branches genuinely changed the same logic. Two fixes that cannot sit together
is a finding the author needs before either merges. Two additions meeting in one
list are a different thing and keep both sides.

It does not claim a fix is present when nothing in the output distinguishes it. A
comment or documentation change has no signature, and saying so is the honest
result.

It does not substitute a variant. A debug build handed over as though it were the
release one is the exact failure this exists to prevent.

## The distinction it is built around

Searching the packaged `.dex` for a symbol is the obvious way to check a fix
arrived, and it fails silently: the strings are encoded, a shrunk build has
renamed them, and finding nothing looks the same as looking in the wrong place.
The intermediates keep real class files, and a disassembler answers the question
properly, including for a change that only moved a constant.
