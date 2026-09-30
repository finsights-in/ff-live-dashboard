# Finsights Fundamental Dashboard — Handover and Runbook

**Read this first.** It is written so that a person who has never seen this
repository — or an AI that is handed a copy of it — can keep the dashboard
running, diagnose a failure, and fix it, without any other source of context.
Everything the system needs to be understood lives in this repository. Nothing
is held in anyone's chat history.

Last revised: 30 September 2026.

---

## 0. Agar kuch toot jaaye — 5 minute me kya karein

Ye ek chhota card hai, sirf tumhare liye. Baaki document English me hai taaki
koi bhi AI ya insaan use padh sake.

1. **Dashboard kholo:** https://finsights-in.github.io/ff-live-dashboard/
   Upar "as of" date dekho. Agar wo aakhri trading day hai → sab theek hai,
   yahin ruk jao.
2. **Purani date hai?** GitHub par jao → repo → **Actions** tab. Sabse upar
   waale run ka rang dekho. **Laal** hai to us par click karo → `update` job →
   jo step laal hai use kholo → **aakhri 30 lines** padho. Wahi asli error hai.
3. **Section 6 ki table me wo error dhundo.** Har dekha hua failure wahan
   likha hai, uske fix ke saath.
4. **Table me nahi mila?** `py make_context_pack.py` chalao (Section 8).
   Wo repo folder ke bagal me `FF_CONTEXT_CORE.md` banata hai. Use kisi bhi
   AI me upload karo, `handover/AI_PROMPT.md` ka text paste karo, aur error
   ki aakhri 30 lines de do.
5. **Kuch bhi delete ya overwrite karne se pehle** — Section 2 padho. Jo
   wahan likha hai wo kabhi nahi badalna.

---

## 1. What this is

A rules-based, long-only Indian equity strategy called **Fundamental First**,
run as an automated pipeline on GitHub Actions and published as a static
dashboard on GitHub Pages.

- **Live dashboard:** https://finsights-in.github.io/ff-live-dashboard/
- **Repository:** https://github.com/finsights-in/ff-live-dashboard
- **Owner:** the GitHub organisation `finsights-in`. Priyanshu's personal
  account is the org owner; Himanshu is a collaborator.
- **Local copy on Priyanshu's laptop:** `C:\Users\hp\GitHub\ff-live-dashboard`,
  managed with **GitHub Desktop**.

Every trading day at 19:00 IST a job downloads the day's prices for 751 NSE
stocks, checks them, looks for new signals under the frozen rules, records
them in an append-only ledger, refreshes a small market strip and a news feed,
rebuilds the dashboard's data files, and pushes the result. Every Sunday a
second job scrapes the latest quarterly results and merges them into the
fundamentals base.

There is no server. There is no database. Everything is a CSV or JSON file in
this repository, and GitHub Actions is the only place code runs.

The strategy's full methodology, its backtest, and every decision taken while
building this system are in `handover/notes/`. Start with
`handover/notes/README.md`, which says which documents are current.

---

## 2. Rules that never change

These are frozen. Changing any of them makes it a different strategy and
invalidates the published track record. **No fix to the pipeline may touch
them, and no AI may be allowed to "improve" them.**

### 2.1 The strategy rules (specification v2.0)

| Rule | Value | Where in code |
|---|---|---|
| Universe | Nifty 500 (500 names) for signals; Micro Cap (251) tracked separately, never published | `ident.csv` `market_type` |
| Price condition | `Close(t) ≤ 0.60 × cummax(Close)` — **closing** prices, all-time high from 1995 | `FF_Signal_Engine_v2.py`, `THRESHOLD = 0.60` |
| Fundamental condition | Net Sales, PAT and Diluted EPS each at an **8-quarter high** | `FF_fundamentals_ingest_v3.py`, `WINDOW = 8` |
| Positivity | All three **> 0** in the governing quarter | `all_hi_pos` flag; the engine reads `all_hi_pos`, never `all_hi` |
| Availability | A quarter is usable only from its announcement date (`avail_date`) — no look-ahead | `avail_date` column, applied point-in-time in the engine |
| Armed state | One signal per drawdown cycle; re-arm only on a fresh all-time-high **close** | engine loop |
| Entry | **Next trading day's Open** | `simulate()` |
| **Exit target** | **The all-time-high close as at the trigger date. Fixed. Never moves.** | `simulate()`, `tgt = ath[ti]` |
| Time cap | 1,095 calendar days | `CAP_DAYS = 1095` |
| Stop loss | **None** | — |
| Price adjustment | Splits and bonuses only; **never dividends** | `FF_OHLC_Updater_v2.py` |

