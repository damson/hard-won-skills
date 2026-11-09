# hard-won-skills

![Terminal-styled banner: a claude session announcing the hard-won-skills marketplace, over the tagline "Hard-won habits for Claude Code"](docs/assets/social-preview.png)

*Hard-won habits for [Claude Code](https://claude.com/claude-code), packaged so
you don't have to win them the hard way too.*

[![CI](https://github.com/damson/hard-won-skills/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/damson/hard-won-skills/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/damson/hard-won-skills?label=release&color=blue)](https://github.com/damson/hard-won-skills/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage](https://codecov.io/gh/damson/hard-won-skills/branch/develop/graph/badge.svg)](https://codecov.io/gh/damson/hard-won-skills/branch/develop)
[![Made for Claude Code](https://img.shields.io/badge/made%20for-Claude%20Code-d97757.svg)](https://claude.com/claude-code)

👋 **Welcome!** This is a marketplace of **52 skills in 6 themed plugins**:
small, careful procedures your agent picks up automatically when a task calls
for them: rebasing a stack of PRs without losing one, proving a screenshot test
actually compared pixels, probing a migration without leaving a trace.

What holds them together is where they came from. **Every skill here was
extracted from a real session where not having it cost something**: a check
that could never fail, a release that could not tag itself, forty-seven stale
branches nobody could see. The measured facts stayed in the text, and so did
the scars: each skill knows not just what to do, but when to stop and ask.

**Jump to:**
[Quick start](#-quick-start) ·
[Pick your themes](#-pick-your-themes) ·
[What a skill looks like](#-what-a-skill-here-looks-like) ·
[The harness](#-the-harness-behind-these-skills) ·
[Contributing](#-contributing) ·
[Releases](#-releases)

## 🚀 Quick start

Two commands and you're in:

```bash
claude plugin marketplace add damson/hard-won-skills
claude plugin install git-workflow@hard-won-skills --yes
```

Swap `git-workflow` for any plugin in [the table below](#-pick-your-themes),
and install as many as you like. Both commands are safe to re-run (idempotent, exit `0`), `--yes` is
only required when stdout is not a TTY, and `claude plugin update` re-fetches
just the plugins whose version moved.

**Then… do nothing.** You don't invoke a skill so much as walk into it: each
one declares the situations and phrases it fires on, and the agent picks it up
when your task matches: "rebase the open PRs", "do the baselines still pass",
a push to a branch with an open PR. Curious what you just installed? Each
plugin's page in the table below lists its skills, and every skill has a README
beside its procedure with its triggers and a worked example.

## 🗂 Pick your themes

| Plugin | Skills | What it is for |
|---|---|---|
| **[git-workflow](plugins/git-workflow/README.md)** | 19 | Branch, worktree and pull-request hygiene |
| **[agent-config](plugins/agent-config/README.md)** | 10 | Writing and auditing agent instruction files |
| **[verification](plugins/verification/README.md)** | 8 | Proving a check can fail before trusting it |
| **[data-safety](plugins/data-safety/README.md)** | 6 | Writes that are hard to undo |
| **[mobile-ui](plugins/mobile-ui/README.md)** | 8 | Android / Compose screenshots, Figma components, on-device checks |
| **[design-ethics](plugins/design-ethics/README.md)** | 1 | Whether a money or consent flow persuades or deceives |

Not sure where to begin? **[verification](plugins/verification/README.md)** takes a minute to
read and changes how you look at every green checkmark you'll ever see again.
If you only ever install one plugin, that's the one we'd hand you.

## 🧬 What a skill here looks like

Every skill is two files:

- **`SKILL.md`**, the procedure the agent follows: frontmatter whose `name`
  matches its folder, a `## Procedure`, and a **`## When to STOP`** section.
  That last one is the part most skill collections leave out, and it is what
  stops a skill firing on a task it should decline: the difference between a
  procedure and a hazard.
- **`README.md`**, the half written for you: what the skill produces, the
  phrases that reach it, a worked example, and the sibling skills it hands
  off to.

Skills are written to be **portable**: none names a path from the repo it came
from, or assumes a folder layout. Where one can take advantage of tooling you
may not have, it says so and degrades instead of failing.

## 🔬 The harness behind these skills

These were extracted while building
**[agent-config-harness](https://github.com/damson/agent-config-harness)**:
agent instruction files, scored and regression-tested like code. If this
marketplace is the habits, that repo is the bench they were measured on, and
`scripts/validate-skills.sh` here is vendored straight from it.

It asks the question a `CLAUDE.md` rarely gets asked: when did you last measure
it? Config files are graded one to five on clarity, conciseness, completeness,
consistency and actionability, out of 25 with a letter grade and named
findings, recorded per domain over time so an improvement is distinguishable
from a rewrite that merely felt productive. A `bats` suite covers the
structural invariants a rubric cannot see, including the skill layout this
marketplace's own CI enforces.

It is also a GitHub Action, so a build fails when config quality slips below a
grade you choose:

```yaml
- uses: actions/checkout@v4
- uses: damson/agent-config-harness@v1
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  with:
    files: CLAUDE.md
    fail-below: C
```

Seeing what a grade looks like costs no API key: two real eval runs ship in the
repo, the same config one edit apart, 24/25 and 13/25.

## 🤝 Contributing

Found a rough edge? That's exactly the kind of thing this repo is made of: a
skill that stopped matching its tool's current behaviour is a bug worth
reporting even without a fix, and small contributions count: a clearer worked
example, a sharper trigger, a STOP case you hit in the wild. The bar for a
new skill is the lineage above: it encodes something that actually went wrong
and would go wrong again.

**[CONTRIBUTING.md](CONTRIBUTING.md) is the complete guide**: ways to
contribute, what a skill ships as, the three validators to run before pushing,
and the conventions they cannot see.

## 📦 Releases

`develop` integrates, `main` is what `claude plugin marketplace add` installs.
A workflow promotes one to the other every three days, but only when there is
something to promote and the CI suite passes: plugins that changed get a patch
bump, the marketplace gets a CalVer tag. Gates, couplings and how to hold a
release: [docs/releases.md](docs/releases.md).

[MIT licensed](LICENSE). Use them, fork them, make them yours.
