# Research artifacts and provenance

## Versioned inputs

- `inputs/tfidf_umap_leiden_assignments.parquet`: seven formation years, five seeds per year, the four-section lexical UMAP3-Leiden route; 66,340 company-fit rows.
- `inputs/tfidf_fused_vectors_2024_seed20260831.npz`: normalized-fusion upstream 50D vectors for 1,910 companies and the frozen SVD seed. No original filing text.
- `inputs/company_metadata_and_coverage_2024.csv`: stable identifiers, company names, descriptive provider sectors and strict complete-month counts. No return observations.
- `inputs/filing_timing_2024.csv`: exact filing accession, fiscal period and availability timestamps, plus SEC source URLs. No section text.
- `inputs/leiden_multiyear.csv` and `inputs/kmeans48_multiyear.csv`: original study comparison aggregates.
- `inputs/section_comparison_2024.csv`: six-decimal values transcribed from the end-2024 annual comparison report.
- `inputs/daily_source_coverage.csv`: daily panel coverage summaries and original file hashes, without return observations.
- `inputs/provenance.json`: identified source runs and SHA-256 checksums. Original local machine paths are omitted.

## Versioned outputs

`results/` contains the frozen 24-stock universe, the 30 pre-cutoff class representatives, all-company ranks, representative-seed evidence, comparison win counts and verification records. `figures/` contains three regenerated comparison charts.

## What can be reproduced?

The default entry point recomputes centrality and selection from vectors and labels, chooses the representative seed from the five observed partitions, validates filing timing, recounts comparative wins and redraws the figures. The optional daily-root argument replays company coverage against local market data.

The committed comparison tables are **upstream measured results**, not new independent reruns of embeddings, UMAP, Leiden, daily pair support or dependence estimation. This repo cannot recreate that entire study from raw inputs; it preserves enough evidence for the present selection and documents the boundary.

## Main upstream checkpoints

- Annual text study: `20260929T155552Z-annual-comparison`, end-2024 formation / 2025 evaluation.
- Persisted lexical embeddings: `20260930T061945Z-tfidf-svd-section-embeddings`.
- Multi-year matched-count results: `20261005-annual-comparison` under `multiyear_umap_kmeans48`.
- Native-count Leiden results: `20261005-nine-routes-final` under `annual_leiden_comparison`.
- Daily return conventions: TBIC's processed annual-security-return panels and retained data-quality notes.

The source study was exploratory. Run IDs and hashes identify evidence; they do not certify point-in-time investability or correct unresolved source observations. Raw market files and prior local working copies are explicitly ignored by Git.