**The ATH target exit is the strategy's distinguishing feature.** It is the
first thing a well-meaning helper will suggest changing ("add a trailing
stop", "take partial profits"). Every such variant was formally tested and
rejected — see `handover/notes/FF_Advisory_Methodology_v1.md`, Section 14. Do
not re-open it as a side effect of a bug fix.

### 2.2 Operating constraints

- **XIRR and CAGR are different products' metrics.** Advisory reports XIRR
  (money-weighted). The Model Portfolio reports CAGR (time-weighted). They are
  never shown together or swapped.
- **The signal ledger is append-only.** A signal, once published, is never
  edited or deleted. If the engine stops producing it, it stays in the ledger
  and is reported.
- **Nothing in the pipeline writes `docs/index.html`.** The page is
  hand-maintained; the pipeline writes only `docs/data/*.json`.
- **Never save tokens or credentials in this repository.** There are none
  today. A Dhan access token in particular carries order-placement rights.
- **Publishing nothing is always better than publishing something wrong.**
  Every gate in the pipeline is built on this. When a check fails, the run
  stops and the previous day's data stays up. That is correct behaviour, not a
  bug to be "fixed" by removing the check.

---

## 3. How it runs

### 3.1 The daily job — `.github/workflows/daily_update.yml`

Schedule: `30 13 * * 1-5` = **19:00 IST, Monday to Friday**. Can also be run
by hand: Actions tab → "Daily Dashboard Update" → "Run workflow".

Step numbers below are the workflow's own, as the Actions log shows them.

| # | Step (as named in the Actions log) | Script | What it does |
|---|---|---|---|
| 1 | Check out the repository | — | |
| 2 | Set up Python | — | Python 3.12 |
| 3 | Install dependencies | — | `pip install yfinance pandas numpy beautifulsoup4 lxml requests` — **unpinned**, see 9.4. The log's `Successfully installed …` line records the exact versions this run used |
| 4 | Record package versions | — | `pip freeze > handover/last_run_versions.txt`; committed in step 16, so every green run's exact versions are in git history (added 30 Sep 2026) |
| 5 | Updater self-test | `FF_OHLC_Updater_v2.py --selftest` | 15 offline checks; run stops here if any fails |
| 6 | **Refresh OHLC data** | `FF_OHLC_Updater_v2.py` | Fetches the last ~10 days from Yahoo for all 751 symbols, vets any corporate action against the price, refuses anything it cannot verify, appends. **Fails the run if more than `max(5, 2% of files)` symbols are refused — 15 today** |
| 7 | Index updater self-test | `FF_index_update.py --selftest` | |
| 8 | Refresh the Nifty 500 index | `FF_index_update.py` | Appends to `indices/Nifty500.csv` |
| 9 | Signal engine acceptance test | `FF_Signal_Engine_v2.py --verify FF_FINAL_v5_n500.csv` | Re-derives the 358-trade backtest from current data and must match it exactly. **This is the guard that proves the rules have not drifted.** |
| 10 | Scan for signals | `FF_Signal_Engine_v2.py --since 2026-06-01` | Writes `signals.csv`, `watchlist_microcap.csv`, `fresh_signals.csv` |
| 11 | Update the signal ledger | `FF_Ledger.py` | Appends new signals to `signal_ledger.csv` / `watchlist_ledger.csv`; records exits |
| 12 | Market strip self-test | `FF_market_update.py --selftest` | |
| 13 | Refresh the market strip | `FF_market_update.py` | NSE `allIndices` + Yahoo → `docs/data/market.json`, appends `indices/market_history.csv`. **Never fatal** — exits 0 whatever happens |
| 14 | Build the dashboard data | `FF_dashboard_data.py` | `docs/data/positions.json`, `closed.json`, `index.json`, `meta.json` |
| 15 | Build the news feed | `FF_news.py` | `docs/data/news.json` |
| 16 | Commit and push updated data + dashboard | — | Adds only files that exist; `git pull --rebase --autostash`; push |
| 17 | Upload the run report | — | `ohlc_update_report.json` + `ohlc_quarantine.txt` as a run artifact, **even on failure** |

GitHub Pages serves the `docs/` folder. A push is live within a minute or two.

### 3.2 The weekly job — `.github/workflows/weekly_fundamentals.yml`

Schedule: `30 4 * * 0` = **10:00 IST, Sunday**.

| # | Step | Script |
|---|---|---|
| 1 | Scrape Screener for every symbol in `tickers.txt` | `FF_Fixed_Gemini_Scraper.py` → `fundamentals_master.csv`; failed tickers retried once, merged by `merge_retry.py` |
| 2 | Merge into the v3 base | `FF_fundamentals_ingest_v3.py` → `fund_flags_v3.csv` |
| 3 | Signal engine acceptance test | same `--verify` as the daily job |
| 4 | Commit and push | adds only files that exist |

Most weeks nothing material changes (results come out once a quarter), so a
"successful" weekly run often commits only float-formatting noise. That is
expected.

### 3.3 Where you see the results

- **Dashboard:** the "as of" date in the header is `meta.json`'s `as_of`. If
  it equals the last trading day, the daily job ran to completion.
- **Actions tab:** every run, green or red, with full logs, kept 90 days.
- **Email:** GitHub emails the repository owner when a scheduled workflow
  fails. That email is the alarm. Do not filter it.

---

## 4. Map of the repository

### 4.1 Files the live pipeline uses

| File | Role |
|---|---|
| `FF_OHLC_Updater_v2.py` | Daily price updater with corporate-action vetting and structural gates. Has `--selftest`, `--dry-run`, `--symbols A,B` |
| `FF_index_update.py` | Nifty 500 index updater. Has `--selftest` |
| `FF_Signal_Engine_v2.py` | The strategy. `--verify <ref.csv>` reproduces the backtest; `--since <date>` scans |
| `FF_Ledger.py` | Append-only ledger and exit tracking |
| `FF_market_update.py` | Market strip. Has `--selftest` |
| `FF_dashboard_data.py` | Builds the dashboard JSON |
| `FF_news.py` | News feed (NSE filings, RBI, SEBI, four newspapers) |
| `FF_Fixed_Gemini_Scraper.py`, `merge_retry.py` | Weekly Screener scrape |
| `FF_fundamentals_ingest_v3.py` | Merges scraped quarters into the base; applies split factors from `corporate_actions.csv` if present |
| `docs/index.html` | The dashboard page. Hand-maintained. Reads `docs/data/*.json` |
| `FF_healthcheck.py` | **Plain-language status check. No dependencies. Run it first when in doubt** |
| `make_context_pack.py` | Bundles everything an AI needs into one folder / zip / single file |

### 4.2 Data files

| File | What it is | Written by |
|---|---|---|
| `ohlc_data/<SYMBOL>.csv` × 751 | Daily OHLCV from 1995, split/bonus adjusted. Columns `Date,Close,High,Low,Open,Volume` | `FF_OHLC_Updater_v2.py` |
| `ident.csv` | The 751-name universe: `symbol`, `market_type` (Large/Mid/Small/Micro Cap), `company`, BSE codes. Exactly one row per price file | hand-maintained |
| `fund_flags_v3.csv` | Quarterly fundamentals with the 8-quarter-high flags. 37k rows, 2006–present. Key columns: `report_date`, `avail_date`, `net_sales`, `pat`, `eps_reported`, `split_factor`, `eps_adj`, `all_hi_pos` | `FF_fundamentals_ingest_v3.py` |
| `fundamentals_master.csv` | Raw output of the weekly scrape | scraper |
| `FF_FINAL_v5_n500.csv` | **The reference backtest — 358 trades, 2012 to July 2026.** The acceptance test compares against this. Never edit | frozen |
| `signal_ledger.csv`, `watchlist_ledger.csv` | The published record (Nifty 500 tier / Micro Cap). Append-only | `FF_Ledger.py` |
| `signals.csv`, `fresh_signals.csv`, `watchlist_microcap.csv` | Today's engine output, overwritten daily | engine |
| `indices/Nifty500.csv` | Nifty 500 daily, the dashboard's reference index | `FF_index_update.py` |
| `indices/market_history.csv` | Daily closes of the five Nifty rows, for the 6-month column | `FF_market_update.py` |
| `docs/data/*.json` | What the page reads: `meta`, `positions`, `closed`, `index`, `market`, `news` | daily job |
| `tickers.txt` | Symbol list for the scraper | hand-maintained |

### 4.3 Data flow, in one picture

```
Yahoo ──► FF_OHLC_Updater_v2.py ──► ohlc_data/*.csv ─┐
NSE   ──► FF_index_update.py    ──► indices/Nifty500 ─┤
                                                      ├─► FF_Signal_Engine_v2.py ──► signals.csv ──► FF_Ledger.py ──► signal_ledger.csv
Screener ─► scraper ─► fundamentals_master ─► ingest_v3 ─► fund_flags_v3.csv ─┘                                              │
                                                                                                                             ▼
NSE allIndices + Yahoo ──► FF_market_update.py ──► docs/data/market.json                    FF_dashboard_data.py ──► docs/data/{meta,positions,closed,index}.json
NSE / RBI / SEBI / press ──► FF_news.py ──► docs/data/news.json                                                                │
                                                                                                          docs/index.html reads all of docs/data/ ──► GitHub Pages
```

### 4.4 Files that are NOT used by anything

These are superseded or one-off tools kept for history. They are safe to
delete and must not be run:

`FF_Yahoo_OHLC_Updater.py` (**the v1 updater that corrupted the price history
— never run it**), `FF_NSE_OHLC_Updater.py`, `FF_fundamentals_ingest.py`,
`FF_Screener_Fundamentals_Scraper.py`, `FF_build_dashboard.py`,
`FF_build_dashboard_v2.py`, `FF_dashboard_template.html`,
`FF_Live_Tracking_Dashboard.html`, `FF_Fresh_Signal_Scanner.py`,
`FF_datefix_compare.py`, `FF_datefix_scan.py`, `FF_rebuild_new.py`,
`FF_reseed_gapfill.py`, `FF_seed_ohlc.py`, `FF_market_probe.py`,
`.github/workflows/market_probe.yml`, `fund_flags.csv` (the pre-v3 base),
`results_dates.csv`, `datefix_signals.csv`.

---

## 5. How to know it is healthy

### Daily — 30 seconds

Open the dashboard. The "as of" date should be the last trading day. Positions
should be listed. The market strip should show numbers, not dashes (the 6M
column is allowed to be blank until March 2027).

### Weekly — 2 minutes, Monday morning

Actions tab. Last five daily runs green. Sunday's weekly run green.

### Monthly — 5 minutes

First click **Fetch origin** (then **Pull origin** if it appears) in GitHub
Desktop. The check reads your local copy, which is only as current as your
last pull — without it, "price data currency" reports the day you last
pulled, not the day the pipeline last ran. Then, from the repository
folder, in Command Prompt:

```
py FF_healthcheck.py
```

Verified on Windows (Python 3.14.7) on 30 September 2026: 14 PASS, 3 WARN.

It needs only Python — no packages. It prints one line per check, `PASS`,
`WARN` or `FAIL`, in plain English, and ends with a verdict and a short list
of what to do. It reads the files; it changes nothing.

It checks: every price file's currency and structure, symbols that have
silently stopped updating, the universe file against the price files, the
fundamentals base's newest quarter, the ledger against the dashboard JSON, the
workflows' known bug guards, the `.git` folder's size and any stale lock files.

Also once a month: look at the repository's size on GitHub (Settings →
General). See open issue 9.3.

