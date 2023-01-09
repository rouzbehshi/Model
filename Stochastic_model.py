import numpy as np
import gurobipy as gp
from gurobipy import GRB
from datetime import datetime
from pytz import timezone
import pandas as pd
import pytz
import os
import matplotlib.pyplot as plt

time=[*range(24)]
dispatchable = ['DG']
storage=['BESS']
generator=['PV', 'DG']
scenario=[1,2,3,4]

fix_cost = {'PV': 510, 'DG': 1000, 'BESS': 500}
#variable_cost = {'PV': 0.01, 'DG': 0.035244, 'BESS_C': 0.03738}
variable_cost = {'PV': 0.5, 'DG': 3.5244, 'BESS_C': 1}

cf_pv={ 0: {1:0, 2:0, 3:0, 4:0},
         1: {1:0, 2:0, 3:0, 4:0},
         2: {1:0, 2:0, 3:0, 4:0},
         3: {1:0, 2:0, 3:0, 4:0},
         4: {1:0, 2:0, 3:0, 4:0},
         5: {1:0, 2:0, 3:0, 4:0},
         6: {1:0, 2:0, 3:0, 4:0},
         7: {1:0.042871048, 2:0.042871048, 3:0.042871048, 4:0.042871048},
         8: {1:0.092273201, 2:0.092273201, 3:0.092273201, 4:0.092273201},
         9: {1:0.138100119, 2:0.138100119, 3:0.138100119, 4:0.138100119},
         10: {1:0.17, 2:0.17, 3:0.17, 4:0.17},
         11: {1:0.17, 2:0.17, 3:0.17, 4:0.17},
         12: {1:0.17, 2:0.17, 3:0.17, 4:0.17},
         13: {1:0.17, 2:0.17, 3:0.17, 4:0.17},
         14: {1:0.17, 2:0.17, 3:0.17, 4:0.17},
         15: {1:0.135985947, 2:0.135985947, 3:0.135985947, 4:0.135985947},
         16: {1:0.09082405, 2:0.09082405, 3:0.09082405, 4:0.09082405},
         17: {1:0.04132661, 2:0.04132661, 3:0.04132661, 4:0.04132661},
         18: {1:0.003142474, 2:0.003142474, 3:0.003142474, 4:0.003142474},
         19: {1:0, 2:0, 3:0, 4:0},
         20: {1:0, 2:0, 3:0, 4:0},
         21: {1:0, 2:0, 3:0, 4:0},
         22: {1:0, 2:0, 3:0, 4:0},
         23: {1:0, 2:0, 3:0, 4:0}
         }

cf_dg= {0:0.6, 1:0.6, 2:0.6, 3:0.6, 4:0.6, 5:0.6, 6:0.6, 7:0.6, 8:0.6, 9:0.6, 10:0.6, 11:0.6, 12:0.6, 13:0.6, 14:0.6, 15:0.6, 16:0.6, 17:0.6, 18:0.6, 19:0.6, 20:0.6, 21:0.6, 22:0.6, 23:0.6}
#demand={0: 19781.98, 1: 18769.72, 2: 18491.02, 3: 18947.71, 4: 20327.76, 5: 22944.45, 6: 24458.89, 7: 24425.4, 8: 26594.33, 9: 27245.98, 10: 28009.92, 11: 29377.48, 12: 29297.16, 13: 30699.8, 14: 33297.74, 15: 36200.69, 16: 34803.29, 17: 32482.14, 18: 31456.71, 19: 30057.95, 20: 28838.95, 21: 27141.28, 22: 24793.39, 23: 21754.59}
cf={"PV": (0, 0,	0,	0,	0,	0,	0,	0.042871048,	0.092273201,	0.138100119,	0.17,	0.17,	0.17,	0.17,	0.17,	0.135985947,	0.09082405,	0.04132661,	0.003142474,	0,	0,	0,	0,	0),
    "DG": (0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6)
    }
