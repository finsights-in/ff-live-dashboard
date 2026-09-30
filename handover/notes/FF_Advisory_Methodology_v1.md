# Fundamental First — Continuous Recommendation (Advisory)
## Methodology Specification

**Version:** 2.0 (Final)
**Date:** 26 August 2026
**Supersedes:** v1.0 (26 Aug 2026), which included Micro Cap
**Backtest reference set:** 351 recommendations, 31 May 2012 – 23 July 2026
**Status:** Rules frozen. Any change requires a new version number and a full re-run.

> **What changed in v2.0.** Micro Cap has been **removed from the universe**. The universe is now the 500 Nifty 500 constituents. When each segment is measured against its own correct benchmark, Micro Cap underperformed the Nifty Microcap 250 index, while the Nifty 500 tier beat the Nifty 500 by a wide and consistent margin. Section 11 sets out the full evidence and explains what kind of investment approach Micro Cap *would* suit. The 4-quarter fundamental window that existed only for Micro Cap is retired; every stock now uses 8 quarters.

> **Note added 30 September 2026 (handover copy).** The reference set was later corrected to **358 trades** (v5) after the corporate-action sweep of 4 September 2026 — see `FF_Data_Integrity_v3.md`. The rules in this document are unchanged; only the data behind the figures moved. The pipeline's acceptance test reproduces the v5 set (`FF_FINAL_v5_n500.csv`).

---

## 1. Purpose and Scope

This document specifies, in full and without ambiguity, the rules of the **Fundamental First (FF) Continuous Recommendation** service — a rules-based, long-only Indian equity strategy.

This is the **Advisory** variant. Every signal the rules generate is issued to the client as a recommendation. There is no cap on the number of open recommendations, no discretionary override, and no view taken on how the client funds the position.

A separate document governs the **Model Portfolio** variant, which applies a position cap and a portfolio-construction layer on top of the identical signal engine. Where the two documents differ, it is only in construction and measurement — never in the signal itself.

**The defining property of this strategy is that it is fully mechanical.** Given the same data, two independent operators must produce identical recommendations on identical dates. Nothing in this document requires judgement.

---

## 2. Investment Philosophy

The strategy buys companies where **price and fundamentals have decoupled in opposite directions**.

Specifically, it requires two things to be true on the same day:

1. The stock has fallen at least 40% from its own all-time-high closing price.
2. The company's most recently published quarterly results are the **best in its recent operating history** — highest Net Sales, highest PAT and highest Diluted EPS in the trailing eight quarters.

Individually, neither is interesting. A 40% drawdown on its own is usually a value trap. A record quarter on its own is usually already priced in. It is the **combination** that carries the edge: the market is pricing the company as though something has gone badly wrong, while the operating statements say the exact opposite.

The exit follows the same logic. The strategy does not attempt to forecast a fair value or a target multiple. It simply asserts that a company whose fundamentals are at a record high has no structural reason to remain 40% below a price the market itself once paid. **The old high is therefore the target.**

### Why this is a *deep value* strategy and not a momentum strategy

Nothing here rewards a rising price. The price filter only fires when the stock is deeply depressed. The strategy is structurally a buyer of falling stocks, held to a fixed recovery target. Investors and reviewers should understand it in that frame.

---

## 3. Universe

**500 listed Indian equities** — the constituents of the Nifty 500.

| Tier | Count | Source |
|---|---|---|
| Large Cap | 100 | Nifty 100 |
| Mid Cap | 150 | Nifty Midcap 150 |
| Small Cap | 250 | Nifty Smallcap 250 |
| **Total** | **500** | **Nifty 500** |

Tier membership is assigned once per stock and held fixed for the entire history.

**Rationale for a fixed 500-name universe.** A fixed, published universe makes the strategy auditable. Any third party can reconstruct the identical signal set from the same list. The Nifty 500 is also an index a client can actually buy, which makes the benchmark comparison in Section 9 a real alternative rather than a theoretical one.

**Rationale for excluding Micro Cap.** Measured against the Nifty Microcap 250 — its own correct benchmark — the strategy's Micro Cap recommendations returned **24.16% against the index's 27.71%**. They lost to the index. Every quality metric was also worse than the Nifty 500 tier: lower median return, lower thesis-completion rate, and nearly double the rate of catastrophic single-name losses. **Section 11 sets out the full evidence**, including what kind of investing approach Micro Cap *would* be appropriate for.

**Rationale for including Small Cap.** Small Cap contributes 192 of the 351 recommendations and the highest tier XIRR (38.8%). Unlike Micro Cap, it clears its benchmark comfortably and its returns are broad-based rather than dependent on a handful of outliers.

> **Disclosed limitation.** Universe membership is taken as of today and applied backwards through history. This introduces **survivorship bias** — companies that were delisted, merged away or failed are absent from the backtest. It is disclosed in Section 12 and must be disclosed to every client. It is not corrected in v2.0.

---

## 4. Data Inputs

### 4.1 Price data

| Attribute | Specification |
|---|---|
| Source | NSE daily bhavcopy (official exchange archive) |
| Fields | Open, High, Low, Close |
| Coverage | 2 January 1995 – 24 August 2026 |
| Adjustment | **Splits and bonuses only** |
| Dividend adjustment | **Not applied** |

**Rationale for split/bonus adjustment.** A split or bonus mechanically changes the price without changing the value of the holding. Leaving it unadjusted would create a false 50% "drawdown" on a 1:2 split date and fire fake signals. Adjustment is mandatory.

**Rationale for *not* adjusting dividends.** This is a deliberate and important choice. The exit target is an **absolute historical price level** — the actual rupee price the market once paid. A dividend-adjusted series shifts every historical price downward and would silently lower the target, manufacturing exits that never happened in reality. Dividends received during the holding period are therefore **not** included in the reported return, which makes the reported performance **conservative**.

### 4.2 Fundamental data

| Attribute | Specification |
|---|---|
| Primary source | CMIE Prowess (historical) |
| Secondary source | Screener.in (recent quarters) |
| Coverage | Quarter-ends from Dec-2006 to Jun-2026 |
| Fields used | Net Sales, Profit After Tax (PAT), Diluted EPS |

**Rationale for these three fields.** They are deliberately chosen to span the income statement: Net Sales tests demand at the top line, PAT tests profitability after all costs and taxes, and Diluted EPS tests that the gains reached the shareholder and were not diluted away by equity issuance. A company can engineer any one of the three in isolation. Requiring all three simultaneously at a record high is difficult to fake.

**Rationale for Diluted (not Basic) EPS.** Diluted EPS accounts for convertibles, warrants and ESOPs. Using Basic EPS would let a company show record per-share earnings while quietly building future dilution.

### 4.3 Benchmark index data

| Index | Source | Coverage | Role |
|---|---|---|---|
| Nifty 500 | NSE / niftyindices.com | Sep-2005 onward | **Primary benchmark** |
| Nifty 50 / 100 / 200 | NSE | 2004–2007 onward | Supplementary |
| Nifty Smallcap 250 | NSE | Apr-2005 onward | Supplementary |
| Nifty Total Market | NSE | Aug-2009 onward | Comparison (Section 10.7) |
| Nifty Microcap 250 | NSE | **Jul-2013 onward** | Micro Cap evidence (Section 11) |

**Every benchmark must match the universe it is being compared against.** Comparing a micro-cap book to the Nifty 500 overstates the edge, because the Nifty 500 excludes micro caps entirely. This was an error in an earlier draft and is corrected throughout v2.0.

---

## 5. Entry Rules

A recommendation is issued on trading day **t** if and only if **all four conditions below are satisfied simultaneously**.

### 5.1 Condition A — Price condition (40% drawdown)

```
Close(t)  ≤  0.60 × ATH_close(t)

where  ATH_close(t) = the highest CLOSING price of the stock
                      on any day from the start of its price
                      history up to and including day t
```

**Rationale for using the closing price, not the intraday high.** Intraday highs are volatile and frequently unrepresentative — a single thin-volume print can set a high that no meaningful quantity traded at. The closing price is the exchange's settlement reference, is used for index calculation and NAV valuation, and represents a price at which real size actually cleared.

**Rationale for internal consistency.** The exit target (Section 7.1) also uses the closing-price all-time high. Using the intraday high for entry and the closing high for exit would mean the threshold and the target were measured on two different yardsticks. **Both use the same yardstick.**

**Rationale for the 0.60 threshold.** A 40% drawdown is deep enough to indicate genuine market pessimism rather than routine volatility, but not so deep that it only captures terminally distressed businesses. It is a fixed constant and is not optimised per stock or per period.

**Rationale for using the full price history back to 1995.** The all-time high is a true all-time high, not a rolling 5-year or 10-year high. If the market once paid a price, that price is a legitimate reference for what the market is capable of paying again.

### 5.2 Condition B — Fundamental condition (8-quarter high)

The **most recent quarterly result available to the public as of day t** (the "governing quarter") must show **all three** of the following at the highest value in its trailing **8 quarters**:

