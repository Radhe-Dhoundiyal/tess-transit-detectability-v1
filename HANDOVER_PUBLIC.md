# TESS Transit Detectability — Migration Handover

Updated: 2026-07-24 (Asia/Calcutta)  
Repository: `<repository-root>`

## Project overview

This is an evidence-first astronomy/data-science repository for a fixed TESS
benchmark, canonical light-curve preprocessing, blind BLS recovery, synthetic
injection-recovery, and preregistered statistical detectability modeling.
Scientific phases are governed by versioned authorizations, frozen protocols,
SHA-256 manifests, validation records, and terminal completion/failure markers.
Historical failures are preserved and must not be silently repaired.

## Current status

Phase 6B.4 is terminally complete under:

- authorization `TS-DETECTABILITY-MODELING-FIGURE-AUTHORITY-1.0.4-P6B4`;
- amendment `DETECTABILITY-MODELING-FIGURE-AUTHORITY-1.0.4-004`;
- protocol `1.0.4`;
- completion marker
  `data/metadata/detectability_modeling_complete_v1_0_4.json`;
- completion SHA-256
  `EE22ADEDB5DEF5A9421DDBA7B5BD27190F7E226F2D1EC3800F73F0652E8E1705`.

The phase reconstructed terminal manifest and lineage authority for all 14
pre-existing detectability figures. All 14 figures passed dependency
validation and temporary regeneration with exact byte equivalence. Existing
PNG bytes, parent authorities, scientific tables, predictions, fits, and
metrics were not changed.

Frozen scientific state:

- 320 trials, 40 targets, 8 target-grouped folds;
- 64 grouped fits plus 4 full-data fits, all 68 converged;
- fits reused/recomputed: 68/0;
- 1,367 probability-grid rows;
- nine sensitivity analyses;
- 1,000 target-level bootstrap replicates;
- primary Model A log loss `0.3198223626785455`;
- Brier score `0.1046725568285409`;
- calibration intercept/slope
  `0.08492457979473397` / `1.071061479973135`;
- ROC/PR AUC `0.9257676043390329` / `0.8056516447845964`;
- bootstrap log-loss interval
  `[0.2534498563390638, 0.3948718757981831]`;
- interaction improvement `0.0038141055083467`, below the frozen `0.005`
  retention threshold; interaction not retained;
- scientific/statistical/modeling changes: 0/0/0;
- BLS/injection/refit/replacement/manual-override executions: 0/0/0/0/0.

## Recent accomplishments

- Phase 6B v1.0.0 performed the preregistered modeling computation but failed
  during prediction-grid generation. Failure SHA-256:
  `8EDF2D489808D5EAAF0DF41269473107D50EA6647C5FC02103D683CCD13418CB`.
- Phase 6B.1 corrected only the grid helper, reused validated fits and OOF
  predictions, generated the frozen products and 14 figures, then failed
  because an exact-set validator rejected two authorized additional figures.
  Failure SHA-256:
  `80E818471234D4D18FF766071CDCF483B484BD0017EE603434457FC0BFEE930D`.
- Phase 6B.2 amended the validator but terminal validation exposed incomplete
  figure manifest/lineage authority. Failure SHA-256:
  `36F64441D56A883B023B84CA64AE4F8BA340832C43BD67D3535CA286B4875EDB`.
- Phase 6B.3 authorized lineage repair for only two figures and failed
  scope-sufficiency preflight when the broader omission was discovered.
  Failure SHA-256:
  `4D2E12020F7C86565E65C83F9C879D1E559F40BA6A5E1262BFA33196F9CD558D`.
- Phase 6B.4 froze comprehensive 14-figure authority before reconstruction.
- Inventoried 14 unique figures with zero duplicates, stale candidates,
  temporary candidates, unauthorized figures, or unreadable files.
- Validated source-table and plotting-code dependencies for all 14.
- Audited two prior partial-lineage entries.
- Regenerated all 14 figures in temporary storage: 14 exact byte matches.
- Created 14-entry manifest and lineage supplements plus unique terminal
  combined views.
- Independently recomputed metrics and bootstrap intervals without refitting.
- Executed the 24-section evidence notebook.
- Passed 252 repository tests and the prepublication validator.
- Wrote the completion marker last and verified zero temporary files and zero
  stale project Python/BLS/injection processes.

## Active branch/workstream

No functional Git repository is discoverable at this checkout. Git commands
report that the path is not a repository; the inspected parent `.git`
directory is empty. There is no discoverable branch, commit, status, or diff
authority. Persisted protocol manifests use `git_commit: null`.

The active workstream is read-only terminal review and handover of Phase 6B.4.
No later scientific phase is authorized.

## Important decisions made

- Figure authority reconstruction covered exactly the complete 14-figure set:
  12 required figures and two preregistered additional figures.
