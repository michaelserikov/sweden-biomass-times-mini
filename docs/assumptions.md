# Data, assumptions and calibration

Levels: **verified** (checked against the primary source), **approximate** (order of magnitude from a named source, or a derived value) and **assumption** (modelling choice, documented). Full list with sources: [`data/sources.csv`](../data/sources.csv).

| Parameter | Value | Source | Level |
|---|---|---|---|
| ReFuelEU minimum SAF and synthetic shares (`SAF_SHR`, `SYN_SHR`) | SAF 2/6/20/34/42/70%; synthetic 1.2/5/10/15/35% (2025-2050) | Regulation (EU) 2023/2405, Annex I | verified |
| Calibration statistics, electricity 2025 | 167.9 TWh (hydro 68.1, nuclear 44.8, wind 39.0) | SCB, Electricity supply 2025 (preliminary) | verified |
| National emissions 2024 relative to 1990 (`RED_2025`) | -33% | Naturvårdsverket, preliminary 2024 statistics | verified |
| 2045 target (`RED_2045`) | -85% vs 1990, applied proportionally to the model scope | Swedish climate policy framework | approximate |
| Jet fuel uplifted in Sweden 2025 (`COM_PROJ` AVF) | 8.5 TWh | EIA jet fuel consumption 2023 (14.4 thousand bbl/day, about 8.1 TWh); Naturvårdsverket international aviation 1.8 Mt CO2e in 2024 (about 7 TWh) plus domestic | approximate |
| Domestic share of jet fuel CO2 (`DOM_SHR`) | 18% | ratio of domestic to international aviation in the Swedish inventory | assumption |
| District heat demand (`COM_PROJ` HET) | 60 TWh in 2025, slowly declining | SCB 2023 (60.5 TWh) | approximate |
| Electricity demand excluding endogenous uses (`COM_PROJ` ELC) | 130 TWh (2025) to 168 TWh (2050) | informed by Energimyndigheten long-term scenarios | assumption |
| Load shape and peak (`G_YRFR`, `COM_FR`) | 9 slices, 100-hour winter peak; peak 26.7 GW (2025), 30.3 GW (2045); growth spread evenly | peak/average about 1.8 for today's demand | assumption |
| Peak contribution (`NCAP_PKCNT`) | hydro 0.82 (13.4 GW), nuclear 0.90, wind 0.09, imports 0.75 of 4 GW | Swedish winter power balance practice (order of magnitude) | assumption |
| Peak reserve margin (`COM_PKRSV`) | 5% (about 1.5 GW) | Svenska kraftnät LMA 2024: 1.8 to 3.6 GW frequency restoration reserves needed in 2045 | approximate |
| Demand response at peak (`DR_ELC`) | up to 0.5 GW new per period from 2030 (2 GW in 2045), 300 EUR/MWh activation | Ei: industrial flexibility capability about 1,700 MW (cited by Jernkontoret); Svenska kraftnät LMA 2024 on flexibility | approximate |
| Electric boilers in the winter peak | off from 2030 | interruptible loads | assumption |
| Forest biomass supply curve (`RES_VOL`, `RES_COST`) | 30/20/15/15 TWh at 15/22/30/42 EUR/MWh | stepwise supply curve | assumption |
| Black liquor, waste, lipid feedstock | 42 / 18 / 8 TWh | constant pulp production; waste must be treated; share of a constrained lipid market | approximate / assumption |
| FT product slate (`PRC_ACTFLO`, `FLO_SHAR`) | per TWh liquids: 0.25 naphtha, 0.15 to 0.55 bio-jet, rest renewable diesel | Kreutz et al. (2008): about 39% gasoline/naphtha in a diesel-gasoline configuration | approximate / assumption |
| HEFA and black liquor gasification jet share of distillates (`FLO_SHAR`) | 10-50% and 20-60% | plants switch between renewable diesel and jet mode | assumption |
| Bio-naphtha export price (`IRE_PRICE`) | 45 EUR/MWh | fossil naphtha parity | assumption |
| Fossil fuel prices | gas 35, jet 55, diesel 60, coal 15 EUR/MWh | constant prices, no separate carbon tax | assumption |
| Technology costs and efficiencies | see `data/processes.csv`, `data/flows.csv` | Danish Energy Agency Technology Data, JRC, IEA (orders of magnitude) | approximate |
| Emission factors | CO2: IPCC 2006 defaults; NOx and PM2.5: EMEP/EEA Guidebook Tier 1 | IPCC 2006; EMEP/EEA 2023 | approximate |
| CO2 storage capacity (`STG_MAX`) | 2/5/8/10/10 Mt/yr (2030-2050) | informed by SOU 2020:4 | assumption |
| Discount rate (`G_DRATE`) | 4% (sensitivity 2% and 7%) | project choice | assumption |

