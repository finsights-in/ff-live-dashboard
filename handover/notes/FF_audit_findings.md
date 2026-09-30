# Fundamental First — Audit Findings

*Status as of 26 Aug 2026. Strategy owner: Priyanshu (Hindesh is his teammate).
Sections 1 and 3 have been superseded — the entry rule is now Close-based ATH
(section 1-bis) and the price data has been rebuilt (section 3-bis). Superseded
text is kept for the historical record.*

**Advisory SOP is now FROZEN at v2.0.** See `FF_Advisory_Methodology_v1.md`
for the complete specification. This document remains the audit/issues log.

**MAJOR CHANGE 26 Aug 2026 (v2.0): Micro Cap removed from the universe.**
Universe is now the 500 Nifty 500 names; reference set is **351 recommendations**
(was 751 names / 614 recommendations). Driver: a benchmark error was found and
corrected — see section 1-quater. Micro Cap's 4-quarter fundamental window is
retired; all tiers now use 8 quarters.

> *Handover note, 30 September 2026: the reference set moved again to **358**
> (v5) on 4 September — see `FF_Data_Integrity_v3.md`. Section 12 below is still
> the reference design for the Model Portfolio. The "Working notes" at the end
> describe how the team works and are still accurate.*

---

## 0. TWO products, TWO SOPs — confirmed by Priyanshu 24 Aug 2026

The same signal-generation logic feeds two different capital-deployment models,
being developed as two separate products with separate documents.

**A. Continuous Recommendation (Research Analyst advisory) — FROZEN v1.0**
- No holding cap — every signal that triggers is recommended.
- Flat ₹1 lakh per signal. No recycling logic needed: XIRR annualises each rupee
  over the exact period it was at risk, so whether the client funds a new
  recommendation from fresh savings or from closed-position proceeds does not
  change any cash-flow date or amount, and therefore does not change XIRR.
  The open questions in old section 9 (items 1-5) are **resolved/moot**.
- Metric: **XIRR** (money-weighted). Benchmark: matched-timing index XIRR.
- Full spec: `FF_Advisory_Methodology_v1.md`.

**B. Model Portfolio — ENGINE BUILT AND TESTED (31 Aug 2026)**
- Same 351-signal engine as Advisory. Cap 20, slot Rs 50,000, minimum Rs 10 L.
- FCFS slot allocation; idle cash parked in a **Nifty 500 index fund**, not liquid.
- **Run-off design is PRIMARY** (see section 12). Metric: CAGR over the
  portfolio's own life, measured across rolling monthly start dates.
- XIRR and CAGR must never be conflated between the two products.
- Full detail in section 12 below.

---

## 1. SUPERSEDED — High-based ATH entry rule