demand = {0: {1:12892, 2:14181.2, 3:11602.8, 4:13536.6},
          1: {1:13478, 2:14825.8, 3:12130.2, 4:14151.9},
          2: {1:12865, 2:14151.5, 3:11578.5, 4:13508.25},
          3: {1:12577, 2:13834.7, 3:11319.3, 4:13205.85},
          4: {1:12517, 2:13768.7, 3:11265.3, 4:13142.85},
          5: {1:12670, 2:13937, 3:11403, 4:13303.5},
          6: {1:13038, 2:14341.8, 3:11734.2, 4:13689.9},
          7: {1:13692, 2:15061.2, 3:12322.8, 4:14376.6},
          8: {1:14297, 2:15726.7, 3:12867.3, 4:15011.85},
          9: {1:14719, 2:16190.9, 3:13247.1, 4:15454.95},
          10: {1:14941, 2:16435.1, 3:13446.9, 4:15688.05},
          11: {1:15184, 2:16702.4, 3:13665.6, 4:15943.2},
          12: {1:15009, 2:16509.9, 3:13508.1, 4:15759.45},
          13: {1:14808, 2:16288.8, 3:13327.2, 4:15548.4},
          14: {1:14522, 2:15974.2, 3:13069.8, 4:15248.1},
          15: {1:14349, 2:15783.9, 3:12914.1, 4:15066.45},
          16: {1:14107, 2:15517.7, 3:12696.3, 4:14812.35},
          17: {1:14410, 2:15851, 3:12969, 4:15130.5},
          18: {1:15174, 2:16691.4, 3:13656.6, 4:15932.7},
          19: {1:15261, 2:16787.1, 3:13734.9, 4:16024.05},
          20: {1:14774, 2:16251.4, 3:13296.6, 4:15512.7},
          21: {1:14363, 2:15799.3, 3:12926.7, 4:15081.15},
          22: {1:14045, 2:15449.5, 3:12640.5, 4:14747.25},
          23: {1:13478, 2:14825.8, 3:12130.2, 4:14151.9}
          }
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

production = m.addVars(generator, time, scenario, vtype=GRB.CONTINUOUS, name='Production level generators')
charge = m.addVars(storage, time, scenario, vtype=GRB.CONTINUOUS, name='Storage charge')
discharge = m.addVars(storage, time, scenario, vtype=GRB.CONTINUOUS, name='Storage discharge')

u_generator = m.addVars(dispatchable,time, scenario,vtype=GRB.BINARY, name='DG status')
u_charge = m.addVars(storage, time, scenario, vtype=GRB.BINARY, name='Charging status')
u_discharge = m.addVars(storage,time, scenario, vtype=GRB.BINARY, name='Discharging status')

enns = m.addVars(time, scenario, vtype=GRB.CONTINUOUS, name='electricity needed but not supplied')

min_production_dg = m.addConstrs((production["DG", t, s] >= min_production_dg*u_generator["DG", t, s]
                                  for t in time
                                  for s in scenario))

max_production_dg = m.addConstrs((production["DG", t,s] <= max_production_dg*u_generator["DG", t, s])
                                 for t in time
                                 for s in scenario)

capacity_factor_dg = m.addConstrs(production["DG", t, s] <= capacity["DG"]*cf_dg[t]
                                  for t in time
                                  for s in scenario)

capacity_factor_pv = m.addConstrs(production["PV", t, s] <= capacity["PV"]*cf_pv[t][s]
                                  for t in time
                                  for s in [*range(1,len(scenario)+1)])

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

ramp_up_2 = m.addConstrs((production["DG", t, s]-production["DG", t-1, s] <= delta_ramp_up
                          for t in [*range(1, len(time))]
                          for s in scenario))
#DG ramp_down
ramp_down_1 = m.addConstrs((production["DG", t-1, s]-production["DG", t, s] <= delta_ramp_down
                            for t in [*range(1, len(time))]
                            for s in scenario))

# Up/Down limit for SOC


initial_discharge=m.addConstrs(discharge['BESS', 0, s]==0 for s in scenario)

#soc_max = m.addConstr (gp.quicksum ((charge['BESS',t]+charge['BESS',t-1])*eff_ch for t in [*range(1,len(time))]) -
                         #gp.quicksum((discharge['BESS',t]+discharge['BESS',t-1])/eff_dch for t in [*range(1,len(time))]) <= soc_max * capacity_storage['BESS'])

soc_max = m.addConstrs (gp.quicksum(charge['BESS', t, s]*eff_ch+charge['BESS', t-1, s]*eff_ch -
                        discharge['BESS', t, s]/eff_dch-discharge['BESS', t-1, s]/eff_dch
                                    for t in [*range(1,len(time))]
                                    for s in scenario) <=
                        soc_max * capacity_storage['BESS']
                        for t in [*range(1,len(time))])

#soc_min = m.addConstr (gp.quicksum((charge['BESS',t]+charge['BESS',t-1])*eff_ch for t in [*range(1,len(time))]) -
                       #gp.quicksum((discharge['BESS',t]+discharge['BESS',t-1])/eff_dch for t in [*range(1,len(time))]) >= soc_min*capacity_storage['BESS'])

