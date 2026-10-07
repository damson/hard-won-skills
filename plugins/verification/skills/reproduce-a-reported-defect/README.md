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

## What it cost to learn

Two findings in one night, both ranked critical, both about behaviour over time.
Both were real, and the probes proved it: one saved the wrong picture after a
swipe, the other threw an `IndexOutOfBoundsException` when a list lost the page
it was showing. In the same batch two other findings were rejected against the
source without a test, and one probe failed for its own reasons first, reporting
`Expected exactly '1' node but found '2'` because a modal sheet composes into a
second window. That failure looked exactly like a reproduction and was not,
which is why step 3 says to read why a probe failed rather than that it failed.
