---
name: audit-a-dependency-from-its-artifact
description: >
  Use when a dependency question needs an answer that prose cannot be trusted
  for: whether anything is behind its latest release, what a version requires of
  the toolchain, or whether an artifact carries any code at all. Fires on "is
  everything up to date", "what does AGP 9.4 need", "can we drop this -ktx
  dependency", and before raising any cap whose comment cites a floor. Owns the
  guard that makes a measurement worth quoting, which is proving the query is
  aimed at the right artifact before reading anything off it. Do NOT fire for
  what a dependency DOES after a bump (that is verify-dependency-behaviour), for
  applying a bump already decided, or where the registry cannot be reached.
---

# Audit a dependency from its artifact

Release notes go stale, changelogs skip minors, and a version table in a comment
is true on the day it is written. The artifact is not any of those: it is what
the build will actually resolve. This skill reads the answer out of the artifact
and, more importantly, refuses to report a number it cannot show is about the
right thing.

The failure it prevents is not a wrong bump. It is a **confident wrong number**:
a measurement is numeric, so it reads as authoritative whatever it measured.

## Procedure

### 1. Ask the registry what exists

```bash
# every published version, from the repository that serves the artifact
curl -sfL "<repo>/<group with slashes>/<artifact>/maven-metadata.xml"
```

Translate the group with `tr '.' '/'` or the host language's own replace. Do
**not** build the path with a shell substitution like `${g//./\/}`: zsh leaves
the backslash in, every URL 404s, and it reads as the registry being wrong.

### 2. Prove the query is aimed right, per row

This is the step the skill exists for. For every artifact, **the version
currently in use must appear in the list that came back**. If it does not, the
coordinates are wrong, the repository is wrong, or the artifact moved, and every
other number from that query is worthless.

```
for each artifact:
    published = versions(coordinates)
    if current_version not in published:
        report "unusable: current <v> is not in the published list"   # never a result
        continue
    latest = max(stable versions)
```

A row that fails this is reported as unusable, never folded into the answer and
never silently dropped. "27 verified, 0 unusable" is the shape of a trustworthy
report; "27 checked" is not.

### 3. Read a constraint out of the artifact, not out of a note

A tool that enforces a floor carries that floor inside itself:

```bash
unzip -p <plugin>.jar | strings          # or unzip -o to a temp dir, then javap
```

Find the class that does the enforcing and read its constants. This answers the
question for a version nobody has written about yet, which is exactly when a
release note cannot help. Say which class the value came from, so the next
reader can repeat it rather than trust the quote.

The same holds for metadata a build tool enforces: an AAR's own metadata entry
states the compile level it demands, and that is what the build will read.

### 4. Judge "does this carry code" by counting, with the caveat

```bash
# an AAR holds its code in an inner classes.jar; a jar holds it directly
unzip -p <artifact>.aar classes.jar > /tmp/inner.jar
unzip -l /tmp/inner.jar | grep -c '\.class$'
```

**A count of 0 has not answered the question until the comparison is non-zero.**
Where the artifact under test and the one you are comparing it against both
report 0, the method has failed, not the artifacts: multiplatform publishing puts
nothing in the top-level artifact and everything in a platform variant. Count the
variant, and read the POM, where an umbrella names its variant as a compile
dependency.

A suffix is never evidence either way. Check each artifact; one that looks like
an empty alias by its name can carry real classes.

### 5. Report the measurement, not a derived difference

Quote what you measured, with when. A delta between two counts taken at
different times, or under different tool versions, is a third number nobody
measured, and it is the one that turns out wrong.

## When to STOP

- **The question is what changes after the bump.** Whether the new version still
  behaves as the code expects is a different job; `verify-dependency-behaviour`
  owns it, and this skill stops at what the artifact is.
- **The registry cannot be reached.** Report the answer as unknown. Falling back
  to release notes is how the stale number gets in, which is what this exists to
  prevent.
- **Step 2 fails for most rows.** One unusable row is a coordinate typo; most of
  them means the wrong repository or a moved group. Fix the query and start
  again rather than reporting the survivors.
- **The cap comment gives a reason this cannot see.** A pin that exists because
  of a bug, a licence or a downstream consumer is not answered by version
  numbers. Read the comment, and hand the decision back.
