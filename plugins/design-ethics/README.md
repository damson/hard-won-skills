# design-ethics

One skill for the check a design pass cannot make: whether a flow that handles
money, consent or cancellation is persuading the user or taking the decision
from them.

```bash
claude plugin install design-ethics@hard-won-skills --yes
```

Persuasion and deception use the same tools. Contrast, defaults, sequence and
copy are how every good flow guides a choice and how every bad one takes it, so
naming the technique never settles which you are looking at. What settles it is
whether the user's understanding of what they agreed to matches what happens.

This exists as its own plugin because a design-quality pass makes the problem
worse rather than better. Polish buys trust, and a misleading default is what
spends it, so the prettier flow is not the more honest one and the pass that
made it pretty was never asking. The skill runs before that pass and again
after it.

## The skills

| Skill | What it does |
|---|---|
| [`separate-persuasion-from-deception`](skills/separate-persuasion-from-deception/README.md) | Name what the user can lose, test every decision point for a gap between understanding and outcome, equal prominence, symmetric friction and default ownership, then rate by loss rather than on a scale that drifts |

Each skill's README carries its triggers and a worked example; the `SKILL.md`
beside it is the procedure the agent follows.

## If this one misfires

The likely failure is a false positive, and it is the expensive one: flag a
fair upsell twice and the next report goes unread, taking the real finding with
it. The skill carries an explicit list of what is not a dark pattern, and a
first step that hands the flow back when nothing the user would struggle to
recover is at stake. If it fires on ordinary visual work or on an internal
tool, that first step was skipped.
