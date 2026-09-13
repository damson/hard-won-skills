---
name: compress-a-doc-set
description: >
  Use when asked to make a set of documents shorter, tighter or more concise:
  "trim this", "it is too long", "can this be smaller", "hardly readable",
  "still too verbose". Fires on a doc SET, a repo's docs/ tree, a playbook, a
  handbook, a skills directory, where facts can hide in more than one file. Do
  NOT fire for a single document, which is just an edit, for prose style or
  tone alone, or for agent config files read as a set, which is
  `agent-config-audit`.
---

# Compress a doc set

Prose is the layer everyone cuts first and the layer with the least in it.
Polishing sentences across a set feels productive, shows a diff, and leaves the
bulk untouched, so the request comes back. The bulk is one fact written in three
places, and a directory nobody has re-justified since the thing it duplicates
arrived.

Cut in the order below and the first pass lands where the third would have.

## Procedure

### 1. Measure before cutting

Lines per file and per directory, recorded now, so the result is a number
rather than a feeling and a regression is visible later.

```bash
find . -name '*.md' -not -path './.git/*' | xargs wc -l | sort -n
```

### 2. Find every fact with more than one owner

This is where the lines are. Grep the distinctive phrasings, not the common
words, and look at what appears in three or more files.

```bash
# Pull the load-bearing phrases out of the set, then see where each one lands.
grep -rhoE '\b[a-z-]{4,}(\s+[a-z-]{4,}){2,3}\b' --include='*.md' . \
  | sort | uniq -c | sort -rn | head -40
grep -rln "<a phrase from that list>" --include='*.md' .
```

A fact in one file is knowledge. The same fact in three is three things to keep
in step, and they will drift on the first edit.

### 3. Give each fact exactly one owner, and link the rest

Decide the owner by what the file is *for*, not by which copy reads best:
reference explains, checklists assert, procedures order, READMEs route. The
other copies become a link, or go.

**This step is the compression.** Expect most of the reduction here.

### 4. Ask what should not exist at all

Whole files and directories, not lines:

- a directory duplicating a capability that is now installed or upstream
- a file marked inferred, recalled or provisional that nobody has since verified
- a section restating what an upstream doc already documents
- an example kept because it was expensive to write

### 5. Only now compress prose

One rule per bullet: the imperative, then the evidence, ending in what it cost.
A bullet needing more than that is two bullets, or it is a story. Cut hedging,
transitions and the sentence that announces what the next sentence will say.

### 6. Enforce it mechanically, and see the guard fail once

A cap the linter checks, so the next contributor cannot undo this by accident.
Prove it can fail before trusting it: pad a file past the cap, watch it go red,
remove the padding.

```bash
for f in $(git ls-files '*.md'); do
  n=$(wc -l < "$f" | tr -d ' ')
  [ "$n" -le "$CAP" ] || echo "FAIL: $f: $n lines, over the $CAP-line cap"
done
```

### 7. Report the delta, and what you refused to cut

Before and after, per area. Name anything left long on purpose, so the next
person does not re-litigate it.

## When to STOP

- **Step 2 found no duplication.** The set is already tight. Say so and stop;
  shaving sentences to show effort is how a good doc set gets worse.
- **Cutting would drop a costed claim.** Length is never worth evidence. Move
  the claim to its owner instead.
- **The duplication crosses a repo boundary**, where the other copy is a skill,
  a package or an upstream doc. Deleting your copy changes what installs
  elsewhere: propose it, do not do it silently.
- **These are agent config files read as a set.** That is `agent-config-audit`,
  which knows the personal-versus-team boundary this skill does not.
- **The set is one document.** Just edit it.