---

## 6. When something breaks

### 6.1 The general procedure

1. **Do not touch the data files.** Every failure so far has left the data
   correct and merely stopped the run. The gates are designed that way.
2. Actions tab → the red run → the `update` job → expand the red step → read
   the **last 30 lines**. The real error is almost always in the last 5.
3. Find the message in 6.3 below.
4. If it is not there: `py FF_healthcheck.py`, then Section 8.
5. After any fix: **re-run the workflow by hand** (Actions → Run workflow) and
   watch it go green. Do not wait for tomorrow's schedule to find out.

### 6.2 What "failed" actually means here

The pipeline is a chain. A failure at step 6 (prices) means steps 7–16 never
ran, so nothing was committed and the dashboard shows yesterday. **Nothing is
corrupted. Nothing needs restoring.** Fix the cause, re-run, and the run picks
up every missed day automatically (the price updater fetches a 10-day window).

### 6.3 Known failures — symptom, cause, fix

Every failure the system has had, with the date it happened.

**One rule before the table.** If the *same* message appears on all (or
nearly all) 751 symbols, the cause is never the stocks — it is the feed, a
package version, or the code. Corporate actions and genuine data faults hit a
handful of symbols with *different* messages. So for an all-symbol failure:
compare the `Successfully installed …` line of this run with
`handover/last_run_versions.txt` from the last green run first, then re-run once by hand, and only then read the code.

