# FF Data Integrity Audit — v3, extended to v5

3 September 2026, updated 4 September 2026.
Companion to `FF_Dashboard_Rebuild_Plan.md`.
Scope: every input the strategy consumes, on the full 751-name Total Market
universe. Run before updating any document, so the numbers do not move again.

---

## Corrections applied in v3

### 1. EPS was never split-adjusted

EPS is a per-share figure, so a share split makes it discontinuous. Screener
restates its history after a split; the Prowess-sourced base did not. Proven on
Info Edge: our Jun/Sep/Dec-2023 EPS were **exactly 5.00×, 4.98× and 4.99×**
Screener's, against a recorded 5.0 split on 7 May 2025.

The consequence was systematic and one-directional. An inflated pre-split value
sitting inside the trailing window makes it arithmetically impossible for EPS to
print a new 8-quarter high, so the rule **suppressed** qualifications; it could
never manufacture one. Measured: 1,110 symbol-quarters had Net Sales *and* PAT
at 8-quarter highs while EPS did not, and 230 of those had a split inside the
window (178 in the Nifty 500 tier).

Fix: `eps_adj = eps_reported ÷ (product of split factors with ex_date after the
quarter)`. 9,732 rows across 256 symbols changed. 199 `all_hi` flags flipped —
**all gained, none lost**, exactly as the mechanism predicts.

*Confirmed independently on 4 September 2026 — see the reconciliation section
below. On rows carrying a split factor, our adjusted EPS matches Screener 58.3%
of the time against 35.2% for the raw column, so the adjustment is the right
direction.*

### 2. Three non-equity bonuses were applied as equity splits

| Symbol | Ex-date | Factor applied | What it actually was |
|---|---|---|---|
| ZEEL | 2014-03-03 | 22.0 | Bonus **preference shares** 21:1 |
| DRREDDY | 2011-03-17 | 7.0 | Bonus **debentures** 6:1 |
| TVSMOTOR | 2025-08-25 | 5.0 | Bonus **NCRPS** 4:1 |

None of these change the equity share count, so none should touch the equity
price. Dividing the history by them left a cliff: ZEEL closed at 12.21 and
reopened at 267.30, a 21.9× jump.

One trade sat across it — ZEEL entered 30 Aug 2013 and exited **on the event
date**, booking +245.8%. That return was an artifact: entry on the divided
scale, exit on the undivided one. Un-applying the three factors restores ratios
of 1.005 / 1.029 / 1.003.

**Rule for the rebuilt pipeline: read the corporate action's `kind` and
`subject`, never the `factor` alone.** "Bonus" is not sufficient — bonus
preference shares, debentures and NCRPS leave the equity price untouched.

### 3. A methodology error, caught by a control test

The first attempt rebuilt every fundamental flag from scratch while adjusting
EPS. That produced XIRR 28.80% — an alarming drop. A control test then asked
whether the from-scratch recompute reproduced the *stored* flags using
*unadjusted* EPS: it matched only **91–95%**. The Prowess-era flag construction
cannot be reproduced exactly, so the 28.80% was measuring a methodology change,
not the EPS fix.

Correct method, now used: compute flags both ways with one consistent function,
take only the **difference**, and apply that difference on top of the stored
flags. Everything else is left untouched. This is the only defensible way to
isolate a single change.

---

## Result

| | Published | Final v3 |
|---|---|---|
| Signals | 351 | **358** |
| Resolved | 275 | 279 |
| Win rate | 76.1% | 76.3% |
| Median return | +66.3% | +65.5% |
| XIRR | 33.49% | **32.15%** |
| Nifty 500, matched timing | 18.00% | 17.96% |
| Excess | +15.49 pp | **+14.19 pp** |
| Cohorts beating the index | 14/15 | **14/15** |
| Only losing cohort | 2018 | **2018** |

XIRR falls 1.34 points, excess 1.30 points. **No structural conclusion changes.**
Largest per-year moves: 2013 (49.40 → 44.50, the ZEEL trade), 2016 (48.40 →
42.96), 2023 (30.80 → 27.51), 2026 (67.20 → 62.10).

---

## Integrity checks — 24 tests

