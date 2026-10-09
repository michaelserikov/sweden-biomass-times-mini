# Extension of the open-source TIMES demo

A first step from the stand-alone model towards the real TIMES code: one Swedish-type process added to the TIMES demo model ([etsap-TIMES/TIMES_Demo](https://github.com/etsap-TIMES/TIMES_Demo), based on Demo12), as a data file only. The TIMES source code is not changed.

| File | Content |
|---|---|
| `swe_btl.dd` | new process `BTLFT01` in REG1: biomass gasification + Fischer-Tropsch; input `BIO`, outputs `KER` (jet, 55%) and `DSL` (diesel, 45%) through `ACT_EFF` 0.5 and `FLO_SHAR`; investment and O&M costs, lifetime 25 years, available from 2030 (`NCAP_START`) |
| `swe_btl_force.dd` | policy variant: at least 100 PJ/yr of biomass into `BTLFT01` in 2030 and 2050 (`ACT_BND` LO) |
| `demo12_swe.run` | `demo12.run` with one added line: `$BATINCLUDE swe_btl.dd` |
| `demo12_swe_force.run` | as above plus `$BATINCLUDE swe_btl_force.dd` |

Not represented in this first step: the heat co-product (the demo has no district heating commodity), electricity input, CO2 capture and a credit for biogenic CO2.

## How to run

1. Download TIMES_Demo and copy the four files into its `model` folder.
2. From that folder: `gams rundemo --runname=demo12_swe` and `gams rundemo --runname=demo12_swe_force`.
3. Compare `OBJECTIVE VALUE` and the activity of `BTLFT01` with the unchanged demo (`gams rundemo`). The difference in objective between the forced and the free run is the cost of the mandate.

## Status

Checked with GAMS 54.5: the extended model compiles, passes the TIMES quality checks without new warnings and adds the new process to the model (4 equations and 8 variables more than the demo). The unchanged demo solves to optimality with TIMES 4.7.3 and GAMS 45.7.

`demo12_swe.run` and `demo12_swe_force.run` are adapted from `demo12.run` of TIMES_Demo (CC BY 4.0). The `.dd` files with the new process are original illustrative data.
