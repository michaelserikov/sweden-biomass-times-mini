*========================================================================
* Reporting and checks (included by core.gms after the solve)
*========================================================================
Sets
   BCAT 'forest biomass use categories'
        / BIOFUEL  'biofuels: jet + diesel (gasification-FT)'
          BIOF_CCS 'biofuels with CO2 capture (BECCS)'
          DH       'district heating and CHP'
          DH_CCS   'CHP with CO2 capture (BECCS)'
          INDUSTRY 'industry' /
   PRC_BCAT(PRC,BCAT)
        / BF_FT.BIOFUEL, BF_FTC.BIOF_CCS, (CHP_BIO, HET_BOB).DH, CHP_BCS.DH_CCS, IND_BIO.INDUSTRY /
   ENC(COM) 'energy commodities (TWh) for the energy-conservation check'
        / ELC, HET, BIO_SOL, BLQ, WST, HEFA_FS, NG, OIL_JET, OIL_DSL, COA,
          BIO_JET, BIO_DSL, SYN_JET, H2, IND, AVF, DSL /;

Parameters
   REP_ACT(PRC,T)       'annual activity'
   REP_FLO(PRC,COM,IO,T) 'annual flows (TWh; CO2_CAP Mt)'
   REP_CAP(PRC,T)       'installed capacity'
   REP_NCAP(PRC,T)      'new capacity'
   REP_ELC(PRC,T)       'electricity generation by process (TWh)'
   REP_HET(PRC,T)       'district heat supply by process (TWh)'
   REP_BIO(PRC,T)       'forest biomass use by process (TWh)'
   REP_BIOALLOC(BCAT,T) 'forest biomass allocation (TWh)'
   REP_BIOSUP(RES,T)    'forest biomass supply by step (TWh)'
   REP_BLQ(PRC,T)       'black liquor use by process (TWh)'
   REP_AVF(PRC,T)       'aviation fuel supply (TWh)'
   REP_DSL(PRC,T)       'road and machinery diesel supply (TWh)'
   REP_H2(PRC,T)        'hydrogen use (+) and production (-) (TWh)'
   REP_EMIS(EM,T)       'emissions (CO2 Mt, NOx and PM2.5 kt)'
   REP_CO2BAL(*,T)      'CO2 balance (Mt)'
   REP_ELCPRICE(T,S)    'electricity price (EUR/MWh, shadow price)'
   REP_ELCAVG(T)        'demand-weighted electricity price (EUR/MWh)'
   REP_CO2PRICE(T)      'CO2 shadow price (EUR/t)'
   REP_BIOPRICE(T)      'forest biomass shadow price (EUR/MWh)'
   REP_PEAK(*,T)        'peak reserve (GW)'
   REP_COST(*)          'system cost (MEUR)'
   REP_CAL(CALITEM,*)   'calibration 2025 (TWh)'
   REP_CHECK(*)         'model checks (0 = pass)'
   REP_SCN(*)           'scenario parameters';

REP_ACT(PRC,T)  = sum(S$PRC_TS(PRC,S), VAR_ACT.l(PRC,T,S));
REP_FLO(PRC,COM,IO,T) = PRC_ACTFLO(PRC,COM,IO) * REP_ACT(PRC,T);
REP_CAP(PRC,T)$PRC_CAPF(PRC) = VAR_CAP.l(PRC,T);
REP_NCAP(PRC,T) = VAR_NCAP.l(PRC,T);
REP_ELC(PRC,T)  = REP_FLO(PRC,'ELC','OUT',T);
REP_HET(PRC,T)  = REP_FLO(PRC,'HET','OUT',T);
REP_BIO(PRC,T)  = REP_FLO(PRC,'BIO_SOL','IN',T);
REP_BIOALLOC(BCAT,T) = sum(PRC$PRC_BCAT(PRC,BCAT), REP_BIO(PRC,T));
REP_BIOSUP(RES_BIO,T) = VAR_SUP.l(RES_BIO,T);
REP_BLQ(PRC,T)  = REP_FLO(PRC,'BLQ','IN',T);
REP_AVF(PRC,T)  = REP_FLO(PRC,'AVF','OUT',T);
REP_DSL(PRC,T)  = REP_FLO(PRC,'DSL','OUT',T);
REP_H2(PRC,T)   = REP_FLO(PRC,'H2','IN',T) - REP_FLO(PRC,'H2','OUT',T);
REP_EMIS(EM,T)  = VAR_EMIS.l(EM,T);

REP_CO2BAL('gross fossil (target scope)',T) = VAR_EMIS.l('CO2_EMIS',T);
REP_CO2BAL('gross cap',T)$(YEAR(T) > 2025)  = CO2_GROSS_FR(T) * E_BASE;
REP_CO2BAL('BECCS stored',T)                = VAR_EMIS.l('CO2_STG',T);
REP_CO2BAL('net',T)      = VAR_EMIS.l('CO2_EMIS',T) - VAR_EMIS.l('CO2_STG',T);
REP_CO2BAL('captured biogenic',T) = sum(PRC, REP_FLO(PRC,'CO2_CAP','OUT',T));
REP_CO2BAL('used for e-kerosene',T) = REP_FLO('EF_EKER','CO2_CAP','IN',T);
REP_CO2BAL('international aviation (memo)',T) = VAR_EMIS.l('CO2_INTAV',T);