- Net Sales at 8-quarter high
- PAT at 8-quarter high
- Diluted EPS at 8-quarter high

**Rationale for requiring all three together.** A single-metric test is easy to satisfy accidentally or through accounting choices. The joint test is a genuine operating-strength filter.

**Rationale for 8 quarters.** Two years spans a full business cycle for most sectors and, critically, contains **two observations of every seasonal quarter**. A company with a strong festive quarter cannot trigger the condition simply because Q3 is always its best quarter — it must beat its *own previous Q3* as well.

> **Change from v1.0.** v1.0 used a relaxed 4-quarter window for Micro Cap, because Micro Cap companies have shorter reported histories. With Micro Cap removed from the universe, that exception no longer applies. **All 500 stocks now use the same 8-quarter window** — one rule, no tier-specific relaxations.

### 5.3 Condition C — Positivity condition

```
Net Sales > 0   AND   PAT > 0   AND   Diluted EPS > 0

         (applied to the GOVERNING QUARTER only)
```

**Rationale.** Without this condition, "PAT at an 8-quarter high" can be satisfied by a company that lost money in all eight quarters and merely lost the *least* money in the most recent one. That is not "strongest operating performance" in any sense the strategy intends to express, and it is not defensible to a client or a reviewer.

**Important — what Condition C does *not* do.** The test is applied to the **governing quarter only**, not to every quarter in the window. A company may have loss-making quarters in its trailing window and still qualify, provided the most recent quarter is both the window high and positive on all three metrics.

This is intentional. A company emerging from a loss-making period into a record profitable quarter is precisely the turnaround the strategy is designed to identify.

> **Worked example — qualifies.** ABFRL, governing quarter Sep-2015. PAT window: −15.7, −70.8, −78.1, −43.5, −42.8, −63.8, −67.9, **+60.7**. Seven consecutive loss quarters followed by a record profitable quarter. The governing quarter is the window high *and* is positive → **accepted**.
>
> **Worked example — rejected.** A company where every quarter in the window is a loss, so the "highest" is simply the smallest loss → **rejected**.

### 5.4 Condition D — Armed state (the one-shot rule)

Each stock carries a binary state, **armed** or **disarmed**.

- Every stock begins **armed**.
- When a recommendation is issued, the stock immediately becomes **disarmed**.
- A disarmed stock **re-arms** only on a day when it makes a **fresh all-time-high closing price**, i.e. `Close(t) ≥ ATH_close(t)`.
- No recommendation can be issued while a stock is disarmed, regardless of how many times Conditions A, B and C are jointly satisfied.

**Rationale.** Without this rule, a stock that stays below the 60% line while continuing to report record quarters would generate a fresh recommendation every single trading day — potentially hundreds on one name. The client would be told to buy the same stock repeatedly on the way down. That is not a strategy; it is averaging into a falling position without a limit.

The one-shot rule enforces the strategy's actual thesis: **one entry per drawdown cycle.** The stock must complete a full round trip — fall 40%, be recommended, and eventually recover all the way to a new all-time high — before it becomes eligible again. A new all-time high is unambiguous evidence that the previous cycle is genuinely over.

**Consequence worth noting.** Because a *rejected* signal does not disarm the stock, a signal blocked by Condition C is deferred rather than deleted — the stock stays armed and fires later, when its fundamentals genuinely turn positive.

### 5.5 Data availability rule (as-of discipline)

```
avail_date = quarter_end_date + 60 calendar days
```

On any day **t**, the engine may only use results whose `avail_date ≤ t`. Results published after day t are invisible to the engine, even though they exist in the database.

**Rationale.** This is the anti-look-ahead control, and it is the single most important integrity rule in the specification. Without it, the backtest would be able to act on a quarter's results *before the market had seen them*, producing performance that could never be achieved in live operation.

**Rationale for 60 days specifically.** SEBI's outer deadline for filing annual audited results is 60 days from the financial-year end. In practice most companies publish quarterly results in 42–45 days. Using 60 days therefore assumes the strategy always acts on the **latest possible** publication date, never the earliest. This makes the backtest **conservative** — a live implementation reading results as they are actually published would enter earlier than the backtest did, not later.

> **Live operation, from 5 September 2026:** the live pipeline uses the **real announcement date** from the NSE event calendar as `avail_date`. The 60-day assumption remains in the historical backtest rows. Measured against real dates it was late a median of 17 days and never early — see `FF_PhaseA_Results.md`.

### 5.6 Combined entry logic

```
FOR each stock s in the 500-name universe, FOR each trading day t:

    ATH = max( Close(s, 1) … Close(s, t) )
    Q   = latest quarterly result of s with avail_date ≤ t

    A = Close(s,t) ≤ 0.60 × ATH
    B = Q.NetSales, Q.PAT and Q.DilutedEPS are each the
        maximum over the trailing 8 quarters ending at Q
    C = Q.NetSales > 0 AND Q.PAT > 0 AND Q.DilutedEPS > 0
    D = state(s) == ARMED

    IF (A AND B AND C AND D):
        ISSUE RECOMMENDATION on stock s, trigger date t
        target(s) = ATH
        state(s)  = DISARMED

    IF Close(s,t) ≥ ATH:
        state(s)  = ARMED
```

---

## 6. Execution

| Parameter | Rule |
|---|---|
| Trigger date | Day **t** on which all conditions are met (evaluated after market close) |
| Entry date | The **next trading day** |
| Entry price | That day's **opening price** |
| Position size | **₹1,00,000** flat per recommendation |
| Position cap | **None** |

**Rationale for entering at the next day's open.** The trigger uses day t's closing price, which is only known after the market has closed. It is therefore impossible to transact on day t. The next trading day's open is the first genuinely executable price. Entering at day t's close would be a look-ahead error.

**Rationale for a flat ₹1,00,000.** The advisory service issues recommendations; it does not manage the client's capital and does not know the client's portfolio size. A flat notional makes every recommendation contribute **equally** to reported performance, so the published track record measures **signal quality** and nothing else. It cannot be inflated by allocating more capital to recommendations that happened to work.

**Rationale for no position cap.** In an advisory service, every signal the rules generate must be communicated. Suppressing a signal because "too many are already open" would require a judgement about the client's capacity — which the advisor does not have and is not licensed to make. The client decides which recommendations to act on; the advisor's obligation is to issue all of them.

> **Capacity disclosure.** Peak concurrent open recommendations reached **83** (on 2 June 2020). Total notional deployed across the full history is **₹3.51 crore**. Clients must be told that the strategy can produce a large number of simultaneously open recommendations, and that they — not the advisor — control position sizing.

---

## 7. Exit Rules

A recommendation is closed on whichever of the following occurs **first**.

### 7.1 Primary exit — Target achieved

```
Target = ATH_close as at the trigger date
       = the identical value used in Condition A

Exit triggered on the first day where:  High(day) ≥ Target
Exit price recorded as:                 Target
```

**Rationale for the target being the old all-time-high close.** This is the direct expression of the investment thesis. The strategy bought because the price was 40% below a level the market had once paid, while fundamentals were at a record. The trade is complete when the price returns to that level. There is no forecast, no valuation model and no discretion involved.

**Rationale for the target being fixed at the trigger date.** The target is locked when the recommendation is issued and never moves, even if the stock subsequently makes a higher high. A moving target would make the exit unfalsifiable and the recommendation unauditable. The client is told the exact rupee target on day one.

**Rationale for detecting on the High but recording the fill at the Target.** If a stock trades through the target during the day, that price was genuinely available to transact at — detecting on the High is realistic. However, recording the exit at the day's high or close would credit the strategy with a *better* price than the target. Recording the fill exactly at the target is the **conservative** treatment.

> **Known cost of this rule — disclosed.** A fixed target caps upside. Of the 157 recommendations that reached their target, **108 (69%) would have been worth more had they simply been held to the 3-year cap** — a median of 45 percentage points more. The rule is retained deliberately: a defined, pre-published exit price is what makes each recommendation auditable and falsifiable, and it is what allows the advisor to tell a client on day one exactly what "done" looks like. That accountability is worth the foregone upside for an advisory product. A different product with a different mandate might reasonably choose otherwise.

### 7.2 Secondary exit — Time cap

```
If the target has not been reached within 1,095 calendar days
(3 years) of the entry date, the position is exited at the
closing price of the last trading day on or before day 1,095.
```

**Rationale for a time cap at all.** Without one, a failed recommendation would remain open indefinitely, and the performance record would consist only of trades that eventually worked. The time cap forces every recommendation to **resolve and be counted**. It is a truth-in-reporting mechanism as much as a risk control.

**Rationale for 3 years.** The strategy is explicitly deep value, and re-rating takes time. Among recommendations that reached their target, the **median holding period was 523 days** (about 17 months) and 35 of 157 took longer than two years. A 1-year or 2-year cap would truncate a meaningful number of trades that were still working.