- Reconstruction establishes current terminal manifest/lineage authority; it
  does not fabricate historical registration.
- The two partial v1.0.1 lineage entries were audited and replaced only in the
  v1.0.4 combined terminal view. The v1.0.1 table was not edited.
- Existing figure bytes were reused only after complete dependency and exact
  regeneration-equivalence validation.
- All scientific outputs, model fits, endpoints, predictors, folds, seeds,
  interactions, sensitivity rules, and bootstrap rules remained frozen.
- Earlier v1.0.0–v1.0.3 failure markers remain authoritative evidence.
- Hash/test/notebook success is bounded computational evidence, not external
  scientific validation or a causal claim.

## Known issues

Verified:

1. No Git authority is available.
2. `pytest` is not installed in the pinned interpreter; the repository uses
   `unittest`. An attempted `python -m pytest -q` failed with
   `No module named pytest`; no installation was performed.
3. Windows notebook execution emits non-fatal ZMQ event-loop and local
   unencrypted TCP kernel warnings.
4. Some v1.0.0 intermediate modeling products exist, but that phase has a
   terminal failure marker and is not the terminal authority.
5. The model is benchmark-specific and lacks external validation.
6. The 320-trial injection design, 40 targets, and central-transit assumptions
   constrain generalization.
7. The reports are evidence summaries, not a publication-ready manuscript.

Unverified or assumption-bound:

- Whether a recoverable Git repository or remote exists elsewhere.
- Whether an independent astronomer/statistician has reviewed the Phase 6B
  modeling assumptions and interpretation.
- Whether the current shared Python environment can be reproduced exactly;
  no project lockfile or isolated environment was created here.

## Verification completed

Executed from repository root with:

```powershell
$env:PYTHONPATH='src'
python -m py_compile scripts\reconstruct_detectability_figure_authority_phase6b4.py
python scripts\reconstruct_detectability_figure_authority_phase6b4.py
python -m py_compile scripts\validate_detectability_figure_authority_phase6b4.py
python scripts\validate_detectability_figure_authority_phase6b4.py
python -m unittest discover -s tests -q
python -m py_compile scripts\publish_detectability_figure_authority_phase6b4.py
python scripts\publish_detectability_figure_authority_phase6b4.py
```

Observed results:

- reconstruction: 14 figures, 14 exact byte equivalents, 0 failures;
- validation: unchanged scientific metrics and 0 refits;
- tests: `Ran 252 tests in 88.553s`, `OK`;
- prepublication status: `PASSED`;
- terminal completion status: `COMPLETE`;
- temporary files: 0;
- stale relevant processes: 0.

Key verified hashes:

- Phase 6A.2 completion:
  `4C940B93B78DB951A1F9561985503B876A730006B53D0C326BE0182FFCE9FB3B`;
- preregistration:
  `AE61C48E46DCD9BBCE1B584288EE0097F58470A7AEF0E6156F59B86D3B0C12AF`;
- parent protocol:
  `F676EA09E1D5D6CC0E9CBB7A4BEEDAC14139A8117BC51EF74EA41458A16DC9C2`;
- v1.0.4 protocol:
  `1C30699F17F34CB3202A7C5F37910464379D856D8FBFC6F9E0C1F6BFC90F88F2`;
- modeling dataset:
  `D166230D9049E8C93AE3F9B37598E55C93B83550AAAF1F7733F2527BE96CB835`;
- prepublication:
  `DFF066E32BFCE0AA2EFBDB9F8351E7BB8291AE0FDA25ABC39A5BEDFBED4B87A6`.

## Verification still required

At the start of the next chat, perform a fresh read-only audit:

1. Rehash the v1.0.4 completion and prepublication records.
2. Rehash all four parent failure markers, preregistration, parent protocol,
   modeling dataset, and Phase 6A.2 completion marker.
3. Rehash all 14 PNGs against
   `detectability_existing_figure_integrity_v1_0_4.csv`.
4. Validate that all 14 figure paths occur once in each v1.0.4 combined
   manifest and lineage table.
5. Confirm the earlier v1.0.1 manifest and lineage hashes remain unchanged.
6. Confirm zero v1.0.4 failure marker, zero temporary files, and no stale
   project Python/BLS/injection process.
7. Confirm no later-phase artifact appeared after this handover.
8. Recheck Git discovery.

Do not regenerate figures or rerun models merely to review the package.

## Immediate next steps

1. Stay read-only.
2. Read the five root handover files, then the v1.0.4 amendment, protocol,
   execution report, prepublication record, and completion marker.
3. Perform the fresh verification above and report verified facts separately
   from assumptions.
4. Review the completed Phase 6B.4 evidence package for internal consistency.
5. If new modeling, external validation, expanded injections, or publication
   analysis is desired, draft a separately versioned authority for review.
   Drafting does not authorize execution.
