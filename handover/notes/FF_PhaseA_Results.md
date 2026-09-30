# Phase A — results announcement dates: what changed

5 September 2026. Companion to `FF_Dashboard_v3_Plan.md`.

---

## What was wrong

`fund_flags_v3.csv` assumed every quarter became public exactly 60 days after the
quarter ended — 36,439 of its 37,191 rows. For the March-2026 quarter that put
every company on 30 May 2026. The June-2026 quarter used a different fiction: the
weekly scraper's own run date, 11 August.

## The source that worked

Six endpoints were probed. **NSE `/api/event-calendar`** won: 5,435 board-meeting
records across April–August 2026, of which 4,812 carry a results purpose, giving
**741 of our 751 symbols** a real Q4 FY26 date and 744 a Q1 FY27 date.

Rejected: `corporates-financial-results` returns 3,816 records but all relate to
the quarter ending 31 December 2024 regardless of the date parameters. BSE
`AnnSubCategoryGetData` with `strCat=Result` returns 4,199 records but keys on
BSE scrip codes, and its other categories returned nothing.

Ten symbols had no results-purpose meeting. Seven were filled by hand
(`manual_web`; `manual_verified` for NAUKRI, whose date matched an NSE board
meeting on the same day). Three — AGL, CCL, ECLERX — remain blank and were proved
inert: a signal needs the quarter to qualify **and** the price to reach 40% below
its high, and none of them does both anywhere in April–September.

## How wrong the assumption was

    741 symbols measured against the assumed 2026-05-30

    assumption was LATE  : 730
    assumption was RIGHT :  11
    assumption was EARLY :   0

    median 17 days late, maximum 51 (TCS and ANANDRATHI, both 9 April)

**The error has a direction, and only one.** The assumption never opened the gate
early.

## What it did to the live record

    signals since 1 June            28   ->   19
    median drawdown at trigger   42.78%  ->  41.12%     (the rule fires at 40.00%)
    deepest drawdown             83.49%  ->  58.48%
    within 2pp of the rule        13/28  ->  12/19      (46% -> 63%)

All three quality measures moved toward the rule, which is the acceptance test
this fix was judged on.

**Twelve left**, their real triggers falling before 1 June: the whole 1-June
cluster — GODREJPROP, HAVELLS, IDEA, IGIL, MAPMYINDIA, NAUKRI, SIGNATURE,
SUPREMEIND, TATATECH, TCS — plus ASTRAL and INFY.

**Three appeared** — HCLTECH (14 Jul), DEVYANI (29 Jul), OIL (7 Aug). Under the
old dates these had **no trigger at all since 2025**. Their real results landed
between 14 July and 7 August while the price was below the line; by 11 August,
when the scraper's date opened the gate, it had recovered above. **The defect did
not only misdate signals — it destroyed three.**

The 11-August cluster dissolved into five separate dates (30 Jul – 6 Aug), which
is what a scraper artifact looks like once the artifact is removed.

## Decisions recorded

**Option A stands.** Signals whose real trigger predates 1 June 2026 are out of
the record. NAUKRI is among them despite having been checked by hand — the record
starts 1 June and nothing before it is admitted.

**The frozen backtest is accepted as it stands** and will not be re-run for this
reason, unless something unavoidable forces it.

The reasoning, and it is sound: the measurement showed the assumption was late
730 times, on time 11, and **early zero times**. Never-early means **no
look-ahead bias** — the backtest never used information before it existed. That
is the one backtest defect that cannot be disclosed away, and it is ruled out by
measurement rather than by assumption.

The remaining nuance, recorded rather than argued: late is not the same as
understated. This strategy buys stocks already far below their high, so a gate
that opens later gives the price more time to fall and produces a *deeper* entry.
Among the seven surviving positions whose entry price changed, five got worse
entries once the real date was used and two got better — a weak signal from seven
observations, pointing to the assumption having mildly flattered entries rather
than penalised them.

So the exposure is bounded, one-directional, and small: a median 17-day lag on a
threshold rule. **The cheap and complete answer is one sentence of disclosure in
the methodology** — that quarterly results are assumed available 60 days after
quarter end, a lag measured against real announcement dates as median 17 days
late and never early. That costs nothing, is true, and closes the question
without re-running anything.

## Files

    results_dates.csv            1,492 rows — 1,485 NSE_event_calendar,
                                 6 manual_web, 1 manual_verified
    fund_flags_v3_datefix.csv    corrected copy
    datefix_signals.csv          the 19 signals since 1 June
    FF_datefix_compare.py        builds the corrected flags and the comparison
    FF_datefix_scan.py           runs the scan off the corrected flags

## State of the ledger — read before the next session touches it

The rebuild was **started and interrupted** when the machine went offline. It is
not known whether any of it ran. Before doing anything else, check the repository
folder:

- `_old_signal_ledger.csv` present → the command ran partway; the ledgers were
  moved aside and not rebuilt.
- absent → nothing ran.

Either way `signal_ledger.pre_datefix.bak`, `watchlist_ledger.pre_datefix.bak`
and `fund_flags_v3.pre_datefix.bak` are the safety copies, and no ledger content
has been lost.

The micro-cap watchlist still needs the same corrected scan — Phase A's scan
covered the Nifty 500 tiers only.

> *Handover note, 30 September 2026: the ledger rebuild described above was
> completed on 5 September; the live record now holds 20 open positions dated
> from 3 June 2026. The safety copies remain on the laptop, untracked.*
