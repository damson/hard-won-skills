---
name: render-android-ui-candidates
description: >
  Use when an Android or Compose appearance decision needs showing rather than
  describing: which icon, how large, which colour, one row or two. Fires when a
  design question has round-tripped in prose, when someone asks "show me" or
  "let's try", or before changing a component whose look is the point. Renders
  each candidate through the project's own screenshot harness and then MEASURES
  the result, because "it looks too big" is settled by numbers and not by more
  adjectives. Do NOT fire for a behavioural question, for a component that does
  not exist yet, or to record goldens, which the baseline-record skill owns.
---

# Render Android UI candidates, then measure them

A rendered candidate ends an argument that prose extends. But a render alone
still leaves "it looks a bit big", which is unanswerable until someone measures
the thing next to it. The measuring is the half people skip, and it is the half
that produces a decision.

## Procedure

### 1. Render through the project's harness, not a new one

Find the screenshot test that already captures this component and copy its
setup: its runner, its qualifiers, its capture helper. A harness invented for
the occasion renders a component in a theme, density and window the app never
uses, and every judgement made from it is about that fiction.

**Capture the `@Preview` functions, not a rebuilt component.** A rebuild drifts
from the real call site, which is exactly what you are trying to judge.

### 2. Parameterise the candidate, temporarily

Add one parameter carrying the variants, an enum with a preview each:

```kotlin
enum class Trial(val ring: Dp, val glyph: Dp) { A(36.dp, 26.dp), B(30.dp, 21.dp) }
```

Thread it through with a default so every existing call site still compiles,
and delete it before the change ships. It is scaffolding, not API.

### 3. Run the record task, never the plain test task

This is the trap that produces no files and no error. Under
`testDebugUnitTest` a screenshot library is inert: the capture calls are no-ops,
the tests pass, and nothing is written. Use the project's record task, and
**list the output directory** rather than trusting the build's exit code.

### 4. Get both themes by merging qualifiers, not by concatenating them

Robolectric merges a method-level `@Config` onto the class's, and only that way
round. A qualifier string glued together by hand fails to parse, and the
segment order is fixed, so `night` sits before density and not at the end.

The cheap shape is one abstract class holding the cases and two subclasses that
differ only in `+night` and `+notnight`.

### 5. Label and stack them at one scale

One image, one row per candidate, each labelled with what it is in words the
person used. Crop across the axis under discussion, never along it. Then open
it, rather than only sending it: a decision gets made in front of the picture.

### 6. Measure the ink, in the units the code uses

The step that ends the argument. Read the rendered pixels, find the bounding box
of each control's ink, and convert with the density the qualifier pinned:

```python
PPD = image_width_px / window_width_dp        # eg 1078 / 411
```

Report each candidate **and its neighbours**, because the question is never
"how big is it" but "how big is it beside the others".

Expect the neighbours to disagree with each other. Material's keyline grid is
deliberately uneven, so square glyphs, wide glyphs and the odd one out all
paint different amounts of ink inside the same box. Match the family the new
control belongs to rather than the box size.

### 7. Ask with the numbers attached

One question, one option per candidate, each carrying its measurement and what
it costs. A choice offered without its price gets re-opened later.

## When to STOP

- **The question is not visual.** When something happens, what it stores, who
  can see it: these render identically either way. Ask in words.
- **There is no component yet.** Build the plainest version first; there is
  nothing to vary until something exists to vary.
- **The harness cannot render it** (a real ad, a camera, a system dialog).
  Say so and drive it on a device instead, which `android-verify-on-device`
  owns.
- **Recording goldens.** A candidate render is throwaway output to a scratch
  directory. Goldens are committed artefacts with their own procedure in
  `android-screenshot-baseline-record`, and mixing the two overwrites the
  baselines with an experiment.
- **The person has already chosen.** Re-asking a settled question reads as not
  having listened. Implement, and say which reading you took.
