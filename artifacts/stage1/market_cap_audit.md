# December 31, 2025 capitalization audit

## Conclusion

All 24 records pass internal date, identity and arithmetic checks. No confirmed split-basis error was found at this endpoint. Use the original vendor values for a disclosed retrospective Stage 1 comparison, with the limitations below. This is NOT independent certification of all 24 market caps or a strict point-in-time dataset.

All prices refer to actual 2025-12-31 bars; all caps are positive USD values. CIK and returned ticker match the dated upstream identity. All 22 available share-class FIGIs match the upstream security ID; AXTA and HELE lack FIGIs and are checked against primary issuer filings. Cap equals unadjusted close times weighted shares for all 24, but that shared vendor identity is not independent evidence.

## Targeted primary-source checks

- **AMBC — Identity corroborated:** AMBC changed to OSG effective 2025-11-20; same issuer and cached CIK/FIGI. Share count not independently confirmed. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/874501/000162828025051169/a04-0893q258xkex991.htm)
- **NYMT — Identity corroborated:** NYMT changed to ADAM effective 2025-09-03; same issuer and cached CIK/FIGI. Share count not independently confirmed. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/1273685/000127368525000075/nymt-20250829.htm)
- **BKH — Disclosed earlier share count corroborated:** Weighted shares 75,473,390 match 2025-11-04 SEC cover count. Lower class field is not used to replace the raw cap. Not an exact independent December 31 count. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/1130464/000119312525268567/R1.htm)
- **HSY — Class scope explained:** 148,171,608 common plus 54,613,514 Class B = 202,785,122 equivalent shares. Q3 cover date 2025-10-24; Class B converts share-for-share. Company-equivalent cap, not just listed class or float. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/47111/000162828025047471/hsy-20250928.htm), [source 2](https://www.sec.gov/Archives/edgar/data/47111/000095014224000438/eh240447519_13ga45-htchsy.htm)
- **EW — Disclosed earlier share count corroborated:** 580.3 million matches shares as of 2025-10-31 in Q3 filing; no 2020 split-basis mismatch at this endpoint. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/1099800/000109980025000062/ew-20250930.htm)
- **HELE — Identity and earlier count corroborated:** 23,028,819 matches 2025-09-30 cover count. CIK/name/ticker corroborate issuer despite missing FIGI. Exact December count not independently confirmed. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/916789/000091678925000097/hele-20250831.htm)
- **AXTA — Identity corroborated; small count discrepancy retained:** Q3 cover identifies AXTA and 213,340,170 shares as of 2025-10-22, matching class shares. Weighted count exceeds it by 3,251 (0.001524%); cause not established. Preserve raw cap. Sources: [source 1](https://ir.axalta.com/sec-filings/all-sec-filings/content/0001628280-25-047015/axta-20250930.htm)
- **VVX — Year-end count corroborated retrospectively:** 31,171,445 outstanding at 2025-12-31 agrees with subsequent annual-report balance sheet. Class field 31,535,083 differs; do not replace the corroborated weighted count. This evidence was published after cutoff. Sources: [source 1](https://d18rn0p25nwr6d.cloudfront.net/CIK-0001601548/0ff045e3-ffab-4091-871f-9a8fb8f9de87.pdf)
- **URI — Disclosed earlier share count corroborated:** 63,630,147 matches 2025-10-20 cover shares. Not an exact independent December 31 share count. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/1067701/000106770125000039/uri-20250930.htm)
- **DG — Disclosed earlier share count corroborated:** 220,118,871 matches 2025-12-02 cover shares. Not an exact independent December 31 share count. Sources: [source 1](https://www.sec.gov/Archives/edgar/data/29534/000110465925118289/dg-20251031x10q.htm)

## What was not established

For the remaining 14 companies, only cached internal consistency was established, not independent year-end shares. SEC companyfacts HTTP requests were rejected with 403; no companyfacts data were saved. Public filings were checked through indexed primary pages for the targeted cases above. Earlier disclosure dates do not prove the share count remained unchanged through December 31. The 1% threshold from the earlier screen is merely a triage choice, not an accuracy criterion.

The raw vendor market caps are unchanged. No prices or shares were shifted to the following day or month. No historical cap series was repaired. AXTA's tiny count difference remains explicitly unresolved. HSY's class difference is economically explained, not a split error. VVX's weighted count is corroborated retrospectively, but the later annual report does not establish that investors knew it at the cutoff.

Use this snapshot as a static, retrospective classroom benchmark. To claim an implementable December 2025 allocation, replace uncertain share inputs in a separate estimate with the most recent shares actually disclosed by the cutoff, track disclosure dates and adjust only corporate actions already effective. That would be a different, expressly labeled information-set construction, not a silent overwrite of vendor raw data.

## Reuse and provenance

The original cached Massive detail responses are copied to `artifacts/input/year_end_sources`; no authenticated request or new Massive download was made for this audit. `year_end_market_cap_2025.csv` preserves the original identity, raw cap and flags and adds audit notes. Monthly returns and the full historical raw cap CSV are not modified. No GitHub push is part of this step.
