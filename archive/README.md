# July 2026 research archive

`2026-07-25/` preserves the 142 files in the project's July 25 snapshot,
including scientific figures, result tables, notebooks, protocols, and release
records. Some handovers and release guides were written as working instructions
at the time. They are kept as part of the history, not as directions for using
the current repository.

For the experiments themselves, start with the current [methods](../docs/METHODS.md),
[development notes](../docs/DEVELOPMENT.md), and [verification guide](../docs/VERIFICATION.md).
The original July [figures](2026-07-25/results/figures/detectability_modeling_v1_0_1/)
and [result tables](2026-07-25/results/tables/) remain available here.
`v1_tests/` retains the V1 test sources used to select the portable tests; it
does not mean the full original test suite was run for this public package.

The snapshot is checked byte-for-byte against the privacy-remediated Git commit
`4ef58998334b9ddf67216a785c49e2326f39669f` using
`python scripts/verify_project.py --provenance` from a full clone. The original
commit dates are preserved, but author email metadata was replaced. The old
`.gitattributes` is named `.gitattributes.snapshot` here to avoid applying its
checkout rules; its contents are unchanged. The snapshot's README calls itself
RC2 although the original commit message says RC3. Use the root README for
current commands and installation steps.
