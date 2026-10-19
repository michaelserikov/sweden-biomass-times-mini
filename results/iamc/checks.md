# Protocol checks on the IAMC export

15 scenarios, 30 variables, years 2025 to 2050.

| Check | Result | Detail |
|---|---|---|
| completeness | pass | all required variables for all scenarios |
| aggregation: Secondary Energy|Electricity | pass | total = sum of 10 components |
| aggregation: Primary Energy|Biomass|Forest | pass | total = sum of 5 components |
| aggregation: Emissions|CO2|Energy and Industrial Processes | pass | total = sum of 4 components |
| gross target | pass | largest gross minus cap: 0 Mt CO2/yr |
| net zero | pass | largest net CO2 in 2045 and 2050: 0 Mt CO2/yr (30 values) |
| calibration | pass | largest deviation of total 2025 electricity: 0.7% |
