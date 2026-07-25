# First-party import resolution rules

Resolution order:

1. Explicit relative imports resolve from the importing package and require an
   existing module file or package directory.
2. Absolute package imports resolve beneath `src/tess_detectability` only when
   an exact module/package path exists.
3. Sibling imports require exactly one existing sibling module/package.
4. Repository packages require a concrete directory or `__init__.py`.
5. Documented `PYTHONPATH=src`, module entry points, or script-directory
   behavior may support—but never replace—path evidence.
6. Standard-library and installed-distribution mappings are checked before an
   unresolved absolute import is declared local.
7. Multiple local candidates or simultaneous local/third-party candidates are
   ambiguous and blocking when active.
