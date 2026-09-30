"""
FF context pack
============================================================================
Bundles everything an AI (or a new maintainer) needs to understand and fix
this repository, small enough to upload anywhere.

    python make_context_pack.py

Writes, ONE LEVEL UP from the repository (so git never sees them):

    ../ff_context_pack/          a folder of the files, ready to upload one by one
    ../ff_context_pack.zip       the same folder, zipped
    ../FF_CONTEXT_ALL.md         everything in ONE Markdown file, for tools that
                                 take a single upload (free Claude, ChatGPT, ...)

It also runs FF_healthcheck.py and includes its output, and records the last
commits and any uncommitted changes, so the pack always describes the
repository as it is right now.

Needs only Python. Reads the repository; never writes inside it.
"""

import datetime as dt
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(ROOT)
PACK = os.path.join(PARENT, "ff_context_pack")
ZIP = os.path.join(PARENT, "ff_context_pack.zip")
ALL = os.path.join(PARENT, "FF_CONTEXT_ALL.md")
CORE = os.path.join(PARENT, "FF_CONTEXT_CORE.md")

# The operational core: enough to diagnose and fix a pipeline failure, small
# enough (~200 KB) for a free-tier AI. Everything else is background for when
# the question is about the strategy itself.
CORE_FILES = {
    "HANDOVER.md", "handover/AI_PROMPT.md", "handover/notes/README.md",
    "handover/notes/FF_Daily_Job_Reliability.md",
    "handover/notes/FF_Repository_Audit_2026-09-29.md",
    ".github/workflows/daily_update.yml", ".github/workflows/weekly_fundamentals.yml",
    "FF_OHLC_Updater_v2.py", "FF_index_update.py", "FF_Signal_Engine_v2.py",
    "FF_Ledger.py", "FF_market_update.py", "FF_dashboard_data.py", "FF_news.py",
    "FF_Fixed_Gemini_Scraper.py", "merge_retry.py", "FF_fundamentals_ingest_v3.py",
    "docs/data/meta.json", "docs/data/market.json", "signal_ledger.csv",
    "ohlc_data/RELIANCE.SAMPLE.csv", ".gitignore",
    "HEALTHCHECK_OUTPUT.txt", "GIT_STATE.txt", "MANIFEST.md",
}

# What goes in, in the order an AI should read it.
FILES = [
    # 1. orientation
    "HANDOVER.md",
    "handover/AI_PROMPT.md",
    "handover/notes/README.md",
    "README.md",
    # 2. how it runs
    ".github/workflows/daily_update.yml",
    ".github/workflows/weekly_fundamentals.yml",
    # 3. the live pipeline
    "FF_OHLC_Updater_v2.py",
    "FF_index_update.py",
    "FF_Signal_Engine_v2.py",
    "FF_Ledger.py",
    "FF_market_update.py",
    "FF_dashboard_data.py",
    "FF_news.py",
    "FF_Fixed_Gemini_Scraper.py",
    "merge_retry.py",
    "FF_fundamentals_ingest_v3.py",
    "FF_healthcheck.py",
    "docs/index.html",
    # 4. small data the AI can reason about
    "ident.csv",
    "tickers.txt",
    "signal_ledger.csv",
    "watchlist_ledger.csv",
    "signals.csv",
    "fresh_signals.csv",
    "FF_FINAL_v5_n500.csv",
    "docs/data/meta.json",
    "docs/data/positions.json",
    "docs/data/closed.json",
    "docs/data/market.json",
    "docs/data/index.json",
    "indices/market_history.csv",
    ".gitignore",
    ".gitattributes",
]

# Large files: include a representative sample, not the whole thing.
SAMPLE_PRICE_FILES = ["RELIANCE", "ZYDUSWELL", "OLECTRA"]
FUND_SAMPLE_ROWS = 400            # first rows of fund_flags_v3.csv
INDEX_TAIL_ROWS = 300             # last rows of indices/Nifty500.csv

# Notes: every markdown file under handover/notes/
NOTES_DIR = os.path.join(ROOT, "handover", "notes")

TEXT_EXT = (".md", ".py", ".yml", ".yaml", ".html", ".json", ".txt", ".csv",
            ".gitignore", ".gitattributes")


def run(cmd):
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                             timeout=120)
        return (out.stdout or "") + (out.stderr or "")
    except Exception as e:
        return f"(could not run {' '.join(cmd)}: {e})\n"


def head(path, n):
    with open(path, encoding="utf-8", errors="replace") as f:
        return "".join(f.readline() for _ in range(n))


def tail_with_header(path, n):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return lines[0] + "".join(lines[-n:]) if lines else ""


