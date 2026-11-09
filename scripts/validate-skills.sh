#!/usr/bin/env bash
#
# Validate the structure of every skill in this marketplace.
#
# ── Vendored ─────────────────────────────────────────────────────────────────
# Adapted from agent-config-harness, bin/validate-skills.sh, at commit
# 232ee14a00902eeacface791103f6236064cdc90. MIT licensed, © 2026 Damien Dagnet.
#
# It stays vendored now that the harness is public for a different reason:
# contributors get the exact check CI runs with zero extra clones, and CI needs
# no network fetch beyond its own checkout. The four logging helpers it took
# from the harness's lib/common.sh are inlined below; nothing else was changed
# except the default root, which walks plugins/*/skills, and one check the
# harness does not have yet: a bare `$N` in a skill body. A refresh keeps it.
#
# Refresh when the harness's copy moves:
#
#   diff scripts/validate-skills.sh <harness>/bin/validate-skills.sh
#
# Usage:
#   ./scripts/validate-skills.sh              # every plugin in this repo
#   ./scripts/validate-skills.sh <dir>        # one skills tree
#
# Exits non-zero if any skill fails, after reporting all of them — a validator
# that stops at the first failure makes you run it once per problem.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Inlined from the harness's lib/common.sh. Colour only when stdout is a
# terminal: GitHub Actions logs keep the escape codes otherwise, which turns
# every failure line into noise.
if [ -t 1 ]; then
    _color() { printf '\033[%sm' "$1"; }
    _reset() { printf '\033[0m'; }
else
    _color() { :; }
    _reset() { :; }
fi
log_ok()    { printf '%s%s%s %s\n' "$(_color '0;32')" "✔" "$(_reset)" "$*"; }
log_warn()  { printf '%s%s%s %s\n' "$(_color '0;33')" "⚠" "$(_reset)" "$*" >&2; }
log_error() { printf '%s%s%s %s\n' "$(_color '0;31')" "✗" "$(_reset)" "$*" >&2; exit 1; }

usage() { sed -n '/^# Usage:/,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

roots=()
label=""
case "${1:-}" in
    -h|--help) usage 0 ;;
    "")
        # Every plugin's skills tree. A plugin without one is not an error —
        # a plugin may ship only commands or agents.
        while IFS= read -r d; do roots+=("$d"); done \
            < <(find "$REPO_ROOT/plugins" -mindepth 2 -maxdepth 2 -type d -name skills | sort)
        [ "${#roots[@]}" -gt 0 ] || log_error "No plugin under plugins/ ships a skills/ directory"
        label="this marketplace"
        ;;
    *)  [ -d "$1" ] || log_error "Not a directory: $1"
        roots=("$1"); label="$1" ;;
esac

# Collect every skill directory: one containing a SKILL.md, at depth 1 (plain)
# or 2 (grouped under a container folder).
skills=()
for r in "${roots[@]}"; do
    while IFS= read -r p; do skills+=("$p"); done < <(
        find "$r" -mindepth 1 -maxdepth 2 -type d -exec test -f '{}/SKILL.md' \; -print | sort
    )
done

[ "${#skills[@]}" -gt 0 ] || log_error "No skills found under $label"

fail=0
problem() { log_warn "$1"; fail=$((fail + 1)); }

# Frontmatter is the first --- ... --- block; read a scalar key out of it.
frontmatter_value() {
    awk -v key="$2" '
        NR == 1 && /^---[[:space:]]*$/ { infm = 1; next }
        infm && /^---[[:space:]]*$/    { exit }
        infm && $0 ~ "^" key ":" {
            sub("^" key ":[[:space:]]*", ""); gsub(/^["'"'"']|["'"'"']$/, "")
            print; exit
        }
    ' "$1"
}

declare -a seen_leaves=()
for p in "${skills[@]}"; do
    leaf=$(basename "$p")
    f="$p/SKILL.md"

    name=$(frontmatter_value "$f" name)
    if [ -z "$name" ]; then
        problem "$leaf: frontmatter has no 'name:'"
    elif [ "$name" != "$leaf" ]; then
        problem "$leaf: frontmatter name is '$name' — it must match the folder name"
    fi

    # A description can be a folded block (description: >), so accept any
    # non-empty content on the key line OR on the lines that follow it.
    if ! awk '
        NR == 1 && /^---[[:space:]]*$/ { infm = 1; next }
        infm && /^---[[:space:]]*$/    { exit }
        infm && /^description:/        { started = 1
                                         sub(/^description:[[:space:]]*>?[[:space:]]*/, "")
                                         if (length($0)) { found = 1 } ; next }
        started && /^[a-zA-Z_-]+:/     { exit }
        started && NF                  { found = 1 }
        END { exit(found ? 0 : 1) }
    ' "$f"; then
        problem "$leaf: frontmatter 'description:' is missing or empty"
    fi

    grep -qE '^## +(Procedure|Step [0-9])' "$f" \
        || problem "$leaf: no '## Procedure' or '## Step N' section"

    grep -qE '^## +When to STOP' "$f" \
        || problem "$leaf: no '## When to STOP' section"

    # A skill body is filled in with its invocation's arguments before the agent
    # reads it, fenced code included: `$1` becomes the second word passed. Invoked
    # with no arguments it reads intact, so nothing else here would notice.
    # `${1}` (shell) and `$(1)` (awk) mean the same and are left alone.
    if lines=$(grep -nE '\$[0-9]' "$f" | cut -d: -f1 | paste -sd, -) && [ -n "$lines" ]; then
        problem "$leaf: bare \$N on line(s) $lines is replaced by the invocation's arguments; write \${N} in shell or \$(N) in awk"
    fi

    for s in ${seen_leaves[@]+"${seen_leaves[@]}"}; do
        [ "$s" = "$leaf" ] && problem "$leaf: duplicate leaf name — skills install flat and would shadow each other"
    done
    seen_leaves+=("$leaf")
done

if [ "$fail" -gt 0 ]; then
    log_error "$fail problem(s) across ${#skills[@]} skill(s) in $label"
fi
log_ok "${#skills[@]} skill(s) in $label pass all structural checks"
