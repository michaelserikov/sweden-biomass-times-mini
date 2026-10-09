# sweden-biomass-times-mini

A TIMES-inspired linear optimisation model of the Swedish energy system in GAMS, built on the TIMES model architecture (sets, parameters, variables and equations follow TIMES naming). It is **not TIMES**, does not use the TIMES source code and is far smaller than TIMES-Sweden. **All data are illustrative**; every number has a source and a verification status in [`data/sources.csv`](data/sources.csv).

## Question

How should Sweden allocate its limited forest biomass between turbine fuels (aviation and peak gas turbines), district heating, industry and BECCS on the way to net zero in 2045? How does the answer depend on biomass availability, on when new conversion technologies become available and on competition with e-fuels, hydrogen and electrification?

## Three numbers (illustrative data)

1. **18 to 22 TWh** of forest biomass goes to plants with CO2 capture (CHP and gasification-FT) in 2045 in all six runs, also when biomass is 30% scarcer. The uses that shrink when biomass is scarce are industrial heat (38 to 21 TWh) and district heating without capture (12 to 6 TWh).
2. **6.2 bn EUR** (NPV 2025-2054, 4%) is the extra system cost of scarce forest biomass, against **0.2 to 0.8 bn EUR** for delaying gasification, black liquor gasification, BECCS and e-kerosene from 2030 to 2040.
3. **At most 37 MEUR** is the expected value of knowing biomass availability before 2040 (upper bound on EVPI, 0.02% of system cost): most 2030s investments are robust. The decision that depends most on biomass is the fuel of the peak gas turbines.

![Forest biomass allocation](results/figures/fig1_biomass_allocation.png)

![Electricity in 2045 and peak gas turbines](results/figures/fig2_power_and_peak_turbines.png)

## Policy-relevant insights

- **Biomass for negative emissions is the robust use.** When forest biomass becomes scarce, the model keeps biomass in plants with CO2 capture and moves low-temperature heat to heat pumps and electrification. Industrial heat is the largest flexible biomass user, so the industry transition and the biomass budget have to be planned together.
- **The turbine fuel for the peak reserve is not robust.** With abundant biomass the model builds about 5.9 GW of gas turbines on liquid biofuel by 2045; with cheap electrolysis it builds about 6 GW of hydrogen turbines; at a 2% discount rate hydrogen turbines win also in Forest first. Fuel-flexible turbines that can run on both biofuels and hydrogen therefore have option value.
- **Technology delay costs less than biomass scarcity, but it shifts aviation fuels.** A ten-year delay costs 0.2 to 0.8 bn EUR, partly through expensive imported e-kerosene in 2030-2035 to meet the ReFuelEU synthetic sub-quota. Gasification-FT with CO2 capture produces bio-jet as a co-product of negative emissions: in Forest first the SAF share in 2045 reaches 98%, well above the 42% mandate, while with scarce biomass it stays near 52%.

The 2045 CO2 shadow price (about 225 EUR/t in most runs) is set by the assumed price gap between imported renewable diesel and fossil diesel. It reflects an assumption, not a forecast.

## Scenarios: narratives translated into parameters

**Forest first.** Forest biomass is easier to mobilise than today (more logging residues, stumps and low-grade wood), new conversion technologies arrive on schedule and aviation grows moderately.

**Scarce forest.** Material use of wood and biodiversity protection reduce the biomass available for energy by 30%, aviation grows strongly and BECCS remains allowed.

**Electrons win.** Biomass stays at today's level, electrolysis and wind become much cheaper and the EU raises the demand for e-fuels (synthetic aviation fuel sub-quota doubled).

| Parameter | Forest first | Scarce forest | Electrons win |
|---|---|---|---|
| Forest biomass supply from 2030 (`BIO_MULT`) | x1.2 | x0.7 | x1.0 |
| Aviation fuel demand growth (`AVI_G`) | 1%/yr | 2%/yr | 1%/yr |
| Electrolysis investment cost (`ELZ_MULT`) | x1.0 | x1.0 | x0.6 |
| Wind investment cost (`WIND_MULT`) | x1.0 | x1.0 | x0.8 |
| Synthetic aviation fuel sub-quota (`SYN_MULT`) | x1 | x1 | x2 (capped at the SAF quota) |

Each narrative is crossed with a **technology-timing axis**, following the idea of Sandberg and Krook-Riekkola (2022): gasification-FT (with and without capture), black liquor gasification, BECCS at CHP and pulp mills and e-kerosene are available from 2030 (on time) or 2040 (delayed). 3 x 2 = 6 runs. Sensitivities: discount rate 2% and 7%, and a factor of 2 on domestic aviation CO2 (non-CO2 effects).

## Model structure

