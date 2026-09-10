# separate-persuasion-from-deception

Checks a flow that handles money, consent or a cancel path for the one thing a
design-quality pass cannot see: whether what the user understood matches what
happens. Persuasion and deception use the same contrast, defaults and sequence,
so the technique never settles it.

Read [SKILL.md](SKILL.md) for the procedure. This file is what a run looks like
and when to reach for it.

## Using it

It fires on the intent, not a command:

- "is this a dark pattern?"
- designing a paywall, trial, upsell, consent dialog or notification opt-in
- a pre-selected option that happens to be the more expensive one
- a cancel path that takes noticeably longer than the signup it reverses
- a conversion number that improved and nobody can say which change earned it

It stays quiet for ordinary visual and usability work, for internal tools, and
for any flow where the user cannot lose something they would struggle to get
back.

## Example

A trial signup, three decision points, two of them clean.

The first is a plan choice with the annual option pre-selected. Default
ownership asks who chose it: nobody had, it came from the pricing page
template. Cheap fix, not a finding.

The second is the trial itself, and it fails the understanding test with a gap
that fits in a sentence: the user would say the trial ends, and what happens is
that it converts to a paid year. Step 4 settles severity on its own, and money
the user did not agree to spend makes it blocking. What equal prominence adds is
the remedy, not a discount on the rating: give "renews at the full annual price
on 14 March" the size and weight of the Start trial button, and the step still
converts, so the flow was not leaning on the omission and one sentence closes
it. Had it stopped converting, the same finding would have needed the offer
rethought rather than disclosed.

The third fails properly. Cancelling runs seven steps against signup's two,
and step five offers a discount before it offers the cancel. The numbers are
the finding, and rating by loss makes it blocking, because the user keeps
paying for a subscription they have already decided to end.

The report is two blocking findings, one closed by a sentence and the other
needing the cancel path rebuilt, plus one cheap default, with an honest
alternative for each. What it is not is three findings of equal weight, which is
how this report usually arrives and why it usually gets skimmed.

## Why it is shaped like this

The four tests exist because a catalogue of named patterns invites matching
rather than judgment, and matching produces false positives. False positives
are what kill this check: flag a fair upsell twice and the next report goes
unread, taking the real finding with it. So the skill spends most of its length
on discrimination, and it carries an explicit list of what is not a dark
pattern.

Rating by what the user loses, rather than on a four-level scale, comes from
the same concern. A scale drifts upward under pressure from whoever wants the
finding to land, and every level above the bottom starts meaning "serious".

The last step, re-running two of the tests after the visual pass, is the part
most easily dropped and the reason the skill is separate from design review.
Polish adds force to a default. The option that read as one of several in
wireframe can read as the only one once it has contrast and weight behind it,
and nothing in a design pass is asking that question.

## Related

Same evidence discipline as `prove-the-check-can-fail`, applied to a claim
about a person rather than a test: build the honest version and watch the flow
fail, rather than arguing that it would.