soc_min = m.addConstrs (gp.quicksum(charge['BESS', t, s]*eff_ch + charge['BESS', t-1, s]*eff_ch -
                       discharge['BESS', t, s]/eff_dch - discharge['BESS', t-1, s]/eff_dch
                                    for t in [*range(1,len(time))]
                                    for s in scenario) >=
                        soc_min*capacity_storage['BESS']
                        for t in [*range(1,len(time))])

initial_charge_status=m.addConstrs(u_charge['BESS', 0, s] == 1 for s in scenario)
initial_discharge_status=m.addConstrs(u_discharge['BESS', 0, s] == 0 for s in scenario)

# max charge
max_charge = m.addConstrs(charge['BESS', t, s] <= max_charge*u_charge['BESS', t, s]
                          for t in [*range(1,len(time))]
                          for s in scenario)
# min charge
#min_charge = m.addConstrs(charge[s,t] >= min_charge*u_charge[s,t]
                          #for t in [*range(1,len(time))]
                          #for s in storage)

# max discharge
max_discharge = m.addConstrs(discharge['BESS', t, s] <= max_discharge * u_discharge['BESS', t, s]
                             for t in [*range(1,len(time))]
                             for s in scenario)
# min discharge
#min_discharge = m.addConstrs(discharge[s,t] >= min_discharge*u_discharge[s,t]
                          #for t in [*range(1, len(time))]
                          #for s in storage)
# charge ramp_up
charge_ramp_up = m.addConstrs(charge['BESS', t, s]-charge['BESS', t-1, s] <= charge_ramp_up*u_charge['BESS', t, s]
                              for t in [*range(1,len(time))]
                              for s in scenario)
# charge ramp_down
charge_ramp_down = m.addConstrs(charge['BESS', t-1, s]-charge['BESS', t, s] <= charge_ramp_down*u_charge['BESS', t, s]
                                for t in [*range(1,len(time))]
                                for s in scenario)
# discharge ramp_up
discharge_ramp_up = m.addConstrs(discharge["BESS", t, s]-discharge['BESS',t-1, s]<=discharge_ramp_up*u_discharge['BESS', t, s]
                                 for t in [*range(1,len(time))]
                                 for s in scenario)
# discharge ramp_down
discharge_ramp_down = m.addConstrs(discharge['BESS', t-1, s]-discharge['BESS', t, s]<=discharge_ramp_down*u_discharge['BESS', t, s]
                                   for t in [*range(1,len(time))]
                                   for s in scenario)
#disabaling simultaneus charge/discharge
simultaneus_charge_discharge = m.addConstrs(u_discharge['BESS', t, s]+u_charge['BESS', t, s]<=1
                                            for t in [*range(1, len(time))]
                                            for s in scenario)

meet_demand1 = m.addConstrs(gp.quicksum(production[g, t, s] for g in generator) +
                            discharge['BESS', t, s] +
                            enns[t, s] -
                            charge['BESS', t, s] ==
                            demand[t][s]
                            for t in time
                            for s in [*range(1,len(scenario)+1)])

meet_demand3 = m.addConstrs(gp.quicksum(production[g, t, s] for g in generator) +
                            discharge['BESS', t, s] -
                            charge['BESS', t, s] >=
                            0.7*demand[t][s]
                            for t in time
                            for s in [*range(1,len(scenario)+1)])

Total_cost = m.setObjective(gp.quicksum(capacity[g] * fix_cost[g] for g in generator) +
                            (capacity_storage['BESS'] * fix_cost['BESS']) +
                            (1/len(scenario)) * gp.quicksum(
                            gp.quicksum(production[g, t, s]*variable_cost[g] for g in generator for t in time) +
                            gp.quicksum(enns[t, s] * c_dist * 20 for t in time) -
                            gp.quicksum(production["DG", t, s] * c_sell for t in time) -
                            gp.quicksum(production["PV", t, s] * c_sell * 40 for t in time) -
                            gp.quicksum(discharge["BESS", t, s] * c_sell * 5 for t in time) -
                            capacity["PV"] * c_res * 9 for s in scenario)
                            , GRB.MINIMIZE)
m.optimize()

for var in m.getVars():
    print("{0} = {1}".format(var.varName, np.round(var.x, 2)))


############Outputs##########
DG_plan_1={}
DG_production_1={}

Discharging_plan_1={}
discharge_value_1={}

Charging_plan_1={}
charge_value_1={}

PV_production_1={}

enns_value_1={}

Demand={}

