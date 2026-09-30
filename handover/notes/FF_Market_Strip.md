# FF — Market strip: sources, and why each one

Date: 2026-09-08. Live on the dashboard as of commit `0c59d62e`.
Built for Himanshu's request: ten instruments with 1D / 1W / 1M / 6M / 1Y.

## What was probed, and what it settled

Four probe runs on the GitHub runner. The container and the desktop are both
blocked from Yahoo and NSE by the proxy, so every question had to be asked
from the runner.

| Question | Answer |
|---|---|
| Yahoo history for the Nifty indices | Works. ~490 daily closes each for Nifty 50, 500, Midcap 150, Smallcap 250 |
| Yahoo history for MICROCAP 250 | **None.** Quotes live, but its own Historical Data tab returns one row for a one-year range |
| Yahoo history for NIFTYGS10YR | Same — live quote, no history |
| NSE `/api/historical/indicesHistory` | **Blocked.** Serves a `noindex` block page, for the NIFTY 500 control too, under every referer and warm-up tried |
| NSE `/api/allIndices` | **Works.** 139 indices including NIFTY MICROCAP 250, with last, 1D, one-week-ago, 30-day and 365-day changes |
| NSE `/api/liveBonds-traded-on-cm` | Works, 3,525 rows — but **no yield field**. Equity-style quote fields only |
| MCX (three paths) | **403 on all.** No rupee gold or crude at source |
| FBIL / CCIL / RBI | Reachable, but each needs its own scraper. Not attempted |

## What ships

**Five Nifty rows from NSE `allIndices`** — Nifty 50, Nifty 500, Midcap 150,
Smallcap 250, Microcap 250. Midcap 150 and Smallcap 250 were chosen because
they are exactly NSE's rank bands 101–250 and 251–500, which is what our own
Large/Mid/Small labels mean; the strip therefore matches our own segments.

**Five Yahoo rows** — Gold, Crude, Bitcoin, USD/INR, Dollar index.
Gold = `GC=F` × USDINR ÷ 31.1035 × 10 → ₹/10g. Crude = `CL=F` × USDINR → ₹/bbl.
Both are *international* prices in rupees, carrying no import duty, so they
read below an MCX screen. The page says this in a footnote; it is not
decoration, it is the only way a reader comparing against a broker screen can
see why the numbers differ.

**Dropped: the India 10Y row.** Himanshu asked for the *yield*. NIFTYGS10YR is
a G-Sec total-return index, not a yield — it moves inversely to yield, and
labelling 2,665 as "India 10Y yield" would be simply false. NSE's G-Sec feed
carries no yield field, and deriving a YTM from thin retail capital-market
quotes would produce a number that looks official and matches nothing anyone
else publishes. The real benchmark comes from FBIL/CCIL and is its own piece
of work.

## Two decisions worth remembering

**One window definition, both sources: calendar days — 7, 30, 182, 365.**
NSE's own 365-day change is calendar based. An early Yahoo probe used 252
trading days, and on 8 September the two conventions disagreed by **1.9
percentage points** on the Nifty 500 1Y (+2.86% vs +0.99%). Same column, two
meanings, nothing on the page to show it. Never mix them.

**6M is built, not fetched.** NSE publishes no six-month field. Rather than
drop the column or fake it, `FF_market_update.py` appends every day's close to
`indices/market_history.csv` and computes 6M from that file once it reaches
back far enough. Until then those cells show a dash. It fills itself in around
March 2027.

## Failure posture

The strip is reference material; the positions are the product. So:
`FF_market_update.py` exits 0 whatever happens, and the page fetches
`market.json` **optionally** — tested with the file 404ing, all 19 positions
still render and the strip says the feed did not load.

## Mistakes made getting here, so they are not repeated

1. **Probe v3 sent `Accept-Encoding: gzip, deflate, br`.** requests cannot
   decode brotli without a package the runner lacks, so every body came back
   as mojibake — including two endpoints that had parsed fine in v2. One
   header wasted a whole run. Every call now prints `Content-Encoding`.
2. **The first probe's auto-picker chose `^TNX` for "India 10Y".** That is the
   *US* 10-year; it was in the candidate list as a control and the picker took
   the first working symbol. A summary line that names a winner must not be
   trusted over the evidence above it.
3. **Blamed OneDrive for stale `.git/*.lock` files.** They were created by git
   commands run through the device bridge, which cannot delete files. Verified
   only after the repo had been moved out of OneDrive — where a fresh lock
   appeared within 41 seconds. The move was still worth doing (785 MB of
   `.git` syncing), but it was not the fix.
4. **History stored at 6 significant figures** wrote `23090` for a close of
   `23089.95` on the very first row. Now 2 decimals. 0.0002% error — which is
   exactly why it would never have been noticed in the 6M figure it feeds.