## Calibration

| Item | Statistics (TWh) | Model 2025 (TWh) | Difference |
|---|---|---|---|
| Hydropower | 68.1 | 67.5 | -0.8% |
| Nuclear | 44.8 | 46.1 | +2.9% |
| Wind | 39.0 | 41.3 | +5.9% |
| Solar | 4.4 | 4.3 | -1.8% |
| Conventional thermal | 11.6 | 9.8 | -15.6% |
| Total electricity production | 167.9 | 169.0 | +0.7% |
| District heating supply | 60.5 | 60.0 | -0.8% |

Electricity: SCB, Electricity supply 2025 (preliminary). District heating: SCB 2023. The 2025 peak load in the model is 26.7 GW. Built-in checks run after every solve: no unserved demand, no negative costs, no process producing more energy than it consumes (heat pumps and industrial electrification excluded), all balances satisfied.

## Co-benefits: stationary NOx and PM2.5 (model scope)

| Scenario | NOx 2025 (kt) | NOx 2045 (kt) | PM2.5 2025 (kt) | PM2.5 2045 (kt) |
|---|---|---|---|---|
| Forest first, on time | 33.1 | 32.6 | 6.1 | 5.7 |
| Scarce forest, on time | 33.1 | 26.0 | 6.1 | 4.2 |
| Electrons win, on time | 33.1 | 29.9 | 6.1 | 5.3 |

Less biomass combustion lowers NOx and PM2.5; liquid-fuel gas turbines have high NOx factors per unit of fuel but run few hours. Factors are Tier 1 orders of magnitude (EMEP/EEA Guidebook) and cover stationary combustion only. Full table: [`results/tables/co_benefits.md`](../results/tables/co_benefits.md).

## Known limitations and next steps

Limitations:

- **Illustrative data.** Costs, efficiencies and supply curves are orders of magnitude, not a calibrated national data set; the model answers relative questions about allocation and trade-offs and does not forecast the Swedish energy system.
- **One region and little trade.** Electricity exports are fixed, imports are capped at 4 GW, bio-naphtha is the only exported fuel and there is no trade in bio-jet or renewable diesel. Surplus SAF could in reality be sold to other EU markets under ReFuelEU.
- **Simplified time slices.** Nine slices with a 100-hour winter peak; the assumption that demand growth after 2025 is flat across slices lowers the 2045 peak by about 3 GW compared with scaling today's load shape. There is no storage process.
- **Peak capacity depends on the demand-response potential.** Demand response reaches its upper bound (2 GW) in every run, so each additional GW of flexibility would replace roughly one GW of gas turbines.
- **Aviation non-CO2 effects are not modelled.** Only a sensitivity with domestic aviation CO2 weighted x2 is included. NOx and PM2.5 are tracked as co-benefits of stationary combustion only.
- **Other simplifications.** Perfect foresight within each scenario, exogenous demands, no land-use or forest carbon accounting (biomass is treated as carbon neutral at combustion) and a CO2 target applied proportionally to the model scope.

Next steps:

- Contrail and NOx-at-altitude effects of aviation by fuel type (fossil jet, bio-jet, e-kerosene), so that the SAF choice also reflects non-CO2 climate effects.
- Sensitivities on the value of the FT naphtha cut and on the demand-response potential, which drive the gasification-FT and gas turbine results.
- Soft-linking with a spatially explicit model of biofuel supply chains (plant locations, feedstock transport, heat sinks) and with a CGE model, in the spirit of the EMEC and TIMES-Sweden linkage (Krook-Riekkola et al. 2017).
- The full two-stage stochastic recourse problem (RP and VSS) and uncertainty in technology timing as a second stochastic dimension.
- Running the same question on the open-source TIMES code with a reduced TIMES-Sweden data set.