**Prices** — 751 symbols; no NaN; no zero or negative closes; dates strictly
increasing with no duplicates; `ath` and `athH` verify as running maxima; every
series ends on the same date; no price frozen for 30+ days.

**Fundamentals** — no duplicate symbol+quarter; `avail_date` never precedes
`report_date`; the historical lag is a uniform 60 days.

**Universe** — no duplicate symbols; 100 Large / 150 Mid / 250 Small / 251
Micro; the Nifty 500 tier is exactly 500 names; every name has price data.

**Index series** — Nifty 500 from 2005-09-26, Total Market from 2009-08-31,
Microcap 250 from 2013-07-25; all clean and strictly increasing.

**Trade construction** — entry strictly after trigger and within 5 calendar
days; exit after entry; no trade exceeds 1,095 days; target exits fill exactly
at the recorded ATH; no overlapping trades in one symbol (the arming rule
holds); no Micro Cap name in the advisory set; no duplicates.

### Three flags raised, all bounded

**OHLC ordering violated in 5,805 rows across 174 symbols.** Every one falls
between 1995 and **12 September 2003**; zero after 2012, and no trade's entry or
exit day is affected. A pre-2004 source-data artifact, harmless to the backtest.

**586 rows carry a NaN in net_sales, PAT or EPS.** None of them ever qualifies
(`all_hi_pos` is false for all 586). 55 of the 4,928 qualifying quarters (1.1%)
have a NaN somewhere in their trailing window, so those highs were judged on
seven values or fewer. Small, but it should be disclosed.

**24 report dates are not March/June/September/December** — ABBOTINDIA,
MPHASIS and PFIZER. These companies use non-March fiscal year ends, so their
quarters legitimately close in Feb/May/Aug/Nov and Jan/Apr/Jul/Oct. Not a
defect; the check was wrong. All 24 are non-qualifying anyway.

### Two warnings

`AGL` appears in `ident.csv` but has no fundamentals at all, so it has never
been scannable. It is Micro Cap, hence outside the recommendable universe.

`BAYERCROP` carries a row dated 2006-12-31 ingested on 11 Aug 2026. This was
originally recorded here as a misparsed quarter label. **That diagnosis was
wrong** — the label parsed correctly and the figures are real. Bayer CropScience
stopped publishing consolidated results long ago, and Screener still displays the
old consolidated table, which holds exactly two columns: Dec-2005 and Dec-2006.
The live scraper read a genuine but stale table. Right number, wrong era. See
the fix-up section below.

---

## Still open, and deliberately not fixed yet

**The Micro Cap watchlist is provisional.** Its stored flags were built on a
4-quarter window while the v3 delta is 8-quarter; mixing the two is incoherent.
The v3 run shows 240 signals at 63.48% XIRR — **do not quote this.** Micro Cap
needs its own full 8-quarter rebuild, and its benchmark only begins in July
2013. It is excluded from Advisory, Model Portfolio and the dashboard, and will
be built as a separate product.

**Pre-2023 fundamentals cannot be cross-checked.** Screener publishes roughly
three years of quarters, so 2010–2022 Prowess data has no second source. Only
internal consistency can be tested there. This is where 257 of the 358 trades
live, so it is the largest remaining exposure.

**Segment classification is not point-in-time.** `ident.csv` carries today's
Large/Mid/Small/Micro labels applied backwards — a stock that is Large Cap now
may have been Small Cap in 2013. This sits alongside the already-disclosed
survivorship bias and remains unquantified.

**Insurer and lending-NBFC line definitions.** Which row is "Net Sales" for an
insurer — premium earned or total income — is a methodology decision that has
never been written down. It drives the largest cluster of disagreements found in
the reconciliation below.

*The two items previously listed here — "PAT has scattered errors" and "basic vs
diluted" — have now been measured. See the section below.*
---

## Full reconciliation against Screener consolidated — 4 September 2026

The re-scrape and reconciliation listed above as "still open" have now run. This
section replaces the placeholder.

### What was collected

`FF_Screener_Rescrape.ipynb` pulled every quarter Screener publishes, on the
consolidated basis, for the whole 751-name universe.

