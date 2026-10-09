# Extension of the open-source TIMES demo

A first step from the stand-alone model towards the real TIMES code: one Swedish-type process added to the TIMES demo model ([etsap-TIMES/TIMES_Demo](https://github.com/etsap-TIMES/TIMES_Demo), based on Demo12), as a data file only. The TIMES source code is not changed.

| File | Content |
|---|---|
| `swe_btl.dd` | new process `BTLFT01` in REG1: biomass gasification + Fischer-Tropsch; input `BIO`, outputs `KER` (jet, 55%) and `DSL` (diesel, 45%) through `ACT_EFF` 0.5 and `FLO_SHAR`; investment and O&M costs, lifetime 25 years, available from 2030 (`NCAP_START`) |
| `swe_btl_force.dd` | policy variant: at least 100 PJ/yr of biomass into `BTLFT01` in 2030 and 2050 (`ACT_BND` LO) |
| `demo12_swe.run` | `demo12.run` with one added line: `$BATINCLUDE swe_btl.dd` |
| `demo12_swe_force.run` | as above plus `$BATINCLUDE swe_btl_force.dd` |
| `swe_btl_biolimit.dd` | biomass-limited variant: domestic biomass supply in REG1 capped at 1,000 PJ/yr from 2030 (`ACT_BND` UP on `MINBIO1`) |
| `demo12_swe_biolimit.run` | `demo12_swe.run` plus `$BATINCLUDE swe_btl_biolimit.dd` |

Not represented in this first step: the heat co-product (the demo has no district heating commodity), electricity input, CO2 capture and a credit for biogenic CO2.

## How to run

1. Download TIMES_Demo and copy the four files into its `model` folder.
2. From that folder: `gams rundemo --runname=demo12_swe`, then the same with `demo12_swe_force` and `demo12_swe_biolimit` (in GAMS Studio: change the default `runname` in `rundemo.gms`).
3. Compare `OBJECTIVE VALUE` and the activity of `BTLFT01` with the unchanged demo (`gams rundemo`). The difference in objective between the forced and the free run is the cost of the mandate.

## Results (TIMES 4.7.3, GAMS 45.7, CBC)

| Run | Objective (MEUR2005) |
|---|---|
| unchanged demo | 23,960,685.7 |
| + `BTLFT01` | 23,569,615.9 |
| + `BTLFT01`, at least 100 PJ forced | 23,569,615.9 |

REG1, PJ per year:

| | Demo 2030 | + BTLFT01 2030 | Demo 2050 | + BTLFT01 2050 |
|---|---|---|---|---|
| domestic biomass (`MINBIO1`) | 632 | 7,270 | 686 | 7,886 |
| biomass into `BTLFT01` | 0 | 6,638 | 0 | 7,200 |
| diesel imports (`IMPDSL1`) | 6,293 | 0 | 7,403 | 0 |
| crude imports = refinery input | 9,920 | 4,619 | 10,073 | 4,692 |

With unlimited biomass at about 4 MEUR/PJ (15 EUR/MWh) against imported diesel and kerosene at 10-11 MEUR/PJ, gasification-FT replaces all diesel imports and half of the refinery throughput in REG1, and biomass use grows elevenfold. The forced variant changes nothing because the model already exceeds the bound. The result is not physically plausible: it shows that the answer is driven by the biomass supply assumption, which is the question the stand-alone model in this repository addresses with a stepwise, scenario-dependent biomass supply. The biomass-limited variant (`demo12_swe_biolimit`) tests the same process when biomass is scarce.

## Status

Checked with GAMS 54.5: all three extended variants compile, passes the TIMES quality checks without new warnings and adds the new process to the model (4 equations and 8 variables more than the demo). The unchanged demo solves to optimality with TIMES 4.7.3 and GAMS 45.7.

`demo12_swe.run` and `demo12_swe_force.run` are adapted from `demo12.run` of TIMES_Demo (CC BY 4.0). The `.dd` files with the new process are original illustrative data.
