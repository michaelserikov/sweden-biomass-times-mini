$title Sweden forest biomass allocation: TIMES-inspired energy system model
$ontext
TIMES-inspired linear optimisation model of the Swedish energy system, built
on the TIMES model architecture: names of sets, parameters, variables and
equations follow TIMES conventions. It is NOT TIMES and does not use the
TIMES source code. All data are illustrative (see data/sources.csv).

Question: how should Sweden's limited forest biomass be allocated between
turbine fuels (aviation, peak gas turbines), district heating, industry and
BECCS on the way to net zero in 2045?

Units: capacity GW (steel: Mt/yr), energy TWh, costs MEUR (NPV, base 2025),
CO2 Mt, NOx and PM2.5 kt. MEUR/TWh = EUR/MWh, MEUR/Mt = EUR/t.

Run:  gams model/core.gms --SCN=forest_first --TIMING=ontime
Options (with defaults):
  --SCN=forest_first | scarce_forest | electrons_win
  --TIMING=ontime (new technologies from 2030) | delay (from 2040)
  --DRATE=0.04      discount rate
  --NONCO2=1        multiplier on domestic aviation CO2 (non-CO2 effects)
  --OUT=<file.gdx>  results file (default results/<SCN>_<TIMING>.gdx)
  Value-of-information runs (scripts/voi.py):
  --BIO40=<x>       forest biomass multiplier from 2040 (uncertainty resolved in 2040)
  --FIX1=<file.gdx> fix investments up to 2035 to those in <file.gdx> (first stage)
$offtext

$setNames "%gams.input%" MODELDIR fname fext
$set DATA   %MODELDIR%..%system.dirsep%data%system.dirsep%
$set SCNDIR %MODELDIR%..%system.dirsep%scenarios%system.dirsep%
$if not set SCN    $set SCN    forest_first
$if not set TIMING $set TIMING ontime
$if not set DRATE  $set DRATE  0.04
$if not set NONCO2 $set NONCO2 1
$if not set OUT    $set OUT    %MODELDIR%..%system.dirsep%results%system.dirsep%%SCN%_%TIMING%.gdx

