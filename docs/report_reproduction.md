# Report links and reproduction

The written report cites fixed snapshots: `d95edd3c3c7c4fbdc5a3a5955423e9961ced5e95` for the course stages and `4eacac41c3fca3c02262c46ed0a1b5a904e087d0` for supplementary tracking. These commits remain in repository history. Their URLs remain valid after merging and changing repository visibility; neither the owner nor repository name changes.

## Current reproduction commands

```bash
python3 -m pip install -r requirements.txt
python3 run_all.py --all
python3 run_research_2026.py
```

The first analysis command rebuilds the four course stages. The second independently refreshes Stage 1 and reproduces baseline 2026 tracking, covariance-only Ledoit–Wolf sensitivity and ledger validation. All computation uses cached inputs, with no authentication or downloads. The optional source-fetch utility needs `requests` and an environment-provided `MASSIVE_API_KEY`; it is not part of either reproduction command.

## Report locations affected by consolidation

- Main report page 9: tracking and shrinkage evidence now also lives on main under `research_2026/`; original pinned links remain valid.
- Appendix B, PDF page 12: includes both the course command and `python3 run_research_2026.py`, with separate reproduction instructions for supplementary evidence.
- Appendix G3, PDF page 22: `research_2026/README.md` and `research_2026/ledoit_wolf/README.md` keep their relative paths and are now part of main. The code index includes the supplementary entry point.
- Fixed commit links can remain unchanged for reproducibility. Use main-relative links in repository Markdown for current navigation.

The repository report, [`FE5108_Project_Report.pdf`](../FE5108_Project_Report.pdf), is the 23-page revised v8. Pages 12 and 22 document the supplementary reproduction entry point. Pages 2 and 12 clarify the Massive-derived daily-return inputs; Appendix H (page 23) summarizes data processing, monthly validation and code availability. All other pages, including contribution signatures, are unchanged from revised v7. The PDF is an authored document and is not rewritten by either command.

## Evidence scope

The 2026 observation window is January 2 open through October 6 close, not the full year. The four report portfolios are sample tangency, Ledoit–Wolf tangency, value weights and equal weights. Text-distance allocations are retained as historical optional research, use SVD-space distances, and are not report evidence. No new performance observations or alternative strategy rules are introduced by the merge.

Public visibility permits anyone to access repository files and history; it is not a teacher-only access setting. Cached observations and sanitized provider responses are retained. Credentials and local daily-data directories remain excluded. Public visibility does not grant additional redistribution rights to third-party data.