---

**Symptom:** `FAILING THE RUN: 751 quarantined, above the tolerance of 15` and
every line reads `QUARANTINED — 1 NaN prices`.

**Cause:** Yahoo's daily bar for the current day had not finished settling
when the job ran; one field was still null for every symbol. Not a data
fault. (21, 28, 29 September 2026.)

**Fix:** Already fixed on 29 September — the updater now drops an incomplete
bar instead of merging it. If it ever recurs with a *different* pattern, the
gate message now names the date and column: `1 NaN prices (first: 2026-09-28
Open)`. Re-run the workflow an hour later; it will pass.

---

**Symptom:** `fatal: pathspec 'corporate_actions.csv' did not match any files`
then `exit code 128` in the commit step, after every other step succeeded.

**Cause:** the commit step named a file that does not exist yet. (5 September
in the daily job; 27 September in the weekly job.)

**Fix:** Both workflows now add files through an existence-checking loop:
```bash
for f in a.csv b.csv; do
  if [ -e "$f" ]; then git add "$f"; else echo "absent, not added: $f"; fi
done
```
If you ever add a new file to a commit step, add it **inside that loop**, never
as a bare `git add file`.

---

**Symptom:** `error: cannot pull with rebase: You have unstaged changes` in
the commit step.

**Cause:** the pipeline wrote a tracked file that the commit step did not add.
(5 September.)

