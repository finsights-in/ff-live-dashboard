# FF — Model Portfolio live dashboard: assessment and plan

Date: 2026-09-11. Companion to section 12 of `FF_audit_findings.md`.
Question asked: can we build a live dashboard for the Model Portfolio, how, and
what should we expect.

## SCOPE — read this first

Priyanshu confirmed on 11 September that this dashboard is **for internal
reference only, not for clients.** That removes the two decisions this document
originally called blockers:

- The **new-subscriber policy** only bites when someone joins an existing
  portfolio. For one internal portfolio with one start date, it does not arise.
  It remains open for the *product*, and must be settled before any client sees
  a Model Portfolio — but it no longer blocks this build.
- **Two dashboards showing different holdings** only confuses when both face
  clients. Internally, the difference is understood.

**One prerequisite survives the change of scope:** re-running the engine on
current data (phase 1 below). Internal or not, a dashboard built on the
351-signal set describes a strategy that has since changed.

## Verdict

Yes, and most of the machinery exists. The Advisory dashboard already provides
the daily workflow, the append-only ledger discipline, the Nifty 500 feed, the
page shell and the hosting. Reusing them for a second product is days, not a
project.

## What must be re-done first

The engine was tested on the **351-signal** set. That has been superseded twice:
the 4 September corporate-action sweep moved the reference to **358 trades**, and
Phase A replaced the assumed 60-day results lag with real announcement dates,
cutting live signals from 28 to 19 and destroying three that never existed under
the old dates.

Re-running `mp_engine.py` on current data is task one, with the same acceptance
discipline the signal engine has: reproduce the current reference exactly, and
explain every difference.

## Build phases

| Phase | Work | Acceptance test |
|---|---|---|
| 0 | Fix the start date and corpus for the internal portfolio | Written down before code runs |
| 1 | Re-run the engine on the 358-trade set and current prices | Reproduces the reference; changes explained |
| 2 | Append-only live portfolio state: NAV, holdings, cash, skipped | A past NAV row can never change; re-running a day is idempotent |
| 3 | Daily job in the existing workflow, after the ledger | Never fatal — must not stop the signal dashboard |
| 4 | Idle-cash vehicle: Nifty 500 daily | Already running |
| 5 | The page, reusing the Advisory shell | Same tokens, theme, mobile behaviour |
| 6 | Backtest information panel | Carries the overlap caveat and the drawdown, not only the CAGR |

Phases 3–5 are quick; the work is 1 and 2.

## Settled design (from section 12)

Nifty 500 universe · cap **20** · FCFS slots · slot ₹50,000 → minimum ₹10 lakh ·
`floor(slot/price)` shares, 0 → skip · no rebalancing · idle cash in the
Nifty 500 · **CAGR**, time-weighted (never XIRR — that is Advisory's metric).

## What the backtest says

91 monthly start dates, run-off basis, **net** of costs and tax, ~5.7 years each.

| | Worst | p10 | Median | p90 | Best |
|---|---|---|---|---|---|
| CAGR | 10.2% | 12.9% | 24.8% | 37.8% | 55.3% |
| Excess over Nifty 500 | −0.9 pp | +2.0 pp | +10.4 pp | +26.9 pp | +39.1 pp |
| Max drawdown | −62.1% | | −46.8% | | −19.2% |

90 of 91 start dates beat the index; none lost money. The exception is April
2018: 12.5% a year against the index's 13.4%.

Average cash holding: **~22%**, parked in the index.

### Gross single-path run (11 Sep 2026, for internal reference)

One portfolio, 1 Jan 2013 → 27 Jul 2026, ₹10 L, cap 20, idle cash in the index,
**no costs and no tax on either line**. Produced `mp_gross_vs_index.csv` and
`FF_MP_vs_Nifty500_gross.html`.

| Window | MP / yr | Nifty 500 / yr | Excess | MP total | Nifty 500 total |
|---|---|---|---|---|---|
| 3Y | +20.64% | +10.97% | +9.67 pp | +75.6% | +36.7% |
| 5Y | +20.42% | +11.18% | +9.24 pp | +153.2% | +69.9% |
| 10Y | +21.88% | +12.22% | +9.65 pp | +623.0% | +216.8% |
| Max | +23.19% | +12.31% | +10.88 pp | +1,593% | +383.1% |

Max drawdown on this path **−56.4%**; **198 of 317 signals skipped** for want of a
slot; average cash 22.0%.

The 3/5/10-year windows are **trailing slices of the 2013 portfolio**, already
fully invested when each window opens — not portfolios that started 3, 5 or 10
years ago. Those would open in cash and take months to fill twenty slots. The
91-start-date study answers that question; this chart does not.

**Gross figures are internal only.** At ₹10 lakh a 1% fee alone takes ~5.6 pp off
the excess.

### Three caveats that must travel with the net numbers

1. **One market history examined 91 ways.** Start dates span 7.5 years while each
   portfolio runs 5.7, so neighbours share almost their whole life. Say "across
   this one market cycle, no start date lost money" — never "the strategy does
   not lose money."
2. **A median drawdown of −46.8% is not a footnote.** Over the same peak-to-trough
   the Nifty 500 fell 35.6% and the portfolio 57.9% — ~1.6× downside beta, and
   structural. Removing the ten worst trades moves max drawdown by 0.2 of a
   point, because the drawdown was a market event. Disclose, do not fix.
3. **Forced exit is a different product.** Median CAGR falls 24.8% → 18.3% and the
   worst start date reaches **−16.9% a year**. That gap is the whole argument for
   a minimum holding period being a rule, not a suggestion.

## Source

`mp_runoff.csv`, `mp_forced_91.csv`, `mp_cap_sens.csv`, `mp_gross_vs_index.csv`,
`mp_engine.py`, `mp_net.py`, and section 12 of `FF_audit_findings.md`. All on the
351-signal set, predating the September corrections — which is why phase 1 exists.

> *Handover note, 30 September 2026: `mp_engine.py` and its outputs are not in
> this repository. They were built in a Claude session and delivered as files;
> copies should be in Priyanshu's OneDrive folder. If they cannot be found, the
> engine must be rebuilt from the settled design above and section 12 of
> `FF_audit_findings.md` — both are complete enough to do so.*
