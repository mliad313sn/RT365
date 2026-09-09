# Meridian packaging — what a build from source found

| Field | Value |
|---|---|
| Date | 2026-09-09 |
| Ran by | Product Owner delegate (RT365), under D-040 |
| Subject | Building an installable Meridian for this programme's own PMO instance |
| Source | mliad313sn/Meridian, branch `claude/meridian-rt365-feedback-d6vo3i`, commit `453d331`, `package.json` version 5.14.0 |
| Host | Linux x64, Node 22.22.2 |
| Artefacts | `Meridian-5.14.0-win-x64.zip` (sha256 `ceac8743…18a3ae7`), `Meridian.exe` inside it (sha256 `6023a6b1…86bd52a`) |

## 1. Why this was a build and not a download

There is no download. `mliad313sn/Meridian` publishes **no GitHub release** —
the releases list is empty — and the newest tag is `v5.9.0`, which is also
the default branch. The 5.14.0 work, including the twelve improvements this
programme filed and the eight requests it proposed (REQ-32..REQ-39, all but
one now marked done in their register v12), exists only on a feature branch.

That is REQ-39 in their own register, still `open`, and this is the first
time its cost has been paid rather than predicted: to obtain the current
Meridian, an operator must clone a branch, install a toolchain, and run a
build that — as §3 shows — does not run on the platform they are building
for.

## 2. What was built, and how it was verified

`npm run package` (`scripts/package/build-exe.mjs`) produces
`dist/Meridian/`: the server as one Node SEA executable, the built client,
the migrations, the winsw service wrapper and two administrator scripts.

The build ran on Linux with one local, non-upstream patch (§3.1) so the SEA
blob could be injected into the **official** `node-v22.22.2-win-x64` binary,
whose SHA-256 was checked against `nodejs.org/dist/v22.22.2/SHASUMS256.txt`
before use.

Verified on the artefact:

- PE32+ x86-64 console executable, 7 sections.
- Exactly one `NODE_SEA_BLOB` resource; exactly one fuse sentinel, and the
  byte following it is `:1` — the fuse is flipped, so Node will read the
  blob rather than behave as a plain interpreter.

A PE cannot be executed on this host, so the payload was proven separately:
the **same** SEA blob was injected into this host's own Node 22.22.2 and
run from the package directory. It applied all 47 migrations against
PostgreSQL and answered

```json
{"ok":true,"version":"5.14.0","build":"packaged","engine":"postgres",
 "instance":{"org":"MERIDIAN","id":null,"migrations":47},
 "backup":{"lastDrillAt":null,"lastAttemptAt":null,"ok":null}}
```

with `GET /` serving the built client (200) and `GET /api/portfolio`
refusing an unauthenticated read (401).

What is **not** proven here, and is stated as unproven wherever this package
is handed over: the Windows service registration, `prepare-db.ps1`, and
SmartScreen behaviour. Those need a Windows host.

## 3. Four findings, each reproducible

### 3.1 The Windows package cannot be built anywhere but Windows — for one line

`build-exe.mjs` copies `process.execPath` as the injection target. The SEA
blob itself is platform-neutral and postject injects into a PE from any
host, so the only thing standing between a Linux CI runner and a Windows
package is that one expression. A single environment override

```js
const SEA_NODE = process.env.MERIDIAN_SEA_NODE || process.execPath;
```

was enough to build this artefact. With it, the release workflow can produce
the download that REQ-39 asks for without a Windows runner — which is the
cheapest available answer to the request that has been open longest.

### 3.2 The documented offline fall-back does not exist in the packaged build

`README-INSTALL.txt`, written by the build itself, says:

> Installing without a network: `powershell -File prepare-db.ps1 -NoDownload`,
> then `Install-Service.cmd`. The book runs on the embedded engine.

`prepare-db.ps1` implements that branch: when no PostgreSQL is found and none
can be installed, it **removes** `DATABASE_URL` from `meridian.config.json`
and writes `PGLITE_DIR` instead, reporting *"configuration : PGlite (base
embarquée) — l'application fonctionne."*

The packaged executable does not implement the other half. `sea-entry.mjs`
exits before the server starts:

```
No DATABASE_URL. Set it in meridian.config.json beside the executable, or in
the environment, and point it at the PostgreSQL 17 database for this instance.
```

