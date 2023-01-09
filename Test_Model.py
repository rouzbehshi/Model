import numpy as np
import gurobipy as gp
from gurobipy import GRB
from datetime import datetime
from pytz import timezone
import pandas as pd
import pytz
import os
import datetime
from datetime import datetime, timedelta


# Sets
# Sets of Technologies and Demands
ntype = 1  # Generator types
nperiod = 24  # Time periods
nscenario = 1  # Number of Scenarios

# Model
m = gp.Model('test_model')

# ##################################################################DG model
# #############Parameters##############
min_production_dg = 1
max_production_dg = 25000
cf_dg = 0.6
delta_ramp_up = 3
delta_ramp_down = 3
L_o = 3  # Min up-time
L_f = 1  # Min down-time
# #############Variables##############
# Capacity of DG
capacity_dg = m.addVars(ntype, vtype=GRB.CONTINUOUS, name='DG capacity')
# Production level of DG at time p and scenario s
production_dg = m.addVars(nperiod, nscenario, vtype=GRB.CONTINUOUS, name='Production level of DG')
# Dispatch strategy of DG at time p and scenario s
u_dg = m.addVars(nperiod, nscenario, vtype=GRB.BINARY, name='DG status')
# #############Constraints##############

# Minimum production level of DG
min_production_dg = m.addConstrs((production_dg[period, scenario]>=min_production_dg*u_dg[period, scenario])
                                 for period in range(nperiod)
                                 for scenario in range(nscenario))
# Maximum production level of DG
max_production_dg = m.addConstrs((production_dg[period, scenario] <= max_production_dg*u_dg[period, scenario])
                                 for period in range(nperiod)
                                 for scenario in range(nscenario))
# Capacity factor
capacity_factor_dg = m.addConstrs((production_dg[period, scenario] <= capacity_dg[typ]*cf_dg)
                                 for period in range(nperiod)
                                 for typ in range(ntype)
                                 for scenario in range(nscenario))
# Strategy
# DG minimum Up-time
# for t=1
min_up_time_1 = m.addConstrs(gp.quicksum(u_dg[l+1, scenario] >= L_o*u_dg[1, scenario]
                                         for l in range(L_o-1))
                             for scenario in range(nscenario))
# for t!=1
min_up_time_2 = m.addConstrs(gp.quicksum(u_dg[t+l, scenario] >= L_o*(u_dg[t, scenario]-u_dg[t-1, scenario])
                                       for t in range(2, nperiod-L_o+1)
                                       for l in range(L_o-1))
                           for scenario in range(nscenario))
#for t ending to nperiod
min_up_time_3 = m.addConstrs(gp.quicksum(u_dg[l, scenario] <= L_o*u_dg[nperiod-L_o+1]
                                       for l in range(nperiod-L_o+1, nperiod))
                           for scenario in range(nscenario))
#DG minimum Down-time
min_down_time=m.addConstrs(gp.quicksum(1-u_dg[t+l,scenario] >= L_f*(u_dg[t-1, scenario]-u_dg[t, scenario])
                                       for t in range(2, nperiod-L_f+1)
                                       for l in range(L_f-1))
                           for scenario in range(nscenario))

#DG ramp_up
ramp_up_1 = m.addConstrs(production_dg[1, scenario] <= delta_ramp_up
                       for scenario in range(nscenario))
ramp_up_2 = m.addConstrs((production_dg[t, scenario]-production_dg[t-1, scenario]) <= delta_ramp_up
                       for t in range(2, nperiod))
#DG ramp_down
ramp_down_1 = m.addConstrs((production_dg[t-1, scenario]-production_dg[t, scenario]) <= delta_ramp_down
                         for t in range(2, nperiod))



# ##################################################################PV model
# #############Parameters##############
u_pv = 1  # Dispatch strategy of PV at time p and scenario s

# ##############Variables##############
# Capacity of PV
capacity_pv = m.addVars(vtype=GRB.CONTINUOUS, name='PV capacity')
# Production level of PV at time p and scenario s
production_pv = m.addVars(nperiod, nscenario, vtype=GRB.CONTINUOUS, name='Production level of pv')
# ##############Constraints###############
# Capacity factor
capacity_factor_pv = m.addConstrs((production_pv[period, scenario] <= capacity_pv*cf_pv[period, scenario])
                                  for period in range(nperiod)
                                  for scenario in range(nscenario))

# ##################################################################BESS model
# ##############Parameters##############
eff_ch = 0.99
eff_dch = 0.99
soc_max = 0.99
soc_min = 0.01
max_charge = 200
min_charge = 10
charge_ramp_up = 40
charge_ramp_down = 40
discharge_ramp_up = 40
discharge_ramp_down = 40
# ##############Variables###############
# Capacity of BESS
capacity_bess = m.addVars(vtype=GRB.CONTINUOUS, name='BESS capacity')
# Charging level of BESS at time p and scenario s
production_bess_charging = m.addVars(nperiod, nscenario, vtype=GRB.CONTINUOUS, name='Charging level of BESS')
# Discharging level of BESS at time p and scenario s
production_bess_discharging = m.addVars(nperiod, nscenario, vtype=GRB.CONTINUOUS, name='Discharging level of BESS')
# Dispatch strategy of BESS Charging at time p and scenario s
u_bess_charging = m.addVars(nperiod, nscenario, vtype=GRB.BINARY, name='BESS charging status')
# Dispatch strategy of BESS Discharging at time p and scenario s
u_bess_discharging = m.addVars(nperiod, nscenario, vtype=GRB.BINARY, name='BESS discharging status')
# ##############Constraints###############
# Up/Down limit for SOC
soc_max = m.addConstrs((production_bess_charging[period, scenario]*eff_ch-production_bess_discharging[period, scenario]/eff_dch) <= soc_max*capacity_bess
                     for period in range(nperiod)
                     for scenario in range(nscenario))
