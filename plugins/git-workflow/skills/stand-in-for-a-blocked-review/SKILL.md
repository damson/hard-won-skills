---
name: stand-in-for-a-blocked-review
description: >
  Use when a pull request's automated review did not happen while its merge
  gate still reads green: the reviewer posted a quota or limit notice, skipped
  the pull request over who opened it, or never ran at all, and its status says
  success anyway. Confirms the review is genuinely missing, takes the cheap
  recoveries first, checks whether this exact content was already reviewed
  somewhere else, and only then commissions an independent agent review, whose
  findings are posted and answered as an ordinary review while the quota trigger
  behind it is not announced, because announcing it is a recipe for draining a
  metered budget. Do
  NOT fire when the reviewer posted findings (answer those instead), when the
  quota resets inside the time you can wait, or to decide whether the pull
  request should merge.
---

# Stand in for a blocked review

A review bot's green mark has two meanings and nothing on the outside separates
them: *reviewed and clean*, and *did not review*. A free-tier reviewer that has
spent its quota writes "Review limit reached" into its comment and leaves its
commit status at `success`. Nothing turns red, no gate blocks, and the pull
request is indistinguishable from one that passed.

That is not hypothetical. On the session this came from, a tier allowing one
review per hour let three pull requests merge into a public repository believed
reviewed, when nothing had read them. All three showed `CodeRabbit success`;
the notice sat in a comment body nobody opened.

This skill decides whether a review is actually missing, which is the step
usually skipped, then commissions one that is genuinely independent, and leaves
the pull request enough of a record to show the gate was satisfied without
publishing what the review found.

## Procedure

1. **Read the body, not the mark.** The mark answers a different question than
   the one being asked of it. Pin the head, then read what the reviewer
   actually wrote:

   ```bash
   pr=<n>; repo=<owner>/<repo>; reviewer=<reviewer-login>
   head=$(gh pr view "$pr" --json headRefOid --jq .headRefOid)

   # The gate can be a commit status OR a check run, and one API does not
   # show the other. A reviewer absent from check-runs may still be reporting
   # green as a status, which is what gates the merge.
   gh api "repos/$repo/commits/$head/status"     --jq '.statuses[]   | [.context, .state] | @tsv'
   gh api "repos/$repo/commits/$head/check-runs" --jq '.check_runs[] | [.name, .conclusion] | @tsv'

   # What it said. Reviewers keep ONE comment and edit it in place, so this is
   # its current body, not a history to scroll.
   gh api "repos/$repo/issues/$pr/comments" --paginate \
     --jq "[.[] | select(.user.login == \"$reviewer\")] | last | .body" > review-body.md
   grep -icE 'review limit reached|rate limit|quota|try again' review-body.md
   ```

   Three readings, and only the first is a review:

   | The reviewer's current body | Meaning |
   |---|---|
   | Findings, or an explicit "no issues", covering this head | It reviewed. Not this skill's job. |
   | A limit, quota or "try again in N minutes" notice | Blocked. Continue. |
   | No comment from it at all | It never ran. Usually step 2's second case. |

   **Its `created_at` cannot tell you whether it read your latest push.** The
   comment is edited in place, so creation time freezes at the first round
   while the body moves on; `updated_at` is the only timestamp that tracks what
   is written there now.

2. **Take the cheap recoveries before commissioning anything.** A real review
   beats a stand-in, and two of the three blocked cases are recoverable in
   minutes:

   - **The notice names a reset you can wait for.** These are often small
     ("next included review available in 3 minutes"). Wait, retrigger once with
     whatever phrase the reviewer documents, and re-read the body. Retriggering
     *inside* the window is worse than doing nothing: it spends the next slot
     to be told the commit was already reviewed.
   - **An app opened the pull request.** Check it, because this failure is
     silent by design: many reviewers skip bot-authored pull requests and say
     so nowhere.

     ```bash
     gh pr view "$pr" --json author --jq '.author | [.login, .is_bot] | @tsv'
     ```

     That is a configuration fix (open automated pull requests with a token
     that authors as a person), not a review problem. Standing in on every one
     of them hides the cause and pays for it forever.
   - **A fix push landed and no new review appeared.** Ambiguous on purpose:
     after a push, a reviewer that re-reads often posts no new object at all,
     and its mark going green on the new head is the only sign it read
     anything. A spent quota produces exactly that green. Step 1's body read is
     what separates them; nothing else does.

3. **Ask whether this content was already reviewed elsewhere.** Squash and
   rebase change the commit, not the tree, so a promotion or a re-cut branch
   often carries content that was reviewed under a different SHA:

   ```bash
   git rev-parse "origin/<branch>^{tree}" "<reviewed-head>^{tree}"
   ```

   Identical hashes retire the question: cite both, name where the review
   happened, and stop. They prove the *content* was seen, not that its findings
   were answered, so confirm the reply exists too. Where the trees differ, the
   stand-in only has to cover the difference:

   ```bash
   git diff "<reviewed-head>" "origin/<branch>"
   ```