exit code 2. Measured twice on the artefact: without `DATABASE_URL`, and
again with `PGLITE_DIR` set to a writable directory — `PGLITE_DIR` is never
consulted, because the check runs first. `@electric-sql/pglite` is also
marked `external` in the esbuild call and is not shipped in `dist/Meridian`,
so the fall-back could not work even if the guard let it through.

The consequence is precise: **an offline install completes, reports success,
and leaves a service that will never start.** The comment at
`prepare-db.ps1:256` shows the refusal was intended for a
`MERIDIAN_REQUIRE_POSTGRES=1` install; the packaged binary refuses
unconditionally. Either the guard should honour `PGLITE_DIR` and the engine
should ship, or the installer's offline branch and the README paragraph
should be deleted. What must not survive is a document promising a
configuration the binary rejects.

### 3.3 The executable is unsigned, and the build says so only as a warning

Injecting the blob invalidates the Authenticode signature Node.js ships on
`node.exe`; postject prints `warning: The signature seems corrupted!` and the
build continues. The result is an unsigned executable that SmartScreen will
warn on — the same defect this programme found in its own Windows binary
(RT365 H-30). There is no signing step, and no published hash for a user to
check instead. A release that publishes SHA-256 sums beside the artefact is
the minimum; a signing step in the release workflow is the answer.

### 3.4 A duplicate object key in the portfolio response

esbuild reports, during the bundle:

```
▲ [WARNING] Duplicate key "caseReconfirmations" in object literal
  server/src/portfolio.js:531:4  (original at 425:4)
```

Two literals assign `caseReconfirmations` in the same object; the second
silently wins and the first computation is dead. This is REQ-22's
re-confirmation data — one of the value objects. Not diagnosed further here:
it is theirs to read, and it is the kind of thing a build warning treated as
an error would have stopped.

## 4. What this says about the tool, beyond the four defects

Every finding above is a **packaging** finding, and packaging is the last
metre between a good PMO product and a team that can use it. Meridian's
engine is strong enough that this programme runs its portfolio, gates and
RAID through it; what stops another team from doing the same on Monday is
that there is nothing to download, and that the one path an air-gapped site
would take is documented but not implemented.

The register's first line (REQ-39) and these four findings together are the
distance between "a very good internal tool" and "a product someone else can
adopt". None of them is architectural. All of them are a release workflow
away.

## 5. The register we handed over did not validate against their own schema

Building from source put their repository on this machine, and with it
`docs/requests/register.schema.json` — the schema our own register file
declares. Validating `docs/REPORTS/meridian_requests_v3.json` against it
produced **55 errors**, in three families:

- `status: "proposed"` is not a status. The enum is
  `open | partial | done | refused`, and `open` already means what we meant.
- `accepted: false` is forbidden on an open line by an explicit rule in the
  schema: *"a line with nothing delivered cannot have been accepted or
  refused acceptance — there is nothing to try. `accepted: false` on an open
  line reads as silence when it is really absence."* It was also wrong in our
  own words: our note beside it said "`accepted` is not set", because saying
  so upstream is a human act (H-31) and no agent here may record one. The
  honest value was `null` all along.
- Every history row we wrote omitted the required `status`.

This is our defect, and it is stated first because the round that found it
was ours. But the reason it survived to be handed over is theirs to fix:
Meridian validates the copy **it** holds, in `scripts/audit/register-schema.mjs`;
the side that *writes* the register has no published way to check the file
before sending it. A contract with a validator on only one end is a contract
that bounces late. Filed as REQ-53.

`registerVersion 8` is the first version of the file that validates clean.
Nothing was re-stated: no title, measure, observation or priority changed.

## 6. Register delta in this round

| Id | Title | Priority |
|---|---|---|
| REQ-49 | The Windows package builds on a Linux runner, so a release can be published without a Windows host | high |
| REQ-50 | The offline install either runs on the embedded engine or stops saying it cannot | high |
| REQ-51 | A published artefact carries a hash, and ideally a signature | medium |
| REQ-52 | A duplicate key in the portfolio response silently discards one computation | medium |
| REQ-53 | The register schema is checkable by the field repository that writes the register | medium |

Ids start at REQ-49 because their registerVersion 12 reaches REQ-48. Read on
that version: of the eight ids RT365 proposed in registerVersion 7
(REQ-32..REQ-39), **seven are marked done** and only REQ-39 — the default
branch and a published release — is still open. That single open line is why
this round exists.
