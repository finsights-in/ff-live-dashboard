"""
FF health check
============================================================================
Answers one question in plain language: is the Fundamental First pipeline in
the state it is supposed to be in?

    python FF_healthcheck.py            # quick: reads the tail of every file
    python FF_healthcheck.py --full     # also scans every row of every price
                                        # file (about 30 seconds)

Needs nothing but Python 3.8 or newer. No pip install. Reads files only -
it never writes, deletes or changes anything, so it is always safe to run.

Every line it prints is PASS, WARN or FAIL, followed by what was found, and
for WARN and FAIL a one-line "-> what to do" that points into HANDOVER.md.

Exit code: 0 when nothing failed (warnings allowed), 2 when something failed.
"""

import csv
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FULL = "--full" in sys.argv
TODAY = dt.date.today()

RESULTS = []      # (level, title, detail, action)


def rec(level, title, detail="", action=""):
    RESULTS.append((level, title, detail, action))


def p(*parts):
    return os.path.join(ROOT, *parts)


def exists(*parts):
    return os.path.exists(p(*parts))


def read_text(*parts):
    with open(p(*parts), encoding="utf-8", errors="replace") as f:
        return f.read()


def tail_lines(path, n=60, chunk=16384):
    """Last n complete lines of a text file without reading the whole file."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - chunk))
        data = f.read().decode("utf-8", errors="replace")
    lines = data.splitlines()
    if size > chunk and lines:
        lines = lines[1:]                 # first line is probably partial
    return [ln for ln in lines if ln.strip()][-n:]


def header_line(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.readline().strip()


def parse_date(s):
    try:
        return dt.date.fromisoformat(s[:10])
    except Exception:
        return None


def weekday_before(d, days):
    """Calendar days back, then step back to a weekday."""
    x = d - dt.timedelta(days=days)
    while x.weekday() >= 5:
        x -= dt.timedelta(days=1)
    return x


# --------------------------------------------------------------------------
# 1. layout
# --------------------------------------------------------------------------

REQUIRED = [
    ".github/workflows/daily_update.yml",
    ".github/workflows/weekly_fundamentals.yml",
    "FF_OHLC_Updater_v2.py", "FF_index_update.py", "FF_Signal_Engine_v2.py",
    "FF_Ledger.py", "FF_market_update.py", "FF_dashboard_data.py", "FF_news.py",
    "FF_Fixed_Gemini_Scraper.py", "merge_retry.py", "FF_fundamentals_ingest_v3.py",
    "ident.csv", "fund_flags_v3.csv", "FF_FINAL_v5_n500.csv", "tickers.txt",
    "signal_ledger.csv", "watchlist_ledger.csv",
    "indices/Nifty500.csv", "docs/index.html",
    "docs/data/meta.json", "docs/data/positions.json", "docs/data/closed.json",
    "docs/data/index.json", "docs/data/market.json", "docs/data/news.json",
    "HANDOVER.md",
]


def check_layout():
    missing = [f for f in REQUIRED if not exists(*f.split("/"))]
    if missing:
        rec("FAIL", "Repository layout",
            "missing: " + ", ".join(missing),
            "Restore from git (GitHub Desktop -> History) or re-clone. HANDOVER.md section 4.")
    else:
        rec("PASS", "Repository layout", f"all {len(REQUIRED)} required files present")


# --------------------------------------------------------------------------
# 2. workflows
# --------------------------------------------------------------------------

def check_workflows():
    for name, want_cron in (("daily_update.yml", "30 13 * * 1-5"),
                            ("weekly_fundamentals.yml", "30 4 * * 0")):
        path = p(".github", "workflows", name)
        if not os.path.exists(path):
            continue
        txt = read_text(".github", "workflows", name)
        problems, notes = [], []
        if want_cron not in txt:
            problems.append(f"schedule is not '{want_cron}'")
        # the exit-128 class: a bare git add of a named file outside the guard loop
        bare_adds = [ln.strip() for ln in txt.splitlines()
                     if re.match(r"\s*git add\s+\S", ln) and '"$f"' not in ln
                     and "-A" not in ln and "." != ln.strip().split()[-1]]
        if bare_adds:
            problems.append("bare 'git add <file>' outside the existence loop: "
                            + "; ".join(bare_adds[:3]))
        if 'if [ -e "$f" ]' not in txt and "git add" in txt:
            problems.append("commit step has no existence-checking loop")
        if "--autostash" not in txt and "git pull" in txt:
            problems.append("git pull without --autostash")
        m = re.search(r"pip install ([^\n]+)", txt)
        if m and "==" not in m.group(1):
            notes.append("dependencies are unpinned (known, HANDOVER.md 9.4)")
        if problems:
            rec("FAIL", f"Workflow {name}", "; ".join(problems),
                "HANDOVER.md section 6.3, the exit-128 and rebase entries.")
        else:
            rec("PASS", f"Workflow {name}",
                "schedule, add-loop and autostash all present"
                + ("; " + "; ".join(notes) if notes else ""))


# --------------------------------------------------------------------------
# 3. price files
# --------------------------------------------------------------------------

HDR = "Date,Close,High,Low,Open,Volume"


def check_prices():
    d = p("ohlc_data")
    if not os.path.isdir(d):
        rec("FAIL", "Price files", "ohlc_data/ folder is missing",
            "Restore from git. Nothing else can run without it.")
        return set()
    files = sorted(f for f in os.listdir(d) if f.endswith(".csv"))
    if len(files) < 700:
        rec("FAIL", "Price files", f"only {len(files)} price files (expected 751)",
            "Some files are missing. Restore from git history.")
    last = {}
    bad_hdr, blanks, nonpos, hl, unsorted_, dup = [], [], [], [], [], []
    for fn in files:
        sym = fn[:-4]
        path = os.path.join(d, fn)
        if header_line(path) != HDR:
            bad_hdr.append(sym)
            continue
        rows = tail_lines(path, 60)
        if FULL:
            with open(path, encoding="utf-8", errors="replace") as f:
                rows = [ln.strip() for ln in f.readlines()[1:] if ln.strip()]
        prev = None
        seen = set()
        nb = nnp = nhl = 0
        for ln in rows:
            parts = ln.split(",")
            if len(parts) < 6:
                nb += 1
                continue
            dte = parts[0]
            if dte in seen:
                dup.append(sym)
            seen.add(dte)
            if prev and dte < prev:
                unsorted_.append(sym)
            prev = dte
            if dte < "2004-01-01":
                continue
            try:
                c, h, l, o = (float(parts[1]), float(parts[2]),
                              float(parts[3]), float(parts[4]))
            except ValueError:
                nb += 1
                continue
            if any(x != x for x in (c, h, l, o)):
                nb += 1
                continue
            if min(c, h, l, o) <= 0:
                nnp += 1
            if h < max(o, c, l) - 1e-6 or l > min(o, c, h) + 1e-6:
                nhl += 1
        if rows:
            last[sym] = rows[-1].split(",")[0]
        if nb:
            blanks.append(sym)
        if nnp:
            nonpos.append(sym)
        if nhl:
            hl.append(sym)

    scope = "every row" if FULL else "the last 60 rows"
    structural = []
    if bad_hdr:
        structural.append(f"{len(bad_hdr)} wrong header ({', '.join(bad_hdr[:5])})")
    if blanks:
        structural.append(f"{len(blanks)} with blank/NaN prices ({', '.join(blanks[:5])})")
    if nonpos:
        structural.append(f"{len(nonpos)} with zero/negative prices ({', '.join(nonpos[:5])})")
    if hl:
        structural.append(f"{len(hl)} where High/Low is not the high/low ({', '.join(hl[:5])})")
    if sorted(set(dup)):
        structural.append(f"{len(set(dup))} with duplicate dates ({', '.join(sorted(set(dup))[:5])})")
    if sorted(set(unsorted_)):
        structural.append(f"{len(set(unsorted_))} with dates out of order")
    if structural:
        rec("FAIL", f"Price file structure ({scope})", "; ".join(structural),
            "Data was written that the gates should have refused. Do NOT run the daily "
            "job until this is understood. HANDOVER.md 6.3, acceptance-test entry; "
            "git history of the affected file shows which commit changed it.")
    else:
        rec("PASS", f"Price file structure ({scope})",
            f"{len(files)} files: no blanks, no bad prices, no duplicate or unordered dates")

    # currency
    if last:
        counts = {}
        for v in last.values():
            counts[v] = counts.get(v, 0) + 1
        majority = max(counts, key=counts.get)
        maj_date = parse_date(majority)
        n_maj = counts[majority]
        stale = sorted((s, v) for s, v in last.items()
                       if parse_date(v) and maj_date and (maj_date - parse_date(v)).days > 5)
        age = (TODAY - maj_date).days if maj_date else 999
        if age > 10:
            rec("FAIL", "Price data currency",
                f"most files end on {majority} - {age} days ago",
                "The daily job has not completed for more than a week. Actions tab -> "
                "latest run -> red step -> last 30 lines. HANDOVER.md section 6.")
        elif age > 4:
            rec("WARN", "Price data currency",
                f"most files end on {majority} - {age} days ago",
                "More than one trading day behind. Check the Actions tab for a red run. "
                "HANDOVER.md 6.1.")
        else:
            rec("PASS", "Price data currency",
                f"{n_maj} of {len(last)} files end on {majority}")
        if stale:
            rec("WARN", "Symbols that have stopped updating",
                f"{len(stale)}: " + ", ".join(f"{s} ({v})" for s, v in stale[:10])
                + (" ..." if len(stale) > 10 else ""),
                "Each is quarantined daily for a reason the log does not keep. "
                "HANDOVER.md 6.3, last entry (dry run on these symbols).")
        else:
            rec("PASS", "Symbols that have stopped updating", "none")
    return {f[:-4] for f in files}


# --------------------------------------------------------------------------
# 4. universe
# --------------------------------------------------------------------------

def check_ident(price_syms):
    if not exists("ident.csv"):
        return
    with open(p("ident.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    syms = {r["symbol"] for r in rows}
    tiers = {}
    for r in rows:
        tiers[r.get("market_type")] = tiers.get(r.get("market_type"), 0) + 1
    only_ident = sorted(syms - price_syms)
    only_files = sorted(price_syms - syms)
    if only_ident or only_files:
        rec("FAIL", "Universe file vs price files",
            (f"in ident.csv but no price file: {only_ident[:8]}; " if only_ident else "")
            + (f"price file but not in ident.csv: {only_files[:8]}" if only_files else ""),
            "The engine reads ident.csv for the universe. Every symbol must have a "
            "price file and vice versa. HANDOVER.md 4.2.")
    else:
        rec("PASS", "Universe file vs price files",
            f"{len(syms)} symbols, one price file each; tiers "
            + ", ".join(f"{k} {v}" for k, v in sorted(tiers.items(), key=lambda z: str(z[0]))))


# --------------------------------------------------------------------------
# 5. fundamentals
# --------------------------------------------------------------------------

def check_fundamentals():
    if not exists("fund_flags_v3.csv"):
        return
    newest = None
    n = 0
    bad_avail = 0
    sources = {}
    qualifying = 0
    with open(p("fund_flags_v3.csv"), newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        needed = {"symbol", "report_date", "avail_date", "all_hi_pos",
                  "eps_adj", "split_factor", "source"}
        missing = needed - set(rd.fieldnames or [])
        if missing:
            rec("FAIL", "Fundamentals base columns",
                f"fund_flags_v3.csv is missing {sorted(missing)}",
                "The ingest wrote the wrong format. Restore the file from the last good "
                "commit. HANDOVER.md 4.2.")
            return
        for r in rd:
            n += 1
            rdate = parse_date(r["report_date"])
            adate = parse_date(r["avail_date"])
            if rdate and (newest is None or rdate > newest):
                newest = rdate
            if rdate and adate and adate < rdate:
                bad_avail += 1
            sources[r["source"]] = sources.get(r["source"], 0) + 1
            if r["all_hi_pos"] in ("True", "true", "1"):
                qualifying += 1
    if bad_avail:
        rec("FAIL", "Fundamentals look-ahead guard",
            f"{bad_avail} rows have avail_date before report_date",
            "A result can never be usable before its quarter ends. This would let the "
            "engine see the future. Find the rows and the commit that added them.")
    else:
        rec("PASS", "Fundamentals look-ahead guard", "avail_date never precedes report_date")
    if newest:
        age = (TODAY - newest).days
        src = ", ".join(f"{k} {v}" for k, v in sorted(sources.items()))
        if age > 110:
            rec("WARN", "Fundamentals currency",
                f"newest quarter is {newest} ({age} days ago); {n} rows; {src}",
                "A quarter is probably missing. Check the last weekly run "
                "(Actions -> Weekly Fundamentals Check). HANDOVER.md 3.2.")
        else:
            rec("PASS", "Fundamentals currency",
                f"newest quarter {newest}; {n} rows; {qualifying} qualifying; {src}")
    if not exists("corporate_actions.csv"):
        rec("WARN", "Corporate-action ledger",
            "corporate_actions.csv does not exist, so new splits are not reaching EPS",
            "Known gap. HANDOVER.md 9.1.")
    else:
        rec("PASS", "Corporate-action ledger", "corporate_actions.csv present")


# --------------------------------------------------------------------------
# 6. ledger and dashboard data
# --------------------------------------------------------------------------

def check_ledger_and_dashboard():
    led = []
    if exists("signal_ledger.csv"):
        with open(p("signal_ledger.csv"), newline="", encoding="utf-8") as f:
            led = list(csv.DictReader(f))
    n_open = sum(1 for r in led if r.get("status") == "OPEN")
    n_closed = sum(1 for r in led if r.get("status") not in ("OPEN", None, ""))
    future = [r["symbol"] for r in led if parse_date(r.get("entry_date", "")) and
              parse_date(r["entry_date"]) > TODAY]
    if future:
        rec("FAIL", "Signal ledger", f"entries dated in the future: {future[:5]}",
            "Impossible dates in the published record. Find the commit.")
    else:
        rec("PASS", "Signal ledger", f"{len(led)} rows: {n_open} open, {n_closed} closed")

    try:
        meta = json.load(open(p("docs", "data", "meta.json"), encoding="utf-8"))
        pos = json.load(open(p("docs", "data", "positions.json"), encoding="utf-8"))
        closed = json.load(open(p("docs", "data", "closed.json"), encoding="utf-8"))
        market = json.load(open(p("docs", "data", "market.json"), encoding="utf-8"))
        news = json.load(open(p("docs", "data", "news.json"), encoding="utf-8"))
        index = json.load(open(p("docs", "data", "index.json"), encoding="utf-8"))
    except Exception as e:
        rec("FAIL", "Dashboard data files", f"could not read docs/data: {e}",
            "A JSON file is missing or corrupt. The page will show 'loading'. "
            "Re-run the daily workflow; if it fails, HANDOVER.md section 6.")
        return
    problems = []
    if meta.get("open") != len(pos):
        problems.append(f"meta.open={meta.get('open')} but positions.json has {len(pos)}")
    if meta.get("closed") != len(closed):
        problems.append(f"meta.closed={meta.get('closed')} but closed.json has {len(closed)}")
    if n_open and meta.get("open") != n_open:
        problems.append(f"ledger has {n_open} open but dashboard shows {meta.get('open')}")
    dates = {"meta": meta.get("as_of"), "index": meta.get("index_as_of"),
             "market": market.get("as_of"), "news": news.get("as_of")}
    if len({v for v in dates.values() if v}) > 1:
        problems.append("as_of dates disagree: " + ", ".join(f"{k}={v}" for k, v in dates.items()))
    as_of = parse_date(meta.get("as_of") or "")
    if problems:
        rec("FAIL", "Dashboard data consistency", "; ".join(problems),
            "The JSON files were built from different states. Re-run the daily workflow. "
            "If it recurs, HANDOVER.md section 6.")
    else:
        age = (TODAY - as_of).days if as_of else 999
        lvl = "PASS" if age <= 4 else ("WARN" if age <= 10 else "FAIL")
        rec(lvl, "Dashboard data consistency",
            f"as of {meta.get('as_of')}; {meta.get('open')} open, {meta.get('closed')} closed; "
            f"{len(market.get('rows', []))} market rows; news "
            + ", ".join(f"{k} {len(v)}" for k, v in news.items() if isinstance(v, list)),
            "" if lvl == "PASS" else
            "Dashboard is behind. Actions tab -> latest run. HANDOVER.md 6.1.")
    # index file currency
    if exists("indices", "Nifty500.csv"):
        last = tail_lines(p("indices", "Nifty500.csv"), 1)
        d = parse_date(last[0].split(",")[0]) if last else None
        if d and (TODAY - d).days > 10:
            rec("WARN", "Nifty 500 index file", f"ends {d}",
                "FF_index_update.py has not appended. Check the daily run's index step.")
        else:
            rec("PASS", "Nifty 500 index file", f"ends {d}")


# --------------------------------------------------------------------------
# 7. the .git folder
# --------------------------------------------------------------------------

def check_git():
    g = p(".git")
    if not os.path.isdir(g):
        rec("PASS", "Git folder", "no .git here (this is a plain copy, not a clone)")
        return
    locks = []
    for name in ("index.lock", "HEAD.lock", "ORIG_HEAD.lock", "config.lock",
                 os.path.join("objects", "maintenance.lock"), "packed-refs.lock"):
        if os.path.exists(os.path.join(g, name)):
            locks.append(name)
    if locks:
        rec("WARN", "Stale git lock files", ", ".join(locks),
            "Close GitHub Desktop, then in Command Prompt:  cd "
            + ROOT + "  &&  del " + " ".join(".git\\" + l.replace("/", "\\") for l in locks)
            + "   (HANDOVER.md 6.3, lock-file entry)")
    else:
        rec("PASS", "Stale git lock files", "none")
    total = 0
    for dp, dn, fn in os.walk(g):
        for f in fn:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    gb = total / 1e9
    tmp = []
    for dp, dn, fn in os.walk(os.path.join(g, "objects")):
        tmp += [f for f in fn if f.startswith("tmp_")]
    if gb > 2.0:
        rec("WARN", "Repository size", f".git is {gb:.2f} GB",
            "Growing ~20 MB per trading day. Decide on a storage change. HANDOVER.md 9.3.")
    else:
        rec("PASS", "Repository size", f".git is {gb:.2f} GB"
            + (f"; {len(tmp)} leftover tmp_* files from interrupted transfers (safe to delete)"
               if tmp else ""))


# --------------------------------------------------------------------------
# 8. secrets and orphans
# --------------------------------------------------------------------------

SECRET_RE = re.compile(r"(eyJ[A-Za-z0-9_-]{30,}|(?i:access[_-]?token|api[_-]?key|client[_-]?secret)\s*[=:]\s*['\"][A-Za-z0-9._-]{16,}['\"])")

ORPHANS = ["FF_Yahoo_OHLC_Updater.py", "FF_NSE_OHLC_Updater.py", "FF_fundamentals_ingest.py",
           "FF_Screener_Fundamentals_Scraper.py", "FF_build_dashboard.py",
           "FF_build_dashboard_v2.py", "FF_dashboard_template.html",
           "FF_Live_Tracking_Dashboard.html", "FF_Fresh_Signal_Scanner.py",
           "FF_datefix_compare.py", "FF_datefix_scan.py", "FF_rebuild_new.py",
           "FF_reseed_gapfill.py", "FF_seed_ohlc.py", "FF_market_probe.py",
           ".github/workflows/market_probe.yml", "fund_flags.csv",
           "results_dates.csv", "datefix_signals.csv"]


def check_secrets_and_orphans():
    hits = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [x for x in dn if x not in (".git", "ohlc_data", "__pycache__")]
        for f in fn:
            if f.endswith((".py", ".yml", ".yaml", ".html", ".json", ".txt", ".md", ".csv")):
                path = os.path.join(dp, f)
                if os.path.getsize(path) > 3_000_000:
                    continue
                try:
                    txt = open(path, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                if SECRET_RE.search(txt):
                    hits.append(os.path.relpath(path, ROOT))
    if hits:
        rec("FAIL", "Credentials in the repository", ", ".join(hits[:5]),
            "Something that looks like a token or key is committed. Remove it, rotate it, "
            "and rewrite history if it was pushed. HANDOVER.md 2.2.")
    else:
        rec("PASS", "Credentials in the repository", "nothing that looks like a token or key")
    present = [o for o in ORPHANS if exists(*o.split("/"))]
    if present:
        rec("WARN", "Unused files still present",
            f"{len(present)} (e.g. {', '.join(present[:4])})",
            "Safe to delete; FF_Yahoo_OHLC_Updater.py first. HANDOVER.md 4.4 and 9.5.")
    else:
        rec("PASS", "Unused files still present", "none")


# --------------------------------------------------------------------------

def main():
    print(f"FF health check   {dt.datetime.now():%Y-%m-%d %H:%M}   "
          f"{'full scan' if FULL else 'quick scan'}")
    print(f"repository: {ROOT}")
    print("-" * 78)
    check_layout()
    check_workflows()
    syms = check_prices()
    check_ident(syms)
    check_fundamentals()
    check_ledger_and_dashboard()
    check_git()
    check_secrets_and_orphans()

    for level, title, detail, action in RESULTS:
        print(f"{level:4}  {title}: {detail}")
    fails = [r for r in RESULTS if r[0] == "FAIL"]
    warns = [r for r in RESULTS if r[0] == "WARN"]
    print("-" * 78)
    if fails:
        print(f"VERDICT: BROKEN - {len(fails)} failure(s), {len(warns)} warning(s)")
    elif warns:
        print(f"VERDICT: RUNNING, ATTENTION NEEDED - {len(warns)} warning(s)")
    else:
        print("VERDICT: HEALTHY")
    todo = [(l, t, a) for l, t, d, a in RESULTS if a]
    if todo:
        print("\nWhat to do next:")
        for i, (l, t, a) in enumerate(todo, 1):
            print(f"  {i}. [{l}] {t}\n       -> {a}")
    print("\nIf this is not enough: python make_context_pack.py, then HANDOVER.md section 8.")
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
