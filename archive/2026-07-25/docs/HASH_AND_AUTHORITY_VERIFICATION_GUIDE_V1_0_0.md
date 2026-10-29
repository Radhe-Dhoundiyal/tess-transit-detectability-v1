# RC1 verification guide

Use SHA-256 on both archives and manifests. Extract RC1 to a temporary
directory, reject absolute or `..` member paths, and compare every payload hash
with the RC1 CSV manifest. Confirm all scientific figure hashes match the
Phase 6B.4 integrity table. No scientific script needs to be executed.
