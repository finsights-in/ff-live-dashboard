# FF Live Dashboard — v3 plan

Updated 6 September 2026. A **client-facing advisory dashboard** for a real client
community. Not a research page.

Phase A's findings and decisions live in `FF_PhaseA_Results.md`.

> *Handover note, 30 September 2026: the URL below is the old personal one. The
> repository moved to the `finsights-in` organisation on 8 September; the current
> URL is https://finsights-in.github.io/ff-live-dashboard/ . The market strip,
> the information panel and the auto-refresh control were added after this plan
> was written — see `FF_Market_Strip.md`.*

---

## Where it stands

| Phase | | |
|---|---|---|
| **A** Real results-announcement dates | ✅ | live |
| **B** JSON data + hand-written page | ✅ | live |
| **C** News | ✅ | live |
| **D** Nifty 500 index kept current | ✅ | live |
| **E** Periodic performance | ✅ | live |
| **F** Presentation | ✅ | Client portal, both themes |
| **G** Compliance footer | ❌ | **needs the business's details** |

`https://priyanshuagarwal8430-dotcom.github.io/ff-live-dashboard/`

## Decisions taken

| Question | Decision |
|---|---|
| June–August signals | Real dates applied; anything triggering before 1 June is out. 19 open positions. |
| Periodic performance | Live signals only. No backtest history on this page. |
| News | NSE filings for the portfolio and the index; RBI and SEBI in full; Indian financial press as headline, outlet and link only. |
| Nifty 500 | A reference number — level, day change, one-year chart. Never a comparison. |
| Strategy rules | Removed. An advisory publishes signals, not its rules. |
| Presentation | One layout: Client portal, dark and light. |
| Micro Cap | Not published. Own dashboard later. |
| Frozen backtest | Accepted as issued; one line of disclosure in the methodology. |
| Discount at entry | Removed from the page. Entry price and the trigger ATH are both on the row. |

## What the page shows

Symbol · Entry date · Entry price · Last close · Return · Trigger ATH / target ·
ATH date · Progress to target · Days held, against the 1,095-day cap.

Filterable by Large / Mid / Small with live counts, searchable, sortable on every
column. Below 700px each position becomes a stacked card — no sideways drag on a
phone. Theme remembered per viewer.

`trigger_reason` (price crossed / results published) stays in `positions.json` as
the cross-check for a deep entry but is not shown. So does
`below_ath_at_entry`.

## Micro Cap, and why it is out

Its stored flags use a **four-quarter** window, not the strategy's eight. Seven of
thirteen watchlist entries fail an eight-quarter test — OPTIEMUS among them, whose
March-2026 Net Sales is a four-quarter high and an eight-quarter low. None of the
nineteen Nifty 500 positions fails. The watchlist was running a looser rule, and
its better average return (+4.06% against +2.26%) is at least partly that.

`FF_Ledger.py` keeps recording it. Nothing is published until its flags are
rebuilt on eight quarters, which is safe for the acceptance test — the reference
set holds no Micro Cap.

---

## What NSE will and will not answer from a GitHub runner

Measured 5 September 2026, not assumed. Phase A had only proved Colab, which is a
different network.

    handshake www.nseindia.com     403     and the APIs answer anyway
    event-calendar                 OK      2,433 records
    corporate-announcements        OK      31,312 records (21.8 MB over 45 days)
    corporates-corporateActions    OK      600 records
    bhavcopy (2 of 3 URL forms)    OK      3,634 rows

The failed handshake is not a blocker and never was: `FF_NSE_OHLC_Updater.py`
already wraps it in try/except. **The bhavcopy switch is viable**, and results
dates no longer need the manual Colab notebook.

## The news card, and the four faults found in it

`FF_news.py` writes four blocks, kept apart on purpose. An NSE filing is the
company's own document; a Mint headline is somebody's writing about one. Merged
into one list a reader cannot tell which is which.

    portfolio   NSE filings for the stocks held
    market      NSE filings across the rest of the Nifty 500
    policy      RBI and SEBI, in full — public documents
    press       ET, Business Standard, Mint, NDTV Profit — headline, outlet, link

Bloomberg and Reuters were never candidates: licensed through the Terminal and
through LSEG, redistribution forbidden. Moneycontrol and Trading Economics refuse
the runner.

The first live run looked fine and was not. Four faults, all found by reading the
counts rather than the page:

1. **SEBI: 30 fetched, 0 kept, no error.** Its dates read `04 Sep, 2026 +0530`
   and parsed to nothing, so a whole source vanished silently. Unparsed dates are
   now counted and printed.
2. **The offset-stripping pattern ate the year** out of `04-09-2026`, leaving
   `04-09`. It now requires whitespace before the offset.
3. **`dayfirst=True` turned `2026-09-04` into 9 April.** ISO dates are no longer
   read day-first.
4. **A deny-list cannot filter a general feed.** "Women's Asia Cup 2026: India
   Bundle Pakistan Out For 55" passed a list holding cricket, T20 and world cup,
   and would have missed the next word too. Press items must now match a finance
   term to appear at all.

Also: NSE's `desc` is a filing category, not a headline — the first run's top
items were "Certificate under SEBI Regulations", "Press Release", "Updates". The
headline now comes from `attchmntText`, and only categories that can move a
position pass.

And a per-outlet cap of eight, because the Economic Times publishes 47 items to
Business Standard's 21: a straight date sort handed it the whole block and two of
the four outlets never appeared.

---

## What is left

**G — compliance footer.** Needs from the business: entity name, SEBI Research
Analyst registration number, contact address, disclaimer and grievance details.
The footer carries a placeholder until then.

**The public URL.** GitHub Pages serves the dashboard to anyone with the link, no
sign-in, and the signals are the product being sold. A business decision, and it
needs one before clients are given the link.

**Micro Cap:** rebuild its flags on eight quarters, then its own dashboard.

**NSE bhavcopy switch:** now proved viable. Daily prices still come from Yahoo
onto an NSE-sourced base.

**Results dates in CI:** `event-calendar` answers the runner, so `results_dates.csv`
can be refreshed automatically instead of by the manual notebook.

**`ff_advisory.html` is stale** and should not be shared; the `.docx` is the one
to send. **Survivorship bias is unquantified**, and `ident.csv` applies today's
Large/Mid/Small labels backwards.

---

## Carried forward, unchanged

- The ATH target exit is the strategy's distinguishing feature and is not altered.
- XIRR (Advisory, money-weighted) and CAGR (Model Portfolio, time-weighted) are
  never conflated.
- The ledger is append-only. A signal the scanner stops producing is kept and
  reported, never deleted.
- Returns carry an explicit sign as well as colour.
- Nothing in the workflow writes `docs/index.html`. That ended the merge conflict
  that recurred on every push.
