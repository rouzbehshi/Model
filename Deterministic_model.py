import numpy as np
import gurobipy as gp
from gurobipy import GRB
from datetime import datetime
from pytz import timezone
import pandas as pd
import pytz
import os
from matplotlib import pyplot

time=[*range(24)]
dispatchable = ['DG']
storage=['BESS']
generator=['PV', 'DG']

fix_cost = {'PV': 510, 'DG': 1000, 'BESS': 500}
#variable_cost = {'PV': 0.01, 'DG': 0.035244, 'BESS_C': 0.03738}
variable_cost = {'PV': 0.5, 'DG': 3.5244, 'BESS_C': 1}
cf_pv = {0: 0, 1: 0, 2: 0 , 3: 0 , 4: 0 , 5: 0, 6: 0, 7: 0.042871048, 8: 0.092273201, 9: 0.138100119, 10: 0.17, 11: 0.17, 12: 0.17, 13: 0.17, 14: 0.17, 15: 0.135985947, 16: 0.09082405, 17: 0.04132661, 18: 0.003142474, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0}
cf_dg= {0:0.6, 1:0.6, 2:0.6, 3:0.6, 4:0.6, 5:0.6, 6:0.6, 7:0.6, 8:0.6, 9:0.6, 10:0.6, 11:0.6, 12:0.6, 13:0.6, 14:0.6, 15:0.6, 16:0.6, 17:0.6, 18:0.6, 19:0.6, 20:0.6, 21:0.6, 22:0.6, 23:0.6}
#demand={0: 19781.98, 1: 18769.72, 2: 18491.02, 3: 18947.71, 4: 20327.76, 5: 22944.45, 6: 24458.89, 7: 24425.4, 8: 26594.33, 9: 27245.98, 10: 28009.92, 11: 29377.48, 12: 29297.16, 13: 30699.8, 14: 33297.74, 15: 36200.69, 16: 34803.29, 17: 32482.14, 18: 31456.71, 19: 30057.95, 20: 28838.95, 21: 27141.28, 22: 24793.39, 23: 21754.59}
cf={"PV": (0, 0,	0,	0,	0,	0,	0,	0.042871048,	0.092273201,	0.138100119,	0.17,	0.17,	0.17,	0.17,	0.17,	0.135985947,	0.09082405,	0.04132661,	0.003142474,	0,	0,	0,	0,	0),
    "DG": (0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6)
    }
demand={0:21502.66946,	1:20001.10632,	2:18833.3824,	3:18100.79079,	4:17868.24467,	5:18155.00399,	6:19158.66163,	7:20173.01925,	8:21376.40975,	9:22146.09461,	10:22779.53312,	11:23574.18459,	12:24177.66317,	13:24957.33467,	14:26120.06527,	15:27157.96283,	16:28297.15349,	17:29155.29147,	18:29794.43663,	19:30012.71612,	20:29587.57045,	21:28671.65261,	22:27527.46863,	23:25167.05418}
c_sell=10
critical_percent=0.8
c_dist=30
c_res=10

min_production_dg = 1000
max_production_dg = 30000
delta_ramp_up = 3000
delta_ramp_down = 3000
L_o = 6  # Min up-time
L_f = 6  # Min down-time

eff_ch = 1
eff_dch = 1
soc_max = 1
soc_min = 0.1
max_charge = 6000
min_charge = 0
max_discharge=6000
min_discharge=0
charge_ramp_up = 20000
charge_ramp_down = 20000
discharge_ramp_up = 20000
discharge_ramp_down = 20000

m = gp.Model('Another one')

capacity = m.addVars(generator, vtype=GRB.CONTINUOUS, name='Generators capacity')
capacity_storage = m.addVars(storage, vtype=GRB.CONTINUOUS, name='Storage capacity')
production = m.addVars(generator,time, vtype=GRB.CONTINUOUS, name='Production level generators')
charge = m.addVars(storage,time, vtype=GRB.CONTINUOUS, name='Storage charge')
discharge = m.addVars(storage,time, vtype=GRB.CONTINUOUS, name='Storage discharge')
u_generator = m.addVars(dispatchable,time, vtype=GRB.BINARY, name='DG status')
u_charge = m.addVars(storage,time, vtype=GRB.BINARY, name='Charging status')
u_discharge = m.addVars(storage,time, vtype=GRB.BINARY, name='Discharging status')
enns = m.addVars(time, vtype=GRB.CONTINUOUS, name='electricity needed but not supplied')

