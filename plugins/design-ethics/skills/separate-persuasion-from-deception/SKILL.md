---
name: separate-persuasion-from-deception
description: >
  Use when a change touches something the user can lose: a price, a fee, a
  recurring charge, a consent or permission grant, a pre-selected default, a
  cancel, unsubscribe or delete path, or a prompt whose job is retention.
  Fires on "is this a dark pattern", on designing a paywall, trial, upsell,
  consent dialog or notification opt-in, and before shipping a flow whose
  conversion depends on what the user does not notice. Do NOT fire for
  ordinary visual or usability work, for an internal tool with no external
  user, or for a flow where nothing the user cannot recover is at stake.
---

# Separate persuasion from deception

Persuasion and deception use the same techniques. Contrast, defaults, sequence
and copy are how every good flow guides a decision, and how every bad one takes
it. The line is not the technique, it is whether the user's understanding of
what they agreed to matches what actually happens.

Which is why a design-quality pass makes deception more effective rather than
less: polish buys trust, and a misleading default is what spends it. Step 7 is
where that gets checked.

## Procedure

1. **Name the stake, or hand the flow back.** What can the user lose here that
   they cannot easily recover: money they did not agree to spend, data they
   cannot retrieve, a right they cannot reclaim, a change they cannot undo?
   Write it in one sentence. Nothing recoverable at risk means this is ordinary
   design review and not this skill; say so and stop.

2. **Enumerate decision points in order, not screens.** A screen can be
   blameless while the sequence it belongs to is not, so walk the path instead
   of judging any single view: click the running flow through, step the frames
   in their intended order, or read the spec's steps in sequence. For each
   point where the user chooses, record what they are deciding, what the
   default is, what each option costs them, and what they have already spent
   in effort to get there. That last column is what turns a truthful
   disclosure on the final step into a finding. The record is the working
   material for step 3.

3. **Run all four tests at every decision point.** They disagree with each
   other on purpose, and a flow that fails one while passing three is the
   common case, not an anomaly.

   - **Understanding.** State, in the user's words, what they would say happens
     next. Compare it to what does happen. The finding is the gap, and it has
     to fit in one sentence: "they believe this is a one-time charge; it renews
     every year." No statable gap means no deception, only friction.
   - **Equal prominence.** Take the fact the design plays down and give it the
     size, contrast and position of the primary action. Then look. If the flow
     stops working, it was depending on that fact being missed, and you have
     just proved it rather than argued it. This is the strongest of the four
     because you can build it. Run it at the highest fidelity the artifact
     supports, and the order is fixed: running code beats a design file, and a
     design file beats a spec. Edit the running code and reload; or duplicate
     the frame and restyle that one fact to match the primary action; or, with
     only a written spec, quote the sentence disclosing the fact beside the
     sentence naming the action and record which comes first and at what
     heading level.
     The written form is the weak one. Report the visual test as still owed
     rather than as run.
   - **Symmetric friction.** Count the steps in and the steps out. Count, do
     not estimate: the two numbers are the evidence. Two taps to subscribe and
     nine to cancel is the finding, stated as those numbers.
   - **Default ownership.** For every pre-selected option, ask who gains and
     who chose it. A default nobody decided is a bug worth fixing cheaply. A
     default chosen because it converts better is a decision, and it owes the
     other three tests an answer.

4. **Rate by what is lost, not by how it feels.** One question decides it: does
   the user lose money they did not agree to spend, data they cannot retrieve,
   or a right they cannot recover? Yes makes the finding blocking. No makes it a
   usability finding, and it belongs to ordinary design review, reported as
   such. Ratings that skip this question inflate, and an inflated report gets
   read once. The four tests decide whether there is a finding and what would
   fix it; they never soften the rating. A gap that costs the user money stays
   blocking even where equal prominence shows one sentence would close it,
   because that result tells you the remedy is cheap and not that the harm is
   small.

5. **Cite a rule only where it changes what you must do.** A regulation named
   for weight is noise, and it trains the reader to skim the ones that matter.
   Where a jurisdiction genuinely forbids the pattern, or sets a form the
   consent must take, name it and say which requirement applies. Where it does
   not, the argument stands on the four tests without help.

6. **Propose the honest alternative that still serves the goal.** A finding
   with no alternative reads as a veto and gets overruled by whoever owns the
   number. Most of these have one: disclose the renewal at the point of
   purchase rather than in the receipt, make the decline path the same length
   as the accept path, let the default be the smaller commitment. If you
   genuinely cannot find one, say that the goal and the user's interest are in
   real conflict here, which is a decision for a person and not a design fix.

7. **Re-run tests 2 and 4 after the visual pass.** Polish is not neutral.
   Contrast, weight and placement give a default force it did not have in
   structure, so the option that read as one of several before the visual work
   can read as the only one after it. This step is the reason the skill exists
   alongside a design-quality pass rather than inside it.

## What is not a dark pattern

Restraint here is what keeps the rest usable. A skill that flags everything is
switched off within a week, and then the real findings go with it.

- An upsell that states its price plainly, at the moment of the decision.
- Scarcity or a deadline that is true, and stays true if the user returns.
- A default that favours the user, whoever it also happens to favour.
- Friction that protects the user: a confirmation on a destructive action, a
  cooling-off step before an irreversible purchase.
- A flow that is merely confusing. Confusion is a usability finding, and step 4
  is where that gets said. Deception needs a beneficiary.

## Sharp edges

- **Every screen can be honest while the flow is not.** Deception lives in
  sequence more often than in wording, and a fee disclosed truthfully on step
  four of four, after three steps of sunk effort, is the classic shape. That is
  why step 2 records the path in order and what the user has already spent. A
  screenshot is the one artifact with no sequence in it.
- **Category convention is not consent.** "Everyone in this market does it" is
  a claim about competitors, not about what this user understood. It changes
  the commercial risk of fixing it and none of the four tests.
- **The strongest test is the one nobody runs.** Equal prominence takes real
  work, because you have to build the honest version to see it fail. That is
  also why its result survives an argument with someone who outranks you.

## When to STOP

- **Nothing recoverable is at stake.** Step 1 failed. Ordinary design review
  owns this, and running the full procedure anyway produces findings that
  cannot be acted on.
- **The question is legal, not design.** Whether a specific consent form meets
  a specific jurisdiction's bar needs counsel. Name the exposure, say plainly
  that it is unresolved, and stop; a confident guess here is worse than none.
- **The constraint is real and disclosed at equal prominence.** A cost the
  business genuinely cannot absorb, stated where the user decides, is a priced
  trade-off. Report it as a trade-off and leave it.
- **You are being asked to bless a shipped decision.** Report what the tests
  found. Do not work backwards from the conclusion someone needs, and do not
  soften step 4 to make the report land more easily.
- **There is no external user.** An internal tool cannot deceive a user it does
  not have. Hand it back.
