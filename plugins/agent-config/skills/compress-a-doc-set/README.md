# compress-a-doc-set

Runs when someone asks for a set of documents to be made shorter, and cuts in
the order that actually finds the bulk: duplicated facts first, whole files
that should not exist second, prose last. The failure it prevents: three rounds
of sentence-polishing that each report a diff and leave the request coming back,
because the length was never in the sentences.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it produces and
how to reach it.

## Using it

It auto-triggers on a request to shorten a doc set, and you can ask directly:

- "trim this" / "it is too long" / "can this be smaller"
- "hardly readable" / "still too verbose"

It fires on a **set**, a `docs/` tree, a playbook, a handbook, a skills
directory, where a fact can hide in more than one file. A single document is
just an edit. Agent config files read as a set go to `agent-config-audit`,
which knows the personal-versus-team boundary this skill does not.

## Example

A private playbook had grown to 1744 lines over five contributions. Two rounds
of prose compression took it to 991 and the request came back both times. The
third round ran this order instead:

```
Duplicated facts (step 2)
  "required check needs a producer on every PR"  → reference, checklist, playbook
  "actions pinned to full commit SHAs"           → reference, checklist, sweep
  "floating major tag moves with the release"    → reference, playbook, launch
Owner assigned (step 3): reference explains, checklists assert, playbooks order

Should not exist (step 4)
  prompts/  (4 files, 210 lines) duplicated four installed skills
  famous-projects.md (44 lines) marked inferred, never verified

Result: 991 → 854 lines in this round, 1744 → 854 across all three
Cap of 100 lines/file enforced in CI
```

The two prose rounds removed 753 lines and this one removed 137, so the
duplication pass was not the larger haul. It was the one that could reach what
the other two had walked past twice: a directory duplicating four installed
skills is invisible to any amount of sentence tightening, and it was still there
after two rounds of looking. That is the argument for the order, and it is about
what each pass can see rather than how much it removes.

Two judgement calls it encodes: repetition is sometimes load-bearing, so a
one-way-line safety fact stated in the checklist a person actually runs is kept
rather than linked; and a guard is not trusted until it has been seen failing,
so the length cap is padded past its limit once and watched go red before the
number is believed.

## Related

- `agent-config-audit`: the same duplication question for CLAUDE.md and
  preference files as a set, and it returns an audit rather than a compression.
- `redundancy-check-before-ship`: the gate that stops a duplicate rule landing;
  this skill is what you run once enough of them already have.
