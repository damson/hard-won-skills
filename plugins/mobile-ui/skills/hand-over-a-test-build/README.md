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

## What it will not do

It does not push the integration, and it does not resolve a conflict between two
branches quietly. Two fixes that cannot sit together is a finding the author
needs before either merges.

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
