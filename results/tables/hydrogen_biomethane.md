# Hydrogen, biomethane and industrial decarbonisation (v0.2, illustrative data)

## 1. Value of hydrogen storage (on time, 2045)

Hydrogen is balanced by season; a lined rock cavern store moves it between seasons. Value of storage = system cost without a store minus system cost with it.

| scenario | H2 demand 2045 (TWh) | electrolysis (GW) | electrolysis without store (GW) | store (TWh) | max level (TWh) | H2 price (EUR/MWh) | H2 price without store | value of storage (MEUR NPV) | store at x0.25 cost (TWh) | value at x0.25 cost (MEUR NPV) | store at x0.1 cost (TWh) | value at x0.1 cost (MEUR NPV) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Forest first | 7.2 | 0.88 | 0.91 | 0.06 | 0.06 | 78.4 | 78.3 | 1 | 0.06 | 26 | 0.26 | 42 |
| Scarce forest | 7.8 | 0.95 | 0.98 | 0.07 | 0.07 | 80.1 | 80.2 | 2 | 0.40 | 39 | 1.06 | 89 |
| Electrons win | 9.9 | 1.25 | 1.25 | 0.00 | 0.00 | 68.8 | 68.8 | 0 | 0.09 | 17 | 0.33 | 32 |

## 2. Abatement cost curve: CO2 price mode, 2045

CO2 price on gross fossil CO2 rising from 80 EUR/t in 2030 to the stated 2045 level (no cap, no net-zero constraint). NEGCR = 1: stored biogenic CO2 earns the price.

### Forest first, stored CO2 paid

| price | gross fossil CO2 | stored CO2 | net CO2 | IHT_FOS | IHT_ELC | IHT_H2 | BG_AD | BG_SNG | GAS_BMG | RD_BMG | H2 | H2 store |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 8.5 | 1.8 | 6.7 | 10.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 7.2 | 0.00 |
| 100 | 8.4 | 8.8 | -0.3 | 10.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 7.2 | 0.00 |
| 125 | 8.1 | 10.0 | -1.9 | 7.8 | 2.2 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 7.2 | 0.00 |
| 150 | 4.6 | 10.0 | -5.4 | 5.8 | 4.2 | 0.0 | 5.9 | 0.0 | 0.0 | -5.9 | 7.2 | 0.00 |
| 200 | 3.6 | 10.0 | -6.4 | 5.3 | 4.7 | 0.0 | 5.9 | 0.0 | 0.0 | -5.9 | 7.2 | 0.06 |
| 250 | 2.6 | 10.0 | -7.4 | 5.2 | 4.7 | 0.0 | 5.9 | 4.9 | -5.1 | -5.8 | 7.2 | 0.06 |
| 300 | 2.4 | 10.0 | -7.6 | 4.6 | 4.7 | 0.7 | 5.9 | 7.6 | -5.1 | -8.4 | 8.0 | 0.07 |
| 400 | 2.4 | 10.0 | -7.6 | 3.8 | 4.7 | 1.4 | 5.9 | 7.5 | -4.3 | -9.1 | 8.8 | 0.08 |
| 500 | 2.4 | 10.0 | -7.6 | 4.5 | 4.7 | 0.8 | 5.9 | 5.0 | -5.0 | -5.9 | 8.1 | 0.07 |

### Forest first, stored CO2 not paid

| price | gross fossil CO2 | stored CO2 | net CO2 | IHT_FOS | IHT_ELC | IHT_H2 | BG_AD | BG_SNG | GAS_BMG | RD_BMG | H2 | H2 store |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 8.5 | 0.0 | 8.5 | 10.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 7.2 | 0.00 |
| 100 | 7.2 | 0.0 | 7.2 | 10.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 7.2 | 0.00 |
| 125 | 6.7 | 0.0 | 6.7 | 10.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 7.2 | 0.00 |
| 150 | 4.8 | 0.0 | 4.8 | 7.6 | 2.4 | 0.0 | 3.6 | 0.0 | 0.0 | -3.6 | 7.2 | 0.06 |
| 200 | 3.6 | 0.0 | 3.6 | 5.3 | 4.7 | 0.0 | 5.9 | 0.0 | 0.0 | -5.9 | 7.2 | 0.06 |
| 250 | 2.4 | 0.0 | 2.4 | 5.3 | 4.7 | 0.0 | 5.1 | 3.3 | -5.9 | -2.5 | 7.2 | 0.06 |
| 300 | 2.4 | 0.0 | 2.4 | 5.3 | 4.7 | 0.0 | 5.1 | 3.8 | -5.9 | -2.9 | 7.2 | 0.06 |
| 400 | 2.4 | 0.0 | 2.4 | 4.6 | 4.7 | 0.7 | 5.1 | 5.9 | -5.2 | -5.8 | 8.0 | 0.00 |
| 500 | 2.4 | 0.0 | 2.4 | 4.4 | 4.7 | 0.8 | 5.1 | 4.1 | -5.0 | -4.2 | 8.2 | 0.00 |

### Electrons win, stored CO2 paid