| | |
|---|---|
| Symbols collected | 748 of 751 on the first pass, **751 of 751** after the fix-up run |
| Rows | 9,362, then 9,446 |
| Window | 2023-06-30 → 2026-06-30 |
| Served consolidated | 8,479 |
| Served standalone (no consolidated statement exists) | 762 |
| Consolidated table stale, taken standalone instead | 205 |

Overlap with our base on the first pass: **9,243 symbol-quarters across 747
symbols**, of which 8,489 are comparable on a consolidated footing. The merged
file is `screener_all.csv`.

### Control test: does the method re-find the error it was built for?

Vedanta was the error that motivated the whole exercise, found by hand. The
reconciliation was pointed at it blind, and returned exactly the same finding:

| Quarter | Our PAT | Screener PAT |
|---|---|---|
| 2024-12-31 | 2,013 | 4,876 |
| 2025-03-31 | 2,537 | 4,961 |
| 2025-09-30 | 402 | 3,479 |
| 2025-12-31 | 3,887 | 7,807 |
| 2026-03-31 | 4,250 | 9,352 |

Plus one wrong revenue (2025-06-30: 37,824 vs 15,754). Five of thirteen PAT
quarters and one of thirteen revenue quarters — the hand-checked result,
reproduced without being told where to look. None of these rows qualifies as a
signal, so Vedanta never entered the trade set.

### How wide the disagreement is

| | Median gap | p99 gap | Beyond 3% | Symbols |
|---|---|---|---|---|
| Net Sales | 0.013% | 19.5% | 167 of 8,485 (1.97%) | 62 |
| PAT | 0.129% | 44.1% | 488 of 8,483 (5.75%) | 173 |

A relative gap on a near-zero PAT is not an error — a swing from ₹0.51 cr to
₹1.00 cr is a 49% "gap" and a rounding difference. Applying a materiality floor
(beyond 3% **and** beyond ₹25 cr for sales; beyond 3%, ₹10 cr **and** 1% of
sales for PAT) leaves **145 sales rows across 54 symbols** and **140 PAT rows
across 68 symbols**.

The sales list is dominated by insurers and lending NBFCs — CHOLAHLDNG, GICRE,
LICI, NIACL, ICICIPRULI, HDFCLIFE account for 70 of the 145 rows. For those,
Screener's "Sales" row is not the line our base uses (premium earned versus
total income). That is a **definition difference, not a wrong number**, and it
is a decision to take, not a defect to repair.

### What it does to the strategy

Materiality on its own does not matter; a flag moving does. Every materially
disagreeing row had Screener's value substituted into our series, the
8-quarter-high test recomputed, and only the flags that flip reported.

Of **1,002 qualifying quarters** in Large/Mid/Small inside the verified window,
12 disagree materially. **13 flags flip** — 4 lost, 9 gained. Two of the
thirteen touch an actual trade.

Backtested with the delta method (stored flags, changed only where the
reconciliation says to):

| | Signals | Win | Median | XIRR | Bench | Excess | Cohorts |
|---|---|---|---|---|---|---|---|
| Published v3 | 358 | 76.3% | +65.48% | 32.15% | 17.96% | +14.19 pp | 14/15 |
| Operating companies only (9 flips) | 358 | 76.3% | +65.48% | 32.15% | 17.96% | +14.19 pp | 14/15 |
| All 13 flips incl. insurers | 357 | 76.2% | +65.49% | 32.15% | 17.96% | +14.19 pp | 14/15 |

Holding the four insurer rows unchanged, **nothing moves at all** — not one
trade. Substituting them too removes exactly one trade: ICICIPRULI entered
2026-06-11, still open and therefore contributing nothing to any published
return.

### EPS: which basis does Screener publish?

The v3 EPS split-adjustment was made on a Prowess-versus-Screener argument that
had never been tested at scale. The re-scrape tests it. On the 688 rows where we
applied a split factor:

| Compared against Screener | Within 5% |
|---|---|
| Our **raw** `eps_reported` | 35.2% |
| Our **split-adjusted** `eps_adj` | 58.3% |

Screener does restate after a split, and the v3 adjustment is the right
direction. The residual is the diluted-versus-basic gap the spec already
records: our base is diluted, Screener publishes basic, and on a knife-edge
quarter a ~1% difference can tip an 8-quarter-high test either way.

