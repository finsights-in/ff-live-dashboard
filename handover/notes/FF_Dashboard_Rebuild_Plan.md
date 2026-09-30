# FF Live Dashboard — Audit and Rebuild Plan

> *Handover note, 30 September 2026: this is the plan that produced the current
> pipeline. Section 3's defect list describes the **old** pipeline, all of which
> has been replaced. Phases 1–6 of section 6 are done; phase 7 (scheduled
> quarterly reconciliation) is not. Kept because it explains why the current
> design is the way it is.*

Status as of 3 September 2026, revised 4 September 2026 after the full data
reconciliation. Companion to `FF_Advisory_Methodology` (spec v2.0),
`FF_audit_findings.md` and `FF_Data_Integrity_v3.md`.

Repo audited: `ff-live-dashboard` (GitHub Pages, published daily).
Live URL: https://priyanshuagarwal8430-dotcom.github.io/ff-live-dashboard/

---

## 1. Decisions taken (locked)

| # | Decision |
|---|---|
| 1 | Live record is **reconstructed from 1 June 2026** under v2.0 rules. Signals before the new scanner goes live are labelled **"reconstructed"**; only signals produced by the new scanner are labelled **"live"**. |
| 2 | `avail_date` = **the date the result was first observed**, recorded truthfully and never edited afterwards. Fundamentals scraping moves from **weekly to daily** so that first-observation is within ~1 day of publication. |
| 3 | Fundamentals source: **NSE/BSE XBRL filings as primary**, Screener as cross-check. Where the two disagree, the run **fails and publishes nothing** rather than guessing. |
| 4 | **Micro Cap is watchlist-only** — and as of 4 September 2026 it is excluded from Advisory, Model Portfolio and this dashboard entirely, to be built later as a separate product with its own 8-quarter flag rebuild. |
| 5 | The Screener reconciliation runs **every quarter, automatically**, once the rebuild is live — not as a one-off. Data quality becomes a standing process rather than an event. |

Rationale for #2: the availability-lag sweep (30/45/60/75/90 days) produced
XIRR of 33.86 / 32.76 / 33.49 / 32.83 / 32.38 — a non-monotonic 1.5-point
spread. Lag choice is noise, not signal, so it should be chosen for
operational honesty rather than for returns.

*(Handover note: decisions 2 and 3 were implemented differently from the plan —
`avail_date` now comes from the NSE event calendar (Phase A), and the
fundamentals scrape stayed weekly on Screener. Decision 5 is still open.)*

---

## 2. What the existing pipeline is

Two GitHub Actions: a daily job (19:00 IST, Mon–Fri) that refreshes OHLC from
Yahoo, scans for signals, builds the dashboard HTML and publishes it to
GitHub Pages; and a weekly job (Sunday) that scrapes Screener for new
quarterly results and merges them.

Data: 751 OHLC CSVs, `fund_flags.csv` (37,060 rows, 750 symbols, 2010–2026),
`ident.csv` (751 names: 100 Large, 150 Mid, 250 Small, 251 Micro).

The automation scaffolding is sound — scheduling, retry, rebase-before-push,
staleness warning, an EPS plausibility check. The defects are in the rules and
the data, not the plumbing.

---

## 3. Defects found

### 3.1 Rules diverge from spec v2.0 — four differences

| Live pipeline | Spec v2.0 | Measured impact |
|---|---|---|
| Universe = Nifty Total Market (751) | Nifty 500 (500) | 24 of 51 live signals (47%) are Micro Cap |
| Trigger `Low <= 0.60 × ATH` (intraday touch) | `Close <= 0.60 × cummax(Close)` | 7 of 43 signals never closed 40% down |
| Micro Cap uses a 4-quarter fundamental window | 8 quarters for every segment | — |
| No positivity filter | Net Sales, PAT, EPS all > 0 | 51 rows carry `all_hi=True` with a non-positive metric |

Net effect: of 43 signals in the repo's `fresh_signals.csv`, only **17 survive
the v2.0 rules**. About 60% of what the live dashboard displays is not a
signal under the frozen spec.

### 3.2 The data-corruption cause — identified

`FF_Yahoo_OHLC_Updater.py` calls `yf.download(..., auto_adjust=False)` and
appends the resulting **unadjusted** rows onto an **adjusted** price history.
It never re-adjusts history. Every split or bonus therefore creates an
artificial cliff in the series: the ATH stays at the pre-split level while the
price halves, and the stock instantly appears to be "40% below its high".

This is the root cause of the corrupted OHLC data, and it manufactures a false
signal at every corporate action. There is no corporate-action handling
anywhere in the live pipeline — only a `-55%` drawdown heuristic that labels a
signal "possibly a CA artifact".

**How much damage it has actually done — measured 4 September 2026.** All 751
stored series were scanned for single-day moves beyond 35%. There are 284 of
them across 149 symbols; 268 predate 2024 and belong to the original historical
base. Inside the live record (since 1 June 2026) there are **four**, and every
one of them puts the stock below the 60% trigger line:

