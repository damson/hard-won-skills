# render-the-candidates

For the moment a layout requirement has round-tripped twice and still is not
what the user meant. Words like *left*, *longest edge* and *alongside* each name
two things, and two people can agree on every sentence while picturing different
screens. This skill stops the third paragraph and puts the readings on screen
instead, because a paragraph is judged against a sentence too.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it does and how
to reach it.

## Using it

It fires on the shape of the disagreement, not on a command:

- "they still don't end up where I said"
- "that's still wrong"
- "I'm still confused by what you did"
- "it had been correctly designed before"

It also fires on your own impulse to explain, one more time, what you think they
meant. That impulse is the signal: the previous two explanations were also
clear, and clarity was never the problem.

It stays quiet on the first miss, and on any disagreement that is not visual.
When something happens, what it stores, or who can see it renders identically
either way.

## Why a separate skill

The other skills in this plugin distrust a *signal*: a check, a badge, a
dependency's documented behaviour. This one distrusts a *sentence*, and the
remedy is the same one they use: stop asserting, produce the artifact, let the
evidence settle it. Its sharpest rule is the plugin's rule exactly: render
through the real code path, because a hand-placed mock-up can show a screen the
code cannot produce, and then the decision is made against a lie.

## What it actually changes

Three things, in order of how often they end the argument on their own:

- **The numbers come first.** A side edge is 891dp upright and 411dp turned.
  Written down, one reading usually stops being plausible before anything is
  rendered.
- **The readings are capped at three, and merged only on a full match.** Two
  candidates are distinct if they differ in anything under dispute: a number, or
  where a named element sits, including its order and its alignment. Only when
  every disputed quantity and placement agrees are they one reading described
  twice, and offering both then makes the choice look harder than it is.
- **Each option carries its price.** What stops working, what code goes dead,
  what the user gives up. A choice presented without its cost gets answered
  again a week later.

## The traps it encodes

- **A mock-up that is not labelled as one** gets treated as a render, and a
  screen the code cannot produce becomes the agreed design.
- **An empty placeholder measures 0x0** and collapses the layout around it, so
  the render shows a screen nobody will ever see.
- **Cropping along the axis under discussion** turns the comparison into a
  framing choice. Crop across it or not at all.
- **The user may already have answered.** A rule stated earlier, such as "left
  and right are always from the portrait perspective", outranks a fresh set of
  options that ignores it, and re-asking reads as not having listened.

## Example

A tablet layout is asked for twice. "Put the controls along the longest edge",
then, after the first build, "no, the longest edge". The second sentence is the
first sentence, and that repetition is the trigger.

Step 1 writes the numbers instead of the words. The device is 891dp on one side
and 411dp on the other. Upright, the longest edge is the vertical one; turned,
it is the horizontal one. The same four words name a different edge in each
case, which is why two more paragraphs would not have helped.

Step 2 yields two readings, not three: controls pinned to the physical long side
of the device whatever the orientation, or controls pinned to whichever side is
longest right now, moving when the device turns. They put a named element on a
different edge, so they do not merge.

Step 3 builds both through the real layout code rather than sketching them,
which is where the second reading turns out to reflow the content area at the
rotation boundary. A hand-placed mock-up would have shown neither the reflow nor
its cost. Both renders are drawn at one scale, aligned on a common edge, with
891dp and 411dp marked on the images themselves.

Step 5 asks once, with the price attached: the first reading keeps one layout
and a control position that never moves, but wastes the short edge in landscape;
the second uses the space and buys an orientation-change path that the reflow
makes expensive.

The answer arrives in one turn, and the two renders go into the pull request
body as the record of what was agreed.

## Related

- `prove-the-check-can-fail` (this plugin): the same discipline pointed at a
  check rather than a sentence.
- `verify-dependency-behaviour` (this plugin): when the ambiguity is in a
  library's documented behaviour rather than in a requirement.
- `figma-to-compose-component` (mobile-ui plugin, if installed): for when the
  design is already settled and only needs building.
