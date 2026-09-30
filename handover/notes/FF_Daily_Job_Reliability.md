# FF — Daily Dashboard Update: the unsettled-bar failure

**Status:** diagnosed and fixed in `FF_OHLC_Updater_v2.py`. Recorded 29 September 2026.

## Symptom

On 21 and 28 September 2026, and again on the first run of 29 September, the
Daily Dashboard Update workflow failed at its fifth step, `Refresh OHLC data`:

```
[751/751] ZYDUSWELL: QUARANTINED — 1 NaN prices
quarantined    751
FAILING THE RUN: 751 quarantined, above the tolerance of 15.
```

Every one of the 751 symbols was quarantined with the identical message, and the
whole pipeline stopped there — index refresh, signal scan, ledger, market strip,
dashboard build, news and the commit/push never ran. The published dashboard
therefore froze on 25 September while the underlying data stayed correct.

## Cause

`check_frame()` counts empty cells across Open/High/Low/Close. "1 NaN prices"
means exactly one empty cell in the whole series — the same single cell on every
symbol, which is the signature of a source-side field, not of corporate actions.

Yahoo's live quote and its historical daily bar are different products. The
website streams a quote; the daily candle `Ticker.history()` reads is assembled
from a vendor feed and finalised some time after the close. Inside that window
the row for the day exists but one field is still null. The run had simply
arrived before the bar had settled.

Confirmed by a same-day A/B: the first run of 29 September failed and a later run
passed, on identical code and identical package versions, and the 28 September
bar arrived complete. An earlier hypothesis that an unpinned dependency
(`peewee` 4.5.2, released 27 September) was responsible is ruled out by the same
evidence.

No bad data ever reached disk. All 751 stored files were verified to hold zero
blank cells throughout, and the gate's refusal to write was correct behaviour.

## Fix

Two changes, both network-free and covered by the self-test (15/15 pass):

1. **An incomplete fetched row is dropped before the merge**, not merged and then
   caught. A bar missing any of its four prices is not data. Tomorrow's run picks
   it up, settled, through the ten-day overlap window. This also prevents an
   unsettled row from overwriting a good stored one, since `merge()` lets new
   rows win on a shared date. A block containing only incomplete bars returns
   `no_new_data` rather than quarantine.
2. **The NaN gate now names the date and the column** — `1 NaN prices (first:
   2026-09-28 Open)` instead of `1 NaN prices`. The gate's job is to refuse to
   publish; it must also say what it saw.

The quarantine tolerance stays at 15. It did its job.

## Open item

The workflow installs its dependencies unpinned (`pip install yfinance pandas
numpy beautifulsoup4 lxml requests`), so every run takes whatever PyPI holds that
morning. This was not the cause here, but it remains a source of unannounced
change in a job nobody watches.
