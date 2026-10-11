# sweden-biomass-times-mini

A self-directed exercise to learn the TIMES model architecture before a PhD in this field. It is a small linear optimisation model of the Swedish energy system in GAMS whose sets, parameters and equations follow TIMES naming. It is **not TIMES** and does not use the TIMES source code. **All data are illustrative**, so the results are relative insights only; every number has a source and a verification status in [`data/sources.csv`](data/sources.csv).

## Question

How should Sweden allocate its limited forest biomass between turbine fuels (aviation and peak gas turbines), district heating, industry and BECCS on the way to net zero in 2045, and how does the answer depend on biomass availability and on when new conversion technologies arrive?

## Three numbers (illustrative data)

1. **15 to 16 TWh** of forest biomass goes to CHP plants with CO2 capture in 2045 in all six runs, also with 30% less biomass. The amount is set by the net-zero constraint: stored CO2 has to balance the residual fossil emissions (4.8 Mt in 2045).
2. **6.0 bn EUR** (NPV 2025-2054, 4%) is the extra system cost of scarce biomass, against **0.3 to 0.8 bn EUR** for a ten-year delay of new conversion technologies.
3. **At most 6 MEUR** is the expected value of knowing biomass availability before 2040 (upper bound on EVPI): the investments of the 2030s hardly depend on it.

![Forest biomass allocation](results/figures/fig1_biomass_allocation.png)

![Electricity in 2045, peak gas turbines and demand response](results/figures/fig2_power_and_peak_turbines.png)

## What the model shows (illustrative)

- When biomass is scarce, industrial heat (47 to 28 TWh) and district heating without capture give way, while biomass with CO2 capture stays.
- Bio-jet and renewable diesel come from black liquor and lipids rather than from solid forest biomass, and the SAF share follows the ReFuelEU minimum (42% in 2045).
- The peak grows from 26.7 to 30.3 GW by 2045 and is met with 2.5 to 3.0 GW of liquid-biofuel gas turbines plus 2 GW of demand response.

## Scenarios

| Parameter | Forest first | Scarce forest | Electrons win |
|---|---|---|---|
| Forest biomass supply from 2030 | x1.2 | x0.7 | x1.0 |
| Aviation fuel demand growth | 1%/yr | 2%/yr | 1%/yr |
| Electrolysis / wind investment cost | x1.0 / x1.0 | x1.0 / x1.0 | x0.6 / x0.8 |
| Synthetic aviation fuel sub-quota | x1 | x1 | x2 |

Each scenario is crossed with a technology-timing axis, following Sandberg and Krook-Riekkola (2022): gasification-FT, black liquor gasification, BECCS and e-kerosene are available from 2030 or from 2040. Sensitivities: discount rate 2% and 7%, and domestic aviation CO2 weighted x2.

## Model structure

39 processes (power, CHP, district heating, industry, steel, biorefineries, e-kerosene, CO2 storage), periods 2025 to 2050 in 5-year steps and 9 time slices (4 seasons x day/night plus a 100-hour winter peak). Gross fossil CO2 follows Sweden's 85% target applied to the model scope, with net zero from 2045; aviation follows the ReFuelEU Aviation quotas. 2025 is calibrated to SCB statistics (total electricity +0.7%).

| Equation | Meaning | TIMES counterpart |
|---|---|---|
| `EQ_OBJ` | NPV of investment, O&M and resources minus salvage | `EQ_OBJ` |
| `EQ_CPT` | capacity = residual + vintages in lifetime | `EQE_CPT` |
| `EQ_CAPACT` | activity <= capacity x availability | `EQL_CAPACT` |
| `EQ_COMBAL` | commodity balance per slice or year | `EQG_COMBAL` |
| `EQ_ACTFLO`, `EQL/EQG_OUTSHR` | refinery output split between bio-jet and diesel | `EQ_ACTFLO`, `EQ_OUTSHR` with `FLO_SHAR` |
| `EQ_PEAK` | firm capacity >= peak x (1 + margin) | `EQ_PEAK` with `NCAP_PKCNT`, `COM_PKRSV` |
| `EQ_CO2GROSS`, `EQ_CO2NET`, `EQ_SAF` | climate target and aviation quotas | `COM_BNDNET`, user constraints |

Names were checked against the open-source TIMES code (TIMES 4.7.3). [`times_extension/`](times_extension/) adds a gasification-FT process to the open-source TIMES demo model as a data file.

More: [data, assumptions, calibration and limitations](docs/assumptions.md), [changelog](CHANGELOG.md) (revised on 11 October 2026 after plausibility checks against Svenska kraftnät and ReFuelEU), [value of information](results/tables/voi.md).

## How to run

GAMS (classic syntax, GAMS 45 or newer; about 1,700 equations, so the demo licence is enough) and Python 3.10+ with pandas and matplotlib.

```bash
gams model/core.gms --SCN=forest_first --TIMING=ontime   # one run
python scripts/run_all.py     # 6 core runs + 9 sensitivities -> results/csv/
python scripts/plots.py       # figures and tables
python scripts/voi.py         # value of information
```

## References

- Sandberg, E. and Krook-Riekkola, A. (2022). The impact of technology availability on the transition to net-zero industry in Sweden. *Journal of Cleaner Production* 363, 132594.
- Krook-Riekkola, A., Wetterlund, E. and Sandberg, E. (2017). *Biomassa, systemmodeller och målkonflikter*. Energiforsk rapport 2017:407.
- Regulation (EU) 2023/2405 (ReFuelEU Aviation), Annex I.
- Svenska kraftnät (2024). Långsiktig marknadsanalys 2024.
- Further sources: [`data/sources.csv`](data/sources.csv) and [`docs/assumptions.md`](docs/assumptions.md).

Author: Mikhail Serikov, 2026.
