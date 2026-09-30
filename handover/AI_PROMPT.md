# Prompt to paste into any AI

Copy everything below the line into a new chat, after uploading
`FF_CONTEXT_ALL.md` (or `HANDOVER.md` plus the files the failure points to).
Then paste the last 30 lines of the failing step, or describe what you see.

---

I maintain an automated stock-strategy pipeline called **Fundamental First**
that runs on GitHub Actions and publishes a dashboard to GitHub Pages. I am not
a programmer. I have uploaded the repository's handover file and the relevant
code and data. I need your help to diagnose and fix a problem.

**Before you do anything else, read `HANDOVER.md` in full.** Then confirm to me,
in your own words, the frozen rules in its Section 2 — especially that the exit
target is the all-time-high close as at the trigger date and never moves, that
there is no stop-loss, and that the threshold is 0.60. If you cannot see
`HANDOVER.md`, tell me and stop.

**How to work with me:**

1. **Diagnose first, fix second.** Tell me what you think the cause is and
   what evidence in the files or the log supports it. If you are guessing, say
   so. Do not propose a change until you have named the cause.
2. **One step at a time.** Do not bundle several changes together. Tell me
   what you want to do, wait for me to say yes, then do it.
3. **Never run or ask me to run anything that writes to the data files**
   (`ohlc_data/`, `fund_flags_v3.csv`, `signal_ledger.csv`,
   `FF_FINAL_v5_n500.csv`) without first explaining exactly what will change.
   Prefer `--selftest` and `--dry-run`, which write nothing.
4. **Give me complete files**, never fragments. If you change a Python script,
   give me the whole script so I can replace the file. If you change a workflow
   YAML, give me the whole YAML. Indentation matters in both.
5. **Tell me how to verify.** Which self-test to run, what "pass" looks like,
   and what to look for in the Actions log after I re-run the workflow.
6. **Give me a commit message** — a one-line summary and a short description
   that says why the change was made, in the style of the existing history.
7. **Never change the strategy rules** in Section 2 of `HANDOVER.md`, never
   remove or loosen a gate or tolerance to make a run pass, and never suggest
   editing the reference backtest file. If you believe one of those is
   genuinely the cause, say so plainly and stop; that is a decision for the
   strategy owner, not a bug fix.
8. **If the problem is in Section 6.3 of `HANDOVER.md`**, say which entry it
   is and apply that fix. Do not invent a new one.
9. **Do not add features.** Fix the problem I described and nothing else. No
   extra options, no refactoring, no "while we're here".
10. **Be honest about limits.** If you need a file I have not uploaded, name it.
    If the log is not enough, tell me exactly which lines you need.

The pipeline runs only on GitHub Actions. My laptop and any AI sandbox are
blocked from Yahoo and NSE, so network tests must be done as a manual workflow
run, not locally.

I will now paste the error.
