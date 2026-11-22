#!/usr/bin/env python3
"""Parse-check every shell block this marketplace publishes.

A skill's shell block is the part a reader pastes into a terminal. A block that
cannot even parse is not a typo in prose: it is a step that cannot be followed,
and one shipped green because nothing here read the shell it publishes.

`bash -n` parses without executing, so this never runs a skill's commands.

A placeholder outside quotes is an error, though bash parses it happily: in
`gh pr view <n>`, `<n>` is a redirect from a file named `n`, so the pasted line
runs a different command or fails on a missing file. Blocks quote it instead
(`gh pr view "<n>"`): one literal word, never a redirect, and nothing stored
for a later line to reuse. A placeholder inside quotes, a comment or a heredoc
body is text, not syntax, except inside a `$(...)` or backticks, which are
commands wherever they sit, an unquoted heredoc body included. The parse blanks
every placeholder before it runs, so what it reports is a real syntax error --
an unbalanced quote, an unterminated loop, a `case` with no `esac`.

Usage:
  python3 scripts/validate-shell-blocks.py              # every plugin here
  python3 scripts/validate-shell-blocks.py <dir>        # one tree

Exits non-zero if any block fails, after reporting all of them.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

# A fence opens on its own line, so a ``` appearing inside a line of code -- a
# regex matching mermaid fences, say -- does not close the block early.
#
# Markdown fences are three or more backticks OR three or more tildes, and a
# block closes only on the same character, at least as long, carrying no info
# string. A checker that recognises only the exact three-backtick form does not
# report the others as bad: it skips them, and reports success for a file it
# never read.
OPENING = re.compile(r"^(\s*)(`{3,}|~{3,})[ \t]*([^`\s]*)[ \t]*$")
CLOSING = re.compile(r"^\s*(`{3,}|~{3,})[ \t]*$")

# `<name>`, `<owner>/<repo>`, `<commit-to-drop>`. Anchored to a letter so that
# process substitution `<(...)`, here-strings `<<<`, and `<!doctype` are left
# alone, and confined to one line so a `->` further down cannot close a match
# that a `<` opened above it. The name never ends in whitespace, optionally
# followed by digits: `sort <in.txt >out.txt` and `<in.txt 2>err` are two
# redirects, not one placeholder.
PLACEHOLDER = re.compile(r"<[A-Za-z](?![^<>\n]*\s\d*>)[^<>\n]*>")

SHELL_LANGS = {"bash", "sh", "shell"}

# A console block is a recorded run: only its `$ ` lines are commands.
CONSOLE_LANGS = {"console"}

# `<<EOF`, `<<-'EOF'`, `<< "EOF"`, `<<\EOF`, `<<END-MSG`: the body that follows
# is text until the terminator line, so a placeholder there is not a redirect.
HEREDOC = re.compile(r"<<(-?)[ \t]*(?:'([^'\n]+)'|\"([^\"\n]+)\"|\\?([^\s;&|<>()'\"]+))")


def closes(marker: str, line: str) -> bool:
    """True when `line` ends a block opened with `marker`."""
    closing = CLOSING.match(line)
    return bool(closing) and closing.group(1)[0] == marker[0] and len(closing.group(1)) >= len(marker)


class Block(NamedTuple):
    """One fenced block: where it opens, its dedented body, and its language."""

    line: int
    code: str
    lang: str
    closed: bool


def iter_blocks(text: str):
    """Yield a Block per shell block, plus any fence left unterminated.

    An unterminated fence is reported whatever its language: it swallows the
    rest of the document, so every shell block after it disappears from the
    walk, and the file passes for having nothing left to check.
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        opening = OPENING.match(lines[i])
        if not opening:
            i += 1
            continue
        indent, marker, lang = opening.group(1), opening.group(2), opening.group(3)
        body: list[str] = []
        j = i + 1
        while j < len(lines) and not closes(marker, lines[j]):
            body.append(lines[j])
            j += 1
        closed = j < len(lines)
        if lang.lower() in SHELL_LANGS | CONSOLE_LANGS or not closed:
            strip = len(indent)
            yield Block(
                i + 1,
                "\n".join(line[strip:] if line[:strip].isspace() else line for line in body),
                lang.lower(),
                closed,
            )
        i = j + 1


def bare_placeholders(code: str) -> list[str]:
    """Each `<name>` bash would read as a redirect: in command position, outside
    quotes, comments, heredoc bodies, `${...}` text and arithmetic. Commands
    inside `$(...)` and backticks are scanned wherever they sit, unquoted
    heredoc bodies included."""
    return [code[start:end] for start, end in bare_spans(code)]


def bare_spans(code: str) -> list[tuple[int, int]]:
    """Where each bare placeholder sits in `code`, as (start, end) offsets."""
    found: list[tuple[int, int]] = []
    _scan(code, 0, None, found)
    return found


