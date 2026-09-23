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
# Candidate phrases, ranked by how many FILES hold them. Ranking the extraction
# itself counts occurrences, which is a different number: on a 119-file set, 8 of
# the top 20 disagreed, once by 3.3x, and in both directions, so a phrase in ten
# files sorted below one confined to two.
grep -rhoE '\b[a-z-]{4,}(\s+[a-z-]{4,}){2,3}\b' --include='*.md' . \
  | sort -u > /tmp/phrases
while IFS= read -r p; do
  n=$(grep -rlF --include='*.md' -- "$p" . | wc -l | tr -d ' ')
  [ "$n" -ge 3 ] && printf '%3d  %s\n' "$n" "$p"
done < /tmp/phrases | sort -rn | head -40
```

**A count is a candidate, not a finding.** Follow the top hits to the files and
measure how much of one document is inside the other, because the same command
returns house style on a set with no duplication and a document copied wholesale
on a set with plenty, and the two outputs look identical. On one repository the
top hit was a README boilerplate phrase in six files, worth nothing. On another
it resolved to one file 95% contained in another, worth the whole pass. Say which
way you divide when you measure: the smaller file inside the larger, and the
larger inside the smaller, differ by more than a factor of two on the same pair.

A fact in one file is knowledge. The same fact in three is three things to keep
in step, and they will drift on the first edit.

### 3. Give each fact exactly one owner, and link the rest

Decide the owner by what the file is *for*, not by which copy reads best:
reference explains, checklists assert, procedures order, READMEs route. The
other copies become a link, or go.

Where a file is genuinely two of those, **the owner is the file a reader has
open at the moment they need the fact.** A safety rule needed while running a
procedure lives in the procedure, even though a reference file also explains
it. When that still ties, the more specific file wins over the more general
one, because a reader arrives at the general one only by search.

**A copy a tool reads by path is not a duplicate.** Before assigning an owner,
ask whether anything loads one of these files from a fixed location: a pull
request template a forge renders, a config a linter opens, a manifest a package
manager reads. Those are instances, and the tool owns the path while the master
owns the content. Replacing one with a link removes the file and the behaviour
with it, silently. On a repository tested with this skill, the single largest
duplication the previous step found, one file 95% contained in another, was
exactly this, and following the rule would have deleted the repository's pull
request form.

**This step is the compression, on a set that has duplication to find.** Expect
most of the reduction here, and see step 7 for what it means when you do not.

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

Set the cap from the set you just cut, not from taste: take the longest file
that survived step 5 and round up. A cap below a file you decided to keep makes
the guard wrong on day one and teaches everyone to ignore it.

```bash
# -z and -0 throughout: a path with a space splits into words otherwise, `wc`
# fails on each fragment, and the empty count then PASSES the comparison, so the
# one file the cap could not read reports as under it
CAP=$(git ls-files -z '*.md' | xargs -0 wc -l | awk '$2!="total"{print $1}' \
        | sort -n | tail -1)                     # the longest survivor
CAP=$(( (CAP + 9) / 10 * 10 ))                   # round up to a readable number
echo "cap: $CAP"
```

**Freeze that number into the check. Do not recompute it there.** A check that
derives its own limit from the tree it is checking cannot fail: pad a file and
the cap moves with it. Run the line above once, read the number, and write it
into the linter as a literal:

```bash
CAP=350                                          # the number you just read

git ls-files -z '*.md' | while IFS= read -r -d '' f; do
  n=$(wc -l < "$f" | tr -d ' ')
  if [ -z "$n" ]
    then echo "UNREAD: $f"                       # never silently a pass
  elif [ "$n" -gt "$CAP" ]
    then echo "FAIL: $f: $n lines, over the $CAP-line cap"
  fi
done
```

Then prove it can fail: pad a file past the cap, watch it go red, remove the
padding. A guard never seen failing is a guard nobody has tested, and with a
recomputed cap that is every run of it.

### 7. Report the delta, and what you refused to cut

Before and after, per area. Name anything left long on purpose, so the next
person does not re-litigate it.

**A small duplication haul is a finding, not a failed pass.** How much each layer
holds depends on the set's history: one never edited for length has prose to lose
first, and one already tightened has nothing left there at all. Measured on a
tightly written 558-line set, a prose pass could touch at most 5 lines while
duplication offered about 40; on a set that had never been cut, the two prose
rounds took 753 and the duplication pass 137. Report which situation you were in,
because it tells the next person whether to run this again.

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
