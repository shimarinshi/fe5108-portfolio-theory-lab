# Universe selection: largest eligible historical-cap member

Use the unchanged end-2024 mixed four-section TF-IDF/SVD → UMAP3 → Leiden partition, selected seed 20260831. All 1,910 members have positive identity-matched historical vendor capitalization in the frozen December 31, 2024 input. Rank within each of the 30 classes by raw company market cap descending, then CIK ascending for ties. Select the first member with 108 complete monthly observations in the original 2017–2025 daily panels. Centrality is retained as descriptive metadata only; its rank no longer controls selection or exclusion. Keep every class.

The 2024 date defines stock selection. The separate 2025-12-31 cap snapshot defines Stage 1 value weights. Do not interchange these two dates, use current caps for selection, or mistake company cap for free float.

## Selected companies

| Class | Ticker | Company | Cap rank in full class | Centrality rank (descriptive) | 2024 cap, USD bn | Complete months |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | SHW | SHERWIN WILLIAMS | 1 | 78 | 85.612 | 108 |
| 1 | AAPL | APPLE INC | 1 | 98 | 3785.304 | 108 |
| 2 | ABBV | ABBVIE INC | 1 | 108 | 314.021 | 108 |
| 3 | PLD | PROLOGIS REIT INC | 1 | 99 | 97.897 | 108 |
| 4 | TMO | THERMO FISHER SCIENTIFIC INC | 1 | 78 | 198.988 | 108 |
| 5 | SF | STIFEL FINANCIAL CORP | 1 | 100 | 10.858 | 108 |
| 6 | VZ | VERIZON COMMUNICATIONS INC | 2 | 77 | 168.343 | 108 |
| 7 | META | META PLATFORMS INC CLASS A | 2 | 28 | 1478.113 | 108 |
| 8 | SCCO | SOUTHERN COPPER CORP | 2 | 69 | 72.030 | 108 |
| 9 | MSFT | MICROSOFT CORP | 1 | 70 | 3133.802 | 108 |
| 10 | UPS | UNITED PARCEL SERVICE INC CLASS B | 1 | 16 | 107.610 | 108 |
| 11 | WMT | WALMART INC | 1 | 11 | 725.816 | 108 |
| 12 | PANW | PALO ALTO NETWORKS INC | 2 | 44 | 119.402 | 108 |
| 13 | RTX | RTX CORP | 1 | 50 | 154.025 | 108 |
| 14 | AFL | AFLAC INC | 4 | 32 | 57.464 | 108 |
| 15 | ACN | ACCENTURE PLC CLASS A | 1 | 37 | 220.038 | 108 |
| 16 | V | VISA INC CLASS A | 1 | 35 | 612.001 | 108 |
| 17 | EXEL | EXELIXIS INC | 3 | 43 | 9.510 | 108 |
| 18 | KO | COCA-COLA | 1 | 15 | 268.203 | 108 |
| 19 | UNH | UNITEDHEALTH GROUP INC | 1 | 25 | 465.535 | 108 |
| 20 | WMB | WILLIAMS INC | 1 | 26 | 65.973 | 108 |
| 21 | MO | ALTRIA GROUP INC | 1 | 31 | 88.622 | 108 |
| 22 | AGNC | AGNC INVESTMENT REIT CORP | 1 | 18 | 8.157 | 108 |
| 23 | CME | CME GROUP INC CLASS A | 2 | 28 | 83.687 | 108 |
| 24 | SRE | SEMPRA | 1 | 7 | 55.562 | 108 |
| 25 | MAR | MARRIOTT INTERNATIONAL INC CLASS A | 1 | 27 | 77.516 | 108 |
| 26 | CMG | CHIPOTLE MEXICAN GRILL INC | 1 | 17 | 82.164 | 108 |
| 27 | TSLA | TESLA INC | 1 | 16 | 1296.350 | 108 |
| 28 | SLB | SCHLUMBERGER NV | 1 | 15 | 54.142 | 108 |
| 29 | DHI | D R HORTON INC | 1 | 9 | 44.858 | 108 |

## Seven coverage substitutions

The absolute vendor-cap leaders TMUS, GOOGL, LIN, PLTR, KKR, MRNA and BX lack 108 complete months under the existing security-ID panel rules. The selected substitutes are VZ, META, SCCO, PANW, AFL, EXEL and CME respectively. This is a panel-coverage statement, not a claim those companies did not exist or trade earlier. Historical security continuity is not silently invented. No returns are imputed, zero-filled or borrowed across security IDs.

## Evidence limits

Historical ticker-overview queries are issuer-identity matched, but vendor share counts can be stale or use differing share-class scopes. Google class shares versus company-level weighted shares can change class-scope diagnostics; class-only market cap is not a universal replacement. Original raw values are kept. No historical largest-company claim is made beyond this frozen vendor input. Full-history eligibility is retrospective selection; the project does not assert this portfolio was available in 2017 or that prior research comparisons validate future performance. The original filing-availability check is narrower: it establishes eligibility of the 2024 filing snapshot.

## Reproduction

`python run_all.py` recreates all rankings and selections. `artifacts/inputs/formation_market_caps_2024.csv` supplies the complete 1,910-member cap table; its hash is in provenance. `artifacts/results/selected_universe.csv` is the canonical selection artifact, independent of asset-count naming. `candidates_30.csv` contains the same retained class representatives.
