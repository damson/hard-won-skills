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
- **The readings are capped at three, and merged when they agree.** Two
  candidates are distinct only if they produce different numbers or put a named
  element on a different edge. Otherwise they are one reading described twice,
  and offering both makes the choice look harder than it is.
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

## Related

- `prove-the-check-can-fail` (this plugin): the same discipline pointed at a
  check rather than a sentence.
- `verify-dependency-behaviour` (this plugin): when the ambiguity is in a
  library's documented behaviour rather than in a requirement.
- `figma-to-compose-component` (mobile-ui plugin, if installed): for when the
  design is already settled and only needs building.
