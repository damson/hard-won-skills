# render-android-ui-candidates

Settles an Android appearance question by rendering each candidate through the
project's own screenshot harness and then measuring the result in dp, rather
than by exchanging adjectives about it.

A render alone is not enough. "It looks a bit big" survives any number of
pictures and dies instantly to a measurement: the glyph beside it paints 27.8dp
of ink, this one paints 36.2, and there is nothing left to discuss.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it looks like in
use and how to reach it.

## In use

A toolbar needed a new button. Five rounds of rendering answered which glyph,
how much emphasis, which parts take the accent colour, and how large, each
round a picture rather than a paragraph. The last round is the one that
mattered:

```
36dp ring -> 36.2dp on screen   palette 27.8dp
30dp ring -> 30.1dp             palette 27.8dp
28dp ring -> 28.2dp             palette 27.8dp
```

The ring had looked oversized for three rounds and nobody could say by how
much. It was 30% wider than its neighbour, because a ring is edge-to-edge
artwork with no keyline margin while every Material glyph beside it keeps one.

## Reaching it

Ask to see the options, or say a design question has gone round twice:

- "show me them in the toolbar first"
- "the icon still seems a bit big"
- "let's try it with a thinner ring"
- "which of these reads better next to the others"

## Two traps it exists to avoid

- **The plain unit-test task writes nothing.** A screenshot library is inert
  under it: no captures, no error, a green build and an empty directory.
- **Theme qualifiers merge at method level only.** Concatenated by hand they
  fail to parse, and the segment order is fixed.