**Fix:** Already present — the pull uses `--rebase --autostash`. If it
recurs, the file being written is new: add it to the loop above.

---

**Symptom:** GitHub Desktop says *"A lock file already exists in the
repository, which blocks this operation from completing."*

**Cause:** a git command was interrupted and left `.git/index.lock` (or
`HEAD.lock`, `ORIG_HEAD.lock`) behind. Common on Windows. (Several times in
September.)

**Fix:** Make sure GitHub Desktop and any terminal running git are closed.
Then delete the lock files. In Command Prompt:
```
cd C:\Users\hp\GitHub\ff-live-dashboard
del .git\index.lock .git\HEAD.lock .git\ORIG_HEAD.lock .git\objects\maintenance.lock
```
(Missing ones just say "could not find" — harmless.) Reopen GitHub Desktop.
`py FF_healthcheck.py` reports stale locks and prints this exact command.

---

**Symptom:** `KeyError` or `ModuleNotFoundError` in a step that worked
yesterday, with no change to the repository.

**Cause:** the workflows install packages **unpinned**; a new release of
`yfinance`, `pandas` or a dependency changed behaviour overnight.

**Fix:** In the failing workflow's `Install dependencies` step, pin the
package to the last version that worked. Since 30 September 2026 every
green run commits `handover/last_run_versions.txt` — open its git history
(GitHub website → the file → History) and take the version from the last
green day. For older runs, the `Install dependencies` step prints
`Successfully installed ...` with every version. Example: `pip install yfinance==1.7.0 pandas==3.0.6 ...`.

---

**Symptom:** the daily run is green but the dashboard's "as of" date is
still old.

**Cause:** either the browser cached the page, or the commit step found
nothing to commit (a market holiday).

**Fix:** Hard-refresh (Ctrl+F5). Then check the Actions log for the commit
step: `absent, not added` lines are fine; look for `nothing to commit`. On an
NSE holiday that is correct.

---

**Symptom:** Signal engine acceptance test fails: `--verify` reports a
difference against `FF_FINAL_v5_n500.csv`.

**Cause:** This is the serious one. Either a price file changed in a way that
alters a historical trade (a corporate action applied wrongly), or the
fundamentals base changed for a past quarter, or someone edited the rules.

**Fix:** **Do not loosen the test.** Read which trades differ (the log lists
them). Check the git history of the affected symbol's price file and of
`fund_flags_v3.csv` for that day's commit. Revert the data change that caused
it. If the reason is a genuine corporate-action correction, the reference set
must be regenerated deliberately and documented — that is a strategy-owner
decision, not a fix.

---

**Symptom:** Weekly job green, but `no corporate_actions.csv — EPS will not be
restated for splits this run` appears in the ingest log.

**Cause:** Known gap, see 9.1. Not a failure.

---

**Symptom:** A few symbols say `QUARANTINED` every day (fewer than 15, so
the run passes).

**Cause:** Usually a corporate action the updater could not verify, or a
symbol Yahoo has renamed or stopped serving. As of 30 September: HEG,
INDIAGLYCO, PGIL, POLICYBZR.

