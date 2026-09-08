# verification

Six skills for the same failure: believing something that has never been
observed doing what it claims, or a summary of it that nobody checked.

```bash
claude plugin install verification@hard-won-skills --yes
```

A green check is not evidence until it has been seen red: passing proves it
ran, only failing proves it was looking at the right thing. And a library's
name, its field names and its README are all claims; the bytecode is what
runs. Every skill here replaces trust with one cheap observation, and they were
earned the usual way: a check that could never have failed got reported as
coverage, and a "fix" that set an option to its own default advertised a
guarantee nobody had added.

If you install only one plugin from this marketplace, make it this one: it
changes how you read every green checkmark that follows.

## The skills

| Skill | What it does |
|---|---|
| [`prove-the-check-can-fail`](skills/prove-the-check-can-fail/README.md) | Introduce the defect the check exists to catch, watch it go red, restore, report both halves, before trusting or citing it |
| [`verify-dependency-behaviour`](skills/verify-dependency-behaviour/README.md) | When docs are absent and naming is suggestive: read the artifact that actually runs, and quote the constant, not the conclusion |
| [`diagnose-a-lying-signal`](skills/diagnose-a-lying-signal/README.md) | When a check, badge or exit code disagrees with reality: read the authoritative record before debugging work that was never broken |
| [`mutation-proof-harness`](skills/mutation-proof-harness/README.md) | Run the break-it-and-watch-it-go-red loop over several guards at once, refusing to count a filter that selected nothing or a mutation that changed nothing |
| [`prove-a-procedure-on-a-fixture`](skills/prove-a-procedure-on-a-fixture/README.md) | Build a throwaway fixture holding every case a documented procedure claims to handle, run its published commands verbatim, and record what the rule it replaced answered |
| [`render-the-candidates`](skills/render-the-candidates/README.md) | When a layout requirement has round-tripped twice: state the numbers, build each reading through the real code path, and ask with the cost of each attached |

Each skill's README carries its triggers and a worked example; the `SKILL.md`
beside it is the procedure the agent follows.

## If one of these misfires

Every skill here was extracted from a real session, which means it is proven
where it was written and nowhere else. Yours is a different project, so the first
report of a command that errors, a flag that has vanished or an assumption that
no longer holds will probably be yours.

- [Report a stale skill](https://github.com/damson/hard-won-skills/issues/new?template=stale-skill.yml)
- [Propose a new one](https://github.com/damson/hard-won-skills/issues/new?template=skill-proposal.yml), for
  something that went wrong and would go wrong again
- [CONTRIBUTING](https://github.com/damson/hard-won-skills/blob/main/CONTRIBUTING.md) has the bar for both
