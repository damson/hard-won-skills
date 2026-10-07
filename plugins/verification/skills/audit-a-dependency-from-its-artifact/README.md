# audit-a-dependency-from-its-artifact

Answers "is anything behind", "what does this version require" and "does this
artifact carry any code" from the published artifact rather than from a release
note or a comment, and refuses to report a number it cannot show is about the
right artifact.

Read [SKILL.md](SKILL.md) for the procedure. This file is when to reach for it
and what the evidence looks like.

## Using it

Fire it before a dependency decision that a stale sentence could misinform:

- a currency pass over a whole version catalogue
- a cap comment that cites a floor ("needs Gradle 9.6.0"), before raising it
- an entry you suspect is a forwarder and want to rename or drop
- any version question about a release recent enough that nobody has written
  about it yet

It does **not** fire for what a library does once bumped, which is
`verify-dependency-behaviour`, nor for applying a bump already decided.

## The failure it prevents

A measurement is numeric, so it reads as authoritative whatever it measured. Two
ways that goes wrong, both seen:

- **The query is aimed at the wrong artifact** and answers confidently anyway. A
  query whose result does not contain the version you are currently running is
  not describing your dependency. The skill makes that a per-row precondition:
  the report says "27 verified, 0 unusable", and a row that fails it is never
  folded into the answer.
- **Zero is read as an answer.** Counting classes to decide whether an artifact
  is an empty forwarder gives 0 for a genuine forwarder and also 0 for the
  umbrella of a multiplatform library whose code sits in a platform variant.
  Zero on both sides of a comparison means the method has failed.

## Example

A catalogue of 27 modules, checked before any bump:

```
name                 current        latest stable  behind
agp                  9.3.3          9.4.1          YES
kotlin               2.4.20         2.4.20         .
...
27 verified, 0 unusable
```

AGP is behind, and its cap comment says the reason is a Gradle floor. Rather
than trusting the comment, read the floor out of the plugin:

```console
$ unzip -oq gradle-9.4.1.jar -d /tmp/agp
$ javap -c -p -cp /tmp/agp com.android.build.gradle.internal.VersionCheckPlugin \
    | grep -nE 'MINIMUM|ldc .*String 9\.'
  14:   ldc           #7    // String 9.6.0
  22:   getstatic     #9    // Field MINIMUM_GRADLE_VERSION
```

**Read the constant the check uses, not every version-shaped string in the
class.** A class that enforces a floor usually mentions other versions too, in a
deprecation message or a second branch, and a bare match on `9.x` prints all of
them in whatever order the constant pool holds. Grepping for the field the
comparison reads, and the `ldc` that loads it, is what ties the number to the
check. Where the two disagree, disassemble the comparing method on its own and
follow the operand.

The comment was right, the wrapper moved first, and the doc now says how to read
the floor rather than listing the one that happened to bind.

## Related

- `verify-dependency-behaviour` picks up where this stops: what the library does
  once it is in.
- `prove-the-check-can-fail` is the same discipline applied to a guard rather
  than to a measurement.