> **Tested.** Caps of 2, 2.5, 4 and 5 years were formally tested (14.8). A 2-year cap produces a higher XIRR; it was rejected because it beats 3 years in only 5 of 10 cohorts, cuts the completion rate to 43.3%, and its 160 time-stopped positions carry a *median return of +12.7%* — they were cut off working, not failing. A 4–5 year cap is XIRR-neutral and was rejected on capital efficiency. **3 years is not the best-performing value and is retained deliberately.**

### 7.3 No stop-loss

**The strategy has no stop-loss.** A recommendation is never exited because the price fell further.

**Rationale.** The entry condition *is* a 40% decline. The strategy is deliberately buying weakness. A stop-loss would exit precisely the situation the strategy was designed to enter, and would convert a value strategy into an incoherent hybrid. Risk is controlled at the **portfolio level** — through position sizing and diversification across many independent recommendations — not at the individual-trade level.

> **Risk disclosure.** The absence of a stop-loss means an individual recommendation can lose a very large proportion of its value. In the reference set the worst outcome was **JPPOWER at −82.9%**, and **11 of 275 resolved recommendations (4.0%) lost more than 50%**. Every client must acknowledge this before subscribing.

### 7.4 Open positions

A recommendation whose target has not been hit and whose 1,095-day cap has not yet expired remains **open**. In performance reporting these are marked to the last available closing price and labelled as unrealised. In the reference set, **76 of 351 recommendations** were still open at the analysis cut-off of 27 July 2026.

---

## 8. Operating Procedure (Daily SOP)

The following is the complete day-to-day process. It requires no judgement at any step.

**Step 1 — After market close (T+0).** Download the NSE bhavcopy. Append to the price database. Apply any corporate-action adjustment (split or bonus) effective that day to the full historical series for the affected stock.

**Step 2 — Update fundamentals as results are published.** Record Net Sales, PAT and Diluted EPS against the quarter-end date. Set `avail_date = quarter_end + 60 days`. Do not backfill or restate prior quarters except to correct a demonstrable data error, which must be logged.

**Step 3 — Evaluate exits, before evaluating entries.** For every open recommendation:
- If today's High ≥ Target → close at Target. Issue an **exit advice**.
- Else if today is on or after entry_date + 1,095 days → close at today's Close. Issue an **exit advice**.
- Else → the recommendation remains open. No communication required.

**Step 4 — Evaluate entries.** Run the Section 5.6 logic across all 500 stocks using data as of today's close.

**Step 5 — Issue recommendations, before market open on T+1.** For each new recommendation, communicate:
- Stock name and symbol
- Trigger date (T+0) and instruction to enter at the T+1 opening price
- The exact rupee **target price**
- The exact **time-cap expiry date** (entry date + 1,095 days)
- The governing quarter and its Net Sales / PAT / EPS figures, with the window they are a high against
- Standard risk disclosure (no stop-loss; possibility of large loss)

**Step 6 — Update state.** Set every newly recommended stock to **disarmed**. Set every stock that closed at a new all-time high today to **armed**.

**Step 7 — Log.** Record the day's evaluation output in an immutable, timestamped log. This log is the audit trail demonstrating that recommendations were generated by the rules and not by discretion, and must be retained per SEBI record-keeping requirements.

### Prohibited actions

The following are **not permitted** and would invalidate the strategy's compliance position:

- Overriding, delaying or suppressing any recommendation the rules generate
- Adding a recommendation the rules did not generate
- Changing a target price after issuance
- Exiting early because of price weakness, news flow or opinion
- Extending a recommendation beyond the 1,095-day cap
- Altering any parameter without a formal version change and full republication of the track record

---

## 9. Performance Measurement

### 9.1 Return metric — XIRR

Advisory performance is measured by **XIRR** (money-weighted internal rate of return over irregularly dated cash flows). Each recommendation contributes two cash flows:

```
(entry_date, −100,000)
(exit_date,  +100,000 × exit_price / entry_price)
```

**Rationale for XIRR rather than CAGR.** CAGR requires a single starting capital amount and a single ending amount over one continuous period. The advisory service has neither — capital is committed on 351 different dates and returned on 351 different dates. XIRR is the mathematically correct metric for irregularly timed cash flows.

**Rationale for why capital recycling is irrelevant.** XIRR annualises each rupee over the exact period that rupee was actually at risk. Whether the client funds each new recommendation from fresh savings or from the proceeds of a closed recommendation does not change any cash-flow date or amount, and therefore does not change XIRR.

> **This figure must never be presented as, or alongside, a portfolio CAGR.** The Model Portfolio document uses CAGR because that product does have a single Day-One capital base. Conflating the two is a material misrepresentation.

### 9.2 Benchmark — matched-timing index XIRR

```
(entry_date, −100,000)
(exit_date,  +100,000 × Index_close(exit) / Index_close(entry))
```

**Rationale.** A simple index CAGR over the same calendar span is not a valid comparison, because the strategy did not hold capital continuously — it held different amounts at different times. The matched-timing construction answers the only question that matters: *had the client put the same money in the index on the same days, what would they have earned?* Any difference is attributable to stock selection alone.

**The benchmark must match the universe.** The primary benchmark is the **Nifty 500**, because the universe *is* the Nifty 500. Using a narrower index (Nifty 50) would flatter the strategy by comparing a broad-cap book against a large-cap-only index.

### 9.3 Supplementary disclosures

Every performance presentation must also state: number of recommendations, win rate, average and median return, average and median holding period, the split of exit reasons, the count and treatment of open positions, and the worst single outcome.

---

## 10. Reference Backtest Results

**Period:** 31 May 2012 – 23 July 2026 (analysis cut-off 27 July 2026)
**Recommendations:** 351 across 270 distinct companies
**Notional per recommendation:** ₹1,00,000

### 10.1 Headline

| Metric | Value |
|---|---|
| Total recommendations | 351 |
| Resolved (target or time cap) | 275 |
| Still open at cut-off | 76 |
| Win rate (all) | 76.1% |
| Win rate (resolved only) | 79.3% |
| Average return | +57.9% |
| Median return | +66.3% |
| Average holding period | 670 days |
| Median holding period | 645 days |
| **Strategy XIRR** | **33.49%** |
| **Nifty 500 (matched timing)** | **18.00%** |
| **Excess** | **+15.49 pp** |

### 10.2 Exit reasons

| Reason | Count | Share |
|---|---|---|
| Target achieved | 157 | 44.7% |
| Time cap (1,095 days) | 118 | 33.6% |
| Still open | 76 | 21.7% |

Of the 275 **resolved** recommendations, **57.1% reached their target**. Among the 157 target hits: median 523 days; 54 within 1 year, 68 in years 1–2, 35 in years 2–3.

### 10.3 Versus matched-timing benchmarks

| Benchmark | Matched XIRR | Strategy excess |
|---|---|---|
| **Nifty 500 (primary)** | **18.00%** | **+15.49 pp** |
| Nifty 50 | 15.90% | +17.59 pp |
| Nifty 100 | 16.71% | +16.78 pp |
| Nifty 200 | 17.28% | +16.21 pp |
| Nifty Total Market | 18.28% | +15.21 pp |
| Nifty Smallcap 250 | 25.24% | +8.25 pp |

The Nifty 500 is the correct primary benchmark because it *is* the universe. Nifty Smallcap 250 is shown because 192 of 351 recommendations are Small Cap; the strategy clears even that harder bar.

### 10.4 By market-cap tier

| Tier | N | Win % | Avg return | Median return | XIRR |
|---|---|---|---|---|---|
| Large Cap | 59 | 76.3% | +48.2% | +68.7% | 23.7% |
| Mid Cap | 100 | 75.0% | +46.5% | +61.3% | 30.6% |
| Small Cap | 192 | 76.6% | +66.8% | +66.1% | 38.8% |

### 10.5 By entry year (Table A — the strategy as it now stands)

**Universe: Nifty 500 · Benchmark: Nifty 500 · every row a valid like-for-like comparison**

