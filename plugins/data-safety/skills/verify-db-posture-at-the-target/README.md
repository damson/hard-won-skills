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
select n.nspname, c.relname, c.relrowsecurity,
       count(*) filter (where p.polcmd in ('r', '*') and p.polpermissive)
         as permissive_select_policies,
       count(p.polname) as policies_any_command
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
left join pg_policy p on p.polrelid = c.oid
where c.relkind = 'r' and n.nspname = 'public' and c.relname = 'widgets'
group by 1, 2, 3;
```

`relrowsecurity = t` with `permissive_select_policies = 0` is the deny-all state
above. That one row is the whole finding, and no migration file states it.

Count the policies that can admit a *read*, not the policies that exist. A bare
`count(p.polname)` is satisfied by a policy for another command entirely, so a
table carrying only an `UPDATE` policy reports a reassuring non-zero while
`SELECT` is still deny-all. Restrictive policies never grant on their own
either, whatever their command, which is why `polpermissive` is in the filter.
Both counts are printed because their disagreement is itself the diagnosis:
policies exist, and none of them lets anyone read.

**No rows at all is a third answer, and it is not a clean one.** It means no
relation of that name in that schema, so there is nothing to report as secure.
Qualify the schema and the relation kind: `widgets` unqualified matches a
same-named table in any schema on the search path, and the row you read may not
be the one the endpoint serves.

The role, including the service account that does the work, not only `anon` and
`authenticated`:

```sql
select r                                                         as role,
       has_table_privilege(r, 'public.widgets', 'select')         as tbl_select,
       has_function_privilege(r, 'public.admin_reset()', 'execute') as fn_exec
-- `service_worker` stands in for whatever this deployment calls the account
-- that does the work; name yours, or the matrix omits the role that matters
from unnest(array['anon', 'authenticated', 'service_worker']) as r;
```

A privilege reaching a role through `PUBLIC` does not appear when `proacl` is
filtered by role name, so a revoke can measure as a no-op while reading as
correct. `has_function_privilege` resolves the inherited path; the `proacl`
filter does not.

The API, as the caller rather than about the caller:

```bash
: "${PUBLISHABLE_KEY:?set it}" "${PROJECT_URL:?set it}"
# the response IS the evidence, so refuse a transport that can rewrite it
case "$PROJECT_URL" in https://*) ;; *) echo "refusing a non-HTTPS target"; exit 1;; esac
curl -sS -w '\nHTTP %{http_code}\n' \
  -H "apikey: $PUBLISHABLE_KEY" \
  "$PROJECT_URL/rest/v1/widgets?select=id&limit=1" || echo "curl failed: $?"
```

**Keep the body.** Discarding it with `-o /dev/null` and reading only the status
code destroys the distinction this whole skill exists to make: `200` with rows
and `200` with `[]` are the same status code, and the second is the deny-all
bug. Print both.

Both directions are the check. What should be readable returns rows, so read
them. What should be closed has two legitimately different answers, and they
mean different things: a role with no table grant is refused outright with `401`
or `403`, while a role that holds the grant but meets a policy admitting nobody
gets `200` and `[]`. Only the first is legible on its own. An empty `200` is the
ambiguous one, so before believing it, confirm with a trusted role that the
table has rows to withhold; otherwise you cannot tell a closed door from an
empty room.

That confirmation is two commands, and which pair of answers you get is the
whole diagnosis:

```bash
: "${ADMIN_URL:?the baseline needs a trusted connection}"
curl -sS -w '\nHTTP %{http_code}\n' -H "apikey: $PUBLISHABLE_KEY" \
  "$PROJECT_URL/rest/v1/widgets?select=id&limit=1"        # the untrusted caller
psql "$ADMIN_URL" -c 'select count(*) from public.widgets;'  # the baseline
```

`200` with `[]` from the first and a count above zero from the second is the
deny-all finding: rows exist and the anonymous caller is admitted by no policy.
`200` with `[]` and a count of zero is not a finding at all, because the table
is empty and the probe has told you nothing either way. Report which of the two
you saw, and never the first half alone.

Fetching any of this through an MCP browser tool proves nothing, because it can
carry deployment protection the anonymous caller does not have.

Where the database has no HTTP layer, connect as the untrusted role and run the
statement:

```bash
: "${ANON_URL:?set it}"
# libpq defaults to sslmode=prefer, which falls back to plaintext without saying so
PGSSLMODE=verify-full \
psql "$ANON_URL" -c "select current_user; select id from public.widgets limit 1;"
```

`verify-full` is not free: libpq verifies against `~/.postgresql/root.crt` and
does **not** fall back to the operating system's trust store, so with no such
file the command fails on the certificate rather than connecting in the clear.
That is the right direction to fail, but the error names the certificate and not
the cause, so point `PGSSLROOTCERT` at the provider's CA bundle before deciding
the database is unreachable.

Connect as the role, rather than assuming it. `set role anon` from a superuser
session needs membership and keeps `BYPASSRLS` where the login role carries it,
so it can read rows the real caller never would. Selecting `current_user` first
is the cheap proof that the connection is who you think.

## Related

- `probe-migration-in-transaction` (this plugin): the same question asked
  *before* the change reaches anything, inside a transaction that rolls back.
  Use that one first; this one is for the database that already received it.
- `read-only-db-probe` (this plugin): the throwaway-script mechanics for
  quoting what a live database actually returned.
- `diagnose-a-lying-signal` (verification plugin, if installed): the general
  case of a green surface that measured nothing, of which the clean advisor
  over a deny-all table is one instance.
