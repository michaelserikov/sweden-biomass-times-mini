# Changelog

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
