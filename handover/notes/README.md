# Project notes — index

These are the working documents written while the strategy and this pipeline
were built, copied here verbatim so they survive without any chat history or
external project. **They are dated records.** Where two disagree, the later
one wins; where a document says something is "not wired" or "not built", check
`HANDOVER.md` for the current state.

## Read these — current

| Document | Date | What it is |
|---|---|---|
| `FF_Advisory_Methodology_v1.md` | 26 Aug 2026 | **The frozen strategy specification, v2.0.** Every rule, its rationale, the reference backtest, the six robustness tests, the mandatory disclosures. The single most important document. Note: its reference set is the older 351-trade one; the pipeline's acceptance test uses the 358-trade v5 set described in `FF_Data_Integrity_v3.md`. The rules are identical. |
| `FF_Data_Integrity_v3.md` | 3–4 Sep 2026 | How the data was corrected to v5: EPS split-adjustment, the six non-equity bonuses (ZEEL class), the Screener reconciliation, the systematic corporate-action sweep. Explains why `FF_FINAL_v5_n500.csv` has 358 trades. |
| `FF_PhaseA_Results.md` | 5 Sep 2026 | Why real results-announcement dates replaced the 60-day assumption, and what that did to the live record (28 → 19 signals). |
| `FF_Backtest_Robustness.md` | 6 Sep 2026 | The COVID question two ways; the basis for the dashboard's information panel (279 closed trades). |
| `FF_Market_Strip.md` | 8 Sep 2026 | Every market-data source that was probed, what worked, what is blocked, and the dead ends. |
| `FF_Daily_Job_Reliability.md` | 29 Sep 2026 | The "unsettled bar" failure — symptom, cause, fix. |
| `FF_Repository_Audit_2026-09-29.md` | 29 Sep 2026 | **Full audit of the repository.** What was verified correct, the open issues (corporate-action ledger, stale symbols, repo growth, unpinned deps), the orphan files. |
| `FF_ModelPortfolio_Dashboard_Plan.md` | 11 Sep 2026 | The Model Portfolio product: settled design, backtest results, what a live dashboard for it would need. Internal use only. |

## Historical — superseded in part

| Document | Date | Status |
|---|---|---|
| `FF_audit_findings.md` | 26–31 Aug 2026 | The running audit log from the research phase. Sections 1–3 are marked superseded inside it. Section 12 (Model Portfolio build log) is still the reference for that product's design. Also holds the "Working notes" on how the team works. |
| `FF_Dashboard_Rebuild_Plan.md` | 3–4 Sep 2026 | The plan that produced the current pipeline. Its defect list describes the **old** pipeline, which has been replaced. Useful for understanding *why* things are built the way they are. |
| `FF_Status.md` | 4 Sep 2026 | A snapshot from mid-rebuild. Its "not wired" table is out of date — everything in it has since been wired. Kept for its "mistakes made" section. |
| `FF_Dashboard_v3_Plan.md` | 5–6 Sep 2026 | The dashboard build plan. Phases A–F are live; G (compliance footer) is still open. The URL it names is the old personal one; the current URL is in `HANDOVER.md`. |

## The numbers to quote

The reference backtest is **358 signals, 31 May 2012 – 23 July 2026** (v5).
Of those, **279 are resolved** (156 reached the target, 123 hit the 1,095-day
cap) and 79 were open at the cut-off.

- Win rate on all 358 at mark-to-market: **76.0%**. On the 279 closed: **78.9%**.
- Median return on the 279 closed: **+68.7%**.
- XIRR **31.77%** against the Nifty 500's matched-timing **17.88%** — excess
  **+13.89 pp**. 14 of 15 entry-year cohorts beat the index; 2018 is the one loss.

Any figure quoted anywhere must say which denominator it is on.