min_production_dg = m.addConstrs((production["DG", t] >= min_production_dg*u_generator["DG", t]
                                 for t in time))

max_production_dg = m.addConstrs((production["DG", t] <= max_production_dg*u_generator["DG", t])
                                 for t in time)

capacity_factor_dg = m.addConstrs(production["DG", t] <= capacity["DG"]*cf["DG"][t]
                                 for t in time)

capacity_factor_pv = m.addConstrs(production["PV", t] <= capacity["PV"]*cf["PV"][t]
                                 for t in time)
max_capacity_pv = m.addConstr(capacity["PV"] <= 60000)
max_capacity_DG = m.addConstr(capacity["DG"] <= 100000)
# DG minimum Up-time
# for t=1

#min_up_time_1 = m.addConstr(gp.quicksum(u_generator["DG",t]
                                          #for t in [*range(L_o - 1)]) >= L_o)
# for t!=1

#min_up_time_2 = m.addConstrs((gp.quicksum(u_generator["DG", t + l]
                                          #for l in [*range(L_o-1)]) >= L_o * (u_generator["DG", t] - u_generator["DG", t-1])
                              #for t in [*range(1, len(time)-L_o+1)]))


# for t ending to nperiod
#min_up_time_3 = m.addConstr(gp.quicksum(u_generator["DG",l]
                                          #for l in [*range(len(time)-L_o+1, len(time))]) <= L_o * u_generator["DG", len(time)-L_o+1])

#DG minimum Down-time

#for t in [*range(1,len(time)-L_f)]:
    #min_down_time=m.addConstr(gp.quicksum(1-u_generator["DG",t+l]
                                            #for l in [*range(L_f-1)]) >= L_f*(u_generator["DG", t-1]-u_generator["DG", t]))

#DG ramp_up
#ramp_up_1 = m.addConstr(production["DG",0] <= delta_ramp_up)

ramp_up_2 = m.addConstrs((production["DG", t]-production["DG", t-1] <= delta_ramp_up for t in [*range(1, len(time))]))
#DG ramp_down
ramp_down_1 = m.addConstrs((production["DG",t-1]-production["DG",t] <= delta_ramp_down for t in [*range(1, len(time))]))



# Up/Down limit for SOC

#initial_charge=m.addConstr(charge['BESS',0]==0)
initial_discharge=m.addConstr(discharge['BESS',0]==0)

#soc_max = m.addConstr (gp.quicksum ((charge['BESS',t]+charge['BESS',t-1])*eff_ch for t in [*range(1,len(time))]) -
                         #gp.quicksum((discharge['BESS',t]+discharge['BESS',t-1])/eff_dch for t in [*range(1,len(time))]) <= soc_max * capacity_storage['BESS'])

soc_max = m.addConstrs (gp.quicksum(charge['BESS',t]*eff_ch+charge['BESS',t-1]*eff_ch -
                        discharge['BESS',t]/eff_dch-discharge['BESS',t-1]/eff_dch for t in [*range(1,len(time))]) <= soc_max * capacity_storage['BESS'] for t in [*range(1,len(time))])

#soc_min = m.addConstr (gp.quicksum((charge['BESS',t]+charge['BESS',t-1])*eff_ch for t in [*range(1,len(time))]) -
                       #gp.quicksum((discharge['BESS',t]+discharge['BESS',t-1])/eff_dch for t in [*range(1,len(time))]) >= soc_min*capacity_storage['BESS'])

soc_min = m.addConstrs (gp.quicksum(charge['BESS',t]*eff_ch + charge['BESS',t-1]*eff_ch -
                       discharge['BESS',t]/eff_dch - discharge['BESS',t-1]/eff_dch for t in [*range(1,len(time))]) >= soc_min*capacity_storage['BESS'] for t in [*range(1,len(time))])

initial_charge_status=m.addConstrs(u_charge[s,0]==1 for s in storage)
initial_discharge_status=m.addConstrs(u_discharge[s,0]==0 for s in storage)