for i in scenario:
    for t in time:
        DG_plan_1[t, i] = u_generator["DG", t, i].x
        Discharging_plan_1[t, i] = u_discharge["BESS", t, i].x
        Charging_plan_1[t, i] = u_charge["BESS", t, i].x
        PV_production_1[t, i] = production["PV", t, i].x
        DG_production_1[t, i] = production["DG", t, i].x
        enns_value_1[t, i] = enns[t, i].x
        charge_value_1[t, i] = charge['BESS', t, i].x
        discharge_value_1[t, i] = discharge['BESS', t, i].x
        Demand[t,i]=demand[t][i]

result_dic_1=[DG_plan_1,DG_production_1,Discharging_plan_1,discharge_value_1,
        Charging_plan_1,charge_value_1,PV_production_1,enns_value_1,Demand]

df= pd.DataFrame(result_dic_1)
result_1=df.rename(index={0: 'DG_plan', 1:'DG_production', 2:'Discharging_plan', 3:'Discharge_value',4:'Charging_plan',
                        5:'Charging_value',6:'PV_production',7:'ENNS',8:'Demand',9:"DG",10:"Charging"})
result_1.to_csv('first results')

scenario1=result_1.iloc[:,:24]
scenario2=result_1.iloc[:,24:48]
scenario3=result_1.iloc[:,48:72]
scenario4=result_1.iloc[:,72:96]

###################Scenario1 plot

scenario1 = scenario1.append(pd.Series(0, index=scenario1.columns), ignore_index=True) #DG
scenario1 = scenario1.append(pd.Series(0, index=scenario1.columns), ignore_index=True) #Charging
scenario1 = scenario1.append(pd.Series(0, index=scenario1.columns), ignore_index=True) #Discharging

scenario1=scenario1.rename(index={0: 'DG_plan', 1:'DG_production', 2:'Discharging_plan', 3:'Discharge_value',4:'Charging_plan',
                        5:'Charging_value',6:'PV_production',7:'ENNS',8:'Demand',9:"DG",10:"Charging",11:'Discharging'})
for t in time:
    scenario1.iloc[9,t]=scenario1.iloc[0,t]*scenario1.iloc[1,t]
    scenario1.iloc[10, t] = scenario1.iloc[4, t] * scenario1.iloc[5, t]
    scenario1.iloc[10, t]=scenario1.iloc[10, t]*-1
    scenario1.iloc[11, t] = scenario1.iloc[2, t] * scenario1.iloc[3, t]

plt.bar([*range(len(time))],scenario1.iloc[10, :],color='blue',alpha=0.7,label="BESS_Charging")
plt.bar([*range(len(time))],scenario1.iloc[6, :],color='orange',alpha=0.7,label="PV")
plt.bar([*range(len(time))],scenario1.iloc[11, :],color='green',bottom=scenario1.iloc[6, :],alpha=0.7,label="BESS_Discharging")
plt.bar([*range(len(time))],scenario1.iloc[9, :],bottom=scenario1.iloc[6, :]+scenario1.iloc[11, :],color='gray',alpha=0.7,label="DG")
plt.plot([*range(len(time))],scenario1.iloc[8, :],linestyle='dashed',color='red',label='Demand')

plt.legend( loc="best",fontsize=7)

# plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.14),
#           ncol=3, fancybox=True, shadow=True)
plt.xlabel('time')
plt.ylabel('Active Power [kW]')
plt.title('Scenario 1')

plt.show()
###################Scenario2 plot
scenario2 = scenario2.append(pd.Series(0, index=scenario2.columns), ignore_index=True) #DG
scenario2 = scenario2.append(pd.Series(0, index=scenario2.columns), ignore_index=True) #Charging
scenario2 = scenario2.append(pd.Series(0, index=scenario2.columns), ignore_index=True) #Discharging

scenario2=scenario2.rename(index={0: 'DG_plan', 1:'DG_production', 2:'Discharging_plan', 3:'Discharge_value',4:'Charging_plan',
                        5:'Charging_value',6:'PV_production',7:'ENNS',8:'Demand',9:"DG",10:"Charging",11:'Discharging'})
for t in time:
    scenario2.iloc[9,t]=scenario2.iloc[0,t]*scenario2.iloc[1,t]
    scenario2.iloc[10, t] = scenario2.iloc[4, t] * scenario2.iloc[5, t]
    scenario2.iloc[10, t]=scenario2.iloc[10, t]*-1
    scenario2.iloc[11, t] = scenario2.iloc[2, t] * scenario2.iloc[3, t]

plt.bar([*range(len(time))],scenario2.iloc[10, :],color='blue',alpha=0.7,label="BESS_Charging")
plt.bar([*range(len(time))],scenario2.iloc[6, :],color='orange',alpha=0.7,label="PV")
plt.bar([*range(len(time))],scenario2.iloc[11, :],color='green',bottom=scenario2.iloc[6, :],alpha=0.7,label="BESS_Discharging")
plt.bar([*range(len(time))],scenario2.iloc[9, :],bottom=scenario2.iloc[6, :]+scenario2.iloc[11, :],color='gray',alpha=0.7,label="DG")
plt.plot([*range(len(time))],scenario2.iloc[8, :],linestyle='dashed',color='red',label='Demand')


