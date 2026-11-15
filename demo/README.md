# Saved-results explorer

Install the project, then run `python demo/serve_demo.py` and open `http://127.0.0.1:8783/index.html`. Stop the local server with Ctrl+C. You can also open `demo/index.html` directly for saved results; the live Depth test requires the server.

The tabs show 70 catalogue-match records, 320 accepted synthetic trials and internal model predictions. WASP-127 b has 8,000 displayed samples from processed TESS observations. Curves for other individual cases and the original injected-flux arrays are not bundled.

Depth test calls the V1 normalization function on five synthetic samples. To run its three standard cases without opening the browser, use `python demo/serve_demo.py --check`.

The server binds to loopback and serves a fixed asset list. See [data sources](../DATA_SOURCES.md) and [acknowledgments](../ACKNOWLEDGMENTS.md) for the records and upstream credits.

Grid comparison adds the V1.1 figures alongside the original views. With the
local server, it reads the canonical paired CSV and statistical summary to
show searchable outcomes by cohort and primary gain/loss. Opening the HTML
directly retains the figures and all original saved views; the paired table
and Depth test require the server. No additional result export is stored.