4. **Brief the stand-in for independence, which is mostly about what you
   withhold.**

   ```bash
   gh pr diff "$pr" > review-input.diff
   wc -l review-input.diff        # an empty or truncated input reviews clean
   ```

   - **Give:** the diff at the pinned head, the repository's agent-facing
     instructions and contributor guide, and the claim the change makes about
     itself.
   - **Withhold:** your reasoning, your pull request description, the
     justifications in your commit messages. A reviewer handed the author's
     rationale grades the rationale, and agrees with it.
   - **Tell it to break the change, not to review it.** "Find where this is
     wrong" and "review this" return different sets from the same model.
   - **A cheap, fast model is the right one.** This is a wide read of a bounded
     diff, not a design judgement, and the cost is what makes it repeatable
     rather than a thing you do once and stop doing.
   - **It must not be the agent that wrote the diff.** A fresh context is the
     whole point; the same context carries the same blind spot and confirms its
     own work.

5. **Make it exercise the guards rather than read them.** This is what a
   stand-in offers that a skim cannot: for each check or test the diff adds,
   break the thing it guards, watch it go red, restore it. A check that has
   never failed is not known to check anything, and a reviewer that only reads
   a new test cannot tell a real one from a decorative one. (The verification
   plugin's `prove-the-check-can-fail` is the same discipline in full.)

   On the batch this came from, the stand-in reported no defects, and that
   verdict was worth something only because every new test in it had been seen
   red first.

6. **Do not announce what triggered this.** The findings are posted. What stays
   unpublished is the fact that a spent quota is what summoned them, and the
   model that produced them.

   The reason is a budget, not modesty. A public "the reviewer was rate limited,
   so an independent review ran instead" tells any reader the sequence that
   converts cheap pull requests into paid review calls, and that a spent free
   tier is what unlocks it. A repository that publishes that on every affected
   pull request has written the instructions for draining it: open enough noise
   to exhaust the free reviewer, then keep going while something metered picks
   up every one. A blocked review is routine, so the notice would appear often
   enough to be noticed.

   **This is about the trigger, not the substance.** The findings are real, they
   are posted in full, and they go out under an account that stands behind them,
   which is what makes it an ordinary review rather than a disguise. Nothing here
   licenses hiding how work was produced when somebody has a reason to ask, and
   nothing here is a reason to omit a finding, soften one, or claim a check ran
   that did not.

   Keep the untruncated account of what happened where the session keeps its own
   working notes: which model, what it was given, what it could not cover. That
   is what you answer from if anyone asks, and it costs nothing because it was
   already written.

7. **Answer every finding as an ordinary review.** One comment, one row per
   finding, in the verdicts an ordinary review reply uses (✅ Applied, 🚫 Skipped
   with a reason, ⏳ Deferred with a link, 💬 Acknowledged), which
   `pr-comment-loop` owns in full.

   - **Verify each finding against the source before acting on it.** A cold
     reader on a cheap model is confidently wrong at a predictable rate, and the
     classic miss is a demanded convention the repository does not have. This
     matters more here than usual: posted without the label, a finding carries
     the weight of the account that posted it.
   - **Write it as the review it is**, about the diff. A finding does not need a
     provenance note to be answerable, and the rows are the same rows either way.
   - **Say what changed**, naming the commits that answer the findings. Those are
     public already and they are what a later reader actually needs.
   - **The merge gate is untouched.** A pull request whose head nothing has read
     still does not merge, stand-in or not.

8. **Tell the person who owns the merge what it actually was.** The gate says
   "reviewed", and they are deciding on that word, so they get the whole picture:
   that the usual reviewer did not run, that a stand-in covered it, which model,
   and what it could not reach. That belongs in the conversation with them, not
   in the pull request, and it is the half that stops a stand-in quietly becoming
   the equivalent of the review that never happened.

## Sharp edges

- **No findings on a large diff is a fact about the brief, not the diff.**
  Confirm the agent received the whole thing: an empty, truncated or unreadable
  input produces a confident clean review with nothing behind it.
- **A stand-in is narrower than the reviewer it replaces.** It sees this diff.
  It does not see the repository's history of making this mistake before. Say
  so rather than reporting an equivalent review.
- **Two reviews of one pull request split the record.** If the real reviewer
  wakes up later and posts findings, answer those in their own thread and leave
  the stand-in's record standing as history rather than merging the two.
- **A record nobody can read is not a record.** "An agent reviewed it", with no
  head, no model and no statement of what fell outside it, satisfies nobody and
  protects nothing. Withholding the findings is not licence to withhold the
  shape of the review.

## When to STOP

- **The reviewer posted findings at this head.** Answer them; a stand-in on top
  adds noise and splits the record.
- **The quota resets inside the time you can wait.** Wait for the real one.
- **The pull request was skipped over its author.** Fix who opens it. Standing
  in every time buys the same review at a higher price and hides the cause.
- **The repository's policy requires a human review.** A stand-in does not
  satisfy it. Report the pull request as blocked and hand back.
- **A finding cannot be verified against the source.** Do not apply it, and do
  not silence it either: mark it skipped with the line that contradicts it.
- **The diff cannot be shown to an independent reviewer** (an embargo, secrets
  inside the change). Report the review as unavailable rather than reviewing
  your own work under another name.
- **Merging.** Green marks plus a stand-in authorise reporting, never the
  merge, which stays wherever it lived before.
