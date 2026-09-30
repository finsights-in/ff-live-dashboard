# FF — where the rebuild actually stands

> **Handover note, 30 September 2026.** This is a snapshot from 4 September,
> mid-rebuild. Its "Built / Verified / Live" table is **out of date**: every item
> marked "not wired" was wired by 6 September, the ledger and dashboard were
> built, and the acceptance test runs in CI. It is kept for its "mistakes made"
> section, which is still the best short list of how this project goes wrong.
> For the current state, read `HANDOVER.md`.

4 September 2026. One page, kept current. Companion to
`FF_Dashboard_Rebuild_Plan.md` (the plan) and `FF_Data_Integrity_v3.md` (the
data audit). This file exists to answer one question without reading either:
**what is done, what is live, and what is left.**

---

## The goal, unchanged

A self-running dashboard on accurate data, serving both the Advisory and the
Model Portfolio products, with an immutable published record.

## The one-line answer

**The foundation is rebuilt and verified. Almost none of it is switched on yet.**

The live site today still produces its signals with the old scanner under the
old rules. What has changed for it so far is the price data underneath — which
is now correct — and nothing else. The dashboard itself has not been started.

---

## Where each piece stands

| Piece | Built | Verified | **Live** |
|---|---|---|---|
| Price base (v5, 751 symbols) | ✅ | ✅ | ✅ |
| CA-aware OHLC updater (Yahoo) | ✅ | ✅ 11 self-tests + live run | ✅ |
| NSE bhavcopy updater | ✅ | ✅ parser on 355 real subjects | ❌ **not wired** |
| Signal engine, spec v2.0 | ✅ | ✅ reproduces 358 trades exactly | ❌ **not wired** |
| Fundamentals ingest → v3 base | ✅ | ✅ idempotent, 131 quarters | ❌ **not wired** |
| Corporate-action ledger | ✅ | — | ❌ empty until the NSE updater runs |
| Append-only signal ledger + exits | ❌ | — | ❌ |
| Dashboard rebuild | ❌ | — | ❌ |
| CI data-quality gates | ❌ | — | ❌ |
| Quarterly reconciliation on a schedule | ❌ | — | ❌ |

**What the daily workflow runs right now:** `FF_OHLC_Updater_v2.py` (new, Yahoo),
then `FF_Fresh_Signal_Scanner.py` (**old**), then `FF_build_dashboard.py` (**old**).
**The weekly workflow runs** `FF_fundamentals_ingest.py` (**old**), which writes a
file nothing reads any more.

So three finished components are sitting in the repository doing nothing. That
is the gap to close next, and it is small: it is wiring, not building.

---

## The numbers, as they now stand (v5)

Everything published should quote these and nothing else.

| | |
|---|---|
| Signals | **358** |
| Resolved | 279 |
| Win rate | 76.0% |
| Median return | +65.4% |
| Target-hit rate | 55.9% |
| **XIRR** | **31.77%** |
| Nifty 500, matched timing | 17.88% |
| **Excess** | **+13.89 pp** |
| Cohorts beating the index | **14 of 15** |
| Only losing cohort | 2018 |

They moved twice today: 32.15% → 31.77% from the corporate-action sweep. All
six robustness tests were re-run on this basis and every conclusion holds.

**Documents on v5:** `FF_Advisory_Methodology.md`, `.docx`, `FF_audit_findings.md`.
**Not on v5:** `ff_advisory.html` — see "known bad" below.

---

## What was actually fixed today

**Prices.** The daily updater appended unadjusted rows onto an adjusted history
and never re-adjusted, so every corporate action left a cliff and the stock
looked "40% below its high". Four such cliffs sat in the live record; one,
TDPOWERSYS, had been **published as a signal** — a 1:2 split read as a 50%
fall. Replaced with an updater that rescales history, refuses a claimed factor
the price does not confirm, and quarantines anything it cannot verify. On its
first live run it handled two real splits correctly and refused a third event
it could not confirm.

**The price base.** `ohlc_data/` re-seeded from the backtest's own validated
base, so the live pipeline and the backtest finally stand on one thing. 219 MB
→ 120 MB, with no loss that reaches the sixth significant figure.