*========================================================================
* 1. Sets
*========================================================================
Sets
   T     'model periods (milestone years, 5-year periods)'
         / 2025, 2030, 2035, 2040, 2045, 2050 /
   S     'time slices (ANNUAL + 4 seasons x day/night + winter peak)'
         / ANNUAL, WI_D, WI_N, SP_D, SP_N, SU_D, SU_N, FA_D, FA_N, WI_P /
   TS(S) 'intra-annual time slices'
         / WI_D, WI_N, SP_D, SP_N, SU_D, SU_N, FA_D, FA_N, WI_P /
   SEAS  'seasons' / WI, SP, SU, FA /
   TS_SEAS(S,SEAS) 'slice to season'
         / (WI_D, WI_N, WI_P).WI, (SP_D, SP_N).SP, (SU_D, SU_N).SU, (FA_D, FA_N).FA /
   PRC   'processes'
         / ELC_HYD  'hydropower (reservoir + run-of-river)'
           ELC_NUC  'nuclear'
           ELC_WON  'onshore wind'
           ELC_WOF  'offshore wind'
           ELC_SOL  'solar PV'
           ELC_IMP  'electricity imports (interconnectors)'
           CHP_BIO  'biomass CHP (district heating)'
           CHP_BCS  'biomass CHP with CO2 capture (BECCS, MEA)'
           CHP_WST  'waste CHP'
           GT_BIO   'gas turbine on liquid biofuel (peak, reserve)'
           GT_H2    'gas turbine on hydrogen'
           GT_NG    'gas turbine on fossil fuel (existing reserve)'
           HET_BOB  'biomass heat-only boiler'
           HET_HP   'large heat pump'
           HET_EB   'electric boiler'
           HET_FOS  'fossil peak boiler'
           HET_XS   'industrial excess heat'
           H2_ELZ   'electrolysis'
           BF_HEFA  'HEFA biorefinery (limited lipid feedstock)'
           BF_FT    'biomass gasification + Fischer-Tropsch'
           BF_FTC   'biomass gasification + FT with CO2 capture'
           BF_BLG   'black liquor gasification (integrated with pulp mill)'
           EF_EKER  'e-kerosene from H2 and captured biogenic CO2'
           IND_BLQ  'pulp mill recovery boiler'
           IND_BLC  'pulp mill recovery boiler with CO2 capture (BECCS)'
           IND_BIO  'industrial biomass boiler'
           IND_ELC  'industrial electrification (e-boilers, heat pumps)'
           IND_FOS  'industrial fossil boiler'
           IND_FCS  'industrial fossil boiler with CCS'
           STL_BF   'blast furnace steel (coal)'
           STL_H2   'hydrogen direct reduction steel (HYBRIT-type)'
           AV_OIL   'fossil jet fuel to aviation'
           AV_BIO   'bio-jet to aviation'
           AV_SYN   'e-kerosene to aviation'
           RD_OIL   'fossil diesel to road and machinery'
           RD_BIO   'renewable diesel to road and machinery'
           CCS_STG  'transport and geological storage of captured CO2' /
   COM   'commodities'
         / ELC, HET, BIO_SOL, BLQ, WST, HEFA_FS, NG, OIL_JET, OIL_DSL, COA,
           BIO_JET, BIO_DSL, SYN_JET, H2, CO2_CAP, IND, STL, AVF, DSL /
   COM_TSL(COM) 'commodities balanced by time slice'  / ELC, HET /
   COM_DEM(COM) 'commodities with exogenous demand'   / ELC, HET, IND, STL, AVF, DSL /
   COM_MUST(COM) 'commodities that must be fully used' / WST /
   COM_FUEL(COM) 'combusted fuels (for NOx and PM2.5)'
         / BIO_SOL, BLQ, WST, HEFA_FS, NG, OIL_JET, OIL_DSL, COA, BIO_DSL, H2 /
   EM    'emission and tracking commodities (TIMES: environmental commodities)'
         / CO2_EMIS  'domestic fossil CO2 (target scope)'
           CO2_INTAV 'CO2 from international aviation (memo item, outside target)'
           CO2_STG   'biogenic CO2 stored (negative emissions)'
           NOX       'nitrogen oxides (stationary combustion)'
           PM25      'fine particulate matter (stationary combustion)' /
   IO    / IN, OUT /
   RES   'resource supply steps and imports'
         / BIO1   'forest biomass: sawmill by-products and bark'
           BIO2   'forest biomass: logging residues (GROT), current'
           BIO3   'forest biomass: additional GROT and stumps'
           BIO4   'forest biomass: low-grade roundwood and imports'
           BLQ    'black liquor (tied to pulp production)'
           WST    'municipal and industrial waste'
           HEFAFS 'lipid feedstock for HEFA (waste oils, limited)'
           NG     'fossil gas'
           OILJ   'fossil jet fuel'
           OILD   'fossil diesel and fuel oil'
           COA    'coal and coke'
           IMPHVO 'imported renewable diesel (limited)'
           IMPSAF 'imported bio-jet (limited)'
           IMPSYN 'imported e-kerosene (limited, high cost)' /
   RES_COM(RES,COM) 'resource to commodity'
         / (BIO1*BIO4).BIO_SOL, BLQ.BLQ, WST.WST, HEFAFS.HEFA_FS, NG.NG,
           OILJ.OIL_JET, OILD.OIL_DSL, COA.COA, IMPHVO.BIO_DSL, IMPSAF.BIO_JET, IMPSYN.SYN_JET /
   RES_BIO(RES) 'forest biomass supply steps' / BIO1*BIO4 /
   PATTR 'process data columns'
         / TSL, CAPF, NEW, NCAP_COST, NCAP_FOM, ACT_COST, NCAP_TLIFE, NCAP_AF,
           NCAP_BND, START, PEAK_CONT, NOX_EF, PM_EF, CAPACT /
   SATTR 'time-slice data columns'
         / G_YRFR, LF_ELC, LF_HET, LF_EXP, AF_NUC, AF_WON, AF_WOF, AF_SOL /
   DITEM 'demand data rows' / ELC, ELC_EXP, HET, IND, STL, DSL, AVF /
   RATTR / VOL, COST /
   POLATTR / SAF_SHR, SYN_SHR, STG_MAX, ELZ_COSTF, WOF_COSTF, SOL_COSTF /
   CALITEM / ELC_HYDRO, ELC_NUCLEAR, ELC_WIND, ELC_SOLAR, ELC_THERMAL, ELC_TOTAL, DH_TOTAL /
   K 'year counter' / 1*100 /;

