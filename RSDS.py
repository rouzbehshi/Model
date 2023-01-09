#Importing libraries
import numpy as np
from datetime import datetime
from pytz import timezone
import pandas as pd
import pytz
import os
import datetime
from datetime import datetime, timedelta
#Importing the dataset
#Solar Irradiance dataset
path="/Users/roozbeh/Desktop/ICSRS/Simulation/"
rsds=pd.read_csv(path+"rsds_day_CNRM-CM5_rcp45.csv")
maxtemp=pd.read_csv(path+"tasmax_day_CNRM-CM5_rcp45.csv")
mintemp=pd.read_csv(path+"tasmin_day_CNRM-CM5_rcp45.csv")

#Converting the time-zone
#date_format='%m/%d/%Y %H:%M:%S %Z'
maxtemp['time']=pd.to_datetime(maxtemp['time'])
maxtemp['time'] = maxtemp['time'].dt.date

mintemp['time']=pd.to_datetime(mintemp['time'])
mintemp['time'] = mintemp['time'].dt.date

rsds['time']=pd.to_datetime(rsds['time'])
rsds['time'] = rsds['time'].dt.date

#date_format='%Y-%m-%d'
#date = datetime.now(tz=pytz.utc)
#print('Current date & time is:', date.strftime(date_format))
#date = date.astimezone(timezone('US/Pacific'))
#date=date.strftime(date_format)

maxtempindex=maxtemp['tasmax_day_CNRM-CM5_rcp45']
mintempindex=mintemp['tasmin_day_CNRM-CM5_rcp45']
rsds.insert(2, "maxtemp", maxtempindex)
rsds.insert(3, "mintemp", mintempindex)
rsds['maxtemp']=rsds['maxtemp']-273.15
rsds['mintemp']=rsds['mintemp']-273.15
rsds['avgtemp']=(rsds['maxtemp']+rsds['mintemp'])/2
rsds = rsds.set_index("time")
#Slicing the dataset for the desired time horizon
startdate = pd.to_datetime("2020-01-01").date()
enddate = pd.to_datetime("2030-01-01").date()
weather=rsds.loc[startdate:enddate]

#Historical irradiance to obrain the pattern
historical_rsds=pd.read_csv("/Users/roozbeh/Desktop/ICSRS/Simulation/2015_Irradiance_hourly.csv")
#Formating the date and time
historical_rsds['time']=pd.to_datetime(historical_rsds['time'],format='%Y%m%d:%H%M')
#Converting to local timezone
historical_rsds['time']=historical_rsds['time'].dt.tz_localize('UCT').dt.tz_convert('America/Los_Angeles').dt.tz_localize(None)
#Extracting month, day,hour
historical_rsds['Year']=pd.DatetimeIndex(historical_rsds['time']).year
historical_rsds['Month']=pd.DatetimeIndex(historical_rsds['time']).month
historical_rsds['Day']=pd.DatetimeIndex(historical_rsds['time']).day
historical_rsds['Hour']=pd.DatetimeIndex(historical_rsds['time']).hour
#Reordering based on the hours in a year and reindexing
target_rows=[0,1,2,3,4,5,6,7]
newrsds=historical_rsds.drop(target_rows).append(historical_rsds.loc[target_rows])
#del newrsds['time']
newrsds.index=range(len(newrsds))
newrsds.insert(0,"date",newrsds['Year'])
newrsds.loc[newrsds.index[8752:8760],'date']='2015'
newrsds['dateInt']=newrsds['Year'].astype(str) + newrsds['Month'].astype(str).str.zfill(2)+ newrsds['Day'].astype(str).str.zfill(2)
newrsds['date'] = pd.to_datetime(newrsds['dateInt'], format='%Y%m%d')
del newrsds['dateInt']
del newrsds['date']

#rsds_sum=newrsds.resample('24H', on='time').sum()
#rsds_sum['Day']=rsds_sum['Day']/24
#rsds_sum['Month']=rsds_sum['Month']/24
newrsds.set_index('time',drop=False,inplace=True)
del newrsds['time']
grouped_rsds = newrsds.resample('D').sum().pad()
grouped_rsds['Month']=grouped_rsds['Month']/24
grouped_rsds['Day']=grouped_rsds['Day']/24
grouped_rsds['Hour']=grouped_rsds['Hour']/12+1
#grouped_rsds['time']=pd.to_datetime(grouped_rsds['time'],format='%Y-%m-%d %H:%M')
# saveasexcel=pd.ExcelWriter('rsds.xlsx')
# rsds.to_excel(saveasexcel, index=True)
# saveasexcel.save()
print(rsds.head(24))
