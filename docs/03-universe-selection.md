# Fixed-universe selection

## Formation and text eligibility

The stock pool uses the **classification formed at December 31, 2024**, based on the annual filings eligible by that formation date. It does **not** mean that every document is a fiscal-year-2024 annual report: the selected fiscal period ends range from June 30, 2023 to November 3, 2024. A calendar-year 2024 10-K normally filed in 2025 must not be relabeled as available in December 2024.

The retained exact-accession metadata confirms that all **1,910 issuer filings** satisfy `available_after <= formation_at`, where `available_after` is the upstream proxy **SEC acceptance timestamp + one calendar day**. The latest retained availability timestamp is December 28, 2024, 21:58:55 UTC, before formation on December 31, 21:00 UTC. The check runs in `run_all.py` and the SEC accession/URL evidence is included.

This supports **no post-cutoff filings under that rule**. It does not establish a perfect real-time timestamp for historical IWV holdings or every other upstream input. More importantly, using this end-2024 classification to select a 2017-2025 sample is retrospective and has look-ahead exposure. Selecting complete histories adds survival/coverage selection. We do not claim the project has “no timing issues.”

## Deterministic selection rule

1. Use the lexical four-section TF-IDF/SVD -> UMAP3 -> Leiden route.
2. Select the end-2024 seed partition with the highest mean adjusted Rand index (ARI) against the other four observed partitions; tie-break by smaller seed. This reproduces **seed 20260831**, with 30 classes. No return performance or target class count chooses the seed.
3. Use its original **50D fused vectors**, not UMAP coordinates, to measure textual centrality. For each company, compute mean cosine distance to **all other companies in its class**. Exclude self-distance, retain the full class for this calculation, and tie-break by CIK.
4. Rank the whole class before examining return coverage. Select its first member with all 108 complete return months in the local annual evaluation panels.
5. Discard the class if that eligible representative's full-class rank is **greater than or equal to 5**. Retain ranks **1-4**. This is the agreed cutoff, not `rank > 5` and not a cap of five rejected companies.
6. Freeze the resulting 24 securities for all course stages. Neither capitalization nor historical performance determines the selection.

The original 30 eligible representatives include six rank-5-or-worse stocks: **SNDX (8), BL (7), SQ (5), RGNX (7), WTI (8), BEN (6)**. Excluding them gives the final 24. The rule was adopted after inspecting the preliminary representatives; it is a transparent post hoc research-universe choice, not a preregistered strategy rule.

## Selected securities

All entries below have 108 complete months in the supplied data. Historical ticker strings are not a statement about current listing status. Business descriptions are interpretive summaries rather than official industry labels.

| Class ID | Ticker at formation | Company | Centrality rank | Indicative business description |
|---|---|---|---:|---|
| 0 | AXTA | AXALTA COATING SYSTEMS LTD | 2 | Coatings and industrial manufacturing |
| 1 | VECO | VEECO INSTRUMENTS INC | 3 | Semiconductor equipment and hardware |
| 3 | HIW | HIGHWOODS PROPERTIES REIT INC | 1 | Commercial-property REITs |
| 4 | EW | EDWARDS LIFESCIENCES CORP | 2 | Medical devices and diagnostics |
| 5 | OSBC | OLD SECOND BANCORP INC | 1 | Banks |
| 6 | URI | UNITED RENTALS INC | 1 | Equipment rental and mixed operating businesses |
| 7 | SSTK | SHUTTERSTOCK INC | 2 | Digital media and platforms |
| 8 | RYI | RYERSON HOLDING CORP | 1 | Metals, materials and distribution |
| 9 | CSGS | CSG SYSTEMS INTERNATIONAL INC | 3 | Enterprise software and technology services |
| 10 | RSG | REPUBLIC SERVICES INC | 1 | Waste, transport and mixed industrial businesses |
| 11 | DG | DOLLAR GENERAL CORP | 1 | Retail |
| 13 | VVX | V2X INC | 2 | Defense contracting and engineering |
| 14 | AMBC | AMBAC FINANCIAL GROUP INC | 1 | Insurance |
| 15 | DFIN | DONNELLEY FINANCIAL SOLUTIONS INC | 2 | Professional and business-support services |
| 18 | HSY | HERSHEY FOODS | 2 | Food and beverages |
| 19 | DVA | DAVITA INC | 1 | Healthcare services and payers |
| 21 | HELE | HELEN OF TROY LTD | 1 | Consumer brands and durable products |
| 22 | NYMT | NEW YORK MORTGAGE TRUST REIT INC | 1 | Mortgage REITs |
| 24 | BKH | BLACK HILLS CORP | 1 | Utilities |
| 25 | BYD | BOYD GAMING CORP | 3 | Gaming and leisure |
| 26 | BLMN | BLOOMIN BRANDS INC | 1 | Restaurants |
| 27 | PLUG | PLUG POWER INC | 4 | Clean-energy equipment |
| 28 | HLX | HELIX ENERGY SOLUTIONS GROUP INC | 2 | Oilfield and offshore energy services |
| 29 | CCS | CENTURY COMMUNITIES INC | 2 | Homebuilding |

## Company-level judgment

The selection is economically plausible for several relatively cohesive groups: banks (OSBC), mortgage REITs (NYMT), utilities (BKH), restaurants (BLMN), homebuilders (CCS), and medical devices (EW). A text medoid need not be a large-cap or well-known company; that is consistent with the chosen objective.

Some representatives describe a narrower sub-business than their whole group: VECO for semiconductor equipment within hardware, HIW for office property within real estate, PLUG for one clean-energy technology, and RSG for waste services within a broader industrial class. Their centrality does not make them exhaustive representatives.

Three previously flagged issues remain in the final universe:

- **URI** is a clear equipment-rental company, but its group mixes industrial, consumer, communication and property businesses.
- **CSGS** is related to enterprise billing/payment/customer-service software, but its original-space distance diagnostic shows an ambiguous class boundary.
- **AMBC** is the class's mathematical center, but its historical financial-guarantee and specialty-insurance mix needs explanation rather than calling it a typical generic insurer.

URI and CSGS have negative original-space silhouette diagnostics in the earlier review: the selected company is on average closer to another class in 50D than to its own. This is a warning about the relationship between UMAP clustering and original-space representation, not evidence that the code miscomputed the center. We retain the agreed rule rather than silently replacing inconvenient selections.

The excluded WTI class mixed 29 energy and 14 healthcare companies. Removing WTI through the rank rule avoids using it in this portfolio, but does not retroactively fix that classification. Excluding other classes also means the final 24 are not a comprehensive market-sector allocation.

## Boundaries

Textual typicality is not return typicality, low risk, investment attractiveness or independence of risk factors. We still need monthly covariance diagnostics for the chosen stocks. The historical complete-data restriction biases the sample toward securities with persistent usable coverage; missing dates can reflect panel membership or identity gaps as well as listing dates and exits.

Monthly total and excess returns are now available for the frozen universe. Tangency weights and CAPM results have not yet been estimated. Follow the [monthly-input workflow](04-next-steps.md) for the remaining capitalization input.

## Reproduction

`python run_all.py` recalculates the representative seed and every class ranking from the preserved labels and vectors, then applies the exact coverage and rank filters. `artifacts/results/candidates_30.csv` retains exclusions; `all_company_rankings_2024.csv` makes rejected and eligible members auditable. `--daily-root ./tbic_returns` independently recomputes coverage from the local return panels.
