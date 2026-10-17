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
- Appendix B, PDF page 12: keep the course command and add `python3 run_research_2026.py` for supplementary evidence. Replace “separate research-branch experiments” with “supplementary 2026 experiments, available through a separate entry point.”
- Appendix G3, PDF page 22 in the revised v6 report: `research_2026/README.md` and `research_2026/ledoit_wolf/README.md` keep their relative paths and are now part of main. Add the supplementary entry point to the code index if revising the PDF.
- Fixed commit links can remain unchanged for reproducibility. Use main-relative links in repository Markdown for current navigation.

The PDFs are authored documents and are not rewritten by either command. The repository PDF and separately supplied revised v6 PDF are different versions; consolidation does not overwrite either one or alter contribution signatures.

## Evidence scope

The 2026 observation window is January 2 open through October 6 close, not the full year. The four report portfolios are sample tangency, Ledoit–Wolf tangency, value weights and equal weights. Text-distance allocations are retained as historical optional research, use SVD-space distances, and are not report evidence. No new performance observations or alternative strategy rules are introduced by the merge.

Public visibility permits anyone to access repository files and history; it is not a teacher-only access setting. Cached observations and sanitized provider responses are retained. Credentials and local daily-data directories remain excluded. Public visibility does not grant additional redistribution rights to third-party data.