Alias (T,V), (S,S2);

* process subsets used in equations and reporting
Sets
   PRC_TSL(PRC)  'processes operating by time slice (others: ANNUAL level)'
   PRC_CAPF(PRC) 'processes with a capacity'
   PRC_NEW(PRC)  'processes allowed to invest'
   PRC_TS(PRC,S) 'time-slice level of each process (TIMES: PRC_TS)'
   PRC_BIO(PRC)  'forest biomass users'  / CHP_BIO, CHP_BCS, HET_BOB, BF_FT, BF_FTC, IND_BIO /
   PRC_GT(PRC)   'gas turbines'          / GT_BIO, GT_H2, GT_NG /
   PRC_CCS(PRC)  'processes with CO2 capture' / CHP_BCS, BF_FTC, IND_BLC, IND_FCS /
   PRC_IND(PRC)  'industry processes'    / IND_BLQ, IND_BLC, IND_BIO, IND_ELC, IND_FOS, IND_FCS, STL_BF, STL_H2 /
   PRC_CHP(PRC)  'CHP plants'            / CHP_BIO, CHP_BCS, CHP_WST /
   PRC_DLY(PRC)  'new technologies on the timing axis'
                 / CHP_BCS, BF_FT, BF_FTC, BF_BLG, EF_EKER, IND_BLC /
   PRC_THERMAL(PRC) 'thermal power for calibration'
                 / CHP_BIO, CHP_BCS, CHP_WST, GT_BIO, GT_H2, GT_NG, IND_BLQ, IND_BLC /;

*========================================================================
* 2. Data
*========================================================================
Table PTAB(PRC,PATTR) 'process data'
$onDelim
$include "%DATA%processes.csv"
$offDelim
;
Parameter PRC_ACTFLO(PRC,COM,IO) 'flow per unit of activity' /
$onDelim
$include "%DATA%flows.csv"
$offDelim
/;
Table PRC_RESID(PRC,T) 'existing capacity remaining in each period'
$onDelim
$include "%DATA%resid.csv"
$offDelim
;
Table STAB(S,SATTR) 'time-slice data'
$onDelim
$include "%DATA%timeslices.csv"
$offDelim
;
Table DTAB(DITEM,T) 'exogenous demand (TWh; STL in Mt)'
$onDelim
$include "%DATA%demand.csv"
$offDelim
;
Table RTAB(RES,RATTR) 'resource volume (TWh/yr) and cost (EUR/MWh)'
$onDelim
$include "%DATA%resources.csv"
$offDelim
;
Table POLTAB(T,POLATTR) 'policy and cost trajectories'
$onDelim
$include "%DATA%policy.csv"
$offDelim
;
Parameter FLO_EMIS(COM) 'fossil CO2 factor (Mt per TWh fuel)' /
$onDelim
$include "%DATA%fuels.csv"
$offDelim
/;
Table CALTAB(CALITEM,*) 'calibration statistics for 2025 (TWh)'
$onDelim
$include "%DATA%calibration.csv"
$offDelim
;

