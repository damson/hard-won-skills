# verify-db-posture-at-the-target

Reads a permission change back from the database that actually received it,
one layer at a time, and reports which layer each claim came from. The failure
it prevents is a permission change reported as done on the strength of the one
surface that agreed with you.

Read [SKILL.md](SKILL.md) for the procedure. This file is what it produces and
how to reach it.

## Using it

Ask for it in any of these shapes; the skill fires on the intent, not on a
command:

- "did the push work?"
- "is the advisor clear now?"
- "check production"
- a policy, grant or function privilege was changed by hand, on a database no
  migration ledger records

It deliberately does **not** fire for:

- schema shape alone: a column, an index, a type
- a change that has not been applied anywhere yet
- a question whose whole answer is whether a test passed

## The disagreement it exists to catch

A permission change has at least three surfaces, and they are allowed to
disagree.

| Layer | Answers | Blind to |
|---|---|---|
| Catalog | is the switch on, does the policy row exist | whether any policy actually admits anyone |
| Role | does this role hold this grant | a privilege arriving through `PUBLIC` |
| API | what a browser key really receives | nothing, which is why it is the tiebreak |

The shape that costs days is row-level security enabled with no policy behind
it. The catalog is clean: `relrowsecurity` is `true`, which is what the
hardening ticket asked for. The role check is clean too: `SELECT` was granted
and never revoked. And the endpoint returns `[]` to every anonymous caller,
because RLS with no permissive policy is deny-all, and PostgREST renders a
denied read as an empty collection rather than an error. An empty list is
indistinguishable from a table that is simply empty, so nothing anywhere goes
red.

## What each layer is asked

The catalog, on the objects the change names rather than the migration that was
written:

```sql
select c.relname, c.relrowsecurity, count(p.polname) as policies
from pg_class c
left join pg_policy p on p.polrelid = c.oid
where c.relname = 'entries'
group by 1, 2;
```

`relrowsecurity = t` with `policies = 0` is the deny-all state above. That one
row is the whole finding, and no migration file states it.

The role, including the service account that does the work, not only `anon` and
`authenticated`:

```sql
select has_table_privilege('anon', 'entries', 'select')      as anon_select,
       has_function_privilege('anon', 'admin_reset()', 'execute') as anon_exec;
```

A privilege reaching a role through `PUBLIC` does not appear when `proacl` is
filtered by role name, so a revoke can measure as a no-op while reading as
correct. `has_function_privilege` resolves the inherited path; the `proacl`
filter does not.

The API, as the caller rather than about the caller:

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "apikey: $PUBLISHABLE_KEY" \
  "$PROJECT_URL/rest/v1/entries?select=id&limit=1"
```

Both directions are the check: what should be readable returns rows, and what
should be closed returns a refusal rather than an empty list. Fetching this
through an MCP browser tool proves nothing, because it can carry deployment
protection the anonymous caller does not have.

Where the database has no HTTP layer, connect as the untrusted role and run the
statement:

```bash
psql "$URL" -c "set role anon; select id from entries limit 1;"
```

## Related

- `probe-migration-in-transaction` (this plugin): the same question asked
  *before* the change reaches anything, inside a transaction that rolls back.
  Use that one first; this one is for the database that already received it.
- `read-only-db-probe` (this plugin): the throwaway-script mechanics for
  quoting what a live database actually returned.
- `diagnose-a-lying-signal` (verification plugin, if installed): the general
  case of a green surface that measured nothing, of which the clean advisor
  over a deny-all table is one instance.