REP_ELCPRICE(T,TS) = EQ_COMBAL.m('ELC',T,TS) / ANNF(T);
REP_ELCAVG(T) = sum(TS, REP_ELCPRICE(T,TS) * DEM('ELC',T,TS)) / sum(TS, DEM('ELC',T,TS));
REP_CO2PRICE(T)$(YEAR(T) > 2025) = -(EQ_CO2GROSS.m(T) + EQ_CO2NET.m(T)) / ANNF(T);
REP_BIOPRICE(T) = EQ_COMBAL.m('BIO_SOL',T,'ANNUAL') / ANNF(T);

REP_PEAK('peak load',T)       = PEAK_LOAD(T);
REP_PEAK('required',T)        = PEAK_LOAD(T) * (1 + PEAK_MARG);
REP_PEAK('firm capacity',T)   = sum(PRC, PEAK_CONT(PRC) * VAR_CAP.l(PRC,T));
REP_PEAK('of which GT',T)     = sum(PRC_GT, PEAK_CONT(PRC_GT) * VAR_CAP.l(PRC_GT,T));
REP_PEAK('GT_BIO capacity',T) = VAR_CAP.l('GT_BIO',T);
REP_PEAK('GT_H2 capacity',T)  = VAR_CAP.l('GT_H2',T);

REP_COST('NPV total')       = VAR_OBJ.l;
REP_COST('NPV investment')  = sum((PRC,T)$PRC_NEW(PRC), NCAP_COST(PRC,T) * INVF(T) * VAR_NCAP.l(PRC,T));
REP_COST('NPV salvage')     = sum((PRC,T)$PRC_NEW(PRC), NCAP_COST(PRC,T) * INVF(T) * SALVF(PRC,T) * VAR_NCAP.l(PRC,T));
REP_COST('NPV fixed O&M')   = sum((PRC,T)$PRC_CAPF(PRC), ANNF(T) * NCAP_FOM(PRC) * VAR_CAP.l(PRC,T));
REP_COST('NPV variable')    = sum((PRC,T,S)$PRC_TS(PRC,S), ANNF(T) * ACT_COST(PRC) * VAR_ACT.l(PRC,T,S));
REP_COST('NPV resources')   = sum((RES,T), ANNF(T) * RES_COST(RES) * VAR_SUP.l(RES,T));
REP_COST('NPV unserved')    = sum((COM,T,S), ANNF(T) * DUM_COST * VAR_DUM.l(COM,T,S));

* calibration against statistics (SCB electricity supply 2025, preliminary;
* district heating: SCB 2023 total supply)
REP_CAL('ELC_HYDRO','model')   = REP_ELC('ELC_HYD','2025');
REP_CAL('ELC_NUCLEAR','model') = REP_ELC('ELC_NUC','2025');
REP_CAL('ELC_WIND','model')    = REP_ELC('ELC_WON','2025') + REP_ELC('ELC_WOF','2025');
REP_CAL('ELC_SOLAR','model')   = REP_ELC('ELC_SOL','2025');
REP_CAL('ELC_THERMAL','model') = sum(PRC_THERMAL, REP_ELC(PRC_THERMAL,'2025'));
REP_CAL('ELC_TOTAL','model')   = sum(PRC$(not sameas(PRC,'ELC_IMP')), REP_ELC(PRC,'2025'));
REP_CAL('DH_TOTAL','model')    = sum(PRC, REP_HET(PRC,'2025'));
REP_CAL(CALITEM,'stat')        = CALTAB(CALITEM,'STAT');
REP_CAL(CALITEM,'diff_pct')$CALTAB(CALITEM,'STAT')
   = 100 * (REP_CAL(CALITEM,'model') - CALTAB(CALITEM,'STAT')) / CALTAB(CALITEM,'STAT');

* checks
REP_CHECK('unserved demand TWh') = sum((COM,T,S), VAR_DUM.l(COM,T,S));
REP_CHECK('negative costs')      = sum(PRC$(ACT_COST(PRC) < 0 or NCAP_FOM(PRC) < 0), 1)
                                 + sum(RES$(RES_COST(RES) < 0), 1);
* no free energy: energy out <= energy in for every conversion process
* (heat pumps excluded: ambient heat; primary sources and steel excluded)
REP_CHECK('processes creating energy') =
   sum(PRC$(sum(ENC, PRC_ACTFLO(PRC,ENC,'IN')) and not sameas(PRC,'HET_HP')
            and not sameas(PRC,'STL_H2') and not sameas(PRC,'IND_ELC')
            and sum(ENC, PRC_ACTFLO(PRC,ENC,'OUT')) > sum(ENC, PRC_ACTFLO(PRC,ENC,'IN')) + 1e-6), 1);
REP_CHECK('balance violations') =
   sum((COM,T,S)$(EQ_COMBAL.l(COM,T,S) < EQ_COMBAL.lo(COM,T,S) - 1e-6), 1);

REP_SCN('BIO_MULT')  = BIO_MULT;
REP_SCN('AVI_G')     = AVI_G;
REP_SCN('ELZ_MULT')  = ELZ_MULT;
REP_SCN('WIND_MULT') = WIND_MULT;
REP_SCN('SYN_MULT')  = SYN_MULT;
REP_SCN('DLY_START') = DLY_START;
REP_SCN('G_DRATE')   = G_DRATE;
REP_SCN('NONCO2')    = NONCO2;
REP_SCN('E_BASE')    = E_BASE;

display REP_CHECK, REP_CAL, REP_BIOALLOC, REP_CO2BAL, REP_CO2PRICE, REP_ELCAVG, REP_COST;

abort$(REP_CHECK('processes creating energy') or REP_CHECK('negative costs')) 'Model check failed', REP_CHECK;