def _scan(code: str, i: int, stop: str | None, found: list[tuple[int, int]]) -> int:
    """Scan command text from i until `stop` (`)` or a backtick) or the end,
    collecting bare placeholders; returns the index just past the stop."""
    n = len(code)
    pending: list[tuple[str, bool, bool]] = []
    depth = 0  # subshells opened inside this scan, so `$( (a); b )` ends at the last `)`
    while i < n:
        c = code[i]
        if c == ")" and depth:
            depth -= 1
            i += 1
            continue
        if stop and c == stop:
            return i + 1
        if c == "\\":
            i += 2
        elif c == "'":
            end = code.find("'", i + 1)
            i = n if end < 0 else end + 1
        elif code.startswith("$'", i):
            i += 2
            while i < n and code[i] != "'":
                i += 2 if code[i] == "\\" else 1
            i += 1
        elif c == '"':
            i = _scan_double(code, i + 1, found)
        elif code.startswith("$((", i) or (code.startswith("((", i) and _command_start(code, i)):
            i = _skip_double_paren(code, i, found)
        elif code.startswith("$(", i):
            i = _scan(code, i + 2, ")", found)
        elif code.startswith("${", i):
            i = _scan_brace(code, i + 2, found)
        elif c == "`":
            i = _scan(code, i + 1, "`", found)
        elif c == "(":
            depth += 1
            i += 1
        elif c == "#" and (i == 0 or code[i - 1] in " \t\n;&|()"):
            end = code.find("\n", i)
            i = n if end < 0 else end
        elif code.startswith("<<<", i):
            i += 3
        elif c == "<":
            heredoc = HEREDOC.match(code, i)
            placeholder = PLACEHOLDER.match(code, i)
            if heredoc and not placeholder:
                word = heredoc.group(2) or heredoc.group(3) or heredoc.group(4)
                quoted = heredoc.group(4) is None or code[heredoc.start(4) - 1] == "\\"
                pending.append((word, heredoc.group(1) == "-", quoted))
                i = heredoc.end()
            elif placeholder:
                found.append(placeholder.span())
                i = placeholder.end()
            else:
                i += 1
        elif c == "\n" and pending:
            i = _skip_heredoc_bodies(code, i + 1, pending, found)
            pending = []
        else:
            i += 1
    return i


# A keyword after which `((` opens an arithmetic command: `for ((`, `if ((`.
KEYWORD_BEFORE = re.compile(r"(?:^|[\s;&|(])(?:for|if|elif|while|until|do|then|else|!)$")


def _command_start(code: str, i: int) -> bool:
    """True when position i begins a command: at a line start, after ; & | (,
    or after a keyword such as `for`, `if` or `while`."""
    before = code[max(0, i - 64):i].rstrip(" \t")  # a bounded tail: the test needs one keyword
    return not before or before[-1] in "\n;&|(" or bool(KEYWORD_BEFORE.search(before))


def _scan_brace(code: str, i: int, found: list[tuple[int, int]]) -> int:
    """Skip a `${...}` from i, just past its `${`. Its own text is a word, not
    a command, but a `$(...)` or backticks inside it are commands again."""
    n, depth = len(code), 1
    while i < n:
        c = code[i]
        if c == "\\":
            i += 2
        elif c == "'":
            end = code.find("'", i + 1)
            i = n if end < 0 else end + 1
        elif c == '"':
            i = _scan_double(code, i + 1, found)
        elif code.startswith("$((", i):
            i = _skip_double_paren(code, i, found)
        elif code.startswith("$(", i):
            i = _scan(code, i + 2, ")", found)
        elif c == "`":
            i = _scan(code, i + 1, "`", found)
        elif code.startswith("${", i):
            depth += 1
            i += 2
        elif c == "}":
            depth -= 1
            i += 1
            if not depth:
                return i
        else:
            i += 1
    return i


def _scan_double(code: str, i: int, found: list[tuple[int, int]]) -> int:
    """Skip a double-quoted string from i, scanning the commands inside it."""
    n = len(code)
    while i < n:
        c = code[i]
        if c == "\\":
            i += 2
        elif c == '"':
            return i + 1
        elif code.startswith("$((", i):
            i = _skip_double_paren(code, i, found)
        elif code.startswith("$(", i):
            i = _scan(code, i + 2, ")", found)
        elif code.startswith("${", i):
            i = _scan_brace(code, i + 2, found)
        elif c == "`":
            i = _scan(code, i + 1, "`", found)
        else:
            i += 1
    return i


def _skip_heredoc_bodies(
    code: str, i: int, pending: list[tuple[str, bool, bool]], found: list[tuple[int, int]]
) -> int:
    """Index of the newline ending the last pending heredoc body, starting at
    the line after the opener. A terminator matches its line exactly; `<<-`
    allows leading tabs. A body whose terminator is unquoted still expands
    `$(...)` and backticks, so those are scanned; the rest of it is text."""
    n = len(code)
    for word, dash, quoted in pending:
        while i < n:
            end = code.find("\n", i)
            end = n if end < 0 else end
            line = code[i:end]
            if (line.lstrip("\t") if dash else line) == word:
                i = end + 1
                break
            if not quoted:
                reached = _scan_expansions(code, i, end, found)
                if reached > end:
                    end = code.find("\n", reached)
                    end = n if end < 0 else end
            i = end + 1
    return max(i - 1, 0) if i <= n else n