| Year | N | Win % | Avg ret | Median | Avg hold | Target | Time cap | Open | XIRR | Nifty 500 | Excess |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2012 | 34 | 67.6% | 75.6% | 83.5% | 900 | 15 | 19 | 0 | 28.4% | 19.9% | +8.5 |
| 2013 | 33 | 87.9% | 113.4% | 81.6% | 740 | 19 | 14 | 0 | 49.4% | 19.7% | +29.7 |
| 2014 | 15 | 80.0% | 72.5% | 39.6% | 948 | 6 | 9 | 0 | 24.9% | 13.2% | +11.7 |
| 2015 | 11 | 90.9% | 88.4% | 69.5% | 1005 | 3 | 8 | 0 | 26.2% | 11.3% | +15.0 |
| 2016 | 16 | 75.0% | 68.9% | 70.8% | 677 | 10 | 6 | 0 | 48.4% | 17.6% | +30.8 |
| 2017 | 8 | 50.0% | 25.9% | 27.9% | 705 | 4 | 4 | 0 | 18.7% | 4.0% | +14.7 |
| **2018** | **28** | **53.6%** | **18.0%** | **8.0%** | **930** | **9** | **19** | **0** | **7.4%** | **13.4%** | **−6.0** |
| 2019 | 32 | 65.6% | 37.9% | 66.2% | 777 | 19 | 13 | 0 | 18.8% | 16.2% | +2.5 |
| 2020 | 35 | 97.1% | 111.9% | 77.0% | 576 | 28 | 7 | 0 | 75.7% | 40.3% | +35.4 |
| 2021 | 8 | 100.0% | 84.1% | 79.5% | 853 | 5 | 3 | 0 | 32.4% | 16.7% | +15.7 |
| 2022 | 33 | 90.9% | 66.2% | 68.9% | 648 | 25 | 8 | 0 | 36.9% | 19.7% | +17.2 |
| 2023 | 18 | 88.9% | 59.4% | 68.2% | 765 | 8 | 8 | 2 | 30.8% | 18.6% | +12.1 |
| 2024 | 9 | 66.7% | 20.9% | 18.7% | 672 | 2 | 0 | 7 | 11.7% | 4.4% | +7.3 |
| 2025 | 37 | 62.2% | 10.6% | 8.8% | 425 | 3 | 0 | 34 | 9.4% | 7.5% | +1.9 |
| 2026 | 34 | 70.6% | 14.7% | 8.8% | 95 | 1 | 0 | 33 | 67.2% | 11.3% | +55.8 |
| **All** | **351** | **76.1%** | **57.9%** | **66.3%** | **670** | **157** | **118** | **76** | **33.49%** | **18.00%** | **+15.49** |

**14 of 15 cohorts beat the Nifty 500.** The single exception is 2018.

> **How to read the 2024–2026 rows.** These cohorts are dominated by open positions that have not had time to reach their targets. Their returns and XIRR figures are **not comparable** to earlier, fully resolved years. The 2026 XIRR of 67.2% is an artefact of very short elapsed holding periods (average 95 days) and must never be quoted in isolation.

### 10.6 The one losing cohort — 2018

| | Strategy | Nifty 500 |
|---|---|---|
| 2018 cohort XIRR | **7.4%** | **13.4%** |

28 recommendations, 53.6% win rate, and the lowest completion rate in the table — only 9 of 28 reached their target against 19 that expired at the 3-year cap.

**What this teaches.** The strategy buys stocks already down 40%. When entries are made shortly before a broad, extended decline in the mid- and small-cap segment, the recovery does not arrive within the 3-year window and positions close at the cap instead of the target. The strategy is not immune to buying too early into a falling market.

**This row must be presented first, not buried.** Any reviewer who has read a backtest before will look for the losing year, and a presentation with no losing year reads as fitted.

### 10.7 Table B — the same rules run on the full Total Market universe (751 names)

**Universe: Nifty 500 + Nifty Microcap 250 · Benchmark: Nifty Total Market**

This is the v1.0 configuration, retained for comparison. It is **not** the strategy as specified.

| Year | N | Win % | Median | Target | Time cap | Open | XIRR | Total Market | Excess |
|---|---|---|---|---|---|---|---|---|---|
| 2011 | 23 | 69.6% | 20.5% | 6 | 17 | 0 | 14.4% | 11.9% | +2.5 |
| 2012 | 55 | 74.5% | 83.3% | 26 | 29 | 0 | 52.1% | 19.5% | +32.6 |
| 2013 | 48 | 85.4% | 75.5% | 22 | 26 | 0 | 43.3% | 18.7% | +24.7 |
| 2014 | 21 | 81.0% | 39.6% | 8 | 13 | 0 | 23.4% | 14.4% | +9.0 |
| 2015 | 17 | 88.2% | 67.9% | 7 | 10 | 0 | 31.2% | 11.5% | +19.7 |
| 2016 | 29 | 58.6% | 59.5% | 13 | 16 | 0 | 22.0% | 15.5% | +6.5 |
| 2017 | 12 | 50.0% | 0.6% | 5 | 7 | 0 | 10.2% | 2.7% | +7.5 |
| 2018 | 51 | 54.9% | 8.7% | 17 | 34 | 0 | 6.7% | 12.3% | −5.6 |
| 2019 | 53 | 71.7% | 66.6% | 32 | 21 | 0 | 23.1% | 16.0% | +7.1 |
| 2020 | 49 | 95.9% | 77.0% | 38 | 11 | 0 | 74.2% | 39.5% | +34.7 |
| 2021 | 16 | 93.8% | 77.6% | 11 | 5 | 0 | 37.3% | 17.2% | +20.1 |
| 2022 | 55 | 85.5% | 68.9% | 42 | 13 | 0 | 38.0% | 19.7% | +18.3 |
| 2023 | 29 | 89.7% | 68.4% | 14 | 11 | 4 | 33.8% | 19.1% | +14.7 |
| 2024 | 16 | 62.5% | 17.9% | 4 | 0 | 12 | 14.1% | 4.8% | +9.4 |
| 2025 | 76 | 55.3% | 6.7% | 12 | 0 | 64 | 11.8% | 7.4% | +4.4 |
| 2026 | 64 | 73.4% | 10.6% | 2 | 0 | 62 | 68.9% | 12.3% | +56.5 |
| **All** | **614** | **73.8%** | **56.4%** | **259** | **213** | **142** | **34.86%** | **16.59%** | **+18.27** |

The headline XIRR looks *higher* than Table A (34.86% vs 33.49%). Section 11 explains why this is misleading.

### 10.8 Table C — Micro Cap alone

**Universe: Nifty Microcap 250 · Benchmark: Nifty Microcap 250 (index begins 25 Jul 2013)**

| Year | N | Win % | Median | Target | Time cap | Open | XIRR | Microcap 250 | Excess |
|---|---|---|---|---|---|---|---|---|---|
| 2011 | 23 | 69.6% | 20.5% | 6 | 17 | 0 | 14.4% | *index n/a* | — |
| 2012 | 21 | 85.7% | 77.7% | 11 | 10 | 0 | 93.8% | *index n/a* | — |
| 2013 | 15 | 80.0% | 65.2% | 3 | 12 | 0 | 32.3% | *index n/a* | — |
| 2014 | 6 | 83.3% | 43.0% | 2 | 4 | 0 | 17.0% | 43.8% | **−26.8** |
| 2015 | 6 | 83.3% | 66.7% | 4 | 2 | 0 | 45.1% | 23.2% | +21.9 |
| 2016 | 13 | 38.5% | −30.2% | 3 | 10 | 0 | **−2.2%** | 10.0% | **−12.3** |
| 2017 | 4 | 50.0% | −22.5% | 1 | 3 | 0 | 1.0% | −12.5% | +13.5 |
| 2018 | 23 | 56.5% | 8.7% | 8 | 15 | 0 | 5.7% | 5.8% | **−0.1** |
| 2019 | 21 | 81.0% | 68.3% | 13 | 8 | 0 | 28.8% | 26.2% | +2.6 |
| 2020 | 14 | 92.9% | 76.5% | 10 | 4 | 0 | 68.8% | 83.8% | **−15.0** |
| 2021 | 8 | 87.5% | 77.0% | 6 | 2 | 0 | 44.0% | 45.7% | **−1.7** |
| 2022 | 22 | 77.3% | 68.8% | 17 | 5 | 0 | 39.8% | 41.0% | **−1.2** |
| 2023 | 11 | 90.9% | 68.4% | 6 | 3 | 2 | 39.4% | 37.1% | +2.3 |
| 2024 | 7 | 57.1% | 17.1% | 2 | 0 | 5 | 18.4% | 7.1% | +11.4 |
| 2025 | 39 | 48.7% | −2.0% | 9 | 0 | 30 | 14.8% | 14.1% | +0.7 |
| 2026 | 30 | 76.7% | 13.8% | 1 | 0 | 29 | 70.7% | 53.1% | +17.5 |

> **The ALL row is deliberately omitted.** The 263-trade Micro Cap XIRR of 36.35% has **no valid benchmark partner**, because the Microcap 250 index does not exist before 25 July 2013 while the first Micro Cap recommendation is dated 31 May 2011. Comparing 36.35% to any Microcap 250 figure would compare two different trade sets. The only valid pair is the 209 recommendations entered on or after 25 July 2013:
>
> **Strategy 24.16% · Nifty Microcap 250 27.71% · excess −3.55 pp**

### 10.9 Distribution of outcomes (275 resolved recommendations)

| Percentile | Return |
|---|---|
| 5th | −45.6% |
| 10th | −32.7% |
| 25th | +15.8% |
| **50th (median)** | **+69.0%** |
| 75th | +86.9% |
| 90th | +168.1% |
| 95th | +238.1% |

Best: OLECTRA **+565.3%**. Worst: JPPOWER **−82.9%**.
Recommendations losing more than 50%: **11 (4.0%)**. Gaining more than 100%: **54 (19.6%)**.

### 10.10 Concentration of profit

Realised P&L was **₹1.96 crore on ₹2.75 crore deployed** across 275 resolved recommendations.

| Cohort | Share of realised profit |
|---|---|
| 2020 | 20.0% |
| 2013 | 19.1% |
| 2012 | 13.1% |
| 2022 | 11.1% |
| 2019 | 6.2% |
| All others | 30.5% |

