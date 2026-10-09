# Extension of the open-source TIMES demo

A first step from the stand-alone model towards the real TIMES code: one Swedish-type process added to the TIMES demo model ([etsap-TIMES/TIMES_Demo](https://github.com/etsap-TIMES/TIMES_Demo), based on Demo12), as a data file only. The TIMES source code is not changed.

| File | Content |
|---|---|
| `swe_btl.dd` | new process `BTLFT01` in REG1: biomass gasification + Fischer-Tropsch; input `BIO`, outputs `KER` (jet, 55%) and `DSL` (diesel, 45%); activity = liquid output, `ACT_EFF` 0.5 (2 PJ biomass per PJ liquids), shares fixed with `FLO_SHAR` in each model year; investment and O&M costs per GW of liquids, lifetime 25 years, available from 2030 (`NCAP_START`) |
| `swe_btl_force.dd` | policy variant: at least 50 PJ/yr of liquids (100 PJ/yr of biomass) from `BTLFT01` in 2030 and 2050 (`ACT_BND` LO) |
| `demo12_swe.run` | `demo12.run` with one added line: `$BATINCLUDE swe_btl.dd` |
| `demo12_swe_force.run` | as above plus `$BATINCLUDE swe_btl_force.dd` |
| `swe_btl_biolimit.dd` | biomass-limited variant: domestic biomass supply in REG1 capped at 1,000 PJ/yr from 2030 (`ACT_BND` UP on `MINBIO1`) |
| `demo12_swe_biolimit.run` | `demo12_swe.run` plus `$BATINCLUDE swe_btl_biolimit.dd` |

Not represented in this first step: the heat co-product (the demo has no district heating commodity), electricity input, CO2 capture and a credit for biogenic CO2.

## How to run

1. Download TIMES_Demo and copy the four files into its `model` folder.
2. From that folder: `gams rundemo --runname=demo12_swe`, then the same with `demo12_swe_force` and `demo12_swe_biolimit` (in GAMS Studio: change the default `runname` in `rundemo.gms`).
3. Compare `OBJECTIVE VALUE` and the activity of `BTLFT01` with the unchanged demo (`gams rundemo`). The difference in objective between the forced and the free run is the cost of the mandate.

## Results

Runs with TIMES 4.7.3 on the demo reduced to the milestone years 2005 and 2030 (the same kind of reduction the demo itself uses to fit the GAMS community licence; here it keeps the model below the GAMS demo licence limit), solved with CPLEX:

| Run | Objective (MEUR2005) | `BTLFT01` in 2030 |
|---|---|---|
| unchanged demo | 15,210,943.1 | |
| + `BTLFT01` | 15,210,943.1 | not built |
| + `BTLFT01`, biomass limited | 15,210,943.1 | not built |
| + `BTLFT01`, 50 PJ liquids forced | 15,213,612.2 | 100 PJ biomass -> 27.5 PJ kerosene + 22.5 PJ diesel |

In the demo, gasification-FT is not chosen on cost alone: the demo has no CO2 price and no SAF mandate, and the liquids compete with imported diesel and kerosene. Forcing 50 PJ/yr of liquids raises the discounted system cost by about 2,700 MEUR2005 in this reduced version. The flows of the forced run confirm the process definition (50% conversion, 55/45 split).

An earlier version of `swe_btl.dd` defined the activity on the biomass input with `ACT_EFF` 0.5. TIMES applies `ACT_EFF` between the primary group and the other side of the process, so that version produced 2 PJ of liquids per PJ of biomass and its full-horizon results (with very large biofuel production) were wrong; they have been withdrawn.

## Status

All variants compile and pass the TIMES quality checks without new warnings. The full-horizon demo (2005-2050) solves to optimality with TIMES 4.7.3 and GAMS 45.7; the corrected extension has so far been solved on the reduced horizon above.

`demo12_swe.run` and `demo12_swe_force.run` are adapted from `demo12.run` of TIMES_Demo (CC BY 4.0). The `.dd` files with the new process are original illustrative data.