**Corporate actions.** A sweep of all 798 recorded events found three more of
the ZEEL class — BRITANNIA, COROMANDEL, NTPC — where a factor of 2 was applied
to an event that never touched the share count. NTPC's "+81.88% target hit" was
the artifact; it is a −8.24% time stop.

**Fundamentals.** Reconciled against an independent Screener re-scrape covering
all 751 symbols. Net Sales agree to a median of 0.013%. The scraper's
stale-table bug was found and fixed. The ingest now writes the corrected base.

**The scanner.** Rewritten to the specification and proven against the
reference set.

---

## What is left, in order

1. **Wire the three finished pieces in.** Point the daily workflow at
   `FF_Signal_Engine_v2.py` and `FF_NSE_OHLC_Updater.py`, the weekly one at
   `FF_fundamentals_ingest_v3.py`. Small, and it makes the last two days of work
   actually count.
2. **Append-only signal ledger and exit tracking** (Phase 4). Today the scanner
   rebuilds every signal from scratch each run, so a published recommendation
   can change or vanish. This was not theory: on 4 September, SUNTV disappeared
   and GODREJCP appeared with a trigger date three weeks old, with no market
   event behind either. A research analyst's record cannot behave like that.
3. **The dashboard** (Phase 5). Open positions, closed trades, live record
   against the Nifty 500. Serving Advisory and Model Portfolio both.
4. **CI gates.** `--verify` as a required step, so a change that breaks the
   358-trade reproduction fails the run instead of shipping.
5. **Quarterly reconciliation on a schedule**, so data quality is a process and
   not an event.
6. **Regenerate `ff_advisory.html`** from the v5 outputs.

---

## Known bad, and known unknown

**`ff_advisory.html` is stale and should not be shared.** Its tables were never
fully updated in the v3 pass either — 2020 shows 35 signals against 37, the
threshold sweep shows 211 at 0.50 against 214, and the per-year chart still
carries a 2013 figure from before v3. Charts, tables and the markdown document
currently give three different answers. It needs regenerating, not patching;
patching is how it drifted. **The `.docx` is the one to send anyone.**

**Micro Cap is out.** Excluded from Advisory, Model Portfolio and the dashboard.
The engine emits it to a separate watchlist file. Its flags still need their own
8-quarter rebuild before it can be a product.

**257 of the 358 trades are still unverified.** Screener publishes about
thirteen quarters, so everything before Jun-2023 has no second source. This is
the largest remaining exposure and no amount of further work on the recent data
reduces it.

**Survivorship bias is unquantified**, and `ident.csv` applies today's
Large/Mid/Small labels backwards — a stock that is Large Cap now may have been
Small Cap in 2013.

**Insurer and lending-NBFC line definitions are undecided.** Which row is "Net
Sales" for an insurer drives the largest cluster of reconciliation
disagreements and has never been written down.

---

## Mistakes made today, so they are not repeated

Recorded because each one nearly shipped, and the pattern in them is the same:
a check that was easy to skip got skipped.

- **Concluded from a stale clone.** Reported "the price bug has never fired" from
  a local checkout three weeks old. It had fired four times, and one was
  published. *Check the data is current before concluding from it.*
- **v3 called done after fixing what was visible.** Three more corporate-action
  errors were sitting in the data and only surfaced when a different task forced
  the systematic sweep. *A check that can be skipped will be.*
- **An ingest that erased a correction.** The first version recomputed split
  factors every run; with no ledger present it set them all to 1 and wiped the
  v3 EPS adjustment from 9,732 rows, silently. Now factors apply once and are
  marked, and a run that would restate a quarter of the file refuses to write.
- **Two acceptance tests that failed on their own design** — a tolerance tighter
  than the stored precision, then a relative tolerance on a percentage-point
  figure. *Fix the measure, never loosen the standard.*
- **A patch that hit the wrong table.** Overwrote the matched-subset results
  with full-set numbers; caught in verification and restored from backup.
- **Asserted the OHLC base was Yahoo-sourced** because the old updater's
  docstring said so. It is NSE bhavcopy throughout. *A comment is not evidence.*