Originally validated 166/166 against the old backtest using
`Close <= 0.60 x rolling-max(HIGH)`. Priyanshu confirmed 24 Aug that his
**design intent was always the closing-price ATH** ("intraday high bahut
volatile hote hai"). Both variants were tested; XIRR was nearly identical
(35.25% High-ATH vs 35.22% Close-ATH). See 1-bis.

## 1-bis. Entry/exit rule — CONFIRMED FINAL: Close-based ATH

```
Entry   : Close(t) <= 0.60 x cummax(CLOSE up to and including t)
          AND Net Sales, PAT, Diluted EPS all at rolling-window high
              (8Q for Large/Mid/Small, 4Q for Micro Cap)
          AND Net Sales > 0 AND PAT > 0 AND Diluted EPS > 0   <- positivity filter
          AND stock is ARMED
Re-arm  : a fresh all-time-high CLOSE arms the stock. Once a signal fires the
          stock is disarmed until it makes a new all-time-high close.
Exit    : cummax(CLOSE) as at trigger date = target (fixed, never moves),
          or 1095 days, whichever first. No stop-loss.
Avail   : quarter_end + 60 calendar days.
Entry   : next trading day's OPEN.
```

Both the entry threshold and the exit target now use the **same** yardstick
(all-time-high closing price) — internally consistent. Verified empirically:
625/625 pre-filter signals had `target_ath == cummax(close)` at trigger date,
max ratio 0.5999, zero above 0.60.

Variant counts (Total Market, 2011+): High-ATH 691 · Close-ATH 625 ·
Close-ATH + positivity **614 (FINAL)**. Overlap between High and Close variants:
459 shared, 232 High-only, 166 Close-only.

## 1-ter. Positivity filter — added 26 Aug 2026

**Problem found.** 18 of the 625 Close-ATH signals had a governing quarter where
PAT/EPS were negative — and in all 18 the *entire* window was loss-making, so
"PAT at an 8-quarter high" practically meant "smallest loss in 8 quarters".
Worst case: IDEA with a −₹5,524 cr quarterly PAT classified as a fundamental
high. Also PAYTM, UCOBANK, TTML, ITI, RTNPOWER, etc.

**Fix.** Add `net_sales > 0 AND pat > 0 AND eps > 0` to the entry condition.

**Scope — important.** The test applies to the **governing quarter only**, not
to every quarter in the window. A company with loss quarters in its window still
qualifies if the most recent quarter is both the window high and positive. This
is deliberate: that is the turnaround case the strategy exists to catch.
Verified: 773 fundamental rows pass the filter despite negative quarters in
their window; 162 of the final 614 signals (26%) have ≥1 loss-making quarter in
window, with a 75.9% win rate (above the 73.8% overall average).
Example that correctly survives — ABFRL Sep-2015, PAT window
−15.7, −70.8, −78.1, −43.5, −42.8, −63.8, −67.9, **+60.7**.

**Effect on count — not a simple subtraction.** Because a rejected signal does
not disarm the stock, those 18 stocks stayed armed and fired later when their
fundamentals genuinely turned positive: **18 removed, 7 new later entries →
614**, not 607. Several deferred entries did much better than the originals
(MASTEK +343.9%, V2RETAIL +415.5%, UCOBANK +204.4%).

**Cost.** XIRR 35.22% → **34.86%** (−36 bps). Win rate 73.6% → 73.8%.
Cheap price for making the stated logic literally true and defensible to a
compliance reviewer.

## 1-quater. BENCHMARK ERROR FOUND AND CORRECTED — 26 Aug 2026

**The error.** Every segment was being compared against the **Nifty 500**,
including the Micro Cap segment and the full Total Market book. The Nifty 500
contains no micro caps at all, so this credited the strategy with segment beta
it had not earned.

**Files obtained.** Priyanshu supplied `Nifty_Indices_Historical.zip` containing
yearly chunks for **Nifty Total Market** (31-Aug-2009 → 26-Aug-2026, 4,212 rows)
and **Nifty Microcap 250** (25-Jul-2013 → 23-Jul-2026, 3,214 rows), plus updated
Smallcap 250 and a bonus LargeMidcap 250. Consolidated into
`indices/Nifty_Total_Market.csv` and `indices/Nifty_Microcap_250.csv`. No gaps
>10 days in either.

**Critical constraint.** The Microcap 250 index **does not exist before
25-Jul-2013**, while the first Micro Cap signal is 31-May-2011. 54 of 263 Micro
Cap trades therefore cannot be benchmarked. The valid comparison is the
**209-trade subset entered on/after 25-Jul-2013**. The 263-trade Micro Cap XIRR
of 36.35% has **no valid benchmark partner** and must never be compared to any
Microcap 250 figure.

**The finding — same 209 trades, only the yardstick changes:**

| Benchmark | Benchmark XIRR | Apparent excess |
|---|---|---|
| Nifty 50 | 12.80% | +11.36 pp |
| Nifty 500 (what we were wrongly using) | 14.70% | +9.46 pp |
| Nifty Total Market | 14.94% | +9.22 pp |
| Nifty Smallcap 250 | 20.36% | +3.80 pp |
| **Nifty Microcap 250 (correct)** | **27.71%** | **−3.55 pp** |

Micro Cap **lags its own benchmark.** Microcap 250 itself compounded at 24.61%
CAGR from Jul-2013 to Jul-2026 vs Nifty 500's 13.35% — an exceptionally hard bar.

**Two effects inflated the earlier number, both in the same direction:**
1. *Benchmark mismatch* — ~13pp of segment beta wrongly credited.
2. *Period mismatch* — dropping the 2011–mid-2013 cohorts takes Micro Cap from
   36.35% to 24.16% (−12.19pp). Micro 2012's 93.8% is itself driven by one trade
   (MARKSANS +1,709%); without it the cohort is 69.2%.

**Level playing field (all entries ≥ 25-Jul-2013, each vs its own benchmark):**

| Segment | n | Strategy | Own benchmark | Excess |
|---|---|---|---|---|
| Nifty 500 tier | 298 | 36.14% | 17.42% | **+18.72 pp** |
| Combined | 507 | 31.69% | 16.69% | +15.00 pp |
| Micro Cap | 209 | 24.16% | 27.71% | **−3.55 pp** |

**Tier-matched cross-check (entries ≥ 14-Jan-2019, each trade vs its own tier
index — the window where all four tier indices exist):**

| Segment | n | Strategy | Tier-blend | Excess |
|---|---|---|---|---|
| Combined | 358 | 36.99% | 32.86% | +4.13 pp |
| Nifty 500 tier | 206 | 37.23% | 29.56% | +7.67 pp |
| Micro Cap | 152 | 36.59% | 37.95% | **−1.36 pp** |

Same conclusion under a different construction and a different window. **Note
also that the Nifty 500 tier's edge narrows from +18.72pp to +7.67pp under
tier-matching** — a large share of the headline is segment beta, not selection.
Both figures must be disclosed (limitation #6 in the spec).

**Other Micro Cap quality failures:** median 40.8% vs 66.3%; hit rate 51.8% vs
57.1%; 7.1% of trades lost >50% vs 4.0%; worst −91.4% vs −82.9%; one outright
negative cohort (2016, −2.2% XIRR, median −30.2%). Avg > median in Micro Cap
(outlier-driven) vs avg < median in the Nifty 500 tier (broad-based).

**Also documented:** the fixed ATH target caps upside. 69% of target-hit trades
would have been worth more held to the 3-year cap — median +45pp (Nifty 500
tier) / +49pp (Micro). Mean foregone is far larger in Micro (+263pp vs +170pp).
Frequency is identical across segments; only the magnitude differs. Retained
deliberately for auditability, now disclosed in spec §7.1 and limitation #11.

**Still missing:** full **Nifty Midcap 150** history (current file starts
2019-01-14). With it, the tier-matched benchmark could be computed from 2012
rather than 2019. Download the same way as the others.

---

## 2. Signal-list completeness — RESOLVED

Old data gave 187 full-universe signals vs 166 in the documents; 21 flagged as
genuinely missing. Re-verified on v3: **20 of 21 now present** in the signal set
(the 21st symbol is not in the 751-name universe). The earlier "187 vs 625"
jump was caused by old sessions applying extra restrictions on signal
generation (likely a `base_sim.pkl` subset), plus the new price history starting
1995 rather than a median of 2010 — not a data error.

---

## 3. SUPERSEDED — original price data was corrupted

Fabricated 28-Jul-2005 bar in 273 stocks caused false ~90-99% crashes and
permanently corrupted the ATH for 52 stocks. Original series was also
dividend-adjusted (wrong basis — exit target is an absolute price level).

## 3-bis. Price data rebuild — COMPLETE

Rebuilt from NSE's own raw daily bhavcopy (fresh pull, not a patch).
`ff_prices_adjusted_v3.parquet`: **751 symbols, 2,930,778 rows,
1995-01-02 to 2026-08-24**, split+bonus adjusted only (no dividend adjustment).

- Corrupted ATHs: **0** (down from 74).
- Unexplained 35%+ single-day drops: 719 (raw) → 17 (final), all pre-2004.
- Junk bars setting an ATH: **0**. Junk bars at a decision point: **0**.
- Phantom dates: 0. Rule violations: 0. Duplicate/overlapping signals: 0.

Total-market expansion beyond 751 is deferred (raw data already downloaded;
only the adjustment pipeline needs rerunning).

---

## 4. Fundamentals data (`fund_flags.csv`) — provenance documented

Per Priyanshu (24 Aug 2026): **CMIE Prowess** through March 2026 (36,439 rows,
`source = historical`), supplemented with **Screener.in** through June 2026
(621 rows, `source = live_scrape`). Total 37,060 rows across 750 of 751 symbols,
quarter-ends Dec-2006 to Jun-2026. Some Screener rows manually cross-checked by
Priyanshu and found correct.

**Reporting lag.** All 36,439 historical rows use a flat 60-day lag from
quarter-end. Live/Screener rows use 42-44 days. The 60-day assumption is SEBI's
outer annual-filing deadline, so it is **conservative** — a live implementation
would enter earlier than the backtest, not later.

**Known glitch (low priority, no impact).** One row — BAYERCROP, report_date
2006-12-31, avail_date 2026-08-11 (7,163-day lag) — is a clear parsing error.
`all_hi = False`, so no signal was ever generated from it.

**Independent audit of `fund_flags.csv` has not started** — deferred; Priyanshu
considers Prowess reliable.

---

## 5. Benchmark methodology — RESOLVED in the Advisory spec

Part B PDF used matched cash-flow-timing XIRR (correct); the old Client
Presentation used plain index CAGR, which roughly doubled the apparent edge.
The frozen Advisory spec mandates **matched-timing XIRR** with **Nifty 500 as
the primary benchmark**. The old Presentation must be rebuilt on this basis.

---

## 6. Other issues in the Part B PDF — to fix on rewrite

Wrong tier benchmark (Nifty Total Market instead of Nifty 500), Nifty Smallcap
250 absent, zero risk disclosures across 33 pages, simulation uncapped while the
product was described as a capped model portfolio, small-sample figures shown
without caveat. Trade counts, win rates and index XIRR calculations all
reproduce exactly — those are fine.

---

## 7. Portfolio cap sensitivity — STALE, needs rerun

| cap | 15 | 18 | 20 | 22 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|
| avg CAGR | 16.07 | 16.36 | 16.31 | 16.04 | 15.68 | 16.39 | 16.49 | 16.40 |

Flat 15.7-16.5%, no monotonic pattern. Run on the OLD corrupted price data and
the old signal subset. **Must be rerun on v3 + full universe + Close-ATH +
positivity filter** before it can inform the cap decision.

---

## 8. Known limitations — accepted/deferred, revisit later

1. **Survivorship bias** — the 751-stock universe is today's index constituents
   rolled backward. Companies that delisted or failed after falling 40%+ are
   absent, which inflates win rate and XIRR by an unquantified amount. This is
   the most significant known limitation. Priyanshu's own check: ~50% of today's
   total-market companies have existed since 2012. Accepted as a consistent
   limitation until a good point-in-time-membership method is found.
2. **Corporate actions during a hold** — not an independent issue; a consequence
   of #1 (a held stock essentially cannot disappear mid-backtest).
3. **Restated fundamentals (look-ahead risk)** — Prowess/Screener may store only
   revised figures, so an 8Q-high check could use a number that was not public
   on the signal date. Flagged, not yet investigated.
4. **Transaction costs** not modeled (brokerage, STT, stamp duty, slippage,
   tax). Deliberately deferred given the ~2-year median hold, but needed for
   compliance-grade disclosure.
5. **`fund_flags.csv` independent audit** — not started, lower priority.
6. **Total Market universe expansion** beyond 751 — raw NSE data already
   downloaded, only the adjustment pipeline needs rerunning.
7. **Liquidity not modeled** — Micro Cap is 263 of 614 signals (43%) and may not
   absorb meaningful capital at modeled prices.
8. **Thin-history cohort (2011-12)** — 44 signals (pre-filter count) qualified on
   the bare minimum quarters needed to form their window. Win rate 65.9% vs
   74.2% for the rest; removing them *raises* XIRR to ~44.35%, so retaining them
   is the conservative choice. Show base + sensitivity side by side.

---

## 9. Open questions — RESOLVED

Items 1-5 (recycling mechanics) are **moot**: XIRR is invariant to how the
client funds each recommendation. Item 6 confirmed (Advisory = flat ₹1L;
Model Portfolio = % equal-weight, 5% max). Item 8 confirmed: **two fully
separate document sets**, one per SOP. Item 7 (cap decision process) remains
open — see section 10.

---

## 9-bis. Robustness testing — COMPLETE, 26 Aug 2026 (spec Section 14)

Six formal tests against the frozen v2.0 spec. **No rule changed.** Full write-up
is Section 14 of the methodology spec; raw results in `FF_research_all_tests.csv`
and `FF_research_timecap.csv`.

| # | Test | Result | Outcome |
|---|---|---|---|
| 1 | Ablation (price-only vs full rule) | Full 33.49% / +15.49pp vs price-only 29.58% / +9.53pp | filter retained |
| 2 | Threshold 0.50–0.70 | Smooth monotonic gradient; 0.60 NOT the optimum (0.50 = 35.42%) | 0.60 retained |
| 3 | Availability lag 30–90 d | XIRR band only 32.38–33.86% | 60 d retained |
| 4 | Partial exit (50% target + trail) | Headline +5.96pp → **+2.00pp after dropping 1 trade**, +1.01pp after 10; 8/15 cohorts | not adopted |
| 5 | Fundamental-break exit | 23.4–27.7% vs 33.49% baseline; all variants worse | rejected |
| 6 | Time cap 2 / 2.5 / 3 / 4 / 5 y | 2y = 37.02% (best XIRR, survives outlier removal) but **5/10 cohorts**, hit rate 43.3%; 4–5y XIRR-neutral | 3y retained |

**Most important finding (Test 1).** The fundamental filter does **not** work by
selection. Only 99 of 351 full-rule trades appear in the price-only set — the two
rules pick *different entry dates on the same stocks*. Under price-only the stock
fires on the first crossing of the 60% line; under the full rule the fundamentals
aren't ready that day, so it stays armed and fires later and **deeper**.

- price-only median entry/ATH **0.591** (75% of entries barely past the line)
- full rule median entry/ATH **0.560**, p90 discount to target 74.2%

The 649 signals the filter declined were **not bad** (29.43% XIRR, +9.59pp excess).
The filter replaces shallow entries with deep ones. **Client-facing material must
describe the mechanism this way** — "we pick better companies" is not what the data
shows. Cohort-level the full rule wins only 6/15 (small-N caveat applies).

Filter retained on three grounds: aggregate XIRR/excess, **actionability** (748
signals, up to 130 in one year, is not something a client can follow), and deeper
entries matching stated intent.

**Test 4 caution.** This is the clearest overfitting near-miss in the project. A
+5.96pp headline collapsed to +2.00pp on removing one trade (ZEEL, 1,609% blended).
Residual 1–2pp advantage looks real — revisit when the resolved-trade count is
materially larger.

**Test 5 caution.** Failed structurally, not statistically: entry requires an 8Q PAT
high, so the next quarter is more likely than not lower. Single-quarter variant
exits 291 of 351 positions at a 149-day average hold. The entry condition is a
point-in-time signal, **not a state that persists** — it cannot be a hold condition.

**Test 6 notes (time cap).** Two surprises. (a) Long caps do **not** hurt XIRR —
5y gives 33.29% vs 3y's 33.49%, essentially flat. (b) Benchmark **excess is
U-shaped with its minimum at 3.0y** (+15.49 vs +17.45 at 2y and +16.63 at 5y),
because matched-timing benchmark XIRR itself falls as holds lengthen (19.56% →
16.66%). So 3 years is the *worst* variant on excess — stated openly in the spec.

The 2-year advantage is **real** (survives outlier removal: +1.7 to +3.5pp at
every drop level — unlike Test 4). It was rejected on cohort consistency (5/10 =
coin flip), completion rate falling to 43.3%, median return 66.3% → 37.6%, and
because its 160 time-stopped positions have a **median return of +12.7%** with
only 41% in loss — those were cut off working, not failing.

4–5y was seriously considered: XIRR-neutral, better on win rate (84.9%),
completion (71.6%), median (73.5%) and excess. Rejected on capital efficiency
(629 vs 473 position-years for the same annualised return), a smaller resolved
track record at launch (93 open vs 76), and client proposition.

Net: **two parameters now** (threshold 0.60, time cap 1095d) have a documented
better-performing value that was identified and deliberately not adopted.

**Explicitly NOT tested** (parameter-fishing on a 275-trade sample): extra
fundamental metrics, sector filters, valuation screens, market-regime filters,
window lengths other than 8Q, price stop-losses (excluded on logic), re-arm
variants (legitimate future question, lower priority).

Scripts: `research.py` (parameterised harness), `t1_ablation.py`, `t2_threshold.py`,
`t3_lag.py`, `exit_tests.py`.

---

## 10. Next steps

1. **New-subscriber policy for the Model Portfolio** (section 12.8 item 1) —
   the largest open design question in the project.
2. Write the Model Portfolio Methodology Spec, mirroring the Advisory spec.
3. Fee structure decision, using the numbers in 12.4.
4. **Update `FF_reading_the_results.md` to v2.0 numbers** — it still describes
   the 614-trade set.
5. Obtain full **Nifty Midcap 150** history so the tier-matched benchmark can be
   computed from 2012 instead of 2019.
6. Quantify survivorship bias — the largest unmeasured hole in both products.
7. Verify tax and transaction-cost assumptions with a compliance/tax adviser.
8. Write the two Client Presentations (one per SOP) — Nifty 500 as primary
   benchmark, tier-matched excess shown alongside, 2018 losing cohort presented
   first, full risk disclosures.

---

## 11. Final Advisory reference numbers (v2.0, 26 Aug 2026)

**351 recommendations · 270 distinct companies · 31 May 2012 – 23 Jul 2026 ·
cut-off 27 Jul 2026 · ₹1,00,000 flat per signal · ₹3.51 cr total notional ·
peak 83 concurrent open positions (2 Jun 2020).**

| Metric | Value |
|---|---|
| Win rate (all / resolved) | 76.1% / 79.3% |
| Average return | +57.9% |
| Median return | +66.3% |
| Average / median hold | 670 d / 645 d |
| Exit: target / time cap / open | 157 / 118 / 76 |
| Hit rate (of resolved) | 57.1% |
| **Strategy XIRR** | **33.49%** |
| **Nifty 500 matched XIRR** | **18.00%** |
| **Excess** | **+15.49 pp** |
| Nifty Total Market matched | 18.28% |
| Nifty Smallcap 250 matched | 25.24% |
| Best / worst | OLECTRA +565.3% / JPPOWER −82.9% |
| Losses > 50% | 11 of 275 resolved (4.0%) |
| Cohorts beating Nifty 500 | 14 of 15 (2018 the exception) |
| Tiers | Large 59 (23.7%) · Mid 100 (30.6%) · Small 192 (38.8%) |
| Realised P&L | ₹1.96 cr on ₹2.75 cr deployed |

Superseded v1.0 numbers (751-name universe, 614 recommendations): XIRR 34.86%
vs Nifty Total Market 16.59%. Retained in the spec as Table B for comparison.

Artifacts on disk (`/home/claude/work`):
- `FF_FINAL_v2_n500.pkl` — **final 351-trade set**
- `FF_advisory_351_v2.csv` — delivered + committed to OneDrive
- `advclose_total_pos.pkl` = `FF_FINAL_advisory.pkl` — v1.0 614-trade set
- `FF_peryear_TRUE_benchmarks.csv` — all three tables, correct benchmarks
- `indices/Nifty_Total_Market.csv`, `indices/Nifty_Microcap_250.csv` — new
- `final_bench.py`, `v2_stats.py`, `split_tables.py` — rerun scripts

Delivered documents (OneDrive + project):
- `FF_Advisory_Methodology.md` / `ff_advisory.html` — spec v2.0, with the three
  backtest tables and three charts (per-year XIRR vs benchmark, segment excess
  vs own benchmark, return distribution)
- `FF_reading_the_results.md` — briefing note on reading the tables
  (**built on v1.0 614-trade numbers — needs updating to v2.0**)

---

## 12. MODEL PORTFOLIO — build and test log (31 Aug 2026)

### 12.1 Settled design

| Item | Decision | How decided |
|---|---|---|
| Universe | Nifty 500 (500 names) | inherited from Advisory v2.0 |
| Signal engine | identical to Advisory, 351 signals | must never diverge |
| Entry / exit rules | inherited unchanged | |
| Slot allocation | **FCFS** | tested, beat ranked alternative |
| Position sizing | NAV / cap at entry, **no rebalancing** | rebalancing would sell winners |
| Slot size | **Rs 50,000** -> minimum **Rs 10 L** at cap 20 | untakeable-signal analysis |
| Untakeable rule | `floor(slot / price)` shares; 0 -> skip, slot stays open | must be IN THE ENGINE, not just the doc |
| Idle cash | **Nifty 500 index fund** | biggest single lever, see 12.3 |
| Measurement | **run-off** primary, forced-exit as conservative check | see 12.5 |
| Backtest start | 2013-01-01 | liquid fund NAV data starts here |
| Benchmark | Nifty 500 price index, same period, same costs+tax | price index is right - we exclude dividends too |

**Cap 20 chosen** (band 15-30 tested). Cap 15 gives higher return but worse
downside on every metric; cap 25 better downside but +Rs 2.5 L minimum and lower
excess. Cap 20 also makes "equal weight, 5% max" self-consistent.

### 12.2 Untakeable-signal analysis

India has no fractional shares, so a slot smaller than one share cannot hold that
stock. Measured on actual (un-adjusted) prices, using the 355-row
`corporate_actions_used.csv` to reverse the split/bonus adjustment:

| Slot | Portfolio (cap 20) | Signals untakeable (recent) | Universe names blocked (today) |
|---|---|---|---|
| Rs 2,500 | Rs 50 k | 7.5% | many |
| Rs 25,000 | Rs 5 L | 0% | 7 |
| **Rs 50,000** | **Rs 10 L** | **0%** | **1 (MRF)** |

**"Untakeable = 0%" cannot be achieved at any retail minimum** — MRF trades near
Rs 1.34 L/share and never splits; a slot big enough needs a ~Rs 27 L portfolio.
MRF has **never generated a signal** in 14 years. Backtest impact at Rs 50 k slot
is **zero signals blocked**. Not a compliance problem: the universe defines
eligibility, not obligation, and the constraint is disclosed and mechanical.

*Correction logged:* an earlier statement that "2 signals are blocked at Rs 25 k"
conflated names blocked at TODAY's prices with signals blocked at their
HISTORICAL entry prices. Historically 0 were blocked at Rs 25 k too.

### 12.3 Idle cash — the finding that saved the product

The portfolio can rarely fill all 20 slots, so ~32% of capital sat idle.

| Idle cash in | 3-yr excess over Nifty 500 | Beat rate | Max drawdown |
|---|---|---|---|
| Liquid fund (6.8% CAGR) | +5.24 pp | 64% | -50.4% |
| **Nifty 500 index fund** | **+8.49 pp** | **80%** | -57.9% |

At +5.24 pp gross, a Rs 25,000 annual fee left the client with **nothing** over
an index fund after costs and tax — the product was not viable. Index parking
fixed that. **It is a conscious trade, not a free lunch: it costs ~7 pp of extra
drawdown**, because parked cash now falls in a crash too.

### 12.4 Costs and tax — measured, not estimated

Assumptions (VERIFY BEFORE PUBLICATION): 0.15% each side + 0.10% slippage;
LTCG 12.5% (>365 d), STCG 20%, debt/liquid gains 30% slab, Rs 1.25 L LTCG
exemption per FY. **Applied to the benchmark too**, else the comparison is unfair.

| Stage | Strategy | Nifty 500 | Excess |
|---|---|---|---|
| Gross | 22.67% | 13.78% | +8.49 |
| + transaction costs | 22.27% | 13.59% | +8.30 |
| **+ tax** | **19.25%** | **12.48%** | **+6.59** |

Transaction costs cost only 0.19 pp of excess (the benchmark pays them too).
**Tax costs 1.71 pp** — that is the turnover penalty, and it is unavoidable.

### 12.5 MEASUREMENT DESIGN CHANGED — run-off is now primary

**The problem.** The original test sold everything on day 1,095, including
positions bought weeks earlier with their own 3-year clocks still running. That
judged the strategy by the calendar rather than by its own rules.

**The change (Priyanshu's proposal, 31 Aug 2026).** Take signals for 3 years, then
stop buying but let every holding run to its own ending (target, or its own
1,095-day cap). Portfolio closes when the last holding closes. Cash from exits
stays parked in the index until then (option (a) — keeps a single NAV and keeps
CAGR meaningful).

**Identical 91 start dates, identical trades, only the exit rule differs:**

| | Positions finish (PRIMARY) | Sold on day 1,095 (conservative) |
|---|---|---|
| Portfolio life | 5.7 yrs | 3.0 yrs |
| Median CAGR | **24.78%** | 18.28% |
| p25 | **18.64%** | 8.96% |
| **Worst** | **+10.18%** | **-16.85%** |
| Excess | **+10.41 pp** | +5.50 pp |
| Beat index | **90 / 91** | 63 / 91 |
| **Lost money** | **0** | **13** |
| Median max drawdown | **-46.8%** | -28.5% |

**Clearest example:** the Jun-2017 start. Forced exit landed on the Covid bottom
-> Rs 5.76 L, -16.85%/yr. Run-off -> **Rs 19.32 L, +12.33%/yr** over 5.66 years.
Same trades.

**Two of my four predictions were wrong** and both errors matter:
- Predicted excess would *shrink* (wind-down tail = index exposure). It **rose**
  from +5.50 to +10.41 pp. Forced liquidation was destroying far more value than
  estimated.
- Predicted drawdown would be roughly unchanged. It **worsened badly**
  (-28.5% -> -46.8%), mechanically: a 5.7-year window is far more likely to
  contain the 2018-2020 crash than a 3-year one.

**Keep both views.** Run-off answers *"what does the strategy deliver?"*;
forced-exit answers *"what if I must exit on a fixed day?"* (worst case -42%),
which is the justification for a minimum holding period being a product rule
rather than a suggestion.

### 12.6 Drawdown — cannot be engineered away

Removing the worst trades from the full-period portfolio barely moves max drawdown:

| Worst N trades removed | 0 | 1 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|---|
| Max drawdown | -57.9% | -57.9% | -57.9% | -57.9% | -57.4% | **-57.7%** |

Because the drawdown was **Jan-2018 -> Mar-2020, a market event** — while the
biggest losing trades mostly occurred after it. Over the same peak-to-trough the
Nifty 500 fell 35.6%; the portfolio fell 57.9%. **~1.6x downside beta, structural**
(buys already-fallen stocks, no stop-loss, small/mid heavy). Disclose, don't fix.

Every drawdown 2013-2026 recovered: 11 falls >10%, 5 falls >20%, **all recovered**.
Median recovery 61 days from trough; longest 471. But the 2018 fall took 798 days
to bottom and 339 to recover — **1,137 days underwater**. One market path only;
not proof future falls recover.

### 12.7 OVERLAP CAVEAT — must accompany every headline number

91 start dates span only **7.5 years** while each portfolio runs **5.7 years**, so
neighbouring portfolios share almost their whole life. These are
**one market history examined 91 ways, not 91 independent results.**
Honest phrasing: *"across this one market cycle, no start date lost money"* —
never "the strategy does not lose money."

### 12.8 Still open

1. **New-subscriber policy** — the biggest unresolved question. A client joining
   mid-stream cannot buy a 2-year-old position at its entry price. Do they buy
   existing holdings at today's prices, or take only signals from their join
   date? This changes reported client returns materially. **Not yet discussed.**
2. Fee structure — depends on 12.4. At Rs 10 L: 1% fee leaves +5.6 pp,
   2.5% leaves +4.1 pp, 5% leaves +1.6 pp.
3. Survivorship bias — inherited from Advisory, still unquantified.
4. Tax rates — assumptions, must be verified.
5. Methodology spec + dashboard for Model Portfolio — not written.
6. Backtest starts 2013 not 2012 (liquid fund data) — 34 signals excluded.

### 12.9 Artifacts

Engine: `mp_engine.py` (base), `mp_net.py` (costs + tax + run-off via `sig_end`).
Data: `mp_runoff.csv` (91 run-off portfolios), `mp_forced_91.csv` (same starts,
forced exit), `mp_dd_windows.csv` (127 3-yr windows), `mp_cap_sens.csv`,
`t_actualpx.pkl` (351 trades with un-adjusted entry prices).
Report: `FF_ModelPortfolio_Three_Journeys.pdf` (10 pp) built by
`pdf2_head.py` + `pdf2_body.py` + `svg2png.py` + `topdf.py` from `mp_report2.json`.

---

## Working notes

- Priyanshu owns the strategy; Hindesh is his teammate. Priyanshu works in
  Google Colab on a Windows laptop, no Dhan account, not code-literate — needs
  complete copy-paste-ready notebook cells, no editing required.
- **Security:** Dhan access tokens carry order-placement capability, not just
  data read. Never paste one into chat. Tokens expire in 24 hours.
- File exchange: Priyanshu places files in his OneDrive folder
  (`NEW FUNDAMENTAL FIRST`); staged into the session from there.
- Colab notebooks built (delivered, reusable): `FF_NSE_Download.ipynb`,
  `FF_NSE_Verify_Clean.ipynb`, `FF_Adjust_Final.ipynb`.