soc_min = m.addConstrs((production_bess_charging[period, scenario]*eff_ch-production_bess_discharging[period, scenario]/eff_dch) >= soc_min*capacity_bess
                     for period in range(nperiod)
                     for scenario in range(nscenario))
# max charge
max_charge = m.addConstrs(production_bess_charging[period, scenario] <= max_charge*u_bess_charging[period, scenario]
                        for period in range(nperiod)
                        for scenario in range(nscenario))
# min charge
min_charge = m.addConstrs(production_bess_charging[period, scenario] <= min_charge*u_bess_charging[period, scenario]
                        for period in range(nperiod)
                        for scenario in range(nscenario))
# charge ramp_up
charge_ramp_up = m.addConstrs((production_bess_charging[t, scenario]-production_bess_charging[t-1, scenario]) <= charge_ramp_up*u_bess_charging[period, scenario]
                            for t in range(1, nperiod)
                            for scenario in range(nscenario))
# charge ramp_down
charge_ramp_down = m.addConstrs((production_bess_charging[t-1, scenario]-production_bess_charging[t, scenario]) <= charge_ramp_down*u_bess_charging[period, scenario]
                              for t in range(1, nperiod)
                              for scenario in range(nscenario))
# discharge ramp_up
discharge_ramp_up = m.addConstrs((production_bess_discharging[t, scenario]-production_bess_discharging[t-1, scenario])<=discharge_ramp_up*u_bess_discharging[period, scenario]
                               for t in range(1, nperiod)
                                 for scenario in range(nscenario))
# discharge ramp_down
discharge_ramp_down = m.addConstrs((production_bess_discharging[t-1, scenario]-production_bess_discharging[t, scenario])<=discharge_ramp_down*u_bess_discharging[period, scenario]
                                 for t in range(1, nperiod)
                                   for scenario in range(nscenario))
#disabaling simultaneus charge/discharge
simultaneus_charge_discharge = m.addConstrs(u_bess_discharging[period, scenario]+u_bess_charging[period, scenario]<=1
                                          for period in range(nperiod)
                                            for scenario in range(nscenario))

#################################
#system model
# ##############parameters##############
demand=[19781.98, 18769.72, 18491.02, 18947.71, 20327.76, 22944.45, 24458.89, 24425.4, 26594.33, 27245.98, 28009.92, 29377.48, 29297.16, 30699.8, 33297.74, 36200.69, 34803.29, 32482.14, 31456.71, 30057.95, 28838.95, 27141.28, 24793.39, 21754.59]
cf_pv=[0, 0, 0, 0, 0, 0, 0, 0.042871048, 0.092273201, 0.138100119, 0.17, 0.17, 0.17, 0.17, 0.17, 0.135985947, 0.09082405, 0.04132661, 0.003142474, 0, 0, 0, 0, 0]
critical_percent=0.8
fc_dg=1000
fc_pv=710
fc_bess=850
# g1=PV, g2=DG, g3=BESS_Charge, g4=BESS_Discharge
vc_dg=0.035244
vc_pv=0.01
vc_dch=0.03738
c_sell=0.186
eps_dg=0.2
eps_pv=0.4
eps_bess=0.3
c_res=100
c_dist=1
# ##############Variables##############
enns = m.addVars(nperiod, nscenario, vtype=GRB.CONTINUOUS, name='electricity needed but not supplied')
# ##############Constraints##############
#Demand and supply balance
meet_demand1 = m.addConstrs(production_pv[period, scenario] + production_dg[period, scenario]+production_bess_discharging[period, scenario]-production_bess_charging[period, scenario]+enns[period, scenario] <= demand[period, scenario]
                          for period in range(nperiod)
                           for scenario in range(nscenario))
meet_demand2 = m.addConstrs(production_pv[period, scenario] + production_dg[period, scenario]+production_bess_discharging[period, scenario]-production_bess_charging[period, scenario]+enns[period, scenario] >= critical_percent * demand[period, scenario]
                          for period in range(nperiod)
                           for scenario in range(nscenario))

Total_cost = m.setObjective((capacity_dg*fc_dg+capacity_pv+fc_pv+capacity_bess*fc_bess)+gp.quicksum(probability[scenario]*(gp.quicksum(production_dg[period,scenario]*vc_dg+
                                                                                                                                     production_pv[period,scenario]*vc_pv+
                                                                                                                                     production_bess_discharging[period,scenario]*vc_dch-
                                                                                                                                     (production_dg[period,scenario]+production_pv[period,scenario]+production_bess_discharging[period,scenario])*c_sell+
                                                                                                                                     (capacity_dg*eps_dg+capacity_pv*eps_pv+capacity_bess*eps_bess)*c_res+
                                                                                                                                     enns[period,scenario]*c_dist
                                                                                                                                     for period in range(nperiod)))
                                                                                                  for scenario in range(nscenario)))
#m.optimize()