def main():
    if os.path.exists(PACK):
        try:
            shutil.rmtree(PACK)
        except OSError:
            print("  (could not clear the old pack folder; overwriting in place)")
    os.makedirs(PACK, exist_ok=True)
    included = []       # (relative name in pack, absolute source, note)

    def add_copy(rel):
        src = os.path.join(ROOT, *rel.split("/"))
        if not os.path.exists(src):
            print(f"  skip (absent): {rel}")
            return
        dst = os.path.join(PACK, *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        included.append((rel, dst, ""))

    def add_text(rel, text, note):
        dst = os.path.join(PACK, *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(text)
        included.append((rel, dst, note))

    print("Collecting files ...")
    for rel in FILES:
        add_copy(rel)

    if os.path.isdir(NOTES_DIR):
        for fn in sorted(os.listdir(NOTES_DIR)):
            if fn.endswith(".md") and fn != "README.md":
                add_copy(f"handover/notes/{fn}")

    for sym in SAMPLE_PRICE_FILES:
        src = os.path.join(ROOT, "ohlc_data", sym + ".csv")
        if os.path.exists(src):
            add_text(f"ohlc_data/{sym}.SAMPLE.csv", tail_with_header(src, 120),
                     f"last 120 rows of ohlc_data/{sym}.csv (751 such files exist)")

    ff = os.path.join(ROOT, "fund_flags_v3.csv")
    if os.path.exists(ff):
        add_text("fund_flags_v3.SAMPLE.csv", head(ff, FUND_SAMPLE_ROWS + 1),
                 f"first {FUND_SAMPLE_ROWS} rows of fund_flags_v3.csv (~37,000 rows exist)")

    ix = os.path.join(ROOT, "indices", "Nifty500.csv")
    if os.path.exists(ix):
        add_text("indices/Nifty500.SAMPLE.csv", tail_with_header(ix, INDEX_TAIL_ROWS),
                 f"last {INDEX_TAIL_ROWS} rows of indices/Nifty500.csv")

    print("Running the health check ...")
    hc = run([sys.executable, os.path.join(ROOT, "FF_healthcheck.py")])
    add_text("HEALTHCHECK_OUTPUT.txt", hc, "output of FF_healthcheck.py at pack time")

    print("Recording git state ...")
    git = ("$ git log --oneline -15\n" + run(["git", "log", "--oneline", "-15"])
           + "\n$ git status --short\n" + run(["git", "status", "--short"])
           + "\n$ git remote -v\n" + run(["git", "remote", "-v"]))
    add_text("GIT_STATE.txt", git, "recent commits and uncommitted changes at pack time")

    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    manifest = [f"# FF context pack - built {stamp}", "",
                "Read in this order: HANDOVER.md, handover/AI_PROMPT.md, then whatever",
                "the failure points to. HEALTHCHECK_OUTPUT.txt says what is wrong right now.",
                "", "| file | note |", "|---|---|"]
    for rel, dst, note in included:
        manifest.append(f"| `{rel}` | {note} |")
    add_text("MANIFEST.md", "\n".join(manifest) + "\n", "this list")

    # ---- single-file versions -----------------------------------------------
    def write_single(path, title, only=None):
        with open(path, "w", encoding="utf-8") as out:
            out.write(f"# {title} - built {stamp}\n\n")
            out.write("This one file contains the Fundamental First repository's handover "
                      "document, its live pipeline, its workflows, samples of its data and "
                      "the current health-check output. Each section below is one file, "
                      "introduced by a heading with its path.\n\n"
                      "READ `HANDOVER.md` FIRST (it is the first section).\n\n")
            out.write(f"**Built {stamp}.** The health-check output and git state inside "
                      "describe the repository at that moment. If the failure you are "
                      "asking about happened AFTER this time, the evidence here predates "
                      "it - run `python make_context_pack.py` again and upload the fresh "
                      "file.\n\n")
            if only is not None:
                out.write("This is the CORE pack: operations only. The full pack "
                          "(FF_CONTEXT_ALL.md) adds the strategy methodology, the data "
                          "integrity history, the universe file and the reference "
                          "backtest.\n\n")
            for rel, dst, note in included:
                if not rel.endswith(TEXT_EXT):
                    continue
                if only is not None and rel not in only:
                    continue
                if rel == "MANIFEST.md" and only is not None:
                    txt = ("# Files in this CORE pack\n\n| file | note |\n|---|---|\n"
                           + "\n".join(f"| `{r}` | {n} |" for r, _, n in included
                                       if r in only and r.endswith(TEXT_EXT)) + "\n")
                else:
                    try:
                        txt = open(dst, encoding="utf-8", errors="replace").read()
                    except OSError:
                        continue
                lang = {".py": "python", ".yml": "yaml", ".yaml": "yaml", ".html": "html",
                        ".json": "json", ".csv": "csv", ".md": "", ".txt": ""}
                ext = os.path.splitext(rel)[1]
                fence = lang.get(ext, "")
                out.write(f"\n\n---\n\n## FILE: `{rel}`" + (f"  ({note})" if note else "") + "\n\n")
                if ext == ".md":
                    out.write(txt)
                else:
                    out.write(f"```{fence}\n{txt}\n```\n")

    print("Writing the single-file versions ...")
    write_single(CORE, "FF CONTEXT PACK (CORE)", only=CORE_FILES)
    write_single(ALL, "FF CONTEXT PACK (ALL)")

    # ---- zip -------------------------------------------------------------------
    print("Zipping ...")
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(PACK):
            for f in fn:
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, PARENT))

    def mb(path):
        return os.path.getsize(path) / 1e6

    folder_mb = sum(os.path.getsize(os.path.join(dp, f))
                    for dp, dn, fn in os.walk(PACK) for f in fn) / 1e6
    print("\nDone.")
    print(f"  folder : {PACK}   ({len(included)} files, {folder_mb:.1f} MB)")
    print(f"  zip    : {ZIP}   ({mb(ZIP):.2f} MB)")
    print(f"  CORE   : {CORE}   ({mb(CORE):.2f} MB)  <- start here for a pipeline fix")
    print(f"  ALL    : {ALL}   ({mb(ALL):.2f} MB)  <- when the question is about the strategy")
    print("\nNext: open a new chat with any AI, upload FF_CONTEXT_CORE.md (or the folder's"
          "\nfiles, HANDOVER.md first), paste handover/AI_PROMPT.md as your first message,"
          "\nthen paste the last 30 lines of the failing step.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