**Five cohorts produced roughly 70% of all profit.** This is normal for a deep-value strategy and must be disclosed. Results are lumpy, arrive in clusters tied to market cycles, and a client who subscribes for two flat years may see very little before the next cluster.

---

## 11. Micro Cap — Why It Is Excluded

### 11.1 The finding

An earlier draft compared Micro Cap recommendations against the **Nifty 500**, which was wrong: the Nifty 500 contains no micro caps at all. When each segment is measured against the index that actually represents it, the conclusion reverses.

On the 209 Micro Cap recommendations entered on or after 25 July 2013 (the first date the Nifty Microcap 250 index exists):

| Benchmark used | Benchmark XIRR | Apparent excess |
|---|---|---|
| Nifty 50 | 12.80% | +11.36 pp |
| Nifty 500 | 14.70% | +9.46 pp |
| Nifty Total Market | 14.94% | +9.22 pp |
| Nifty Smallcap 250 | 20.36% | +3.80 pp |
| **Nifty Microcap 250 (correct)** | **27.71%** | **−3.55 pp** |

The Nifty Microcap 250 compounded at **24.61% a year** from July 2013 to July 2026, against the Nifty 500's 13.35%. Micro caps as a segment were exceptional in this period. **The strategy did not beat that segment — it lagged it.**

### 11.2 Why the earlier number looked good

Two effects pushed the same way:

**Benchmark mismatch.** Comparing micro caps to the Nifty 500 credits the strategy with roughly 13 percentage points of segment beta that any micro-cap index fund would also have delivered.

**Period mismatch.** Micro Cap's full-period XIRR of 36.35% rests on the 2011–mid-2013 cohorts, which the Microcap 250 index cannot benchmark. Dropping those 54 recommendations takes the strategy figure from **36.35% to 24.16%** — a 12.19 point fall. In particular, the 2012 Micro Cap cohort's 93.8% XIRR is driven by a single position (MARKSANS, +1,709%); excluding that one trade takes the cohort to 69.2%.

### 11.3 Every quality metric is worse

Measured over the common window (entries from 25 July 2013):

| Metric | Nifty 500 tier | Micro Cap |
|---|---|---|
| Strategy XIRR | 36.14% | 24.16% |
| Own benchmark | 17.42% | 27.71% |
| **Excess vs own benchmark** | **+18.72 pp** | **−3.55 pp** |
| Cohorts beating own benchmark | 14 of 15 | **8 of 14** |
| Median return (full set) | +66.3% | +40.8% |
| Thesis completion (target hit, of resolved) | 57.1% | 51.8% |
| Recommendations losing >50% | 4.0% | **7.1%** |
| Worst single outcome | −82.9% | **−91.4%** |

Micro Cap also shows a **negative cohort** — 2016, at −2.2% XIRR with a median return of −30.2%. No Nifty 500 tier cohort is negative.

A further tell is the relationship between average and median. In the Nifty 500 tier the average return (57.9%) is *below* the median (66.3%), meaning returns are broad-based. In Micro Cap the average (54.9%) is *above* the median (40.8%), meaning a handful of extreme winners carry the segment while the typical position does much less.

### 11.4 A cleaner cross-check

Restricting all segments to entries from 14 January 2019 — the window where every tier index exists — and benchmarking each recommendation against **its own tier's index**:

| Segment | n | Strategy | Tier-matched benchmark | Excess |
|---|---|---|---|---|
| Nifty 500 tier | 206 | 37.23% | 29.56% | **+7.67 pp** |
| Micro Cap | 152 | 36.59% | 37.95% | **−1.36 pp** |

The same conclusion holds under a completely different construction and a different time window.

### 11.5 The decision

**Micro Cap is removed from the Continuous Recommendation universe.** The reasoning is not that micro caps performed badly — they performed extremely well as a segment. It is that **this particular rule set added nothing on top of that segment**, while adding materially more single-name risk, worse liquidity, and a lower completion rate.

For an advisory product where a client acts on each individual recommendation, that combination is not defensible. If a client wants micro-cap exposure, the honest advice supported by this evidence is to buy the Nifty Microcap 250 index rather than to follow stock-level recommendations that lagged it.

### 11.6 Where Micro Cap *would* be appropriate

The exclusion is specific to this product. The data does suggest conditions under which micro caps could be used sensibly — but each is a different product with a different mandate, not a variation of this one.

**Micro Cap's actual return profile in this rule set is venture-like, not advisory-like.** 21.8% of resolved Micro Cap recommendations returned more than +100%, while 7.1% lost more than half. The mean sits far above the median. Returns come from a small number of extreme outcomes, not from a reliable central tendency. Any product built on it must be structured for that shape.

That points to four conditions:

**1. A wide, index-like allocation rather than individual recommendations.** With a 51.8% completion rate and fat tails in both directions, the outcome of any single position is close to unpredictable. A portfolio holding many micro-cap names can harvest the segment; a client acting on five recommendations cannot. If the goal is simply micro-cap exposure, an index fund tracking the Nifty Microcap 250 is the more rational vehicle — it beat this rule set.

**2. A small satellite allocation with explicit high-risk framing.** A −91.4% single-name outcome is inside the normal range of this segment. Micro caps belong in a sleeve sized so that such an outcome is survivable — never in a core allocation, and never in a product where each recommendation carries the advisor's name individually.

**3. A different exit discipline — no fixed target.** The fixed all-time-high target caps upside. Of the 102 Micro Cap recommendations that hit their target, 69% would have been worth more had they simply been held to the 3-year cap — a median of 49 percentage points more, and a *mean* of 263 percentage points more. (The same rule caps the Nifty 500 tier too, at the same 69% frequency, but the foregone amount is far smaller: a mean of 170 points.) Because micro-cap upside is fatter-tailed, a trailing exit or a "let winners run" rule would suit that segment considerably better than a pre-set price target. **That is a genuinely different strategy, and it would need its own specification and its own backtest — nothing here validates it.**

**4. A longer horizon than three years.** Micro Cap's completion rate is lower and its 2016 cohort was outright negative over the 3-year window. A structure without a hard time cap — or with a five-year one — would give the thesis room that a 3-year cap does not.

**What Micro Cap is not suitable for is precisely this product**: a continuous stream of individually-issued, individually-accountable recommendations, each with a published target price and a defined completion criterion. That format demands a reliable central outcome, and Micro Cap in this rule set does not have one.

---

## 12. Known Limitations (Mandatory Disclosures)

These must appear in every client-facing document and presentation.

**1. Survivorship bias.** The 500-name universe is today's index membership applied backwards. Companies delisted, merged or failed during the period are absent. This biases reported performance **upward** by an amount that has not been quantified. This is the most significant known limitation.

**2. Backtested, not live.** All results in Section 10 are simulated on historical data. No client capital was deployed. Past performance does not indicate future results.

**3. Open positions.** 76 of 351 recommendations (22%) are unresolved and marked to market. Their final outcomes are unknown and could be materially different.

**4. No transaction costs.** Brokerage, STT, exchange charges, GST, stamp duty and slippage are **not** deducted. Actual client returns will be lower.

**5. No dividends.** Dividends received during holding periods are excluded, which understates returns. This partially offsets item 4.

**6. Segment beta versus stock selection.** A meaningful share of the headline excess return reflects the strong performance of the mid- and small-cap segments over this period, not stock selection alone. The tier-matched cross-check in Section 11.4 shows the Nifty 500 tier's excess narrowing from +18.72 pp to +7.67 pp when each recommendation is measured against its own tier's index. Both figures should be presented.

**7. Fundamental data dependency.** The strategy depends on the accuracy of third-party fundamental data (Prowess, Screener). Restatements, reclassifications or vendor errors would change historical signals.

**8. Reporting-lag assumption.** The flat 60-day availability assumption is applied uniformly. Actual publication dates vary by company and quarter. The assumption is conservative but not exact.

**9. Concentration and capacity.** Up to 83 recommendations may be open simultaneously. Clients acting on all of them require substantial capital and will hold a large number of positions.

**10. No stop-loss.** Individual recommendations can and do lose more than 80% of their value.

**11. Upside is capped by design.** 69% of target-hit recommendations would have been worth more if simply held to the 3-year cap. This is an accepted cost of a pre-published, auditable exit.

**12. Lumpy results.** Five entry cohorts produced roughly 70% of realised profit. Clients may experience extended flat periods.

---

## 13. Frozen Parameters and Change Control

| Parameter | Value |
|---|---|
| Universe | Nifty 500 — 500 fixed names |
| Drawdown threshold | 0.60 × all-time-high close |
| ATH basis | Closing price, full history from 1995 |
| Fundamental window | 8 quarters (all tiers) |
| Fundamental metrics | Net Sales, PAT, Diluted EPS |
| Positivity requirement | All three > 0 in the governing quarter |
| Positivity scope | Governing quarter only, not the full window |
| Data availability lag | Quarter end + 60 calendar days |
| Re-arm trigger | Fresh all-time-high close |
| Entry execution | Next trading day's open |
| Position size | ₹1,00,000 flat |
| Position cap | None |
| Exit target | All-time-high close as at trigger date (fixed) |
| Time cap | 1,095 calendar days |
| Stop-loss | None |
| Price adjustment | Splits and bonuses only |
| Primary benchmark | Nifty 500, matched timing |