**Reference energy system.** Forest biomass (4-step supply curve), black liquor (tied to pulp production), waste, lipid feedstock, fossil fuels and limited biofuel imports feed 37 processes: hydro, nuclear, onshore and offshore wind, solar, interconnector imports, biomass CHP with and without CO2 capture, waste CHP, gas turbines on liquid biofuel, hydrogen and fossil fuel, heat-only boilers, large heat pumps, electric boilers, industrial excess heat, electrolysis, HEFA, gasification-FT (outputs bio-jet, bio-diesel and heat to district heating), black liquor gasification, e-kerosene from H2 and captured biogenic CO2, industrial heat options (black liquor recovery boilers with and without capture, biomass, electrification, fossil with and without CCS), blast furnace and hydrogen direct reduction steel and CO2 storage. Demands: electricity (including net exports), district heat, industrial process heat, steel, road and machinery diesel and aviation fuel.

**Time.** Periods 2025 (calibration), 2030, ..., 2050 of 5 years; 4 seasons x day/night + a 100-hour winter peak = 9 time slices. Electricity and heat are balanced per slice; fuels, hydrogen and CO2 per year. Hydropower has an annual energy budget, a seasonal limit and a minimum flow.

**Climate target.** Gross domestic fossil CO2 in the model scope falls linearly to (1 - 0.85)/(1 - 0.33) of the 2025 model level by 2045, which applies Sweden's 85% reduction target (relative to 1990, with emissions 33% below 1990 in 2024) proportionally to the model scope. From 2045 net emissions (gross minus stored biogenic CO2) must be at most zero. International aviation is reported as a memo item and is regulated through the ReFuelEU Aviation quotas instead.

### Equations and their TIMES counterparts

| Equation in `model/core.gms` | Meaning | TIMES counterpart |
|---|---|---|
| `EQ_OBJ` | NPV of investment minus salvage value, fixed and variable O&M, resources | `EQ_OBJ` (investment, fixed, variable and salvage terms) |
| `EQ_CPT` | capacity = residual capacity + vintages within technical lifetime | `EQ_CPT` |
| `EQ_CAPACT` | activity <= capacity x availability x slice length | `EQ_CAPACT` |
| `EQ_COMBAL` | production + supply >= consumption + demand, per slice or year | `EQ_COMBAL` |
| `EQ_MUSTUSE` | all supplied waste is incinerated | bound on commodity net (`COM_BNDNET`) |
| `EQ_CO2CAP` | captured biogenic CO2 = storage (BECCS) + CCU (e-kerosene) | `EQ_COMBAL` with `=E=` for an environmental commodity |
| `EQ_HYDAFA`, `EQ_HYDSEAS` | hydro annual and seasonal energy | `NCAP_AF` with `ANNUAL`/`SEASON` time-slice levels |
| `EQ_EMIS` | CO2, NOx and PM2.5 accounting per unit of activity | `ENV_ACT` / `FLO_EMIS` |
| `EQ_CO2GROSS`, `EQ_CO2NET` | gross cap and net zero from 2045 | `COM_BNDNET` / user constraint on emissions |
| `EQ_SAF`, `EQ_SYN` | ReFuelEU minimum SAF and synthetic shares | user constraints (`UC_ACT`) |
| `EQ_PEAK` | firm capacity >= peak load x (1 + margin) | `EQ_PEAK` with `NCAP_PKCNT`, `COM_PKRSV` |
| variable bounds | supply steps, technology start year, growth limit per period | `ACT_BND` on supply processes, `NCAP_START`, `NCAP_BND` |

Differences from TIMES, stated plainly: all input and output shares are fixed, so flows are expressed through `VAR_ACT` and `PRC_ACTFLO` and `VAR_FLO` is eliminated by substitution; processes operate either at slice level or at annual level (`PRC_TS`); there is no trade between regions, no elastic demand and no storage process (hydrogen is balanced annually, with a storage cost added to hydrogen turbines).

### Calibration (2025 vs statistics)

| Item | Statistics (TWh) | Model 2025 (TWh) | Difference |
|---|---|---|---|
| Hydropower | 68.1 | 67.5 | -0.8% |
| Nuclear | 44.8 | 46.1 | +2.9% |
| Wind | 39.0 | 41.3 | +5.9% |
| Solar | 4.4 | 4.3 | -1.8% |
| Conventional thermal | 11.6 | 9.8 | -15.6% |
| Total electricity production | 167.9 | 169.0 | +0.7% |
| District heating supply | 60.5 | 60.0 | -0.8% |

Electricity: SCB, Electricity supply 2025 (preliminary). District heating: SCB 2023. Built-in checks run after every solve: no unserved demand, no negative costs, no process producing more energy than it consumes (heat pumps and industrial electrification excluded), all balances satisfied.

### Co-benefits: stationary NOx and PM2.5 (model scope)

