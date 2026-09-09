---
name: verify-db-posture-at-the-target
description: >
  Use after a change to row-level security, grants, policies or function
  privileges reaches a live Postgres or Supabase project, and before reporting
  it closed. Fires on "verify it", "did the push work", "is the advisor clear
  now", "check production", and after a hand-run fix on a database no migration
  ledger records. Do NOT fire for schema shape alone (a column, an index, a
  type), for a change that has not been applied anywhere yet, or when the only
  question is whether a test passed.
---

# Verify database posture at the target

A permission change has at least three surfaces and they disagree. The catalog
says a switch is on. The privilege functions say a role holds a grant. The API
says what a person with a browser key actually receives. Reading one and
reporting the others is how a production endpoint served an empty list to every
anonymous caller for days while `pg_class` looked perfectly healthy: row-level
security was on with no policy behind it, which is catalog-clean, deny-all, and
indistinguishable from a table that is simply empty.

Read every layer separately, and when two disagree, the API is the one users
live in.

## Procedure

1. **Catalog.** Query the objects the change names, never the migration you
   just wrote: `pg_class.relrowsecurity`, `pg_policy`, `pg_proc.proacl` and
   `proconfig`, `information_schema.role_table_grants`. A migration is a
   statement of intent; this is the outcome.

2. **Role.** Ask `has_table_privilege` and `has_function_privilege` for each
   role that matters, including the service account that actually performs the
   work, not only `anon` and `authenticated`. A privilege reaching a role
   through `PUBLIC` is invisible when you filter `proacl` by role name, so the
   obvious revoke can measure as a no-op while reading as correct.

3. **API.** GET the REST surface with the publishable key, the one that ships in
   the browser bundle. This is the layer the catalog cannot answer. Keep the
   response body: a status code alone cannot tell rows from an empty list, and
   that is the distinction. What should be readable returns rows. What should be
   closed refuses outright when the role holds no grant, but answers `200` with
   an empty list when it holds the grant and no policy admits it, so read an
   empty result against a trusted-role baseline confirming the table has rows to
   withhold. An MCP fetch proves nothing here, because it bypasses deployment
   protection; use `curl`. Where the database has no HTTP layer, connect as the
   untrusted role itself and run the statement: the point is to be the caller,
   not to describe them.

4. **Advisor, where the platform has one.** Re-run it and diff against the list
   from before the change. Classify every survivor out loud as deliberate,
   inapplicable, or open. A finding that is *new* may name an object no
   migration created: check `pg_event_trigger` and function ownership, because
   platform-managed objects and someone's pasted snippet look identical until
   you read the owner.

5. **Report per layer**, and say which layer each claim came from. "The advisor
   is clear" and "the endpoint serves rows" are different sentences.

## When to STOP

- **Never write to production to test.** A `DO` block that raises to roll itself
  back is the only mutation worth running, and only when no read can answer the
  question. Capture the exact recreate DDL with `pg_get_functiondef` before
  dropping anything.
- **Hand back** if the question needs a write and production is the only
  reachable database.
- **Do not infer the fix from a green deploy.** A migration job reporting
  success says statements ran, not that a role lost a privilege.
