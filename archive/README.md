# Historical material

`2026-07-25/` preserves all 142 files of the historical July 25 tree
as Git blob bytes. Its privacy-remediated historical root is
`4ef58998334b9ddf67216a785c49e2326f39669f`. Author and committer dates remain
2026-07-25T21:37:23+05:30; only their email metadata was replaced.
It described RC2 in its README even though its commit message named RC3.
One filename is intentionally inert: the original `.gitattributes` bytes are
stored as `.gitattributes.snapshot`, so archived checkout rules cannot
override the current byte-preservation policy. The verifier maps that name
back to the original Git object; its content is unchanged.

These files are historical evidence. Their old version labels, paths,
installation commands, manifests and release gates describe that snapshot
and may refer to omitted material. Use the current root README for runnable
commands and current manifests for this candidate. Historical verifier
scripts are retained for inspection, not presented as working release tools.
Nothing in the archive authorizes a scientific rerun or a public release.

`v1_tests/` contains complete current local V1 test sources from which
portable unit tests were selected. Their existence does not mean the full
private suite ran. The current verification script checks the historical
snapshot against the original Git tree independently of old manifests.
