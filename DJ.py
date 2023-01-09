import matplotlib.pyplot as plt
import pandas as pd
from Deterministic_model import result_new

def charge_result(Charging_plan,charge_value):
    result = {key: Charging_plan[key] * charge_value[key] * (-1) for key in Charging_plan}
    return result

def discharge_result(Discharging_plan,discharge_value):
    result={key: Discharging_plan[key] * discharge_value[key] for key in Discharging_plan}
    return result

def dg_result (DG_plan, DG_production):
    result= {key: DG_plan[key] * DG_production[key] for key in DG_plan}
    return result

res=[]
res['DG_result']=dg_result(result_new.loc[0],result_new.loc[1])

print(res)


cf_pv = {0: {0, 0, 0, 0},
         1: {0, 0, 0, 0},
         2: (0, 0, 0, 0),
         3: (0, 0, 0, 0),
         4: (0, 0, 0, 0),
         5: (0, 0, 0, 0),
         6: (0, 0, 0, 0),
         7: (0.042871048, 0.042871048, 0.042871048, 0.042871048),
         8: (0.092273201, 0.092273201, 0.092273201, 0.092273201),
         9: (0.138100119, 0.138100119, 0.138100119, 0.138100119),
         10: (0.17, 0.17, 0.17, 0.17),
         11: (0.17, 0.17, 0.17, 0.17),
         12: (0.17, 0.17, 0.17, 0.17),
         13: (0.17, 0.17, 0.17, 0.17),
         14: (0.17, 0.17, 0.17, 0.17),
         15: (0.135985947, 0.135985947, 0.135985947, 0.135985947),
         16: (0.09082405, 0.09082405, 0.09082405, 0.09082405),
         17: (0.04132661, 0.04132661, 0.04132661, 0.04132661),
         18: (0.003142474, 0.003142474, 0.003142474, 0.003142474),
         19: (0, 0, 0, 0),
         20: (0, 0, 0, 0),
         21: (0, 0, 0, 0),
         22: (0, 0, 0, 0),
         23: (0, 0, 0, 0)
         }