| Symbol | Date | Move | Close vs running max |
|---|---|---|---|
| TRIVENI | 2026-07-22 | −41.6% | 275.50 vs 501.87 |
| KIRLPNU | 2026-08-18 | −50.5% | 760.20 vs 2081.96 |
| TDPOWERSYS | 2026-08-24 | −49.2% | 780.10 vs 1586.60 |
| INDIAGLYCO | 2026-09-02 | −78.8% | 236.20 vs 1203.30 |

Three of the four are 1:2 or larger splits that the updater never re-adjusted
for. They land roughly one every five trading days.

**One of them was published as a signal.** `fresh_signals.csv` on the remote
carries `TDPOWERSYS, Micro Cap, trigger 2026-08-24, entry 2026-08-25 at 780.20,
target 1586.60, drawdown −50.8%`. The stock did not fall 50%; it split two for
one. The target is the pre-split all-time high, which the post-split price
cannot reach — it would need a 103% gain that is not a gain. The recommendation
is an artifact end to end.

It is Micro Cap, so it sits outside the recommendable universe under decision 4
and would not have reached a client. It was still published on the dashboard.

*Correction, recorded rather than quietly fixed.* An earlier version of this
section reported **one** cliff and **zero** affected signals, and concluded the
bug "has not fired yet". That scan was run against the local clone, whose data
stopped on 14 August — three weeks stale — and the three additional cliffs all
occurred after that date. The stale clone was not checked before the conclusion
was drawn from it. The rules divergences remain the larger source of bad
signals, but the price corruption is not a latent hazard: it has already
produced a published recommendation.

### 3.3 Live-operation defects

- **Signals are recomputed from scratch every day** and `fresh_signals.csv` is
  overwritten. A recommendation already issued can therefore change or vanish
  if the underlying data changes. A research analyst's record must be
  immutable.
- **No exit tracking at all.** `FF_build_dashboard.py` has no target-hit check
  and no 1,095-day cap enforcement; every row is hardcoded `isNew:true`. A
  position that reaches its target keeps showing as open.
- **No closed-trade record, no realised performance, no benchmark.**

### 3.4 The scraper accepts stale tables — found 4 September 2026

The scraper decided a page's basis on **whether a quarterly table exists**, not
on whether that table reaches the present. Several companies stopped publishing
consolidated results years ago and Screener still shows the old consolidated
table: Tata Elxsi's ends Mar-2015, Bayer CropScience's holds only Dec-2005 and
Dec-2006, Tata Teleservices' ends Mar-2010. The scraper accepted those pages as
current consolidated data, and the fallback to standalone never fired because it
was written to trigger only when **no table at all** was found.

Eighteen symbols were affected — three returning nothing, and fifteen whose
consolidated table stops between Mar-2020 and Sep-2025, so their older quarters
came through and their recent ones silently did not. Six sit in
Large/Mid/Small: RAILTEL, AAVAS, 3MINDIA, HDBFS, SBFC, UCOBANK.

**This is where the BAYERCROP Dec-2006 row came from.** The audit had recorded
it as a misparsed quarter label; that was wrong. The label parsed correctly and
the figures are real — they are simply twenty years old.

Fixed in `FF_Screener_Fixups.ipynb`: `fetch()` parses the quarter labels before
accepting a page, rejects a consolidated table whose newest quarter is more than
15 months old, and records in the `basis` column which path was taken. Backtest
impact of the repair: **none — not one trade added or removed.** The value is
entirely forward-looking, because the same parser feeds the live dashboard,
where this bug writes stale figures every week without raising an error.

### 3.5 Data-quality findings

- `AGL` appears in `ident.csv` but has **zero** rows in `fund_flags.csv` — it
  has never been scannable. (Micro Cap, so outside the recommendable universe.)
- **130 of 750 symbols never received the Jun-2026 quarter** (54 Micro, 42
  Small, 27 Mid, 7 Large); they remain frozen on March.
- The 51 false qualifiers split 34 Micro / 10 Small / 5 Mid / 2 Large —
  **17 of them inside the Nifty 500 universe**.
- No duplicate symbol+quarter rows. 741 of 750 symbols have 8+ quarters of
  history, so an 8-quarter window is viable universe-wide.

### 3.6 The scrape-date artifact

Every `historical` row carries a lag of exactly 60 days. Every `live_scrape`
row carries a lag of exactly 42 days, because all 620 June-quarter rows were
ingested on a **single date, 11 August 2026** — the weekly scraper succeeded
only once in three months.

The consequence is visible in the signal file: **11 of 43 signals (26%)
trigger on 11 August 2026** — SHAREINDIA, AARTIIND, SAFARI, PNCINFRA, PCBL,
DEVYANI, DEEPAKNTR, CMSINFO, BLUEDART, SAPPHIRE, KANSAINER. Nothing happened
in the market that day; that is simply the day the scraper ran. This single
observation justifies the move to daily scraping.

