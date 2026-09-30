# FF — Backtest robustness: the COVID question, two ways

Date: 2026-09-06
Source: `FF_FINAL_v5_n500.csv` (358 signals; 156 ATH_TARGET, 123 TIME_STOP, 79 DATA_END)
and `FF_covid_timestop_recovery.csv` (the 28).

## Basis

All figures are on the **279 resolved trades** (ATH_TARGET + TIME_STOP). The 79
still open at the end of the test are excluded throughout, because "did it reach
its target" cannot be asked of a position still running.

This is NOT the denominator behind the methodology document's headline win rate
of 76.0%, which is taken over all 358 including the 79 at mark-to-market. On the
279 that closed, the win rate is 78.9%. Both are correct; they answer different
questions. Any client-facing surface must state which one it is using.

## There are two different "exclude COVID" questions

They pull in opposite directions, and conflating them is how a backtest gets
talked into looking better than it is.

**(a) The 28 COVID time-stops.** Trades whose 1,095-day cap fired between April
2020 and January 2023 while the position was still under water. Every one of the
28 is a loss (15 Small, 10 Mid, 3 Large). Removing them removes 28 losers and
zero winners, so every metric must improve — arithmetic, not evidence.

**(b) The 2020 entries.** Signals that fired during the crash and rode the
recovery. 36 of them, win rate 97.3%, and March 2020 alone is 26 of the 279.
Removing them removes mostly winners, so every metric must worsen.

Neither is a robustness test on its own. Together they bracket the answer.
There is **no overlap** between the two sets.

## The table, all caps

| Outcome | All 279 | Excl. the 28 | Excl. 2020 entries | Excl. both |
|---|---|---|---|---|
| Trades closed | 279 | 251 | 243 | 215 |
| Avg months to reach the high | 16.8 | 16.8 | 17.4 | 17.4 |
| Reached the high | 55.9% | 62.2% | 51.9% | 58.6% |
| Median return, reached the high | +75.0% | +75.0% | +73.4% | +73.4% |
| Hit the 1,095-day cap | 44.1% | 37.8% | 48.1% | 41.4% |
| Win rate at the cap | 52.0% | 67.4% | 49.6% | 65.2% |
| Median return at the cap | +4.8% | +17.4% | −0.8% | +15.9% |
| Overall win rate | 78.9% | 87.6% | 75.7% | 85.6% |
| Overall median return | +68.7% | +70.4% | +67.7% | +68.9% |

## Reading

1. **The median return is the stable number.** It sits between +67.7% and +70.4%
   across every scenario. Whatever is done to the COVID cohort, the median trade
   does roughly the same thing — because the median trade was never in either set.
2. **The win rate is the fragile number.** 75.7% to 87.6% depending purely on
   which COVID cohort is dropped. An 11.9-point range on a definitional choice.
   This is why the win rate should never be quoted without its denominator and
   its scope.
3. **The 1,095-day cap is where COVID actually landed.** Median return at the cap
   ranges from −0.8% to +17.4%. Under the honest all-279 figure it is +4.8%; drop
   the 2020 entries and it is negative. The cap bucket is thin and event-driven,
   and it should be presented as such.
4. **What the 28 went on to do.** After the forced exit, **27 of 28 broke even**
   (median 360 days later) and **20 went on to reach the old target** (median 833
   days later). Only BANDHANBNK never broke even. Eight never reached the target:
   SAIL, IFCI, SUNTV, PNBHOUSING, GRAPHITE, HEG, M&MFIN, BANDHANBNK. This is the
   strongest available argument for revisiting the 1,095-day cap — but the cap is
   a frozen rule and any change is a separate, deliberate decision, not a
   consequence of this table.
5. Segment ordering is stable in every scenario; the exclusions do not change
   which cap band looks better.

## What may and may not be published

- **Publishable:** the all-279 column, labelled backtested, with the 60-day-lag
  disclosure.
- **Not publishable:** the "excl. the 28" column as a strategy result. It is a
  diagnostic of the cap rule, nothing more.
- If a COVID-adjusted figure is ever shown to a client, **both** the 28-excluded
  and the 2020-excluded columns must appear together, or neither.

## Caveats that still stand

- Cap labels come from `ident.csv` and apply **today's** Large/Mid/Small
  classification backwards. Segment splits should be read with that in mind.
- Survivorship bias is unquantified.
- Quarterly results are assumed public 60 days after quarter end. Measured
  against real announcement dates that assumption runs a **median 17 days late,
  never early** (730 late, 11 right, 0 early). Correcting it moved the live
  signal count from 28 to 19.
