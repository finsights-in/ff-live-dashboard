# FF — full repository audit, 29 September 2026

Repository: `finsights-in/ff-live-dashboard`. Everything below was measured, not
assumed; where a check could not be completed from here it says so.

Scope: 804 tracked files, 2,950,209 price rows across 751 symbols, three
workflows, ten scripts in the live pipeline, six published JSON files.

---

## 1. Verified correct

**Price data — clean on every structural test.**

| Test | Result |
|---|---|
| Files scanned | 751 (2,950,209 rows) |
| Duplicate dates | 0 |
| Out-of-order dates | 0 |
| Blank / NaN prices (from 2004) | 0 |
| Non-positive prices (from 2004) | 0 |
| High not the high, Low not the low | 0 |
| Header format | uniform across all 751 |
| Current to 29 September 2026 | 747 of 751 |

**Identity file.** `ident.csv` holds 751 symbols and maps one-to-one onto the
751 price files, in both directions, with no orphan on either side. Tiers:
Large 100, Mid 150, Small 250, Micro 251.

**The frozen v2.0 rules are intact in code.** Read line by line in
`FF_Signal_Engine_v2.py`:

- entry condition `Close(t) <= 0.60 * cummax(Close)`, on a close basis, with
  `THRESHOLD = 0.60`
- re-arm only on a fresh all-time-high close
- entry at the **next trading day's Open**
- target fixed at the trigger date's ATH and never moved afterwards
- `CAP_DAYS = 1095`, no stop loss
- exit reasons separated correctly into ATH_TARGET, TIME_STOP and DATA_END
- fundamentals applied point-in-time through `avail_date`, so no look-ahead
- `FROZEN_BEFORE = "2026-04-01"` still scopes the acceptance test

**The ATH target exit is untouched.**

**The fundamental gate is the right one.** The engine reads `all_hi_pos`, not
`all_hi` — an 8-quarter high in net sales, PAT and split-adjusted EPS *and* all
three positive. `WINDOW = 8` for every tier with no exceptions.

**The Phase A announcement-date fix survived.** 35,702 rows sit at the 60-day
fallback lag, against 36,439 in the pre-fix backup. `fund_flags_v3.csv` holds
37,191 rows over 751 symbols, 2006-12 to 2026-06, from 36,439 historical rows
plus 752 live-scrape rows.

**The published dashboard is internally consistent.** All six JSON files carry
`as_of: 2026-09-29`; `meta.open` of 20 matches the 20 entries in
`positions.json`; `meta.closed` of 0 matches an empty `closed.json`; the index
series carries 249 points to the same date.

**No credentials anywhere.** A pattern scan for tokens, API keys, bearer values
and JWTs across every tracked file returned nothing. This matters more than
usual here: a Dhan token carries order-placement rights, not just data read.

**The multi-year history gaps are harmless.** Nineteen symbols have a hole of
more than 120 days, the worst being IONEXCHANG (2002 to 2022) and FORCEMOT
(2002 to 2019); RAIN carries a 20x level break across a four-year hole at
2008-03-03. Each was checked individually against the rule that actually
consumes it: in every one of the nineteen the post-gap high far exceeds the
pre-gap high, so the old segment never becomes the running maximum and cannot
manufacture a false "60% below the high" entry. No action needed; recorded so
the question is not reopened.

**`.gitattributes`** correctly forces LF endings and prevents the phantom
755-file diff on a Windows checkout.

---

## 2. Needs attention

### 2.1 New corporate actions never reach the fundamentals base

`FF_fundamentals_ingest_v3.py` reads `corporate_actions.csv` to restate EPS for
splits. **Nothing in the repository writes that file.** The OHLC updater detects
and vets corporate actions every single day — that is its central guard — but it
records none of them. Every weekly run therefore prints:

```
no corporate_actions.csv — EPS will not be restated for splits this run
```

The historical position is safe: `split_factor` is populated from the v3 seed,
with 9,732 of 37,191 rows carrying a factor other than 1.0, and the ingest is
deliberately written never to recompute that baseline. The exposure is forward
only — from the seed date onward, a split rescales the price history correctly
but leaves reported EPS on the old scale. The 8-quarter EPS high test then sees
an artificial level break and suppresses that symbol for eight quarters.

It is silent, it is dated, and it grows. The fix is small: have the updater
append each accepted action to the ledger the ingest already knows how to read.

### 2.2 Four symbols are silently frozen

| Symbol | Last price stored | Sessions behind |
|---|---|---|
| INDIAGLYCO | 2026-08-24 | about five weeks |
| HEG | 2026-09-04 | about three weeks |
| PGIL | 2026-09-10 | about two weeks |
| POLICYBZR | 2026-09-23 | four |

Four is well under the tolerance of 15, so the run passes and nobody is told.
`ohlc_quarantine.txt` is in `.gitignore`, so no record of *which* symbols were
skipped survives in the repository — the only trace is a run artifact that
expires. A symbol can therefore stay stale indefinitely without anyone noticing.

The cause for each is unknown from here and needs one dry run against the feed:
`python FF_OHLC_Updater_v2.py --dry-run --symbols HEG,INDIAGLYCO,PGIL,POLICYBZR`,
which writes nothing at all.

### 2.3 The repository is growing about 20 MB a day

`.git` stands at 1.09 GB after six and a half weeks and 48 automated daily
commits; the working tree is 139 MB, of which 121 MB is `ohlc_data`. The cause
is structural: every daily commit rewrites all 751 CSV files. At this rate the
repository passes 4–5 GB within a year, and GitHub begins warning past 1 GB.

Cleaning 30 interrupted-transfer temp files during this audit recovered 80 MB.
A `git gc` would recover more — the object store reports 11 packs and 1,497
prune-packable objects — but that treats the symptom.

### 2.4 Both workflows install dependencies unpinned

`pip install yfinance pandas numpy beautifulsoup4 lxml requests` takes whatever
PyPI holds that morning. This was not the cause of the September failures — a
same-day rerun on identical versions passed — but it is an unannounced change
in a job nobody watches.

---

## 3. Safe to remove

Fifteen scripts and three data files are referenced by nothing in the live
pipeline, and only ever appear in comments explaining what replaced them:

- superseded: `FF_Yahoo_OHLC_Updater.py`, `FF_NSE_OHLC_Updater.py`,
  `FF_fundamentals_ingest.py`, `FF_Screener_Fundamentals_Scraper.py`,
  `FF_build_dashboard.py`, `FF_build_dashboard_v2.py`,
  `FF_dashboard_template.html`, `FF_Live_Tracking_Dashboard.html`,
  `FF_Fresh_Signal_Scanner.py`
- one-off tools, job done: `FF_datefix_compare.py`, `FF_datefix_scan.py`,
  `FF_rebuild_new.py`, `FF_reseed_gapfill.py`, `FF_seed_ohlc.py`
- the probe, whose own header says to delete it once read:
  `FF_market_probe.py` and `.github/workflows/market_probe.yml`
- dead data: `fund_flags.csv` (3.5 MB, the pre-v3 base nothing reads),
  `results_dates.csv`, `datefix_signals.csv`

`FF_Yahoo_OHLC_Updater.py` deserves singling out. It is the v1 that appended
unadjusted rows onto an adjusted history and manufactured a signal at every
split — the exact corruption the current updater exists to prevent. Leaving it
runnable in the repository serves no purpose.

---

## 4. Worth a decision, not a fix

The backtest figures in the dashboard's information panel are hardcoded — 279
closed of 358 signals, 2012 to July 2026. They are correct as of the last
reference run, but nothing updates them and nothing warns when they drift. They
need an owner and a review date.
