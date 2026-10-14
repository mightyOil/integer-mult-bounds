# PR455 complex-template hash reconciliation

**Source consolidation; no new κ and no acceptance/disposition change.** The
fourth100 review leaves PR455 open because its regenerated complex template
hash is `62d1e17f…`, while the original expects `02d4d003…`. Two lossless
serialization changes reproduce **the complete original expected hash**:

1. Set byte 9 of the generated `LOCAL-PROGRAMS.json.gz` header to decimal 10
   (`0x0a`), retaining every other byte and the complete decompressed payload.
2. Serialize generated `DATA-PHASES.json` with CRLF line endings. Every JSON
   value and every non-newline byte stays identical.

The exact target is
`02d4d0031a173664f8adc5bccf0244f8ce349307eac09c0d48a3c8948a7f5b17`.
Neither change alone suffices. There is no expected-digest replacement, no
omitted field, no changed supplier word and no changed paid profile.

## Scope and evidence

The historical source is Dugongue's PR455 head
`f76fc4e36030d4e00b4cbb83b1dbc661a0974c4e`. Research base:
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The exact files, Git objects and
SHA256 pins are in [SOURCES.json](SOURCES.json); the original full package
remains in its existing source archive. The small `pr455-sources.tar.gz`
contains only 22 byte-identical needed source/input/credit files, so replay
does not require fetching historical PR refs. Every member, original Git
blob and author manifest pin is checked before temporary extraction. Four
original commands execute unchanged:

- Local program emission and exact forward/backward checks of all 800 live
  columns per orientation; 24,857 events per orientation.
- Complete data-phase generation, including 40,960 exact polynomial checks,
  120 terminal-omission controls and the original finite cover checks.
- Complete complex whole-owner emission: 88 invocations, 49,280 residuals.
- Original independent routing audit, including all ten mutation controls:
  443,520 occupied axis cells, rank mass 851,136, unchanged complete profile.

The fresh routing receipt agrees with the retained fourth100 receipt in every
scientific field. Exactly `template_sha256` and its `source_bindings` differ;
inside the latter, only `phase_sha256` differs. The original assertion-enabled
source runs as child processes even when this harness is invoked with `-O`.
Ten additional controls reject source/object substitutions, altered local
instructions, a changed phase translation, corrupted owners, paid idle ranks,
terminal correction and forged generated-file bindings.

This is a new explanation and executable reconciliation of the recorded hash
blocker, not a new independent implementation of the inherited mathematics.
The source's scalar/frame audit and Clifford recipes retain their original
scope. No full bit/native/outer replay, complete multiplication theorem,
selected construction replay, new supplier adoption or closure is claimed.

## Why the original result varies across platforms

The global template is serialized canonically, but it embeds raw-file hashes
of both a regenerated gzip file and a pretty-printed JSON file. Thus canonical
serialization of the outer object does not remove those inner differences.
The author's `VALIDATION.json` records Windows CPython 3.11.9. Official zlib's
[WIN32 branch](https://github.com/madler/zlib/blob/v1.3.1/zutil.h) sets `OS_CODE`
to 10; [CPython's release dependency file](https://github.com/python/cpython/blob/v3.11.9/PCbuild/get_externals.bat)
pins zlib 1.3.1. This supports the platform explanation; this work did not run
Windows. No different deflate stream or zlib build is required to reproduce
the original digest here.

The finite diagnostic domain was compression levels 1–9, all 256 OS-header
bytes and LF/CRLF phase output: 4,608 combinations on the fixed emitted
payload. The exact match was level 9, OS byte 10, CRLF. This identifies a
reconstruction in that bounded domain; it is not a theorem about all possible
serializations. The permanent replay uses the proved reconstruction directly,
not that exploratory search.

The shipped `historical-compatible-local-programs.json.gz` is an explicitly
**reconstructed encoding**, not a recovered author output file. Its 2,088,490
uncompressed bytes are compared byte-for-byte with every fresh local emission
before it can be used. Its compressed SHA256 is
`4208096ba6a9b358f4c8687c514da29f15c5245169719b313a9a409d028b537f`.
Shipping that small encoding makes the exact historical-hash reconstruction
independent of the reader's compressor implementation. It does not substitute
for fresh instruction generation or its complete equality check.

The additional payload-bound template hash is
`0b9538eb416a7bf0360d9d3f8f8b25224269200884536f2ae085af2234288e26`.
It replaces exactly the two generated-file digest values with their full
uncompressed/LF payload hashes **after validating their complete preimages**.
Every other key, value, instruction, owner, correction and order is included.
It is a scoped portable comparison certificate, not a new frozen-source API.

## Reproduce

Repository history for the registered base provenance is required; the
original PR455 source subset is included and independently pinned. No network,
native compiler, optimizer, NumPy or SymPy is used.
From the repository root:

```sh
python3.12 scripts/research_package.py --package research/pr455-template-reconciliation
```

Expected: `PASS_PR455_TEMPLATE_RECONCILIATION`, original hash `02d4d003…`,
88 calls, 49,280 residuals, ten inherited and ten additional rejected controls;
then `PASS_REGISTERED_RESEARCH_PACKAGE`. To retain all logs and outputs:

```sh
python3.12 -I -O -B research/pr455-template-reconciliation/verify.py --work /absolute/new/output-directory
```

The replay writes only new temporary/output files. It does not rewrite frozen
sources, historical receipts, selected records, source archives or the ledger.
The original expected digest remains an independent required endpoint.

## Open next questions

The named hash blocker is explained and reproduced. A maintainer can now run
the full original PR455 wrapper with these two proved output-serialization
adapters plus the already-established bit geometry newline adapter. Retain
every original final expected value and all full bit/native/outer checks.
That full replay and any disposition decision remain separate work; the
structured question and first step are in [TASK.json](TASK.json).

## Credit

PR455's construction and original replay belong to Dugongue, with its existing
OpenAI assistance disclosure. The unchanged whole-complex emitter credits
Zhihao Chen (#377), icekylinx (#433), DaysSky (#442), and chafreaky. The full
archived `PROVENANCE.md` and six original license/notice files are authenticated
and extracted beside the executed sources; all earlier attribution remains.
The fourth100 maintainer review identified the unresolved mismatch and retained
the successful scientific stages. Maxime Fleury's
[container reproducibility audit](../gzip-container-reproducibility/README.md),
following Antoine Olivier's replay findings, supplies the prior general
payload-versus-container convention. This work supplies the missing exact
PR455 preimage and replay; it does not claim that general insight as new.

Prepared for Philipp / mightyOil with substantial OpenAI Codex assistance
(GPT-6 Astra Ultra). New work is Apache-2.0; no independent human review is
claimed. OS assignment seed 97 selected the consolidation track. The source
and selected frontier are unchanged.