plt.xlabel('time')
plt.ylabel('Active Power [kW]')
plt.legend( loc="best",fontsize=7)
plt.title('Scenario 2')

plt.show()
###################Scenario3 plot
scenario3 = scenario3.append(pd.Series(0, index=scenario3.columns), ignore_index=True) #DG
scenario3 = scenario3.append(pd.Series(0, index=scenario3.columns), ignore_index=True) #Charging
scenario3 = scenario3.append(pd.Series(0, index=scenario3.columns), ignore_index=True) #Discharging

scenario3=scenario3.rename(index={0: 'DG_plan', 1:'DG_production', 2:'Discharging_plan', 3:'Discharge_value',4:'Charging_plan',
                        5:'Charging_value',6:'PV_production',7:'ENNS',8:'Demand',9:"DG",10:"Charging",11:'Discharging'})
for t in time:
    scenario3.iloc[9,t]=scenario3.iloc[0,t]*scenario3.iloc[1,t]
    scenario3.iloc[10, t] = scenario3.iloc[4, t] * scenario3.iloc[5, t]
    scenario3.iloc[10, t]=scenario3.iloc[10, t]*-1
    scenario3.iloc[11, t] = scenario3.iloc[2, t] * scenario3.iloc[3, t]

plt.bar([*range(len(time))],scenario3.iloc[10, :],color='blue',alpha=0.7,label="BESS_Charging")
plt.bar([*range(len(time))],scenario3.iloc[6, :],color='orange',alpha=0.7,label="PV")
plt.bar([*range(len(time))],scenario3.iloc[11, :],color='green',bottom=scenario3.iloc[6, :],alpha=0.7,label="BESS_Discharging")
plt.bar([*range(len(time))],scenario3.iloc[9, :],bottom=scenario3.iloc[6, :]+scenario3.iloc[11, :],color='gray',alpha=0.7,label="DG")
plt.plot([*range(len(time))],scenario3.iloc[8, :],linestyle='dashed',color='red',label='Demand')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.14),
          ncol=3, fancybox=True, shadow=True)
plt.xlabel('time')
plt.ylabel('Active Power [kW]')
plt.legend( loc="best",fontsize=7)
plt.title('Scenario 3')
plt.show()
###################Scenario4 plot
scenario4 = scenario4.append(pd.Series(0, index=scenario4.columns), ignore_index=True) #DG
scenario4 = scenario4.append(pd.Series(0, index=scenario4.columns), ignore_index=True) #Charging
scenario4 = scenario4.append(pd.Series(0, index=scenario4.columns), ignore_index=True) #Discharging

scenario4=scenario4.rename(index={0: 'DG_plan', 1:'DG_production', 2:'Discharging_plan', 3:'Discharge_value',4:'Charging_plan',
                        5:'Charging_value',6:'PV_production',7:'ENNS',8:'Demand',9:"DG",10:"Charging",11:'Discharging'})
for t in time:
    scenario4.iloc[9,t]=scenario4.iloc[0,t]*scenario4.iloc[1,t]
    scenario4.iloc[10, t] = scenario4.iloc[4, t] * scenario4.iloc[5, t]
    scenario4.iloc[10, t]=scenario4.iloc[10, t]*-1
    scenario4.iloc[11, t] = scenario4.iloc[2, t] * scenario4.iloc[3, t]

plt.bar([*range(len(time))],scenario4.iloc[10, :],color='blue',alpha=0.7,label="BESS_Charging")
plt.bar([*range(len(time))],scenario4.iloc[6, :],color='orange',alpha=0.7,label="PV")
plt.bar([*range(len(time))],scenario4.iloc[11, :],color='green',bottom=scenario4.iloc[6, :],alpha=0.7,label="BESS_Discharging")
plt.bar([*range(len(time))],scenario4.iloc[9, :],bottom=scenario4.iloc[6, :]+scenario4.iloc[11, :],color='gray',alpha=0.7,label="DG")
plt.plot([*range(len(time))],scenario4.iloc[8, :],linestyle='dashed',color='red',label='Demand')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.14),
          ncol=3, fancybox=True, shadow=True)
plt.xlabel('time')
plt.ylabel('Active Power [kW]')
plt.legend( loc="best",fontsize=7)
plt.title('Scenario 4')
plt.show()