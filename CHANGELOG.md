# Changelog

## 12 November 2026: version 0.2, hydrogen, biomethane and industrial decarbonisation

New processes: anaerobic digestion with upgrading (`BG_AD`, three feedstock steps `DIG1-3`), gasification to bio-SNG (`BG_SNG`), biomethane injection (`GAS_BMG`) and use in heavy road transport (`RD_BMG`), liquefaction of the CO2 from upgrading (`CC_BGP`), hydrogen storage in lined rock caverns (`H2_STG`) and high-temperature industrial heat (`IHT` demand of 10 TWh; `IHT_FOS`, `IHT_H2`, `IHT_ELC`). Hydrogen is balanced by season with a cyclic storage level (`EQ_H2BAL`, `EQ_H2STG`); injected biomethane earns a credit only against gas use without CO2 capture (`EQ_BMGGO`). New options `--CO2P`, `--NEGCR`, `--BIOC`, `--NOH2STG`, `--H2STGC` and the script `scripts/hydrogen_biomethane.py`.

Effect on the earlier results: the hydrogen storage surcharge of 15 EUR/MWh that `GT_H2` carried in place of a storage process is removed, and the new high-temperature heat demand raises 2025 model emissions, so the gross cap scales up (residual 2045 emissions 5.2 instead of 4.8 Mt). Core results with v0.2 (v0.1 in brackets): forest biomass to CHP with capture 14 TWh (15 to 16), extra cost of Scarce forest 6.1 bn EUR (6.0), cost of a ten-year technology delay 0.4 to 0.8 bn EUR (0.3 to 0.8), upper bound on the EVPI of biomass availability 33 MEUR (6), peak gas turbines on liquid biofuel 2.3 to 2.9 GW (2.5 to 3.0).

Fix: `scripts/residuals.py` classified every infeasible run as "infeasible without CO2 cap", because the GAMS listing echoes both abort messages; it now reads the model status of each solve. The frontier runs from 94% are infeasible under the CO2 cap, as the README of v0.1 already stated; the e-kerosene gap is infeasible without the cap (ReFuelEU quota), as before.

## 20 October 2026: residual emissions

New options `--RED45` (gross reduction in 2045) and `--NOTECH` (technology not available) and a report of gross fossil CO2 by process. `scripts/residuals.py` adds the residual by sector, seven innovation-gap runs and a frontier from 85% to 100% gross reduction; the IAMC export now carries CO2 by sector. Results of the existing runs are unchanged.

## 19 October 2026: IAMC export

All runs exported to IAMC format with pyam, with protocol-style checks (`scripts/to_iamc.py`).

## 11 October 2026: plausibility fixes

Two results of the first version were implausible and are corrected:

| Result (2045) | First version | Revised |
|---|---|---|
| SAF share of jet fuel (Forest first / Scarce forest / Electrons win, on time) | 98% / 52% / 77% | 42% / 42% / 47% |
| New and existing peak gas turbines (on time) | 8.6 / 8.0 / 8.1 GW, fuel switching between liquid biofuel and hydrogen | 3.2 / 2.7 / 2.8 GW, mostly liquid biofuel |
| Forest biomass to plants with CO2 capture (six runs) | 18 to 22 TWh (CHP and gasification-FT) | 15 to 16 TWh (CHP) |
| Extra cost of Scarce forest vs Forest first | 6.2 bn EUR | 6.0 bn EUR |
| Upper bound on EVPI | 37 MEUR | 6 MEUR |
| Calibration, total electricity 2025 | +0.7% | +0.7% |

Causes and fixes: refinery products were produced in fixed shares, so bio-jet was a forced co-product of renewable diesel and negative emissions; the jet fuel demand was annualised from one low-season month; all electricity demand growth inherited today's winter-peaking load shape; electric boilers ran in the winter peak on electricity from gas turbines; and demand flexibility could not contribute to the peak. See the commit history for each change.

## 9 October 2026

First version: model, six scenarios, sensitivities, value of information and the TIMES demo extension.