**Changing any one of these creates a different strategy** and requires a new version number, a full historical re-run, and republication of the entire track record.

**These parameters have been tested for robustness.** Section 14 documents six formal tests run against the specification — three on entry, three on exit. None produced a change. Every parameter above survived challenge on evidence, not on assertion.

### Version history

| Version | Date | Change |
|---|---|---|
| 1.0 | 26 Aug 2026 | Initial frozen specification. Close-based ATH confirmed for both entry threshold and exit target. Positivity condition added. Universe 751 names including Micro Cap. Reference set: 614 recommendations. |
| **2.0** | **26 Aug 2026** | **Micro Cap removed from the universe** following correct-benchmark analysis (Section 11). Universe reduced to the 500 Nifty 500 constituents. Micro Cap's 4-quarter fundamental window retired; all tiers now use 8 quarters. Primary benchmark set to Nifty 500. Reference set: 351 recommendations. Added Section 11 (Micro Cap exclusion rationale and where micro caps would be appropriate), the upside-cap disclosure in Section 7.1, and limitations 6, 11 and 12. |
| 2.0 | 26 Aug 2026 | **Section 14 added — Robustness and Research Testing.** Six formal tests run against the frozen specification (three entry, three exit). No rule changed. Documented: the fundamental filter's true mechanism is entry timing rather than stock selection; 0.60 is not the optimal threshold; the edge is insensitive to entry timing across a 60-day band; a partial-exit variant's apparent gain does not survive outlier removal; a fundamental-deterioration exit fails structurally; and a 2-year time cap outperforms on XIRR but fails cohort consistency. **No change to Section 13 parameters.** |

---

## 14. Robustness and Research Testing

### 14.1 Purpose and standard of proof

Six formal tests were run against the frozen specification — three challenging the entry rules, three challenging the exit rule. **None produced a change to the specification.** This section records what was tested, what was found, and why each rule was retained.

Every test was specified **before** it was run. Results are reported whether favourable or not, including one test where an apparently large improvement did not survive scrutiny.

**The standard applied.** A variant was only considered for adoption if it improved the aggregate XIRR **and** was consistent across entry-year cohorts **and** survived removal of its largest contributing trades. With 275 resolved recommendations, any single-criterion improvement is within the range that random variation can produce. A rule change on aggregate XIRR alone would be curve-fitting.

### 14.2 Summary of the six tests

| # | Test | Question | Result | Outcome |
|---|---|---|---|---|
| 1 | Ablation | Does the fundamental filter earn its place? | Yes — +3.91 pp XIRR, +5.96 pp excess. Mechanism is entry timing, not stock selection. | **Filter retained** |
| 2 | Threshold sweep | Is 0.60 an optimised peak? | No. Smooth monotonic gradient across 0.50–0.70; **0.60 is not the optimum.** | **0.60 retained** |
| 3 | Availability lag | Is the edge sensitive to entry timing? | No. XIRR stays in a 1.5 pp band across a 60-day swing (30–90 days). | **60 days retained** |
| 4 | Partial exit | Would trailing half the position beat a full exit at target? | Headline +5.96 pp, but **collapses to +2.00 pp on removing one trade** and +1.01 pp on removing ten. Consistent in only 8 of 15 cohorts. | **Not adopted** |
| 5 | Fundamental-break exit | Should a position exit when fundamentals deteriorate? | No. Every variant is materially worse — XIRR 23.4–27.7% against 33.49%. | **Rejected** |
| 6 | Time cap length | Would 2, 2.5, 4 or 5 years beat 3? | A 2-year cap raises XIRR by ~3.5 pp and the gain **survives outlier removal**. But it beats 3 years in only **5 of 10 cohorts** and cuts the completion rate to 43.3%. 4–5 years is XIRR-neutral but far more capital-hungry. | **3 years retained** |

### 14.3 Test 1 — Ablation: does the fundamental filter earn its place?

**Method.** The full rule was compared against a **price-only** variant: `Close ≤ 0.60 × ATH_close` with the same one-shot re-arm logic and the same exit rules, but with the fundamental conditions (B and C) removed entirely.

| | N | Win | Median | Avg | Hit rate | Hold | XIRR | Nifty 500 | Excess |
|---|---|---|---|---|---|---|---|---|---|
| **Full rule** | 351 | 76.1% | 66.3% | 57.9% | 57.1% | 669 | **33.49%** | 18.00% | **+15.49 pp** |
| Price only | 748 | 78.7% | 65.6% | 39.9% | 73.6% | 568 | 29.58% | 20.05% | +9.53 pp |

**Finding 1 — the filter adds value in aggregate.** +3.91 pp of XIRR and +5.96 pp of benchmark-relative excess.

**Finding 2 — the mechanism is not what was assumed.** The filter does not remove poor-quality signals. Only **99 of the 351 full-rule trades appear in the price-only set at all** — the two rules largely select *different entry dates on the same stocks*.

The reason is the interaction with the one-shot rule (5.4). The price-only variant fires on the **first** day a stock crosses below the 60% line. Under the full rule the fundamental condition is usually not yet satisfied on that day, so the stock stays armed and fires **later and deeper** in the drawdown.

| | Entry price ÷ ATH (median) | Share entering above 0.58 | p90 discount to target |
|---|---|---|---|
| Price only | 0.591 | 75% | 43.9% |
| **Full rule** | **0.560** | 38% | **74.2%** |

Decomposing the two sets:

| Group | n | XIRR | Median | Hit rate | Hold |
|---|---|---|---|---|---|
| Both rules chose the same day | 99 | 31.14% | 49.5% | 68.6% | 562 |
| **Only the full rule took (it waited)** | **252** | **33.66%** | 66.6% | 53.2% | 711 |
| Only price-only took (full rule skipped) | 649 | 29.43% | 65.8% | 74.3% | 569 |

The 649 signals the filter declined were **not bad trades** — they returned 29.43% XIRR and beat the Nifty 500 by 9.59 pp on their own. The filter is not discarding losers; it is **replacing shallow entries with deeper ones**.

**Finding 3 — cohort consistency is weak.** Compared year by year, the full rule beats price-only in only **6 of 15 cohorts**. The aggregate advantage is concentrated in four years (2012, 2016, 2022, 2026). Note that per-year comparison is unreliable here because signal counts differ sharply between the variants (2014: 15 vs 5; 2012: 34 vs 7).

**Conclusion — the filter is retained, on three grounds:**

1. It improves aggregate XIRR and benchmark-relative excess.
2. It makes the product **actionable**. 748 recommendations over the period — more than double the current count, and up to 130 in a single year — is not a set any client can realistically act on. Selectivity has standalone product value independent of return.
3. It moves entries materially deeper into the drawdown, which is the strategy's stated intent.

**What this requires the presentation to say.** The claim that the strategy "selects companies with record fundamentals" is accurate, but the edge does **not** arise from picking better companies. It arises because the fundamental condition makes the strategy **wait for a deeper entry point**. Any client-facing material must describe the mechanism this way. A reviewer who runs this ablation independently will reach the same conclusion, and it is better for the document to have stated it first.

### 14.4 Test 2 — Threshold: is 0.60 an optimised peak?

**Method.** The complete rule was re-run at drawdown thresholds of 0.50, 0.55, 0.60, 0.65 and 0.70.

| Threshold | N | Median | Hit rate | Hold | XIRR | Nifty 500 | Excess | Cohorts beating index |
|---|---|---|---|---|---|---|---|---|
| 0.50 | 211 | 77.5% | 46.0% | 750 | **35.42%** | 17.82% | +17.60 | 14/15 |
| 0.55 | 285 | 76.4% | 52.7% | 695 | 34.43% | 18.04% | +16.39 | 13/15 |
| **0.60 (current)** | **351** | **66.3%** | **57.1%** | **669** | **33.49%** | **18.00%** | **+15.49** | **14/15** |
| 0.65 | 448 | 54.2% | 63.9% | 616 | 33.05% | 17.62% | +15.43 | 13/15 |
| 0.70 | 552 | 43.3% | 67.7% | 585 | 31.52% | 17.07% | +14.45 | 12/15 |

**Finding — there is no peak.** XIRR declines smoothly and monotonically as the threshold loosens. There is no cliff, no local maximum, and no evidence of a fitted parameter.

**0.60 is demonstrably not the optimum.** A tighter threshold of 0.50 produces a higher XIRR (35.42%) and a higher excess (+17.60 pp). The specification does not use it.

**Why 0.60 is retained rather than 0.50.** The gradient reflects a genuine trade-off, not free performance:

- Signal count falls from 351 to **211** — a 40% reduction in the service's output.
- The thesis-completion rate falls from 57.1% to **46.0%** — fewer than half of all recommendations would reach their published target.
- Median holding period rises to 750 days.