| price | gross fossil CO2 | stored CO2 | net CO2 | IHT_FOS | IHT_ELC | IHT_H2 | BG_AD | BG_SNG | GAS_BMG | RD_BMG | H2 | H2 store |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 8.7 | 0.9 | 7.8 | 10.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 9.9 | 0.00 |
| 100 | 8.4 | 2.2 | 6.3 | 8.3 | 1.7 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 9.9 | 0.00 |
| 125 | 7.7 | 10.0 | -2.3 | 5.3 | 4.7 | 0.0 | 2.9 | 0.0 | 0.0 | -2.9 | 9.9 | 0.00 |
| 150 | 5.4 | 10.0 | -4.6 | 5.3 | 4.7 | 0.0 | 5.9 | 0.0 | 0.0 | -5.9 | 9.9 | 0.00 |
| 200 | 2.7 | 10.0 | -7.3 | 1.2 | 4.7 | 4.1 | 5.9 | 7.1 | 0.0 | -13.0 | 14.5 | 0.00 |
| 250 | 2.4 | 10.0 | -7.6 | 0.0 | 4.7 | 5.3 | 5.9 | 7.9 | -0.1 | -13.7 | 15.8 | 0.00 |
| 300 | 2.4 | 10.0 | -7.6 | 0.1 | 4.7 | 5.2 | 5.1 | 9.1 | -0.2 | -14.0 | 15.7 | 0.00 |
| 400 | 2.4 | 10.0 | -7.6 | 0.0 | 4.7 | 5.3 | 5.1 | 9.1 | -0.1 | -14.1 | 15.8 | 0.00 |
| 500 | 2.4 | 10.0 | -7.6 | 0.0 | 4.7 | 5.3 | 5.1 | 7.2 | -0.1 | -12.2 | 15.8 | 0.00 |

IHT_*: high-temperature heat by process (TWh); IHT_FOS burns grid gas, which includes injected biomethane (GAS_BMG, negative = use). BG_*: biomethane production (TWh). RD_BMG: biomethane to heavy road transport.

## 3. Biogenic carbon debt on additional forest biomass (cap mode, on time, 2045)

| scenario | carbon debt share | forest biomass (TWh) | of which CHP with capture | carbon debt (Mt) | stored CO2 (Mt) | biomethane (TWh) | CO2 price (EUR/t) | extra cost (MEUR NPV) |
|---|---|---|---|---|---|---|---|---|
| Forest first | 0.0 | 72.8 | 14.0 | 0.0 | 5.2 | 4.4 | 145 | 0 |
| Forest first | 0.3 | 60.0 | 21.5 | 2.9 | 8.1 | 5.9 | 194 | 1,545 |
| Forest first | 0.6 | 36.0 | 13.5 | 0.0 | 5.2 | 5.9 | 211 | 2,024 |
| Scarce forest | 0.0 | 45.5 | 14.1 | 0.0 | 5.2 | 5.0 | 195 | 0 |
| Scarce forest | 0.3 | 35.6 | 16.7 | 1.8 | 7.0 | 5.9 | 225 | 1,222 |
| Scarce forest | 0.6 | 21.0 | 4.6 | 0.0 | 5.2 | 5.9 | 225 | 1,628 |
| Electrons win | 0.0 | 57.6 | 14.4 | 0.0 | 5.2 | 6.2 | 171 | 0 |
| Electrons win | 0.3 | 47.7 | 21.0 | 2.1 | 7.3 | 5.0 | 202 | 1,236 |
| Electrons win | 0.6 | 30.0 | 9.6 | 0.0 | 5.2 | 5.9 | 225 | 1,362 |

## 4. Cost of avoided CO2 by technology at 2045 shadow prices (Forest first, on time)

Prices used (EUR/MWh): NG 35, COA 15, OIL_JET 55, OIL_DSL 60, ELC 43, H2 78, BMG 73, BIO_SOL 30, HET 48; CO2 storage 50 EUR/t. Levelised capital at 4%.

| option | unit | cost | reference cost | CO2 avoided (t per unit) | cost of avoided CO2 (EUR/t) |
|---|---|---|---|---|---|
| Industrial heat: electrification | EUR/MWh | 52.5 | 42.8 | 0.224 | 43 |
| Hydrogen direct reduction steel | EUR/t steel | 321.9 | 185.7 | 1.870 | 73 |
| Bio-CCS at CHP | EUR/MWh el | 162.9 | 28.6 | 1.810 | 74 |
| Biogenic CO2 from upgrading, stored | EUR/t CO2 | 75.2 | 0.0 | 1.000 | 75 |
| High-temperature heat: electric | EUR/MWh | 73.1 | 42.8 | 0.224 | 135 |
| Heavy road: biomethane | EUR/MWh | 98.6 | 60.0 | 0.267 | 145 |
| High-temperature heat: biomethane | EUR/MWh | 86.9 | 42.8 | 0.224 | 197 |
| High-temperature heat: hydrogen | EUR/MWh | 93.9 | 42.8 | 0.224 | 228 |
| Industrial heat: fossil gas with CCS | EUR/MWh | 92.3 | 42.8 | 0.199 | 248 |
| Aviation: e-kerosene (biogenic CO2) | EUR/MWh | 157.0 | 55.0 | 0.257 | 397 |
