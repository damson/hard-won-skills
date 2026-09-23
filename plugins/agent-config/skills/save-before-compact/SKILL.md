---
name: save-before-compact
description: >
  Use ONLY when the user explicitly wants to compact a long session without
  losing its learnings — triggers like "save before compact" / "wrap up and
  compact" / "session's too long, compact but keep the takeaways" / "capture
  learnings then compact". NEVER fire unsolicited. This skill APPLIES changes
  (CLAUDE.md / preference-file additions, memory, new skills) and writes a resume
  brief, then stops for the user to run /compact — it never runs /compact itself.
  Memory entries and ordinary documentation that clear Step 4's bar apply
  automatically, weak candidates are discarded, and CLAUDE.md / AGENTS.md /
  preference files and skills always ask; "prompt-all" (or "ask me about
  everything") restores per-item approval for every target. Thin sessions get
  only the resume brief; in-flight high-stakes ops defer (Step 1 has the
  thresholds).
---

# Save before compact

## Procedure

Run a task per step, in order. Any step can short-circuit per its stated skip
conditions.

### Step 1 — Pre-flight

- Count substantive turns (ignore < 10-word acknowledgements: `thanks`, `ok`,
  `yes`, `nice`). If `< 15`, say so and skip straight to the resume brief (Step 8)
  — nothing worth persisting, but the pick-up note still gets written.
- Detect context: is there a `CLAUDE.md` / `AGENTS.md` nearby? a skill-structure
  test suite or a config eval command, if the repo ships either (check its
  README / justfile / package scripts — do not assume names)? Record what's
  available — later steps branch on it.
- Settle the **approval mode**, and carry it into every later step. Default is
  **auto**: memory entries and ordinary documentation that clear Step 4's bar are
  written without asking, while instruction files (`CLAUDE.md`, `AGENTS.md`,
  preference files) and skills always ask. **prompt-all** restores per-item
  approval for every target, and is triggered either by an argument to the skill
  (`prompt-all`, `--prompt-all`, `ask-all`) or by a plain-language request in the
  same invocation: "ask me about everything", "prompt for all", "review each
  one", "don't write anything without asking". No mode runs the other way: there
  is no setting that makes a skill apply itself.
- Defer (one line, then stop) if a high-stakes op is in flight — scan the last
  ~5 turns for a deploy / merge / rebase / migration / incident command whose
  completion was never confirmed (confirmed = its success output is in the
  transcript, or the user said it landed) — or if this is another operator's transcript.

### Step 2 — Reflect & route

List candidate facts under these categories: commands discovered, code-style
patterns followed, testing approaches that worked, environment/config quirks,
gotchas, decisions made. Then apply the **keep-test** — keep a fact only if (a) it
would prevent a mistake a capable future session would realistically make (not
restate the default behaviour, or what a neighbouring directive/test already
implies) and (b) it is not already stated in an existing config/CLAUDE.md file.
When unsure, drop it: a weak addition bloats the file and lowers eval scores; a
missed one costs nothing. For each keeper, pick a target — **versioned first**:

| Target | For | Class (Step 4) |
|---|---|---|
| `CLAUDE.md` / `AGENTS.md` (team-shared) | Repo-wide facts future sessions need | 3, always ask |
| personal preference files — the ones `readlink ~/.claude/*.md` resolves into the config repo (none resolving → no such layer exists; route to memory) | Personal cross-project preferences | 3, always ask |
| ordinary documentation: a file under `docs/`, a reference page, a sibling `README.md` | Procedure and rationale too long for an instruction file | 2, auto |
| memory store (`~/.claude/…/memory/`) — **last** | Durable facts fitting no versioned file (un-versioned, lowest priority) | 1, auto |

The class decides who applies the line, never where it belongs: route by the
table's middle column first, then read the class off the row you landed on.
Routing a fact to `docs/` because class 2 applies itself is the one way to
misuse this table.

Respect repo conventions: don't fatten a file the repo keeps as a one-line pointer
to a sibling; keep whatever style and secret-lint rules it enforces; match the
target file's format.

### Step 3 — Draft (brevity gate)

One concept per line, minimal, in the target's format. Anything that failed the
Step 2 keep-test, or restates an existing line, does not get drafted. Shorter is
better as long as it stays relevant and performant.

### Step 4 — Assess and apply

Say which mode you are in, in one line, **before writing anything**: "Mode:
auto, memory and documentation additions that clear the bar apply without
asking, instruction files and skills ask" or "Mode: prompt-all, every addition
asks". An automatic write is never silent about being automatic.

In **prompt-all**, show each addition as a diff (target, why in one line, the
line) and the user applies or skips each. That is the whole step.

In **auto**, sort every drafted addition by the **class of its target**, using
the same classes as Step 2's routing table, and sort it before touching a file:

| Class | Target | Outcome |
|---|---|---|
| 1. Memory | the memory store | Apply automatically when it clears the bar below, else discard |
| 2. Ordinary documentation | a file under `docs/`, a reference page, a sibling `README.md` | Apply automatically when it clears the bar below, else discard |
| 3. Agent instruction files | `CLAUDE.md`, `AGENTS.md`, a personal preference file | **Always ask**, with the audit in hand (below). A candidate that fails the keep-test is discarded rather than asked about |
| 4. Skills | a new or materially changed `SKILL.md` | **Always ask** (Step 7 owns the procedure) |

Classes 3 and 4 are never automatic, at any quality: an instruction file loads
into every future session, and a bad line there is paid for over and over, where
a wrong `docs/` paragraph is read once by someone who can see it is wrong. Class
4 costs more still, per Step 7.

**The bar, for classes 1 and 2: clearly relevant AND clearly high quality, both
halves required.**

- *Clearly relevant*: the fact came out of something that actually happened this
  session (a command that failed, a correction the user made, a quirk that cost
  time), it is about the repo or toolchain the session worked in, the target
  file is one that loads for that work, and it passes both clauses of the Step 2
  keep-test.
- *Clearly high quality*: score the drafted line on Step 5's five dimensions
  before writing it. Automatic apply needs the top band, `A` (≥ 23/25) with no
  single dimension under 4. `B` is deliberately not the bar here: `B` ships a
  skill the user chose to create, it does not authorise a write nobody was asked
  about.

**Never automatic even in classes 1 and 2, whatever it scores.** Ask, or drop
the candidate: a line that contradicts or rewrites an existing line rather than
adding to one (resolving a contradiction is a decision, not an addition); an
edit to a file the repo keeps as a one-line pointer; the creation of a new
versioned documentation file (a new memory file is that store's normal shape and
stays automatic); anything carrying a credential, a token or a personal path;
anything outside the repo and the personal config layer.

**Before prompting for a class 3 change, put an audit in the prompt.** The user
decides with the finding in hand or not at all.

- Run `agent-config-audit` (Skill tool) **once for the whole batch**, not per
  line: it reads the instruction stack, so per-candidate runs multiply the wait
  for the same answer.
- *Availability*: look for `agent-config-audit` in the session's available
  skills before invoking it, and treat an invocation that errors as unknown as
  unavailable. It ships in this same plugin, so it is normally present, but a
  partial or single-skill install is exactly the case that breaks silently.
  Unavailable means prompt anyway, and the prompt says the audit did not run:
  an unaudited prompt must never read like an audited one.
- *Bound the wait at 2 minutes.* The audit resolves which instruction files load
  and reads that handful; past two minutes it is sweeping something larger than
  the stack, and the user is at the end of a long session waiting to press
  `/compact`. When the bound trips, stop waiting, prompt, and say the audit was
  skipped for time.
- The audit *informs* the prompt, it does not decide it. Quote the findings that
  touch the file being changed (a contradiction with an existing line, a
  duplicate of a rule the stack already carries, a boundary violation), then
  still ask, and the user still applies or skips.

**Discarding is the point, not a loss.** A candidate that is unsure, marginal or
low-impact is dropped. Surfacing it "just in case" is the exact failure this
step replaces: it turns a free automatic step back into an interruption, and a
user interrupted over a weak line approves it to get moving, which is how the
file bloats. Step 2 already says a missed fact costs nothing; here that is
enforced rather than handed to the user.

When no user reply can arrive (a headless or scheduled run, anything where
asking cannot block), the automatic band still applies, because it asks nothing;
everything in the ask band is recorded in the resume brief as proposed, not
applied.

Keep a three-way ledger: applied automatically, applied after approval,
discarded with a one-line reason each. For every class 3 candidate, record
which of the three audit states it was prompted under: audited, audit
unavailable, audit skipped for time.

### Step 5 — Verify & score

After applying:
- **Structural**: if any skill file was touched and Step 1 found a
  skill-structure suite, run it; otherwise (no suite, or no skill file touched)
  re-Read each edited file and check two things: the applied line is exactly
  what Step 4 drafted, the approved diff in prompt-all, and any YAML
  frontmatter still parses (a stray `:` or unclosed quote silently breaks the
  whole file's load).
- **Score** the changed files with the repo's eval command if Step 1 found one,
  reading the **newest** result artifact it writes and checking its mtime —
  a stale artifact from a previous run reads exactly like a fresh score;
  otherwise an inline rubric, 1–5 per dimension — clarity (unambiguous on
  first read), conciseness (nothing restated), completeness (no undefined
  branch), consistency (no two rules disagree), actionability (every step maps
  to a command or edit). Anchors: 5 = no violation found; 4 = one minor; 3 =
  a violation a future session would trip on; 2–1 = actively misleading. Map
  the /25 total as the harness does: A ≥ 23, B ≥ 20, C ≥ 17, D ≥ 14, else F.
- A score regression or a violated repo rule (a file kept as a one-line pointer
  fattened, a character the repo's lint bans, anything a secret scanner would
  catch) means the line does not stand. Revert an automatically applied line
  first and report the revert, because nobody approved it; for an approved one,
  surface it and offer to tighten or revert. Never silently ship a regression.

### Step 6 — Memory (lowest priority)

Only durable facts that fit no versioned file. Write per the memory-file
convention (frontmatter + one fact) and add the one-line `MEMORY.md` pointer.
Skip entirely if no memory store exists. This is class 1: in auto mode an entry
that cleared Step 4's bar is written here without asking, and one that did not
is discarded, not offered; in prompt-all it is shown and approved like the rest.

### Step 7 — Suggest & create skills

Invoke `skill-opportunity-finder` (Skill tool) to surface repeated patterns worth
a new skill; where it is not installed, scan for its patterns inline — repeated
corrections, repeated manual operations, repeated discovery work — and say the
scan was inline. Present each candidate — name · one-line rationale · concrete past
trigger. For each the user **approves, create it now, before compaction**, via the
skill-verification loop: write the new `SKILL.md` → run the repo's skill structure
tests → score it with the repo's eval command (inline rubric where no harness) →
address actionable findings (**B ships**). Same draft, approve, verify, score
discipline as Steps 4 and 5. Creation runs here, not after `/compact`, because
authoring a good skill needs the live session context compaction discards.
Declined candidates go into the resume brief for later. Skip the step if no
repeated pattern surfaced.

**A skill always asks, in every mode and every run.** No argument, no
plain-language request and no headless run makes skill creation automatic:
prompt-all widens what is asked about, nothing narrows it, and a headless run
records skill candidates as proposed rather than creating them. The asymmetry
with classes 1 and 2 is the point. A skill changes behaviour in every future
session and in every install that has the plugin, including other people's;
a memory line or a documentation paragraph changes one project's context and is
undone by deleting one line. Unequal blast radius, unequal gate.

### Step 8 — Resume brief

Compose a tight *pick-up-here* note — never a transcript: **Goal · Done ·
Next actions · Open questions · Key files/commands/decisions**. Save it, then mirror it to a stable
pointer:

```bash
repo=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-'); : "${branch:=nobranch}"
ts=$(date +%Y%m%d-%H%M%S)
sid=$(echo "${CLAUDE_SESSION_ID:-$PWD}" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1); : "${sid:=nosession}"
dir=.claude; mkdir -p "$dir" && [ -w "$dir" ] || dir="${TMPDIR:-/tmp}"   # fall back if the repo dir is unwritable
f="$dir/${repo}-${branch}-${ts}-${sid}.md"
```

Write the brief to `$f` and copy it to `$dir/session-resume-latest.md` so a
post-compact "read the latest brief" always resolves. Echo the brief inline — the
file survives compaction where an inline note may be compressed.

### Step 9 — Compact handoff

Print the mode, then the ledger in three bands, so the user can audit what
happened without having been asked:

- **Applied automatically**: target, the line, and the one reason it cleared the
  bar.
- **Applied after approval**: every instruction-file change (with the audit
  state it was prompted under: audited, audit unavailable, audit skipped for
  time), every skill created, and in prompt-all everything else.
- **Discarded**: the candidate in a few words, and which half of the bar it
  failed.

Then the scores, the memory entries written, any declined skill suggestions, and
the resume-brief path. Then say:

> Learnings saved and verified, resume brief at `<path>` — safe to run `/compact`
> now. I'll read it to pick up.

Stop. The user presses `/compact`.

## When to STOP

The gates live inside the steps: the bar and the class split in Step 4, the
audited prompt every instruction-file change waits on there, the unconditional
skill approval in Step 7, regression and repo-rule checks in Step 5,
thin-session and high-stakes short-circuits in Step 1. When one fires, act as
written there and say so in one line. Two stops end the skill itself: Step 1's
high-stakes defer, and Step 9's handoff waiting for the user to run `/compact`.
