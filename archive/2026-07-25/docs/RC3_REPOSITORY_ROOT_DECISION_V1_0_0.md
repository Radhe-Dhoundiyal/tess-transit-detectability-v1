# RC3 repository-root decision

Decision: `RC3_STAGING_IS_RECOMMENDED_REPOSITORY_ROOT`.

The private project root contains restricted/source data and migration
controls and is not authorized for publication. RC3 is self-contained and
contains `.gitignore`, `.gitattributes`, manifests, documentation, evidence,
and read-only verification tools. The future repository should not track the
outer RC3 ZIP because the unpacked repository already contains its payload and
manifests.