| Scenario | NOx 2025 (kt) | NOx 2045 (kt) | PM2.5 2025 (kt) | PM2.5 2045 (kt) |
|---|---|---|---|---|
| Forest first, on time | 33.1 | 33.7 | 6.1 | 5.4 |
| Scarce forest, on time | 33.1 | 27.4 | 6.1 | 4.1 |
| Electrons win, on time | 33.1 | 31.9 | 6.1 | 5.3 |

Less biomass combustion lowers NOx and PM2.5; liquid-fuel gas turbines have high NOx factors per unit of fuel but run few hours. Factors are Tier 1 orders of magnitude (EMEP/EEA Guidebook) and cover stationary combustion only. Full table: [`results/tables/co_benefits.md`](results/tables/co_benefits.md).

### Value of information

Simplified analogue of the stochastic mode of TIMES ([`scripts/voi.py`](scripts/voi.py)): biomass availability is the same until 2035 and revealed in 2040 (x1.2, x1.0 or x0.7, probability 1/3 each). The expected-value plan (EV) fixes all investments up to 2035 and is re-solved in each state (EEV); the wait-and-see solutions (WS) know the state in advance. EEV - WS = 37 MEUR is an upper bound on EVPI. The first-stage decisions that differ most across states are liquid-biofuel versus hydrogen gas turbines (2 GW range) and onshore wind (1.2 GW). The full two-stage recourse problem (RP, and VSS = EEV - RP) exceeds the GAMS demo licence used for development and is left for a run with a full licence. Results: [`results/tables/voi.md`](results/tables/voi.md).

More figures: [district heating by source](results/figures/fig3_district_heat.png), [system cost and CO2 shadow price](results/figures/fig4_cost_and_co2_price.png).

## How to run

Requirements: GAMS (developed with GAMS 54.5, written in classic syntax for GAMS 45 or newer) and Python 3.10+ with pandas and matplotlib. The full model has about 1,530 equations and 1,620 variables, so it also solves under the GAMS demo licence.

```bash
gams model/core.gms --SCN=forest_first --TIMING=ontime   # one run, writes results/forest_first_ontime.gdx
python scripts/run_all.py     # 6 core runs + 9 sensitivity runs -> results/csv/
python scripts/plots.py       # figures and tables -> results/figures/, results/tables/
python scripts/voi.py         # value of information -> results/tables/voi.md
```

The Python scripts find GAMS through the `GAMS_SYSDIR` environment variable, the `gamspy_base` package or `gams` on the PATH, and read GDX files with `gams.transfer` (for GAMS 45: `pip install "gamsapi[transfer]==45.*"`; or `pip install gamspy`, which bundles a GAMS system).

```
model/core.gms        sets, data, variables, equations, solve (TIMES names)
model/report.gms      reporting and model checks
scenarios/*.gms       scenario narratives as parameter values
data/*.csv            processes, flows, residual capacity, time slices, demand, resources, policy
data/sources.csv      source and verification status of every number
scripts/              run_all.py, plots.py, voi.py, gdxio.py
results/              figures, tables and CSV results
```

## Limitations

Illustrative data, one region without electricity trade beyond a fixed export and a capped import, fixed output shares, perfect foresight within each scenario, exogenous demands, no land-use or forest carbon accounting (biomass is treated as carbon neutral at combustion) and a CO2 target applied proportionally to the model scope. The model answers relative questions about allocation and trade-offs; it does not forecast the Swedish energy system.

## Future work

- Soft-linking with a spatially explicit model of biofuel supply chains (plant locations, feedstock transport, heat sinks) and with a CGE model, in the spirit of the EMEC and TIMES-Sweden linkage (Krook-Riekkola et al. 2017).
- The full two-stage stochastic recourse problem (RP and VSS) and uncertainty in technology timing as a second stochastic dimension.
- Running the same question on the open-source TIMES code with a reduced TIMES-Sweden data set.

## References

- Sandberg, E. and Krook-Riekkola, A. (2022). The impact of technology availability on the transition to net-zero industry in Sweden. *Journal of Cleaner Production* 363, 132594. doi:10.1016/j.jclepro.2022.132594
- Krook-Riekkola, A., Wetterlund, E. and Sandberg, E. (2017). *Biomassa, systemmodeller och målkonflikter*. Energiforsk rapport 2017:407.
- Krook-Riekkola, A., Berg, C., Ahlgren, E. O. and Söderholm, P. (2017). Challenges in top-down and bottom-up soft-linking: Lessons from linking a Swedish energy system model with a CGE model. *Energy* 141, 803-817.
- Regulation (EU) 2023/2405 (ReFuelEU Aviation), Annex I.
- SCB: Electricity supply 2025 (preliminary); district heating supply by type of plant 2023.
- Naturvårdsverket: preliminary greenhouse gas statistics for 2024 (June 2025).
- Danish Energy Agency: Technology Data catalogues; EMEP/EEA Air Pollutant Emission Inventory Guidebook; IPCC 2006 Guidelines (emission factors).

Author: Mikhail Serikov, 2026.
