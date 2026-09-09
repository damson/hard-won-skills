# stand-in-for-a-blocked-review

Answers a question the merge gate cannot: was this pull request actually
reviewed? A review bot reports the same green whether it read the diff and
found nothing or never read it at all, and the second case is written only in
a comment body. When the review really is missing, this skill commissions one
that is independent enough to be worth the word, and posts it as the record
instead of letting a green mark stand in silently.

The failure it prevents is not a bad review. It is a pull request that merges
looking reviewed. On the session this came from, a free tier allowing one
review per hour spent its quota mid-batch and wrote "Review limit reached" into
its comment while its commit status stayed `success`. Three pull requests
merged into a public repository on the strength of that green. Nobody was
careless; the signal everyone was watching said what it always says.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it does and how
to reach it.

## Using it

It fires when a review is expected and its evidence is missing:

- "CodeRabbit hasn't reviewed this, it's rate limited"
- "the review bot says limit reached, can we still merge?"
- "no review on this PR and the checks are green"
- an automated pull request the reviewer silently skipped

It deliberately does **not** fire on:

- a review that posted findings; those get answered, one row per finding, and
  `pr-comment-loop` owns that
- a quota that resets in minutes, where waiting buys the real review
- the question of whether the change should merge; it produces a review, not a
  decision

## Example

A release batch, four pull requests, every commit status green. The skill reads
past the status to the reviewer's own comment and finds two of the four
carrying a warning block: *Review limit reached. Next included review available
in 3 minutes.* The status on both said `success` the whole time.

Three minutes is inside the waiting window, so the cheap recovery goes first: a
retrigger, then the body again. When the quota is still spent, the skill checks
whether the content was reviewed anywhere else before commissioning anything:

```bash
git rev-parse "origin/main^{tree}" "origin/develop^{tree}"
```

Equal hashes on the promotion retire it outright, because a squash changes the
commit and not the tree, and those commits were each reviewed at their own
heads. That leaves one pull request genuinely unreviewed.

Its stand-in gets the diff at the pinned head and the repository's own
conventions, and is not told why any of it was written that way, because a
reviewer given the author's rationale grades the rationale. It is told to break
the change rather than review it, and to treat each new test as unproven until
it has been watched failing:

```bash
gh pr diff "$pr" > review-input.diff
wc -l review-input.diff        # an empty input reviews clean and says nothing
```

It came back with no defects, having sabotaged each new test and confirmed it
went red. That is a verdict worth posting; the same words from a reviewer that
only read the tests would not be.

The comment says who reviewed and what they could not see: a stand-in reads the
diff, not the repository's history of making the same mistake before. Merging
stays where it was.

## Related

- `pr-comment-loop` (this plugin): the normal path, when a review did post
  findings; this skill borrows its verdict vocabulary for the answer table.
- `merge-on-go-ahead` (this plugin): the gate that asks whether the review is
  answered before pressing the button.
- `await-pr-checks` (this plugin): the same lesson on the other signal, where
  an empty conclusion reads as passing.
- `prove-the-check-can-fail` (verification plugin): the discipline step 5 asks
  the stand-in to apply to every new test.