**Fix:** Run a dry run against just those symbols to see the reason — it
writes nothing:
```
python FF_OHLC_Updater_v2.py --dry-run --symbols HEG,INDIAGLYCO,PGIL,POLICYBZR
```
(Needs `pip install yfinance pandas` and internet; simplest to add a temporary
manual workflow, as `market_probe.yml` once did.) If the reason is a genuine
split the price does not confirm, that is a data decision. If Yahoo has
renamed the symbol, `yahoo_fetch()` builds the ticker as `f"{symbol}.NS"` and
has **no mapping table today** — one would have to be added there.

---

### 6.4 Things that look like failures but are not

- **Warnings about `absent, not added: corporate_actions.csv`** — expected.
- **Weekly run commits 1,240 rows of `-1.642` → `-1.6420000000000001`** —
  float formatting noise, no data change.
- **`FF_market_update.py` prints an error but the run is green** — by design;
  the strip is optional and must never take the positions down.
- **6M column shows a dash for the Nifty rows** — fills itself in around
  March 2027 as `market_history.csv` grows.

---

## 7. Doing things yourself

### 7.1 Tools you need

- **GitHub Desktop** — to see changes, commit and push. Always **Fetch/Pull**
  before you edit anything; the daily job commits every evening.
- **A text editor** — VS Code or Notepad++. Never Word.
- **Python 3** on the laptop, for `FF_healthcheck.py` and
  `make_context_pack.py` (no packages needed). **Not installed by default on
  Windows.** If typing `python` says *"Python was not found; run without
  arguments to install from the Microsoft Store"*, or opens the Store, Python
  is missing. What worked on 30 September 2026 (first fire drill):
  1. Install **Python Install Manager** from the Microsoft Store page that
     opens (publisher: Python Software Foundation).
  2. Open a **new** Command Prompt and type `py install default`. (Plain
     `py install` without `default` gives an error. Typing `py --version`
     also works — with no Python present it installs the latest release
     automatically.)
  3. If it asks to add a directory to PATH, answer `y`.
  4. Check with `py --version`.
  From then on use **`py`**, not `python`. If `py` is "not recognized":
  Start → *Manage app execution aliases* → turn **off** "App Installer —
  python.exe / python3.exe", toggle "Python (default)" and "Python install
  manager" off and on, open a new Command Prompt.
- **How to run a script from the repository** — Start → type `cmd` → open
  Command Prompt, then type exactly:
  ```
  cd C:\Users\hp\GitHub\ff-live-dashboard
  py FF_healthcheck.py
  ```
  The `cd` line matters: without it Windows looks for the file in the wrong
  folder.
- **The GitHub website** — Actions tab for logs and manual runs; Settings for
  the org.

### 7.2 Editing a file safely

1. Fetch in GitHub Desktop first.
2. Make the change.
3. If it is a Python script with a `--selftest`, run it:
   `py FF_OHLC_Updater_v2.py --selftest` — needs `py -m pip install pandas numpy`
   once. `ALL CHECKS PASSED` or do not commit.
4. Commit with a message that says **why**, not just what. The existing
   history is the model.
5. Push. Then Actions → Run workflow → watch it.

### 7.3 Things never to do

- Never edit a file in `ohlc_data/` by hand.
- Never edit `FF_FINAL_v5_n500.csv`.
- Never edit `signal_ledger.csv` except to *append*.
- Never run `FF_Yahoo_OHLC_Updater.py` or any script in 4.4.
- Never change a number in Section 2 to make a test pass.
- Never commit a token, password or API key.
- Never remove a gate because it fired. Find out why it fired.

---

## 8. Getting help from an AI

There are three tiers. Use the lowest one that works.

### Tier 1 — the runbook (this file) and `FF_healthcheck.py`

Most failures are in 6.3. The health check says what is wrong in plain
English.

### Tier 2 — free Claude (claude.ai), or any AI that accepts file uploads