For an advisory product in which every recommendation carries a **published target price and a defined completion criterion**, a completion rate below 50% is a materially worse client proposition than the 3.7 pp of additional annualised return is worth. 0.60 is retained on product grounds, with the performance cost accepted and disclosed here.

**Compliance significance.** This test converts the most obviously arbitrary constant in the specification from an assertion into a documented finding: the parameter space was examined, the response surface is smooth, and the value in use is **not** the best-performing one.

### 14.5 Test 3 — Availability lag: is the edge timing-fragile?

**Method.** The availability assumption (5.5) was varied from 30 to 90 days from quarter-end, shifting every entry in the backtest earlier or later.

| Lag | N | Win | Median | Hit rate | XIRR | Nifty 500 | Excess | Cohorts beating index |
|---|---|---|---|---|---|---|---|---|
| 30 days | 349 | 74.8% | 66.8% | 58.7% | 33.86% | 17.17% | +16.69 | 14/15 |
| 45 days | 347 | 75.8% | 66.4% | 57.7% | 32.76% | 17.80% | +14.95 | 14/15 |
| **60 days (current)** | **351** | **76.1%** | **66.3%** | **57.1%** | **33.49%** | **18.00%** | **+15.49** | **14/15** |
| 75 days | 353 | 74.2% | 66.5% | 56.9% | 32.83% | 17.38% | +15.45 | 14/15 |
| 90 days | 356 | 75.8% | 63.6% | 56.2% | 32.38% | 17.66% | +14.73 | 13/15 |

**Finding — the edge is not timing-fragile.** A 60-day swing in entry timing moves XIRR within a band of **1.5 percentage points** (32.38%–33.86%). Excess return stays between +14.73 and +16.69 pp. Cohort consistency is 13–14 of 15 throughout.

A combined stress test across both parameters confirms the same picture — nine combinations, all within a 2.3 pp band:

| | lag 45 | lag 60 | lag 75 |
|---|---|---|---|
| threshold 0.55 | 34.92% | 34.43% | 34.17% |
| **threshold 0.60** | 32.76% | **33.49%** | 32.83% |
| threshold 0.65 | 32.61% | 33.05% | 32.86% |

**Why this matters.** If the edge had depended on entering within a narrow window after results publication, it would be unlikely to survive live operation, where publication dates vary by company and quarter. It does not. Real-world publication occurs at 42–45 days; the specification assumes 60; both produce materially the same outcome.

**60 days is retained** because it is the conservative assumption — it models the latest possible publication date under SEBI's outer filing deadline, so a live implementation will enter earlier than the backtest rather than later.

### 14.6 Test 4 — Partial exit: 50% at target, 50% trailed

**Method.** The ATH target is preserved exactly as specified. At the target, **half** the position is sold at the target price. The remaining half continues under a trailing stop set at a fixed percentage below its running maximum close, still subject to the 1,095-day cap. Trailing widths of 15%, 20%, 25% and 30% were tested.

| Variant | N | Win | Median | Avg | Hold | XIRR |
|---|---|---|---|---|---|---|
| **Baseline (full exit at target)** | 351 | 76.1% | **66.3%** | 57.9% | 669 | **33.49%** |
| 50% target + 15% trail | 351 | 76.1% | 54.2% | 71.8% | 722 | 40.07% |
| 50% target + 20% trail | 351 | 76.1% | 52.3% | 75.3% | 755 | 39.45% |
| 50% target + 25% trail | 351 | 76.1% | 48.5% | 81.4% | 794 | 39.92% |
| 50% target + 30% trail | 351 | 76.1% | 47.5% | 80.9% | 818 | 39.08% |

At face value this is a large improvement — roughly **+6 pp of XIRR**, stable across every trailing width. It was not adopted, for three reasons found on further testing.

**Reason 1 — the gain does not survive removal of its largest contributors.** Re-running both the baseline and the partial-exit variant with the largest winners removed from each:

| Largest trades removed | Baseline XIRR | Partial-exit XIRR | Difference |
|---|---|---|---|
| 0 | 33.49% | 39.45% | **+5.96 pp** |
| 1 | 32.65% | 34.65% | **+2.00 pp** |
| 2 | 32.42% | 34.37% | +1.95 pp |
| 3 | 31.66% | 33.61% | +1.95 pp |
| 5 | 30.81% | 32.25% | +1.44 pp |
| 10 | 28.32% | 29.33% | +1.01 pp |

**Two-thirds of the headline advantage comes from a single trade** (ZEEL, whose trailed half compounded to a 1,609% blended return against 565% for the best baseline trade). Once that one position is removed, the advantage falls from +5.96 pp to +2.00 pp.

A residual advantage of roughly 1–2 pp does persist, and is real. But it is an order of magnitude smaller than the headline, and far too small to justify a structural change on a 275-trade sample.

**Reason 2 — cohort consistency is weak.** The partial exit beats the baseline in only **8 of 15** cohorts, and loses in 2014, 2015, 2016, 2020, 2021, 2024 and 2026. Its wins are concentrated in 2013 (+12.00 pp), 2017 (+9.30 pp), 2018 (+5.68 pp) and 2019 (+5.73 pp).

**Reason 3 — the median return falls.** Median blended return drops from 66.3% to 52.3%. The variant raises the *mean* while lowering the *typical* outcome — it converts a broad-based return profile into an outlier-dependent one. For a product whose clients act on individual recommendations, that is a worse proposition even where the aggregate arithmetic favours it.

**A further consideration, not the deciding one.** The trailed half has **no pre-published exit price**. A client could be told the target for the first half on day one, but not what "done" looks like for the second. That partially dissolves the auditability property that makes each recommendation falsifiable (7.1).

**Conclusion — not adopted.** The current full exit at target is retained. The finding is recorded because a residual advantage of 1–2 pp does appear to exist, and the question is worth revisiting once the resolved-trade count is materially larger.

### 14.7 Test 5 — Fundamental deterioration exit

**Method.** An additional early-exit trigger was added alongside the existing rules: the position exits at the close following the first quarterly result in which **PAT falls below the PAT of the governing quarter** (the quarter that triggered entry). One, two and three consecutive breaching quarters were tested. The ATH target and 1,095-day cap remain in force; whichever triggers first applies.

| Variant | N | Win | Median | Avg | Hold | Target hits | Fundamental exits | XIRR |
|---|---|---|---|---|---|---|---|---|
| **Baseline (no fundamental exit)** | 351 | **76.1%** | **66.3%** | 57.9% | 669 | 157 | — | **33.49%** |
| PAT below governing, 1 quarter | 351 | 56.4% | 3.9% | 10.1% | 149 | 23 | 291 | 23.43% |
| PAT below governing, 2 quarters | 351 | 63.0% | 9.0% | 19.6% | 274 | 46 | 244 | 27.06% |
| PAT below governing, 3 quarters | 351 | 63.8% | 10.8% | 30.3% | 369 | 76 | 198 | 27.67% |

**Finding — clearly worse on every measure**, in every variant. XIRR falls from 33.49% to 23.4–27.7%. Win rate falls from 76.1% to 56–64%. Median return collapses from 66.3% to 3.9–10.8%.

**Why it fails, and why the failure is logically obvious in hindsight.** The entry condition requires PAT to be at an **8-quarter high**. By construction, the very next quarter is more likely than not to be lower — that is what a local maximum means. Under the single-quarter variant, **291 of 351 positions exit on a fundamental break**, at an average holding period of 149 days. The rule terminates almost the entire book before the price recovery the strategy exists to capture has had any time to occur.

**Conclusion — rejected.** The idea was worth testing precisely because it is intellectually appealing: exiting when the condition that justified entry disappears is symmetric and coherent. The data shows the symmetry is false. The entry condition is a **point-in-time** signal about operating strength; it is not a state that persists, and it cannot be used as a continuing hold condition.

The exit remains price-based: the all-time-high close, or the 1,095-day cap.

### 14.8 Test 6 — Time cap length

**Method.** The 1,095-day cap was varied to 730 days (2 years), 913 (2.5), 1,460 (4) and 1,825 (5). Everything else — universe, entry conditions, ATH target — is unchanged.

Because a shorter cap resolves positions that a longer cap leaves open, results are reported on two bases: the **full 351-signal set** (open positions marked to market, as in Section 10) and a **matched subset** of the 218 entries made on or before 28 July 2021, which are fully resolved under all five caps.

#### Full set (351 signals)

| Cap | Target hits | Hit rate | Win | Median | Hold | Position-years | XIRR | Nifty 500 | Excess | Cohorts |
|---|---|---|---|---|---|---|---|---|---|---|
| **2.0 y** | 122 | 43.3% | 74.4% | 37.6% | 529 | 509 | **37.02%** | 19.56% | **+17.45** | **12/15** |
| 2.5 y | 144 | 52.0% | 76.1% | 53.7% | 604 | 581 | 35.43% | 19.36% | +16.07 | 14/15 |
| **3.0 y (current)** | 157 | 57.1% | 76.1% | 66.3% | 669 | 643 | 33.49% | 18.00% | **+15.49** | 14/15 |
| 4.0 y | 182 | 68.7% | 78.6% | 67.6% | 773 | 743 | 32.98% | 16.62% | +16.35 | 14/15 |
| 5.0 y | 196 | **76.0%** | **81.2%** | **68.1%** | 847 | 814 | 33.29% | 16.66% | +16.63 | 14/15 |