# max charge
max_charge = m.addConstrs(charge[s,t] <= max_charge*u_charge[s,t]
                          for t in [*range(1,len(time))]
                          for s in storage)
# min charge
#min_charge = m.addConstrs(charge[s,t] >= min_charge*u_charge[s,t]
                          #for t in [*range(1,len(time))]
                          #for s in storage)

# max discharge
max_discharge = m.addConstrs(discharge['BESS',t] <= max_discharge * u_discharge['BESS',t]
                          for t in [*range(1,len(time))]
)
# min discharge
#min_discharge = m.addConstrs(discharge[s,t] >= min_discharge*u_discharge[s,t]
                          #for t in [*range(1, len(time))]
                          #for s in storage)
# charge ramp_up
charge_ramp_up = m.addConstrs(charge[s,t]-charge[s,t-1] <= charge_ramp_up*u_charge[s,t]
                              for t in [*range(1,len(time))]
                              for s in storage)
# charge ramp_down
charge_ramp_down = m.addConstrs(charge[s,t-1]-charge[s,t] <= charge_ramp_down*u_charge[s,t]
                                for t in [*range(1,len(time))]
                                for s in storage)
# discharge ramp_up
discharge_ramp_up = m.addConstrs(discharge[s,t]-discharge[s,t-1]<=discharge_ramp_up*u_discharge[s,t]
                                 for t in [*range(1,len(time))]
                                 for s in storage)
# discharge ramp_down
discharge_ramp_down = m.addConstrs(discharge[s,t-1]-discharge[s,t]<=discharge_ramp_down*u_discharge[s,t]
                                   for t in [*range(1,len(time))]
                                   for s in storage)
#disabaling simultaneus charge/discharge
simultaneus_charge_discharge = m.addConstrs(u_discharge[s,t]+u_charge[s,t]<=1
                                            for t in [*range(1, len(time))]
                                            for s in storage)

meet_demand1 = m.addConstrs(gp.quicksum(production[g,t] for g in generator)+gp.quicksum(discharge[s,t] for s in storage) +enns[t]-gp.quicksum(charge[s,t] for s in storage) == demand[t]
                            for t in time)
#meet_demand2 = m.addConstrs(gp.quicksum(production[g,t] for g in generator) +enns[t]>= demand[t]
                            #for t in time)
meet_demand3 = m.addConstrs(gp.quicksum(production[g,t] for g in generator)+gp.quicksum(discharge[s,t] for s in storage)-gp.quicksum(charge[s,t] for s in storage)>= 0.7*demand[t]
                            for t in time)

Total_cost = m.setObjective(gp.quicksum(capacity[g]*fix_cost[g] for g in generator) +
                            (capacity_storage['BESS']*fix_cost['BESS'])+
                            gp.quicksum(production[g, t]*variable_cost[g] for g in generator for t in time)+
                            gp.quicksum(enns[t]*c_dist*20 for t in time)-
                            gp.quicksum(production["DG", t]*c_sell for t in time)-
                            gp.quicksum(production["PV", t]*c_sell*40 for t in time)-
                            gp.quicksum(discharge["BESS", t]*c_sell*5 for t in time)-
                            capacity["PV"]*c_res*9
                            , GRB.MINIMIZE)
m.optimize()




############Outputs##########
DG_plan={}
DG_production={}

Discharging_plan={}
discharge_value={}

Charging_plan={}
charge_value={}

PV_production={}

enns_value={}

for t in time:
    DG_plan[t]=u_generator["DG",t].x
    Discharging_plan[t]=u_discharge["BESS",t].x
    Charging_plan[t]=u_charge["BESS",t].x
    PV_production[t]=production["PV",t].x
    DG_production[t] = production["DG", t].x
    enns_value[t] = enns[t].x
    charge_value[t]=charge['BESS',t].x
    discharge_value[t] = discharge['BESS', t].x

result_dic=[DG_plan,DG_production,Discharging_plan,discharge_value,
        Charging_plan,charge_value,PV_production,enns_value,demand]

df= pd.DataFrame(result_dic)
result_new=df.rename(index={0: 'DG_plan', 1:'DG_production', 2:'Discharging_plan', 3:'Discharge_value',4:'Charging_plan',
                        5:'Charging_value',6:'PV_production',7:'ENNS',8:'Demand'})
result_new.to_csv('first results')