An earlier attempt to classify the residual by how much each symbol's ratio
varied was discarded — the measure was outlier-driven, calling a symbol
"stepping" on the strength of one bad row in thirteen. Replaced with the direct
test: substitute Screener's EPS and see whether the flag moves.

That produces 97 flag changes, of which **28 sit on a full 8-quarter window**
inside the Screener span (the rest straddle the boundary, so they are
suggestive only). Backtested, including a deliberately harsh scenario that
applies every one of the 97 plus all 13 sales/PAT flips:

| | Signals | Win | Median | XIRR | Excess | Cohorts | Only loss |
|---|---|---|---|---|---|---|---|
| Published v3 | 358 | 76.3% | +65.48% | 32.15% | +14.19 pp | 14/15 | 2018 |
| EPS, full-window flips | 360 | 76.1% | +65.36% | 32.15% | +14.19 pp | 14/15 | 2018 |
| EPS, all 97 (outer bound) | 361 | 75.9% | +65.26% | 32.13% | +14.19 pp | 14/15 | 2018 |
| **Everything combined** | **360** | **75.8%** | **+65.36%** | **32.13%** | **+14.19 pp** | **14/15** | **2018** |

Under the harshest scenario the headline moves by **0.02 of a percentage point**
and the excess over the index does not move at all. Every affected trade is a
2025 or 2026 entry: **all 257 pre-2023 trades are byte-identical in every
scenario.**

### A parser bug the three missing symbols exposed

BAYERCROP, TATAELXSI and TTML each returned **zero quarters while reporting
basis `consolidated`** — a contradiction. Priyanshu checked the pages by hand
and found the cause: all three stopped publishing consolidated results years
ago, and Screener still shows the old consolidated table. Tata Elxsi's ends
Mar-2015, Bayer CropScience's holds only Dec-2005 and Dec-2006, Tata
Teleservices' ends Mar-2010.

So `fetch()` found a table, accepted the page as consolidated, and the year
filter then correctly discarded every row. The fallback to standalone never
fired, because it was written to trigger only when **no table at all** was
found. The scraper was deciding the basis on whether a table exists rather than
on whether it reaches the present.

The same bug, silently, affected **fifteen more symbols** whose consolidated
table stops between Mar-2020 and Sep-2025 — their older quarters came through
and their recent ones did not. Six sit in Large/Mid/Small: RAILTEL (Sep-2023),
AAVAS (Mar-2024), 3MINDIA (Jun-2024), HDBFS, SBFC and UCOBANK (all Mar-2025).
UCOBANK had appeared in the EPS flip list, so that comparison had been made
against incomplete data.

**Fix:** `fetch()` now parses the quarter labels *before* accepting a page and
rejects a consolidated table whose newest quarter is more than 15 months old,
falling back to standalone and recording which happened
(`standalone_consolidated_stale` versus plain `standalone`), so the basis is
never silently assumed. A second, smaller fix: an empty result frame no longer
crashes on `df.symbol`.

Re-running the 18 affected symbols: sixteen now return 13 recent quarters
through the standalone fallback, and CERA and JAIBALAJI keep a consolidated
table that is current enough to pass the gate. Across 215 overlapping
symbol-quarters there are **2 material disagreements** (3MINDIA) and **4 flag
flips** (3MINDIA, SBFC, UCOBANK, JAIBALAJI). Backtested with the delta method:
**358 signals, XIRR 32.15%, excess +14.19 pp, cohorts 14/15 — not one trade
added or removed.**

This is a rebuild finding rather than a backtest finding, and that is the point.
The same parser is what feeds the live dashboard, where the bug would write
stale figures into the series every week without ever raising an error.

### What this settles, and what it does not

**Settled.** The base survives its first independent check. Net Sales agree to a
median of 0.013%. The PAT errors are real but scattered, and where they land they
land almost entirely on quarters that never qualified. No published number
changes; no structural conclusion changes; the 2018 cohort remains the only loss
under every scenario tested.

**Not settled.**

