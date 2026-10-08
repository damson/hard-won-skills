# reproduce-a-reported-defect

For the moment a review hands you a defect you did not find yourself, and you are
about to change code on its word. A cold reader is confidently wrong at a
predictable rate, and it is wrong in the same voice it is right in: severity does
not separate the two, because a finding ranked critical is still a claim about
code the reader never ran.

This skill makes the claim produce an artifact before it produces a patch.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it does and how to
reach it.

## Using it

It fires on receiving a finding, not on a command:

- "fix the findings from the review"
- "it says there is a race in there"
- "address the critical one"
- a bot review, a stand-in, a bug report, a colleague's comment

It stays quiet for a defect you watched happen yourself, and for a finding that
one line of source settles. Most findings are that kind, and the skill says so
in its own first step rather than sending you to build a test for them.

## Why a separate skill

`prove-the-check-can-fail` is the mirror of this one and not a substitute. That
skill asks whether a guard you wrote can fail, before you count it as coverage.
This one asks whether a defect somebody else reported exists, before you fix it.
One is about trusting your own work; the other is about trusting somebody
else's reading of it.

`pr-comment-loop` already says to check each finding against the source. It is
right, and it is where this starts, in step 1. What it does not carry is what to
do when the source cannot settle the claim, which is every finding about an
order, a race, a bound or a moment, and those are the ones worth the most and
cost the most to get wrong.

## Example

A finding ranked critical: the gallery saves the wrong picture after a swipe.
Step 1 cannot settle that, because it is a claim about order rather than about a
line, so the probe drives exactly the sequence the finding describes and nothing
else:

```console
$ cat app/src/androidTest/java/.../ProbeSwipeThenSave.kt
@Test fun probe_swipeThenSave_savesTheVisiblePage() {
    composeRule.onNodeWithTag("pager").performTouchInput { swipeLeft() }
    composeRule.onNodeWithTag("save").performClick()
    assertEquals(1, savedIndex)          // the page now on screen
}
$ ./gradlew :app:connectedDebugAndroidTest --tests '*ProbeSwipeThenSave*'
> expected:<1> but was:<0>
```

**Read why, not that.** `expected:<1> but was:<0>` is the claim: the save used
the index from before the swipe. A probe that had died on
`Expected exactly '1' node but found '2'` would have been just as red and would
have proved nothing, which happened in the same batch when a modal sheet composed
into a second window.

Reproduced, so the fix lands, the probe is renamed into the suite for the
behaviour rather than the bug, and it is run once against the unfixed code so the
record shows it catching what it was written for.

Two other findings in that batch were rejected without a test, and a rejection
carries the same burden as a reproduction: the line that contradicts the claim
gets quoted. "Checked, not an issue" is not a rejection anybody can audit.

## What it cost to learn

Two findings in one night, both ranked critical, both about behaviour over time.
Both were real, and the probes proved it: one saved the wrong picture after a
swipe, the other threw an `IndexOutOfBoundsException` when a list lost the page
it was showing. In the same batch two other findings were rejected against the
source without a test, and one probe failed for its own reasons first, reporting
`Expected exactly '1' node but found '2'` because a modal sheet composes into a
second window. That failure looked exactly like a reproduction and was not,
which is why step 3 says to read why a probe failed rather than that it failed.
