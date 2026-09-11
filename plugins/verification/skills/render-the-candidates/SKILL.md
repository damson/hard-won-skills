---
name: render-the-candidates
description: >
  Use when a requirement about layout, geometry or visual arrangement has
  round-tripped twice without converging: you changed the code, the user
  restated the requirement, and it is still not what they meant. Fires on
  "still don't end up", "that's still wrong", "I'm still confused by", "it had
  been correctly designed", and on your own impulse to write a third paragraph
  explaining what you think they mean. Do NOT fire on the first miss, where
  only one reading is actually plausible, or where the disagreement is about
  behaviour rather than about something that can be seen.
---

# Render the candidates

Words like *left*, *longest edge* and *alongside* each name two things: an edge
of the device or an edge of the display, the long side now or the long side once
it turns. Two people can agree on every sentence and mean different screens, and
neither can see which reading the other took. A third paragraph is judged against
a sentence too, so it repeats the round with better vocabulary.

## Procedure

1. **Say the numbers first.** Whatever the disagreement is measured in (dp,
   pixels, aspect ratio, count), state the actual figures for each reading, in
   one line each. Often this alone ends it: "a side edge is 891dp upright and
   411dp turned" is not a matter of opinion, and one reading usually stops being
   plausible the moment its number is written down.

2. **Enumerate the readings, and cap them at three.** Two readings are distinct
   if they differ in **anything under dispute**: a number from step 1, or where
   a named element sits: which edge, which order, which alignment. Merge only
   when every disputed quantity and every placement is identical. Two screens
   can agree on an edge and a dimension and still order or align their contents
   differently, and merging on the coarser test discards a candidate before
   anyone has seen it, which is the failure this skill exists to prevent. Name
   each in the user's own words, not yours.

   The cap is a budget, never a licence to drop the fourth quietly. If more than
   three survive the merge, list every one of them in a single line each with
   its numbers from step 1, and ask which three to render. The reading you would
   have discarded is the one they have been trying to describe often enough that
   this is worth a turn.

3. **Build each one as a picture.** Not a description of a picture.
   - Prefer a render **through the real code path**: call the actual mapping,
     the actual layout, the actual component. A hand-placed mock-up can show a
     screen the code cannot produce, and then the decision is made against a
     lie.
   - Where the code for a reading does not exist yet, a mock-up is legitimate
     but **must be labelled as one** in the image itself.
   - Fill the placeholders. An empty slot measures 0x0 and collapses the layout
     around it, so a stand-in with the real dimensions is part of the render,
     not a nicety.

4. **Put them at one scale, and label the quantity in dispute.** Same
   px-per-unit for every candidate, aligned on a common edge, with the measured
   dimension drawn on rather than written underneath. Crop *across* the axis
   being measured if you must crop; never along it, or the comparison is a
   framing choice rather than evidence.

5. **Ask, with the consequence attached.** One `AskUserQuestion`, one option per
   candidate, and each option says what it costs: what stops working, what code
   becomes dead, what the user gives up. A choice presented without its price is
   answered again later. Where the host offers no such tool, a numbered list in
   a single message does the same work, provided the answer is written back into
   the record rather than left in the scrollback.

6. **Only then implement.** And keep the renders: they are the before/after for
   the pull request body, and they date-stamp what was agreed.

## When to STOP

- **The question is not visual.** A disagreement about when something happens,
  what it stores, or who can see it renders identically either way. Ask in
  words.
- **One reading is plainly right.** Rendering two candidates to prove one absurd
  wastes the user's turn; implement, and say which reading you took.
- **The renders would cost more than a wrong build.** Where the component is
  cheap to build and cheap to change, build it and show the result. The trigger
  for this skill is a requirement that has *already* round-tripped, which is what
  makes the render cheaper than the next guess.
- **Nothing here can produce a picture**: no harness, no headless renderer, no
  way to screenshot the real path. Say so, then run steps 1 and 2 anyway and ask
  on the numbers: a labelled comparison of measurements is weaker than a render
  and far stronger than a third paragraph. What you must not do is quietly
  promote a sketch into the evidence slot the render was going to fill.
- **The user has already answered the geometric question.** Re-asking a settled
  one reads as not having listened. Check the transcript for a rule they stated
  ("left and right are always from the portrait perspective") before drafting
  options that ignore it.