- The window is **2023-06 to 2026-06 only**. Screener publishes about thirteen
  quarters, so 2010–2022 — which is where 257 of the 358 trades live — still has
  no second source. This check covers the trades that matter least.
- TATAELXSI's two trades (2019-01-29, +66.7% at target; 2023-03-02, −27.4% at
  time stop) are **still unverified even after the fix-up**, because both are
  governed by quarters that fall before the Screener window opens. The same is
  true of UCOBANK's 2022 trade and AAVAS's 2022 trade. Collecting the symbol did
  not make its trades checkable.
- The **insurer and lending-NBFC definition question** is open. Which line is
  "Net Sales" for an insurer is a methodology decision that should be written
  down, not left to whichever row the parser matched first.
- **Micro Cap was excluded** from every test in this section, per the decision to
  hold it out of Advisory and Model Portfolio.

---

## The systematic corporate-action sweep — 4 September 2026 (v5)

### Why it was run

Section 2 above repaired three corporate actions. Those three were found **by
eye**, by looking at the largest visible cliffs in the price series. No check was
ever run over all of them. While verifying the corporate-action parser for the
rebuilt updater, that sweep finally happened, and it found three more of exactly
the same kind.

### The method

Adjustment exists so that a split leaves no step in the series. So for every one
of the 798 recorded corporate actions, the sweep measures the ratio across the
ex-date in the *adjusted* series. It should be about 1. Where it is not:

    stored_before = raw_before / f_applied
    ratio         = stored_before / stored_after = (raw_before / raw_after) / f_applied
    implied_true  = ratio x f_applied

`implied_true` is then snapped to a ratio a real action can produce — a bonus
a:b, a face-value split, a bonus and a split together, or 1.0 meaning no equity
event at all. Where it snaps to nothing, the event is reported and left alone.

### Two thresholds that were wrong first

**A candidate set that was too dense.** The first attempt generated every
`(a+b)/b` for a and b up to 20, which is dense enough that any number lands near
something. NTPC's implied factor of 1.0636 "snapped" to a bonus of 1:16 — a
ratio that does not occur — and the pass reported 326 corrections, meaning 41%
of all events were supposedly wrong. The honest reading of 1.0636 is 1.0: no
equity event, and a 6% move the stock made by itself that day.

**A bar set below the circuit limit.** With the candidate set fixed, the sweep
acted on any break beyond 10% and produced 19 corrections — of which six had a
multiplier of exactly 1.20. Six different symbols, across 2012 to 2025, all at
exactly 1.20 is not six coincidences. Their subjects settle it: Cochin
Shipyard's is "Face Value Split From Rs 10/- To Rs 5/-", a factor of 2, and 2 is
what was applied. India's daily circuit limit is 20%, and these stocks closed at
the upper circuit on their ex-date. The adjustment was right; the residual was
the market.

The bar is therefore **25%** — above anything a single day's trading can
produce. What survives cannot be a price move.

### What it found

| | |
|---|---|
| Events examined | 798 |
| Already continuous within 25% | **794** |
| Corrections to apply | **3** |
| Could not be resolved | 0 |

| Symbol | Ex-date | Factor applied | Implied true factor | Correction |
|---|---|---|---|---|
| BRITANNIA | 2010-03-08 | 2.0 | 1.08 | x2.0 |
| COROMANDEL | 2012-07-13 | 2.0 | 1.04 | x2.0 |
| NTPC | 2015-03-20 | 2.0 | 1.06 | x2.0 |

All three are the ZEEL class: a factor of 2 applied where the equity price did
not move. NTPC and Britannia both issued **bonus debentures** on those dates —
shareholders received debentures, not shares, so the share count never changed.
All three also share a signature: `source = api_only` in `events_final.csv`,
meaning the factor came from the API with no price observation to check it
against. That is the condition under which this error happens.

### What it changed

One trade. NTPC entered 31 May 2013 with its target set on the halved scale, and
the doubling on 20 March 2015 was read as the target being hit:

| | Entry | Exit | Return | Reason |
|---|---|---|---|---|
| Before | 2013-05-31 | 2015-03-20 | **+81.88%** | ATH_TARGET |
| After | 2013-05-31 | 2016-05-30 | **−8.24%** | TIME_STOP |