---

## 4. Source of the fundamentals — resolved

`fund_flags.csv` in the repo and the local backtest copy are **byte-identical**
(same MD5), so the backtest and the live pipeline share one fundamentals base.

A boundary test (implied share count = PAT ÷ EPS, across the
historical/live_scrape join) gives a median ratio of **1.0002**, with 70% of
620 symbols within ±2% — no change of basis at the join. The eleven symbols
beyond ±2x (SKFINDUS ~10x, ZFCVINDIA/JLHL/AIIL ~5x, RBLBANK/VEDL/LLOYDSENT
~2x) look like genuine recent corporate actions.

**Source: the historical rows are Prowess-sourced.** An earlier version of this
plan concluded they were Screener-sourced because a Dabur India screenshot
matched our stored values exactly across all thirteen quarters. That inference
was wrong: agreement between two sources is a *validation*, not an
identification. Priyanshu confirmed the history to March 2026 came from Prowess.

The figures are **consolidated** (Dabur's standalone quarterly revenue is
~₹2,200–2,600 cr; these are ₹3,000–3,700 cr).

**Basic vs diluted — resolved.** RBL Bank's consolidated view settled it: our
EPS runs a consistent ~1% below Screener's, which is the dilution gap. Our base
is **diluted** and **consolidated**, exactly as the spec says. The full
reconciliation confirmed this at scale, and also that Screener **restates EPS
after a split** — on the 688 rows carrying a split factor, our split-adjusted
column matches Screener 58.3% of the time against 35.2% for the raw column.

The live scraper, however, reads Screener's default page, which is *basic* and
sometimes *standalone*. That is a real defect to fix in the rebuild, not a
question still open.

---

## 5. Foundations that are already sound

- `pxd_v5.pkl`: **751 symbols, split- and bonus-adjusted, with six non-equity
  bonus factors un-applied** — ZEEL, DRREDDY, TVSMOTOR found by eye in v3, and
  BRITANNIA, COROMANDEL, NTPC found by the systematic sweep on 4 September.
  Validated against the 358-trade reference set.
- The universe splits cleanly: **500 Nifty 500 names + 251 Micro Cap**, with
  no name missing from either the price base or the fundamentals.
- A corporate-action pipeline already exists from the original build:
  `corporate_actions_used.csv` (355 applied events),
  `events_final.csv` (798 validated events with observed factor, volume ratio
  and snap error), `factors_from_data.csv` (1,005 factors inferred from price
  data). **This is precisely what the live repo lacks.**
- **An independent second source now exists for fundamentals** from Jun-2023
  onward: `screener_all.csv`, 9,446 rows across all 751 symbols. See
  `FF_Data_Integrity_v3.md`.

Gap to close: prices from the end of the current series to today.

---

## 6. Plan

| Phase | Work | Acceptance test |
|---|---|---|
| 1 | Audit the fundamentals base; fix the universe; establish the adjusted price foundation | Complete — see sections 3–5 |
| 1b | Full reconciliation against an independent source | Complete — 751/751 symbols; worst-case impact 0.02 pp on XIRR |
| 2 | New OHLC updater with real corporate-action handling and history re-adjustment | A simulated split produces no signal |
| 3 | Rewrite the scanner to v2.0 rules | **Must reproduce the 358-trade v5 backtest exactly** |
| 4 | Append-only signal ledger + exit engine (ATH target, 1,095-day cap) | A published signal can never change retroactively |
| 5 | Rebuild the dashboard: open positions, closed trades, live record vs Nifty 500 | Serves both Advisory and Model Portfolio |
| 6 | Data-quality gates in CI | Bad data fails the run instead of publishing |
| 7 | Quarterly reconciliation on a schedule | A new Screener quarter triggers the check automatically |

Note on Phase 3: the acceptance target is **358 trades, XIRR 31.77%, excess
+13.89 pp, 14/15 cohorts** — the v5 set, after the systematic corporate-action
sweep of 4 September. Earlier versions of this plan named 351 (pre-v3) and then
32.15% (v3, before the sweep found the NTPC-class errors).

Goal: a self-running dashboard on genuinely accurate data, serving both the
Advisory and the Model Portfolio products.

## 7. Expected outcome

Signal count falls — probably from 51 to somewhere near 15–20 — and that is
the point: what remains will be real under the spec. CA artifacts disappear,
so the "flagged for verification" category goes away. The dashboard and the
methodology document finally say the same thing. And a genuine live track
record begins, immutable and benchmarked, which is the asset clients will ask
for once the backtest conversation is over.

What this does not do: retroactively repair the 1 June – 3 September 2026
record. That period was produced under v1.0 rules and is being recomputed, not
corrected in place.