#### Matched subset (218 entries, fully resolved under every cap)

| Cap | Target hits | Hit rate | Win | Median | Avg | Hold | Position-years | XIRR | Nifty 500 | Excess |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.0 y | 87 | 39.9% | 75.2% | 64.4% | 56.5% | 602 | 360 | **37.17%** | 19.88% | **+17.29** |
| 2.5 y | 107 | 49.1% | 76.6% | 67.7% | 66.9% | 702 | 419 | 35.59% | 19.65% | +15.94 |
| **3.0 y (current)** | 118 | 54.1% | 76.1% | 68.8% | 72.8% | 791 | 473 | 33.65% | 18.25% | **+15.41** |
| 4.0 y | 142 | 65.1% | 81.2% | 71.5% | 89.8% | 937 | 559 | 33.17% | 16.85% | +16.32 |
| 5.0 y | 156 | 71.6% | **84.9%** | **73.5%** | **100.6%** | 1,053 | 629 | 33.49% | 16.89% | +16.60 |

Both bases give the same shape, which is the point of running them.

#### Finding 1 — XIRR falls as the cap lengthens, but flattens after 3 years

37.02% at 2 years, 33.49% at 3, 32.98% at 4, 33.29% at 5. The decline is real between 2 and 3 years and essentially disappears beyond it. A 5-year cap is **XIRR-neutral against the current 3-year cap** (−0.20 pp).

#### Finding 2 — benchmark excess is U-shaped, with its minimum at 3 years

| Cap | 2.0 y | 2.5 y | **3.0 y** | 4.0 y | 5.0 y |
|---|---|---|---|---|---|
| Excess (pp) | +17.45 | +16.07 | **+15.49** | +16.35 | +16.63 |

**On benchmark-relative terms, the 3-year cap is the worst of the five tested.** This is recorded plainly because it is true and because an independent reviewer would find it.

The mechanism is that the benchmark itself moves with the cap: matched-timing index XIRR is computed over the same holding periods, so shorter holds are matched against shorter — and in this period higher-annualising — index windows. The index return falls from 19.56% at a 2-year cap to 16.66% at 5 years.

#### Finding 3 — the 2-year advantage is real, unlike Test 4's

Re-running with the largest winners removed from every variant:

| Largest trades removed | 2.0 y | 2.5 y | 3.0 y | 4.0 y | 5.0 y |
|---|---|---|---|---|---|
| 0 | 37.02% | 35.43% | 33.49% | 32.98% | 33.29% |
| 1 | 35.47% | 34.20% | 32.65% | 32.37% | 32.37% |
| 3 | 35.12% | 33.77% | 31.66% | 31.04% | 30.89% |
| 5 | 33.57% | 32.39% | 30.81% | 29.76% | 29.44% |
| 10 | 30.03% | 30.54% | 28.32% | 28.26% | 27.64% |

The 2-year cap retains a **+1.7 to +3.5 pp** XIRR advantage at every level of outlier removal. This is a genuine effect, not a single-position artefact of the kind that disqualified the partial-exit variant (14.6).

On benchmark **excess**, however, the advantage erodes sharply — from +1.96 pp with all trades to **+0.40 pp** with the ten largest removed.

#### Finding 4 — but cohort consistency fails

Compared cohort by cohort against the 3-year cap on the matched subset:

| Variant | Beats 3-year in | Loses in |
|---|---|---|
| **2.0 y** | **5 of 10** | 2014, 2015, 2018, 2019, 2021 |
| 2.5 y | 7 of 10 | 2014, 2018, 2021 |
| 4.0 y | 7 of 10 | 2012, 2015, 2016 |
| 5.0 y | 7 of 10 | 2012, 2015, 2016 |

**A 5-of-10 record is indistinguishable from chance.** Under the standard set in 14.1, that alone disqualifies the 2-year cap regardless of its aggregate XIRR.

#### Finding 5 — what the time cap is actually cutting

| Cap | Time-stopped positions | Avg return | Median return | Share ending in loss |
|---|---|---|---|---|
| 2.0 y | 160 | +23.3% | **+12.7%** | 41% |
| 2.5 y | 133 | +27.3% | +8.2% | 43% |
| 3.0 y | 118 | +27.5% | +4.0% | 48% |
| 4.0 y | 83 | +33.6% | −4.4% | 54% |
| 5.0 y | 62 | +13.6% | **−8.1%** | 53% |

This is the most informative table in the test. As the cap lengthens, the residue left at the cap becomes progressively **worse** — because the recoverable positions have escaped through the target, leaving only genuinely broken ones. At 5 years just 62 positions remain unresolved by the thesis.

The reverse reading matters more for the 2-year case. Its 160 time-stopped positions have a **median return of +12.7%** and only 41% end in loss. Those are not failed recommendations — they are recommendations **cut off before they finished**. A 2-year cap raises XIRR partly by ending healthy positions early and recycling the capital.

#### Finding 6 — a longer cap was seriously considered

The 4- and 5-year variants were not dismissed. On the matched subset, a 5-year cap delivers essentially the same XIRR as 3 years (33.49% vs 33.65%) while improving nearly every other measure: win rate 84.9% vs 76.1%, completion rate 71.6% vs 54.1%, median return 73.5% vs 68.8%, and benchmark excess +16.60 vs +15.41.

It was rejected on three grounds:

1. **Capital efficiency.** A 5-year cap consumes **629 position-years against 473** — 33% more capital-time to produce the same annualised return. The higher completion rate is largely mechanical: given more time, more positions reach any fixed target. It does not translate into more money per year at risk.
2. **Evidence base.** At a 5-year cap, 93 of 351 recommendations remain open against 76 today. A newly launched product needs the largest possible resolved track record, not the smallest.
3. **Client proposition.** A defined three-year horizon is communicable and holdable. "You may still be holding this in five years" is materially harder to set as an expectation and to sustain.

#### Conclusion — 3 years retained, and it is not the optimum

**The 3-year cap is not the best-performing value on any single metric tested.** It is beaten on XIRR by 2 and 2.5 years, and on benchmark excess by every other variant tested.

It is retained because the time cap is not a performance parameter. Its function (7.2) is **truth in reporting** — forcing every recommendation to resolve so the track record cannot consist only of trades that eventually worked. Its length should therefore be set by how long the thesis genuinely needs, and the data answers that directly: the median time to target is **523 days**, and **35 of 157 target hits arrive after the second year**. A 2-year cap does not give the thesis the time it demonstrably requires — Finding 5 shows exactly what it cuts.

This is the second parameter (after the drawdown threshold, 14.4) where a better-performing value exists, was identified, and was deliberately not adopted.

### 14.9 What was deliberately not tested

The following were considered and excluded as parameter-fishing on a sample too small to support them. Testing many variants and adopting the best would produce an apparent improvement by chance alone, and would forfeit the strategy's principal defence — that nothing in it has been fitted.

- Additional fundamental metrics (ROE, debt/equity, margins, cash flow)
- Sector or industry filters
- Valuation screens (P/E or P/B caps)
- Market-regime filters (suppressing signals when the index is elevated)
- Fundamental window lengths other than 8 quarters
- Price-based stop-losses — excluded on logic, not statistics: the entry condition *is* a 40% decline, so a stop-loss would exit precisely the situation the strategy is designed to enter (7.3)
- Re-arm conditions other than a fresh all-time-high close — noted as a legitimate future question, but of lower value than the five tests above

### 14.10 Overall conclusion

Six tests, three on entry and three on exit. **The specification is unchanged.**

- Two entry parameters (threshold, availability lag) were shown to sit on **flat or smoothly sloping response surfaces**, with the values in use not being the best-performing ones.
- The **time cap** was shown to have a better-performing value at 2 years — an advantage that survived outlier removal but failed on cohort consistency (5 of 10) and cut the completion rate to 43.3%. A longer 4–5 year cap was found XIRR-neutral and rejected on capital efficiency.
- The fundamental filter was shown to **earn its place**, though by a different mechanism than previously described — a correction now reflected in this document.
- One exit variant showed an apparently large gain that **did not survive outlier removal or cohort testing**, and was rejected.
- One exit variant **failed outright** for a reason that is structural rather than statistical.

**Two parameters — the drawdown threshold and the time cap — have a documented better-performing value that was identified and deliberately not adopted.** The strategy's parameters are not merely unoptimised: they have been **tested, found not to be optimal**, and retained on stated product grounds. That is a stronger position than an untested specification.

---

*This document describes a rules-based research methodology. It is not investment advice and does not constitute a recommendation to buy or sell any security. Past performance, including backtested performance, is not indicative of future results.*