1. In the repository folder run:
   ```
   py make_context_pack.py
   ```
   It creates, **one level up** (next to the repository folder, so git never
   sees them):
   - `FF_CONTEXT_CORE.md` — **one text file, ~0.2 MB: everything needed to
     fix a pipeline failure.** Start with this one.
   - `FF_CONTEXT_ALL.md` — one text file, ~0.6 MB: the core plus the strategy
     methodology, the data-integrity history, the universe and the reference
     backtest. For questions about the strategy itself, or a failing
     acceptance test.
   - `ff_context_pack\` — the same content as a folder of files, and
     `ff_context_pack.zip` — zipped, for tools that take a zip
   It also runs the health check and includes its output, and records the
   last 15 commits and any uncommitted changes.
2. Start a new chat. Upload `FF_CONTEXT_CORE.md` (or the individual files —
   `HANDOVER.md` first, then whatever the failure points to).
3. Paste the contents of `handover/AI_PROMPT.md` as your first message. It
   tells the AI the constraints, how to work, and what it must never change.
4. Then paste the last 30 lines of the failing step.

If the AI's plan supports Projects, put the pack in a Project's knowledge
once; every chat then sees it.

**What is set up today (30 September 2026).** Priyanshu's free claude.ai
account has a Project, *FF DASHBOARD MANTAINANCE*, with project instructions
based on `handover/AI_PROMPT.md`. Its **Context** holds the repository's key
files added with **+ → Add from GitHub**, so they can be refreshed with
**Sync** instead of rebuilding a pack. Selected: the whole `.github/` and
`handover/` folders, `HANDOVER.md`, the ten live scripts in Section 4.1,
`signal_ledger.csv` and `docs/data/meta.json` — about 14% of the free
project's capacity. The picker shows each item's share of capacity; **never
add `ohlc_data/` (it alone is ~4,500%) or `fund_flags_v3.csv`**, and avoid
`indices/` and the whole `docs/` folder — not needed to diagnose the pipeline. When asking for help, click Sync first, then paste the failing
step's last 30 lines; paste `py FF_healthcheck.py` output too if you can. Tested
30 September on the 28 September NaN log: it matched the 6.3 entry and proposed
no change.

### Tier 3 — any other AI (ChatGPT, Gemini, a local model)

Same files, same prompt. `FF_CONTEXT_CORE.md` is plain Markdown; every tool
reads it. If it is too large for the tool, upload `HANDOVER.md` +
`handover/AI_PROMPT.md` + the one script the failing step names.

### What to demand from any AI, every time

- It must read `HANDOVER.md` Section 2 and repeat the frozen rules back before
  proposing anything.
- It must explain the cause **before** offering a fix, and name the evidence.
- It must give you the **complete file**, not a fragment to splice in.
- It must tell you which self-test to run and what "pass" looks like.
- It must give you the commit message.
- If it proposes removing a gate, loosening a tolerance, or changing anything
  in Section 2, **stop and ask a human who knows the strategy.**

---

## 9. Known open issues (30 September 2026)

Recorded from the full repository audit of 29 September
(`handover/notes/FF_Repository_Audit_2026-09-29.md`). None is urgent; all are
real.

### 9.1 New corporate actions do not reach the fundamentals

`FF_fundamentals_ingest_v3.py` restates EPS for splits by reading
`corporate_actions.csv`. **Nothing writes that file.** The price updater vets
splits every day but records none of them. Historical splits are already in
`split_factor` (9,732 rows), so the base is correct up to the v3 seed (early
September 2026). From then on, a split rescales the price history correctly
but leaves EPS on the old scale, which suppresses that symbol's 8-quarter EPS
test for eight quarters. **Fix:** make `FF_OHLC_Updater_v2.py` append each
accepted action to `corporate_actions.csv` (`symbol,ex_date,factor,applied`).
The ingest already knows how to read it.

### 9.2 Silently stale symbols

Symbols quarantined every day are invisible because 4 < 15 and the quarantine
list is gitignored. See 6.3, last entry. **Fix:** commit
`ohlc_quarantine.txt`, or have the health check's "symbols behind" list looked
at monthly (it does this).

### 9.3 Repository growth

`.git` is ~1.1 GB after seven weeks: every daily commit rewrites 751 CSVs.
~20 MB/day → ~4–5 GB in a year. GitHub warns above 1 GB and gets slow. Options,
in order of effort: (a) `git gc` locally now and then; (b) store prices as one
consolidated file rewritten daily instead of 751 (one blob per day, far
smaller history); (c) Git LFS for `ohlc_data/`; (d) periodically squash
history. Decide before ~March 2027.

### 9.4 Unpinned dependencies

Both workflows `pip install` without versions. See 6.3. **Fix:** pin every
package to the versions in the last green run's `Successfully installed` line
and bump them deliberately. **Done 30 September 2026 as an interim step:**
the daily workflow now writes `pip freeze > handover/last_run_versions.txt`
and commits it, so the versions of every green run are in git history, not
in a log that expires after 90 days. Pinning itself is still open.

### 9.4b Two small improvements to the updater's own evidence

Found by a blind test of this handover (an AI given only the context pack and
an invented failure). Neither is urgent; both make the next diagnosis faster.

- `ohlc_update_report.json` records each symbol's notes but not what was
  fetched. One note per symbol — `fetched N rows, first D1, last D2` — would
  have settled the invented failure instantly. Add it in `update_one()`.
- `check_overlap()` in `FF_OHLC_Updater_v2.py` is dead code that prints the
  same message as the live path (`overlap_ratio()` returning `None` in
  `update_one()`). A search for the message lands on the wrong function.
  Delete it.

### 9.5 Orphan files

Section 4.4. Delete when convenient; `FF_Yahoo_OHLC_Updater.py` first.

### 9.6 Hardcoded backtest figures in the dashboard

`docs/index.html` carries the information-panel figures as constants (279
closed of 358, to July 2026). Correct today; nothing updates them. When the
reference set is next regenerated, update `BACKTEST` in the page by hand.

### 9.7 Product items, not pipeline items

Compliance footer needs the entity name, SEBI RA number, address and
grievance details. Real India 10-year **yield** needs an FBIL/CCIL source (the
NSE G-Sec index is not a yield). Micro Cap needs its own 8-quarter flag rebuild
before it can be published. Model Portfolio engine must be re-run on the
358-trade set. Survivorship bias remains unquantified.

---

## 10. Dead ends — do not retry these

Each cost a run or a day. They are recorded so nobody spends it again.

| Tried | Result |
|---|---|
| Yahoo history for `NIFTY_MICROCAP250.NS` or `NIFTYGS10YR.NS` | Live quote only; **no historical data at all** (verified on Yahoo's own page) |
| NSE `/api/historical/indicesHistory` from a GitHub runner | **Blocked** — serves a `noindex` page, even for the Nifty 500 control |
| MCX price pages (three URL forms) | **403** everywhere |
| Adding `br` (brotli) to `Accept-Encoding` in a `requests` scraper | Every response becomes unreadable — `requests` cannot decode brotli without an extra package. Use `gzip, deflate` only |
| `^TNX` as "India 10Y" | That is the **US** 10-year |
| Comparing 252-trading-day and 365-calendar-day returns | Disagree by ~2 pp on the same index. All windows are calendar days: 7/30/182/365 |
| Storing index history at 6 significant figures | Wrote `23090` for `23089.95`. Use 2 decimals |
| Running the yfinance fetch from a laptop or a Claude sandbox | Yahoo and NSE are blocked from both by proxy. **Only the GitHub runner reaches them** |
| Concluding from a stale local clone | Done twice; wrong both times. Fetch first |

---

## 11. Accounts and access

- GitHub organisation **`finsights-in`**, owner Priyanshu
  (`priyanshuagarwal8430-dotcom`). Himanshu is a member. The org's Actions
  policy allows all actions; the Pages source is the `docs/` folder on `main`.
- The dashboard URL is public. It is not shared with clients (decision 8
  September 2026). GitHub Pages cannot be password-protected on a free plan;
  Cloudflare Pages + Access can, and needs a domain. Decide before any client
  gets the link.
- **No secrets exist in this repository or its workflows.** The pipeline uses
  only public, unauthenticated sources. Keep it that way.
- **The org must always have two owners.** If one account is lost, the other
  can still manage the repository, Actions and Pages. Check at
  https://github.com/orgs/finsights-in/people — both Priyanshu and Himanshu
  should show the role **Owner**.

---

## 12. Glossary

| Term | Meaning |
|---|---|
| ATH | All-time-high **closing** price, from 1995 |
| Trigger date | The day all entry conditions were met, evaluated after close |
| Entry date / price | Next trading day, at its Open |
| Target | The ATH as at the trigger date. Fixed |
| Time stop / cap | Exit at 1,095 days if the target has not been reached |
| Armed / disarmed | Whether a stock may fire; disarmed after a signal until a new ATH close |
| `avail_date` | The first date a quarter's results could be used (its announcement date) |
| `all_hi_pos` | The qualifying flag: 8-quarter high on all three metrics **and** all positive |
| Quarantine | The updater's refusal to write a symbol it could not verify. Its stored data is untouched |
| Reference set | `FF_FINAL_v5_n500.csv`, 358 trades — what the acceptance test reproduces |
| XIRR | Money-weighted return; the Advisory product's metric |
| CAGR | Time-weighted return; the Model Portfolio's metric |
| Run-off | Model Portfolio measurement: stop buying after 3 years, let every holding finish |