The target was never reached. Britannia's and Coromandel's repairs changed no
trade at all.

| | v3 | **v5** |
|---|---|---|
| Signals | 358 | **358** |
| Resolved | 279 | 279 |
| Win rate | 76.3% | **76.0%** |
| Median return | +65.5% | **+65.4%** |
| Target-hit rate | 55.9% | 55.9% |
| XIRR | 32.15% | **31.77%** |
| Nifty 500, matched timing | 17.96% | 17.88% |
| Excess | +14.19 pp | **+13.89 pp** |
| Cohorts beating the index | 14/15 | **14/15** |
| Only losing cohort | 2018 | **2018** |

Per-year, only 2013 moves: XIRR 44.50% to 42.98%, excess 24.88 to 23.78 pp.
Every other year is unchanged.

All three robustness tests were re-run on v5 and hold. The fundamental filter
still earns its place (full rule +13.89 pp and 14/15 cohorts, against price-only
+9.54 pp and 13/15). The 0.60 threshold still sits on a plateau. The
availability-lag sweep is still non-monotonic — 32.41 / 31.37 / 31.77 / 31.16 /
30.72 across 30/45/60/75/90 days — so the lag remains a choice about operational
honesty, not returns.

### What this says about the earlier verdict

The reconciliation section above concluded that the base "survives its first
independent check" and that no published number changes. The first half stands.
The second half did not survive this sweep: XIRR moves 0.38 points and the
excess 0.30. The structural conclusions — 14 of 15 cohorts, 2018 the only loss,
the fundamental filter adding value — are unchanged.

The lesson is narrow and worth stating plainly: **v3 fixed the errors that were
visible, and called it done.** Three more of the same kind were sitting in the
data the whole time, and they only surfaced because a different task made the
systematic check unavoidable. A check that is easy to skip will be skipped.

Files: `FF_ca_repair.py` (the sweep), `FF_ca_repair_table.csv` (the three
corrections), `FF_ca_residual_jumps.csv` (every ex-date and its residual),
`build_v5.py`, `pxd_v5.pkl`, `FF_FINAL_v5_n500.csv`, `FF_peryear_v5.csv`,
`FF_research_v5.csv`.

---

## Files

`fund_flags_v3.csv` (corrected fundamentals, with `eps_reported`,
`split_factor` and `eps_adj` side by side) · `pxd_v4.pkl` (prices with the three
non-equity bonuses un-applied; series run to 24 Aug 2026) ·
`FF_FINAL_v3_n500.csv` (358 advisory trades) · `FF_peryear_v3.csv` ·
`build_v3.py`, `run_v3.py`, `integrity.py` (reproducible).

Reconciliation, 4 September 2026: `FF_Screener_Rescrape.ipynb` (the scrape) ·
`FF_Screener_Fixups.ipynb` (corrected `fetch()`, the 18 repaired symbols) ·
`screener_consolidated.csv` (9,362 rows) · `screener_fixups.csv` ·
**`screener_all.csv`** (9,446 rows, 751 symbols — use this one) ·
`FF_reconcile_v3.py`, `FF_reconcile_pass2.py`, `FF_reconcile_pass3.py`,
`FF_reconcile_pass4.py`, `FF_reconcile_fixups.py` · `FF_reconcile_report.csv`,
`FF_reconcile_material.csv`, `FF_reconcile_flips.csv`, `FF_eps_flips.csv`,
`FF_fixup_flips.csv` · `FF_reconcile_summary.txt`, `FF_reconcile_pass2.txt`,
`FF_reconcile_pass3.txt`, `FF_reconcile_pass4.txt`, `FF_reconcile_fixups.txt` ·
`delta_recon.py`, `delta_eps.py` (the backtest deltas).

> *Handover note, 30 September 2026: the research files listed here (`.pkl`,
> `.ipynb`, the `FF_reconcile_*` and `build_*` scripts) live in Priyanshu's
> OneDrive folder `NEW FUNDAMENTAL FIRST`, not in this repository. The
> repository holds only what the live pipeline needs: `fund_flags_v3.csv`,
> `FF_FINAL_v5_n500.csv` and `ohlc_data/`.*
