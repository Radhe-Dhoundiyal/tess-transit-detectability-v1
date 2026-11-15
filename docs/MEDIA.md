# Figures and sources

| Figure | What it shows |
|---|---|
| [WASP-127 b](media/wasp127.png) | The same 8,000 processed TESS observations plotted chronologically and folded using the catalogue period and epoch |
| [Synthetic trial matrix](media/synthetic-trials.png) | All 320 accepted injections across 40 hosts; 98 direct, 25 harmonic, 12 alias and 185 nonrecoveries |
| [Results explorer](media/explorer.png) | A browser capture of the saved-results interface |

The WASP-127 b figure uses BTJD and dimensionless, zero-centered detrended flux. The trial matrix identifies each experiment as `IR-{host row:02d}-{injection index:02d}`. These are synthetic transits inserted into observed light curves, not 320 newly observed planets.

The figures credit NASA/TESS/MAST, the NASA Exoplanet Archive and Astropy. File identities, figure transformations and linked records are in [image provenance](../provenance/images.json); software and collaboration credits are in [acknowledgments](../ACKNOWLEDGMENTS.md).

## V1.1 figures

| Figure | Source and caption |
|---|---|
| [Recovery comparison](../results/figures/period_grid_recovery_v1_1_0.png) | Primary top-10 recovery 98/320→117/320 and literal rank-1 72/320→94/320. The separate paired-difference panel shows +5.9375 percentage points and the descriptive 95% host-bootstrap interval +2.8125 to +9.6875 points; it is not an error bar for either individual rate. |
| [All host changes](../results/figures/period_grid_hosts_v1_1_0.png) | Primary gains and losses across all 40 hosts, eight trials each. Negative bars preserve the single loss. Open markers identify the original four exploratory hosts at their net change. |

Both figures read the [paired records](../data/records/period_grid_pairs_v1_1_0.csv)
and recompute the relevant aggregations using
[`scripts/plot_grid_comparison.py`](../scripts/plot_grid_comparison.py).
The first also uses the same saved-result host-bootstrap calculation as
the verifier. They use DejaVu Sans, the existing blue/teal/ochre palette,
light backgrounds, restrained grid lines and 3,840-pixel-wide PNG output.
These analysis graphics describe synthetic injections in observed TESS
substrates. They are not new observations, detection-significance tests or
population-completeness estimates. Original V1 images are unchanged.
