# Portfolio Theory in Practice

**FE5108 group project: from portfolio choice to CAPM, factor models and investment judgment.**

This repository covers the **whole project**, not only Stage 1. The current checkpoint establishes the data specification, the evidence for text-based universe construction, and a frozen universe of **24 US stocks**. Portfolio estimates, CAPM regressions, factor models and the final memo are the next stages; they have not been completed here.

## Research design

1. Reuse carefully processed **daily total returns**, then compound the chosen stocks to monthly frequency.
2. Use an existing multi-year SEC text-classification study to choose an economically motivated grouping framework.
3. Freeze the **end-2024 four-section TF-IDF/SVD -> UMAP3 -> Leiden** classification.
4. Within each class, rank companies by mean cosine distance to the other members in the original fused 50-dimensional representation. Select the first company with complete 2017-2025 return coverage; discard that class if the selected company's original rank is **5 or worse**.
5. Hold the resulting 24-stock universe fixed for the course analysis. Compare estimated tangency weights with value weights, then examine CAPM, additional factors and robustness.

This is a **retrospectively constructed research universe**, not a strategy that could have been selected in 2017. Formation-time filing eligibility is checked separately from look-ahead and survival selection in the full historical study.

## Frozen universe

AXTA, VECO, HIW, EW, OSBC, URI, SSTK, RYI, CSGS, RSG, DG, VVX, AMBC, DFIN, HSY, DVA, HELE, NYMT, BKH, BYD, BLMN, PLUG, HLX, CCS.

All 24 have complete daily-return coverage for the **108 months from January 2017 through December 2025** in the supplied panels. Tickers identify the end-2024 formation; stable security IDs, not ticker strings, govern return joins.

- [Selection method and company-level judgment](docs/03-universe-selection.md)
- [Machine-readable 24-stock universe](artifacts/results/selected_universe_24.csv)
- [All 30 eligible class representatives, including six exclusions](artifacts/results/candidates_30.csv)

## Why this text framework?

In the matched 48-group study, lexical four-section TF-IDF/SVD classifications exceed FF48 on both Pearson and empirical lower-tail gaps in all seven evaluated years. The single- versus multi-section comparison supports four-section fusion for the lexical method in the end-2024 experiment, not a universal improvement for all representations.

Among nine **native-count Leiden** routes, TF-IDF/SVD + UMAP3 has the highest next-year Pearson within-minus-across gap in all seven years. It also exceeds the historical-return control in **five of six** comparable years. Leiden does not require a fixed number of clusters, which is convenient for an emergent business grouping; it still depends on graph and resolution choices. Neither that property nor these descriptive results proves superior portfolio performance or universally better separation.

![Native Leiden comparison](artifacts/figures/03_native_leiden_multiyear.png)

*Takeaway: lexical UMAP3 leads these Leiden routes, but group counts vary. FF48 and historical-return controls are contextual benchmarks, not matched-count superiority tests.*

Read [method comparisons and all three figures](docs/02-classification-evidence.md) for the KMeans48, multi-text and encoder comparisons, including qualifications.

## Data remain local

**No daily prices, daily returns, raw SEC text, API responses, credentials, downloaded RF observations or market-cap series are committed.** Only research classification artifacts, compressed text vectors, filing metadata, coverage counts, comparison aggregates and selected-universe outputs are versioned.

The supplied daily panel spans **2016-09-30 to 2025-12-31**, with its first finite return on **2016-10-03**. The project uses the nine full years **2017-2025**. Monthly risk-free returns are already available locally; usable historical market capitalizations are still outstanding.

See [data sources and processing](docs/01-data.md) and [artifact provenance and reproduction boundaries](artifacts/README.md).

## Reproduce this checkpoint

Python 3.12+ is recommended. Recorded execution versions are in [environment.json](artifacts/results/environment.json).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py
python -m unittest discover -s tests -v
```

The default command reproduces the universe selection, three comparison figures, win counts and filing-time checks from the committed derived artifacts. It does **not** refit TF-IDF/SVD, UMAP or Leiden, recompute the upstream stock-pair dependence study, or execute unfinished course stages.

To independently replay coverage from the locally supplied daily panels:

```bash
python run_all.py --daily-root ./tbic_returns
```

The optional local replay checks every one of the 1,910 candidate companies. It fails if the recorded coverage and the supplied panels differ. No external API calls or downloads occur during either command.

## Whole-project roadmap

| Stage | Required analysis | Status |
|---|---|---|
| Data and universe | Sources, classification evidence, frozen stock selection | Completed checkpoint; market-cap input outstanding |
| Stage 1: portfolio choice | Monthly summary statistics, tangency vs value weights, subsample sensitivity | Next |
| Stage 2: CAPM | Alpha/beta regressions, SML, joint alpha assessment | Planned |
| Stage 3: factors | At least two additional factors, before/after alpha comparison | Planned |
| Stage 4: judgment | Investment memo, alternative market proxy, limitations | Planned |

[Next-step input contracts](docs/04-next-steps.md) specify monthly compounding, RF units, and lagged market-cap weights. [Team contribution template](docs/contributions.md) is for the final submission.

## Attribution

Upstream data and text-classification research: TBIC / Tuoyuan, with specific run IDs and hashes recorded in [provenance](artifacts/inputs/provenance.json). Market data: Massive; filings: SEC EDGAR; historical universe proxy: iShares IWV holdings; standard benchmark: SEC SIC mapped to Fama-French 48 industries; risk-free series: Kenneth French Data Library.

AI assistance: OpenAI Codex assisted with data auditing, reproducible selection code, evidence visualization and documentation. The team remains responsible for all results and interpretations. This repository is a research checkpoint, not an investment recommendation.