def _scan_expansions(code: str, i: int, end: int, found: list[tuple[int, int]]) -> int:
    """Scan the commands in text that only expands, such as an unquoted
    heredoc body, from i to end; returns where scanning stopped."""
    n = len(code)
    while i < end:
        c = code[i]
        if c == "\\":
            i += 2
        elif code.startswith("$((", i):
            i = _skip_double_paren(code, i, found)
        elif code.startswith("$(", i):
            i = _scan(code, i + 2, ")", found)
        elif code.startswith("${", i):
            i = _scan_brace(code, i + 2, found)
        elif c == "`":
            i = _scan(code, i + 1, "`", found)
        else:
            i += 1
    return i


def _skip_double_paren(code: str, start: int, found: list[tuple[int, int]]) -> int:
    """Skip a `$((` or `((` construct from start. Bash reads it as arithmetic
    when it closes with `))`, and otherwise as a subshell opening a
    substitution or a command, `$((gh pr view <n>); true)`, whose text is
    commands again and is scanned as such."""
    n = len(code)
    dollar = code[start] == "$"
    inside: list[tuple[int, int]] = []
    end = _skip_arith(code, start + (3 if dollar else 2), inside)
    if end >= n or code[end] == ")":
        found.extend(inside)
        return min(end + 1, n)
    return _scan(code, start + (2 if dollar else 1), ")", found)


def _skip_arith(code: str, i: int, found: list[tuple[int, int]]) -> int:
    """Skip arithmetic from i, just past its opening parentheses, to just past
    the first `)` that closes them. A `<` there is a comparison or a shift, but
    a `$(...)`, backticks or a `${...}` inside it are scanned."""
    depth, n = 1, len(code)
    while i < n and depth:
        c = code[i]
        if c == "\\":
            i += 2
        elif code.startswith("$(", i) and not code.startswith("$((", i):
            i = _scan(code, i + 2, ")", found)
        elif c == "`":
            i = _scan(code, i + 1, "`", found)
        elif code.startswith("${", i):
            i = _scan_brace(code, i + 2, found)
        else:
            depth += c == "("
            depth -= c == ")"
            i += 1
    return i


def console_commands(code: str) -> str:
    """The commands of a recorded run: each `$ ` line and its `\\` continuations."""
    out: list[str] = []
    cont = False
    for line in code.splitlines():
        if cont or line.startswith("$ "):
            out.append(line[2:] if not cont else line)
            cont = line.rstrip().endswith("\\")
    return "\n".join(out)


def parse_error(code: str) -> str | None:
    """Return bash's complaint about `code`, or None when it parses."""
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as handle:
        handle.write(PLACEHOLDER.sub("PLACEHOLDER", code))
        path = handle.name
    try:
        done = subprocess.run(
            ["bash", "-n", path], capture_output=True, text=True, check=False
        )
    finally:
        Path(path).unlink(missing_ok=True)
    if done.returncode == 0:
        return None
    # bash prefixes each line with the temp file's name, which says nothing.
    complaint = done.stderr.strip().splitlines()
    return "; ".join(line.split(": ", 1)[-1] for line in complaint) or "does not parse"


def check(root: Path) -> int:
    sources = sorted(root.glob("plugins/*/skills/*/*.md")) or sorted(root.glob("**/*.md"))
    blocks = failures = 0
    for source in sources:
        if source.is_symlink() or not source.is_file():
            # A link can point at a FIFO or a device, which a read never finishes.
            failures += 1
            print(f"✘ {source} — not a regular file; skills are plain files", file=sys.stderr)
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            failures += 1
            print(f"✘ {source} — not UTF-8 ({error.reason} at byte {error.start})", file=sys.stderr)
            continue
        for block in iter_blocks(text):
            rel = source.relative_to(root) if source.is_relative_to(root) else source
            if not block.closed:
                failures += 1
                opened = f"{block.lang} fence" if block.lang else "fence"
                print(f"✘ {rel}:{block.line} — unterminated {opened}", file=sys.stderr)
                continue
            blocks += 1
            console = block.lang in CONSOLE_LANGS
            try:
                bare = bare_placeholders(console_commands(block.code) if console else block.code)
            except RecursionError:
                failures += 1
                print(f"✘ {rel}:{block.line} — too deeply nested to scan", file=sys.stderr)
                continue
            if bare:
                failures += 1
                print(
                    f"✘ {rel}:{block.line} — bash reads {', '.join(bare)} as a redirect;"
                    " quote it, e.g. gh pr view \"<n>\"",
                    file=sys.stderr,
                )
            complaint = None if console else parse_error(block.code)
            if complaint is None:
                continue
            failures += 1
            print(f"✘ {rel}:{block.line} — {complaint}", file=sys.stderr)
            print(f"    {block.code.strip().splitlines()[0][:76]}", file=sys.stderr)
    if failures:
        checked = f"{blocks} shell block(s) checked" if blocks else "no shell block reached"
        print(f"\n✘ {failures} problem(s); {checked}", file=sys.stderr)
        return 1
    print(f"✔ {blocks} shell block(s) parse under bash -n, no bare placeholder")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    return check(Path(args[0]) if args else Path(__file__).resolve().parent.parent)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