* scenario parameters (defaults, overwritten by scenarios/*.gms)
Scalars
   BIO_MULT  'forest biomass availability multiplier (from 2030)' / 1 /
   AVI_G     'annual growth of aviation fuel demand'               / 0.01 /
   ELZ_MULT  'electrolysis investment cost multiplier'             / 1 /
   WIND_MULT 'wind investment cost multiplier'                     / 1 /
   SYN_MULT  'multiplier on the synthetic aviation fuel sub-quota' / 1 /;
$include "%SCNDIR%%SCN%.gms"

Scalars
   G_DRATE   'discount rate'                                       / %DRATE% /
   NONCO2    'multiplier on domestic aviation CO2 (non-CO2 effects)' / %NONCO2% /
   DLY_START 'first year of technologies on the timing axis'       / 2030 /
   DOM_SHR   'domestic share of jet fuel uplifted in Sweden'       / 0.18 /
   RED_2025  'national GHG reduction vs 1990 reached by 2024'      / 0.33 /
   RED_2045  'national target: territorial reduction vs 1990'      / 0.85 /
   PEAK_MARG 'peak reserve margin'                                 / 0.05 /
   HYD_AFA   'hydro annual energy availability'                    / 0.47 /
   HYD_SEAS  'max share of annual hydro energy in one season'      / 0.32 /
   HYD_MIN   'min hydro output per slice (share of capacity)'      / 0.15 /
   DUM_COST  'cost of unserved demand (EUR/MWh)'                   / 10000 /
   CO2ON     'switch for CO2 constraints'                          / 0 /;
$ifi "%TIMING%"=="delay" DLY_START = 2040;

Parameters
   YEAR(T)          'milestone year'
   G_YRFR(S)        'fraction of the year in time slice'
   COM_FR(COM,S)    'demand fraction by time slice'
   EXP_FR(S)        'export profile by time slice'
   NCAP_COST(PRC,T) 'investment cost (MEUR per GW or per Mt/yr)'
   NCAP_FOM(PRC)    'fixed O&M (MEUR per GW per year)'
   ACT_COST(PRC)    'variable cost (MEUR per unit activity)'
   NCAP_TLIFE(PRC)  'technical lifetime (years)'
   NCAP_AFS(PRC,S)  'availability factor by time slice'
   NCAP_BND(PRC)    'max new capacity per period'
   START(PRC)       'first year of availability'
   PEAK_CONT(PRC)   'contribution of capacity to peak reserve'
   CAPACT(PRC)      'activity per unit capacity per year'
   ENV_ACT(PRC,EM)  'emission per unit of activity'
   COM_PROJ(COM,T)  'exogenous demand'
   DEM(COM,T,S)     'demand by time slice'
   PEAK_LOAD(T)     'domestic peak load (GW)'
   RES_VOL(RES,T)   'resource volume (TWh/yr)'
   RES_COST(RES)    'resource cost (MEUR/TWh)'
   SAF_SHR(T)       'ReFuelEU minimum SAF share'
   SYN_SHR(T)       'ReFuelEU minimum synthetic fuel share'
   STG_MAX(T)       'CO2 storage capacity (Mt/yr)'
   CO2_GROSS_FR(T)  'gross fossil CO2 cap as share of 2025 model emissions'
   ANNF(T)          'discount factor for annual costs in period'
   INVF(T)          'discount factor for investment in period'
   SALVF(PRC,T)     'salvage share of investment made in period'
   E_BASE           'model CO2 emissions in 2025 (Mt)' / 0 /;

YEAR(T)   = 2025 + 5*(ord(T) - 1);
G_YRFR(S) = STAB(S,'G_YRFR');
G_YRFR('ANNUAL') = 1;

COM_FR('ELC',TS) = STAB(TS,'LF_ELC')*G_YRFR(TS) / sum(S2$TS(S2), STAB(S2,'LF_ELC')*G_YRFR(S2));
COM_FR('HET',TS) = STAB(TS,'LF_HET')*G_YRFR(TS) / sum(S2$TS(S2), STAB(S2,'LF_HET')*G_YRFR(S2));
EXP_FR(TS)       = STAB(TS,'LF_EXP')*G_YRFR(TS) / sum(S2$TS(S2), STAB(S2,'LF_EXP')*G_YRFR(S2));
COM_FR(COM,'ANNUAL')$(not COM_TSL(COM)) = 1;

PRC_TSL(PRC)  = PTAB(PRC,'TSL') > 0;
PRC_CAPF(PRC) = PTAB(PRC,'CAPF') > 0;
PRC_NEW(PRC)  = PTAB(PRC,'NEW') > 0;
PRC_TS(PRC,TS)$PRC_TSL(PRC) = yes;
PRC_TS(PRC,'ANNUAL')$(not PRC_TSL(PRC)) = yes;

NCAP_COST(PRC,T) = PTAB(PRC,'NCAP_COST');
NCAP_COST('H2_ELZ',T)  = NCAP_COST('H2_ELZ',T)  * POLTAB(T,'ELZ_COSTF') * ELZ_MULT;
NCAP_COST('ELC_WOF',T) = NCAP_COST('ELC_WOF',T) * POLTAB(T,'WOF_COSTF') * WIND_MULT;
NCAP_COST('ELC_WON',T) = NCAP_COST('ELC_WON',T) * WIND_MULT;
NCAP_COST('ELC_SOL',T) = NCAP_COST('ELC_SOL',T) * POLTAB(T,'SOL_COSTF');
NCAP_FOM(PRC)   = PTAB(PRC,'NCAP_FOM');
ACT_COST(PRC)   = PTAB(PRC,'ACT_COST');
NCAP_TLIFE(PRC) = PTAB(PRC,'NCAP_TLIFE');
NCAP_BND(PRC)   = PTAB(PRC,'NCAP_BND');
START(PRC)      = PTAB(PRC,'START');
START(PRC_DLY)  = max(START(PRC_DLY), DLY_START);
PEAK_CONT(PRC)  = PTAB(PRC,'PEAK_CONT');
CAPACT(PRC)     = PTAB(PRC,'CAPACT');

NCAP_AFS(PRC,S)$PRC_TS(PRC,S) = PTAB(PRC,'NCAP_AF');
NCAP_AFS('ELC_NUC',TS) = STAB(TS,'AF_NUC');
NCAP_AFS('ELC_WON',TS) = STAB(TS,'AF_WON');
NCAP_AFS('ELC_WOF',TS) = STAB(TS,'AF_WOF');
NCAP_AFS('ELC_SOL',TS) = STAB(TS,'AF_SOL');

* emissions per unit of activity, derived from fuel inputs
ENV_ACT(PRC,'CO2_EMIS') = sum(COM, PRC_ACTFLO(PRC,COM,'IN') * FLO_EMIS(COM));
ENV_ACT('IND_FCS','CO2_EMIS') = 0.1 * ENV_ACT('IND_FCS','CO2_EMIS');
ENV_ACT('AV_OIL','CO2_INTAV') = (1 - DOM_SHR) * ENV_ACT('AV_OIL','CO2_EMIS');
ENV_ACT('AV_OIL','CO2_EMIS')  = DOM_SHR * NONCO2 * ENV_ACT('AV_OIL','CO2_EMIS');
ENV_ACT('CCS_STG','CO2_STG')  = 1;
ENV_ACT(PRC,'NOX')  = PTAB(PRC,'NOX_EF') * sum(COM_FUEL, PRC_ACTFLO(PRC,COM_FUEL,'IN'));
ENV_ACT(PRC,'PM25') = PTAB(PRC,'PM_EF')  * sum(COM_FUEL, PRC_ACTFLO(PRC,COM_FUEL,'IN'));

* demand
COM_PROJ(COM,T)$COM_DEM(COM) = sum(DITEM$sameas(DITEM,COM), DTAB(DITEM,T));
COM_PROJ('AVF',T) = DTAB('AVF','2025') * (1 + AVI_G)**(YEAR(T) - 2025);
DEM(COM,T,TS)$COM_TSL(COM) = COM_PROJ(COM,T) * COM_FR(COM,TS);
DEM('ELC',T,TS) = DEM('ELC',T,TS) + DTAB('ELC_EXP',T) * EXP_FR(TS);
DEM(COM,T,'ANNUAL')$(COM_DEM(COM) and not COM_TSL(COM)) = COM_PROJ(COM,T);
PEAK_LOAD(T) = COM_PROJ('ELC',T) * COM_FR('ELC','WI_P') / (G_YRFR('WI_P') * 8.76);

* resources
RES_VOL(RES,T)  = RTAB(RES,'VOL');
RES_VOL(RES_BIO,T)$(YEAR(T) > 2025) = RTAB(RES_BIO,'VOL') * BIO_MULT;
$if set BIO40 RES_VOL(RES_BIO,T)$(YEAR(T) >= 2040) = RTAB(RES_BIO,'VOL') * %BIO40%;
RES_COST(RES)   = RTAB(RES,'COST');

* policy
SAF_SHR(T) = POLTAB(T,'SAF_SHR');
SYN_SHR(T) = min(POLTAB(T,'SYN_SHR') * SYN_MULT, POLTAB(T,'SAF_SHR'));
STG_MAX(T) = POLTAB(T,'STG_MAX');
CO2_GROSS_FR(T) = 1 - (1 - (1 - RED_2045)/(1 - RED_2025)) * min(1, (YEAR(T) - 2025)/20);

* discounting: period t covers years t..t+4, investment at year t
ANNF(T) = sum(K$(ord(K) <= 5), (1 + G_DRATE)**(-(YEAR(T) - 2025 + ord(K) - 1)));
INVF(T) = (1 + G_DRATE)**(-(YEAR(T) - 2025));
* salvage: share of the annuity value of an investment falling after the
* last model year (2054), valued at the investment year
SALVF(PRC,T)$(PRC_NEW(PRC) and YEAR(T) + NCAP_TLIFE(PRC) - 1 > 2054)
   = sum(K$(ord(K) > 2054 - YEAR(T) + 1 and ord(K) <= NCAP_TLIFE(PRC)), (1 + G_DRATE)**(-ord(K)))
   / sum(K$(ord(K) <= NCAP_TLIFE(PRC)), (1 + G_DRATE)**(-ord(K)));

*========================================================================
* 3. Variables
*========================================================================
Positive Variables
   VAR_NCAP(PRC,T)   'new capacity'
   VAR_CAP(PRC,T)    'installed capacity'
   VAR_ACT(PRC,T,S)  'process activity (TWh; STL Mt; CCS_STG Mt)'
   VAR_SUP(RES,T)    'resource supply (TWh/yr)'
   VAR_DUM(COM,T,S)  'unserved demand (should be zero)';
Variables
   VAR_EMIS(EM,T)    'emissions and tracked flows'
   VAR_OBJ           'NPV of total system cost (MEUR)';

* availability, bounds
VAR_NCAP.fx(PRC,T)$(not PRC_NEW(PRC)) = 0;
VAR_NCAP.fx(PRC,T)$(YEAR(T) < START(PRC) or YEAR(T) = 2025) = 0;
VAR_NCAP.up(PRC,T)$(PRC_NEW(PRC) and YEAR(T) >= START(PRC) and YEAR(T) > 2025) = NCAP_BND(PRC);
VAR_SUP.up(RES,T) = RES_VOL(RES,T);
VAR_SUP.lo('WST',T) = RES_VOL('WST',T);
VAR_ACT.lo('ELC_HYD',T,TS) = HYD_MIN * G_YRFR(TS) * 8.76 * PRC_RESID('ELC_HYD',T);
VAR_ACT.up('CCS_STG',T,'ANNUAL') = STG_MAX(T);
VAR_DUM.fx(COM,T,S)$(not (COM_DEM(COM) and DEM(COM,T,S))) = 0;

* first-stage decisions fixed from another run (value of information)
$ifthen set FIX1
Parameter NCAP_FIX(PRC,T) 'new capacity from the first-stage run';
execute_load '%FIX1%', NCAP_FIX=REP_NCAP;
VAR_NCAP.fx(PRC,T)$(YEAR(T) <= 2035) = NCAP_FIX(PRC,T);
$endif

*========================================================================
* 4. Equations (TIMES names where an equivalent exists)
*========================================================================
Equations
   EQ_OBJ               'objective: NPV of system cost minus salvage'
   EQ_CPT(PRC,T)        'capacity transfer: residual + new vintages in lifetime'
   EQ_CAPACT(PRC,T,S)   'activity <= capacity x availability x slice length'
   EQ_COMBAL(COM,T,S)   'commodity balance: production + supply >= use + demand'
   EQ_MUSTUSE(COM,T)    'commodities that must be fully used (waste)'
   EQ_CO2CAP(T)         'captured biogenic CO2 = storage (BECCS) + CCU (e-kerosene)'
   EQ_HYDAFA(T)         'hydro annual energy (inflow)'
   EQ_HYDSEAS(T,SEAS)   'hydro seasonal energy (reservoir limit)'
   EQ_EMIS(EM,T)        'emission accounting'
   EQ_CO2GROSS(T)       'gross domestic fossil CO2 cap (85% below 1990 by 2045)'
   EQ_CO2NET(T)         'net zero from 2045: gross fossil CO2 - BECCS <= 0'
   EQ_SAF(T)            'ReFuelEU: bio-jet + e-kerosene >= SAF share x demand'
   EQ_SYN(T)            'ReFuelEU: e-kerosene >= synthetic share x demand'
   EQ_PEAK(T)           'peak reserve: firm capacity >= peak load x (1 + margin)';

EQ_OBJ..
   VAR_OBJ =e=
     sum(T, sum(PRC$PRC_NEW(PRC), NCAP_COST(PRC,T) * (INVF(T) - INVF(T)*SALVF(PRC,T)) * VAR_NCAP(PRC,T))
          + ANNF(T) * ( sum(PRC$PRC_CAPF(PRC), NCAP_FOM(PRC) * VAR_CAP(PRC,T))
                      + sum((PRC,S)$PRC_TS(PRC,S), ACT_COST(PRC) * VAR_ACT(PRC,T,S))
                      + sum(RES, RES_COST(RES) * VAR_SUP(RES,T))
                      + sum((COM,S), DUM_COST * VAR_DUM(COM,T,S)) ));

EQ_CPT(PRC,T)$PRC_CAPF(PRC)..
   VAR_CAP(PRC,T) =e= PRC_RESID(PRC,T)
     + sum(V$(PRC_NEW(PRC) and YEAR(V) <= YEAR(T) and YEAR(T) - YEAR(V) < NCAP_TLIFE(PRC)), VAR_NCAP(PRC,V));

EQ_CAPACT(PRC,T,S)$(PRC_CAPF(PRC) and PRC_TS(PRC,S))..
   VAR_ACT(PRC,T,S) =l= NCAP_AFS(PRC,S) * G_YRFR(S) * CAPACT(PRC) * VAR_CAP(PRC,T);

* sliced commodities: balance in each slice; annual processes deliver flat.
* annual commodities: balance over the year, summing all slices.
EQ_COMBAL(COM,T,S)$(not sameas(COM,'CO2_CAP') and
                    ((COM_TSL(COM) and TS(S)) or (not COM_TSL(COM) and sameas(S,'ANNUAL'))))..
   sum(PRC$(PRC_ACTFLO(PRC,COM,'OUT') or PRC_ACTFLO(PRC,COM,'IN')),
       (PRC_ACTFLO(PRC,COM,'OUT') - PRC_ACTFLO(PRC,COM,'IN'))
       * ( sum(S2$(PRC_TS(PRC,S2) and (sameas(S2,S) or not COM_TSL(COM))), VAR_ACT(PRC,T,S2))
         + (G_YRFR(S) * VAR_ACT(PRC,T,'ANNUAL'))$(COM_TSL(COM) and PRC_TS(PRC,'ANNUAL')) ))
   + sum(RES$RES_COM(RES,COM), VAR_SUP(RES,T))$(not COM_TSL(COM))
   + VAR_DUM(COM,T,S)
   =g= DEM(COM,T,S);

* waste must be treated: all supplied waste is incinerated (no free disposal)
EQ_MUSTUSE(COM,T)$COM_MUST(COM)..
   sum((PRC,S)$PRC_TS(PRC,S), PRC_ACTFLO(PRC,COM,'IN') * VAR_ACT(PRC,T,S))
   =g= sum(RES$RES_COM(RES,COM), VAR_SUP(RES,T));

EQ_CO2CAP(T)..
   sum((PRC,S)$PRC_TS(PRC,S), PRC_ACTFLO(PRC,'CO2_CAP','OUT') * VAR_ACT(PRC,T,S))
   =e= sum((PRC,S)$PRC_TS(PRC,S), PRC_ACTFLO(PRC,'CO2_CAP','IN') * VAR_ACT(PRC,T,S));

EQ_HYDAFA(T)..
   sum(TS, VAR_ACT('ELC_HYD',T,TS)) =l= HYD_AFA * 8.76 * VAR_CAP('ELC_HYD',T);

EQ_HYDSEAS(T,SEAS)..
   sum(TS$TS_SEAS(TS,SEAS), VAR_ACT('ELC_HYD',T,TS)) =l= HYD_SEAS * HYD_AFA * 8.76 * VAR_CAP('ELC_HYD',T);

EQ_EMIS(EM,T)..
   VAR_EMIS(EM,T) =e= sum((PRC,S)$(PRC_TS(PRC,S) and ENV_ACT(PRC,EM)), ENV_ACT(PRC,EM) * VAR_ACT(PRC,T,S));

EQ_CO2GROSS(T)$(CO2ON and YEAR(T) > 2025)..
   VAR_EMIS('CO2_EMIS',T) =l= CO2_GROSS_FR(T) * E_BASE;

EQ_CO2NET(T)$(CO2ON and YEAR(T) >= 2045)..
   VAR_EMIS('CO2_EMIS',T) - VAR_EMIS('CO2_STG',T) =l= 0;

EQ_SAF(T)..
   VAR_ACT('AV_BIO',T,'ANNUAL') + VAR_ACT('AV_SYN',T,'ANNUAL') =g= SAF_SHR(T) * COM_PROJ('AVF',T);

EQ_SYN(T)$SYN_SHR(T)..
   VAR_ACT('AV_SYN',T,'ANNUAL') =g= SYN_SHR(T) * COM_PROJ('AVF',T);

EQ_PEAK(T)$(YEAR(T) > 2025)..
   sum(PRC$PEAK_CONT(PRC), PEAK_CONT(PRC) * VAR_CAP(PRC,T)) =g= PEAK_LOAD(T) * (1 + PEAK_MARG);

Model SWE_TIMES_MINI / all /;
SWE_TIMES_MINI.holdfixed = 1;
option limrow = 0, limcol = 0, solprint = off;

*========================================================================
* 5. Solve: (a) calibration run without CO2 constraints gives the 2025
*    emission level; (b) main run with the CO2 trajectory.
*    2025 has no new investment, so its dispatch does not depend on (b).
*========================================================================
CO2ON = 0;
Solve SWE_TIMES_MINI using lp minimizing VAR_OBJ;
abort$(SWE_TIMES_MINI.modelstat <> 1) 'Calibration run not optimal';
E_BASE = VAR_EMIS.l('CO2_EMIS','2025');

CO2ON = 1;
Solve SWE_TIMES_MINI using lp minimizing VAR_OBJ;
abort$(SWE_TIMES_MINI.modelstat <> 1) 'Main run not optimal';

$include "%MODELDIR%report.gms"

execute_unload '%OUT%';
