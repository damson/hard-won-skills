# save-before-compact

A pre-compaction gate for long sessions: captures what the session taught into
the right homes (CLAUDE.md / preference files / docs / memory; versioned targets
first), optionally creates the skills the session earned, writes a resume
brief, then stops for you to run `/compact`. The failure it prevents: a long
session's hard-won learnings evaporating because compaction summarised them
away.

It asks you about what is expensive to get wrong, and only that. A memory entry
or an ordinary documentation addition is applied for you when it clears the bar,
and dropped when it does not. A change to an instruction file (CLAUDE.md,
AGENTS.md, a preference file) always asks, with a config audit in the prompt
where one can run. A new or changed skill always asks. Want the old behaviour,
prompted on every last line? Invoke it with `prompt-all`, or just say "ask me
about everything".

Read [SKILL.md](SKILL.md) for the nine-step procedure.

**It never fires unsolicited**, and it never runs `/compact` itself: that last
keypress is always yours.

## Using it

- "save before compact"
- "wrap up and compact"
- "session's too long, compact but keep the takeaways"
- "capture learnings then compact"
- "save before compact, prompt-all" (or "ask me about everything"), when you
  want to approve every line, memory and docs included

It skips thin sessions (fewer than ~15 substantive turns go straight to the
resume brief), defers when a high-stakes operation is in flight (deploy,
mid-merge, incident), and refuses to run on someone else's transcript.

## Example

After a 40-turn debugging session:

1. It states the mode it is running in, then lists candidate facts (commands
   discovered, gotchas, decisions) and applies the keep-test: keep only what
   would prevent a realistic future mistake and is not already written down.
   Weak candidates are dropped without a question: a missed one costs nothing,
   a weak one bloats the file, and being asked about one costs you the
   interruption the automatic step was meant to save.
2. Each survivor is sorted by where it lands. A memory entry or a `docs/`
   addition that clears the bar (relevant to what actually happened this
   session, and top-band on the five-dimension rubric) is **applied for you**.
   A CLAUDE.md, AGENTS.md or preference-file line is **shown and waits for
   you**, with `agent-config-audit`'s findings quoted in the prompt when it is
   installed and returns inside two minutes, and a plain note that it did not
   when it isn't or doesn't.
3. Applied changes are verified (the repo's skill-structure tests or eval
   command if it ships one, an inline five-dimension rubric otherwise).
4. `skill-opportunity-finder` runs (or, where that plugin is not installed,
   the same pattern scan happens inline and says so); approved skill
   candidates are created *now*, before compaction: authoring a good skill
   needs the live context that compaction discards.
5. A resume brief (Goal · Done · Next actions · Open questions · Key files) is
   written into `.claude/` with a stable `session-resume-latest.md` pointer,
   the ledger is printed in three bands (applied automatically, applied after
   your approval, discarded and why), and the skill stops:

   > Learnings saved and verified, resume brief at `.claude/…`, safe to run
   > `/compact` now. I'll read it to pick up.

## Related

- `skill-opportunity-finder`: invoked as step 7 to surface patterns worth a
  new skill.
- `agent-config-audit`: invoked in step 4 before an instruction-file prompt, so
  you decide with its findings in front of you rather than after the write.
- `session-retro`, the report-only sibling: it produces signal and applies
  nothing, where this skill applies approved changes before the context is
  lost.
