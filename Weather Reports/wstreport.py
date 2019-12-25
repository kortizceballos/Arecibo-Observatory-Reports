#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 00:00:51 2019

Arecibo Observatory Weather Report Generator

Author: Kevin N. Ortiz Ceballos
        Planetary Habitability Laboratory
        University of Puerto Rico at Arecibo
        
*************************************************************************
        
Run this program in the following format:
    wstreport.py yyyymmdd hh:mm

Example for an observation done on Dec. 21 2019 at 18:00:
    wstreport.py 20191221 18:00

Important Notes:
    hh:mm MUST be in UTC
    Make sure to run this program in the same folder as the relevant wst files
"""

import sys
from datetime import timedelta, datetime
import pandas as pd
import matplotlib.pyplot as plt

#STEP 1: Create DataFrame with all weather information for the three days
#surrounding the observation.

obs_dt_input = sys.argv[1] + sys.argv[2]
obs_dt = datetime.strptime(obs_dt_input, '%Y%m%d%H:%M')

date_prev = obs_dt - timedelta(1)
date_post = obs_dt + timedelta(1)

wst_header=['Time','Wind Speed','Raw Wind Direction','Adjusted Wind Direction',\
        '3 Second Rolling Average Wind Speed','3 Second Rolling Average Wind \
        Direction','2 Minute Rolling Average Wind Speed','2 Minute Rolling \
        Average Wind Direction','10 Minute Rolling Average Wind Speed',\
        '10 Minute Rolling Average Wind Direction','10 Minute Gust Wind \
        Direction','10 Minute Gust Wind Speed','10 Minute Gust Time','60 \
        Minute Gust Wind Direction','60 Minute Gust Wind Speed','60 Minute \
        Gust Time','Temperature 1','Relative Humidity','Wind Chill','Heat \
        Index','Dew Point','Degree Days','Average Temperature Today','Degree \
        Day Start','Raw Barometric Pressure','Adjusted Barometric Pressure',\
        'Density Altitude','Wet Bulb Globe Temperature','Saturated Vapor \
        Pressure','Vapor Pressure','Dry Air Pressure','Dry Air Density',\
        'Wet Air Density','Absolute Humidity','Air Density Ratio',\
        'Adjusted Altitude','SAE Correction Factor','Rain Today',\
        'Rain this week','Rain this month','Rain this year','Rain Intensity',\
        'Rain Duration','Hail','Hail Duration','Empty','Empty2']

wst_file_list = ['wst_%s.csv' % date_prev.strftime('%y%m%d'), \
                 'wst_%s.csv' % obs_dt.strftime('%y%m%d'), \
                 'wst_%s.csv' % date_post.strftime('%y%m%d')]

li = []
for file in wst_file_list:
    df = pd.read_csv(file, header=None, names=wst_header)
    li.append(df)
    
frame = pd.concat(li, axis=0, ignore_index=True)
frame.columns = [c.replace(' ', '_') for c in frame.columns]

#STEP 2: Pick out the 48 hour window centered on the time of observation.

#Define function for finding nearest date to input
def nearest(items,pivot):
    return min(items, key=lambda x: abs(x - pivot))

#Create list of possible datetime objects corresponding to wst sampled times
pos_dt=[]
for f in frame["Time"]:
    pos_dt.append(datetime.strptime(f, '%m/%d/%y %H:%M:%S'))

center = nearest(pos_dt,obs_dt)
edge_prev = nearest(pos_dt,obs_dt-timedelta(1))
edge_post = nearest(pos_dt,obs_dt+timedelta(1))

#The 'center' has now been identified. This step is necessary since the 
#weather station will not always take data at the exact time the observation 
#began.

center_index = frame.Time[frame.Time == \
                          center.strftime('%m/%d/%y %H:%M:%S')].index.tolist()

#Pick out list of times in the window
time_str_list = frame.loc[range(center_index[0] - 5760,center_index[0]+5760),["Time"]].Time.tolist()

#Make into a datetime values list
times = []
for f in time_str_list:
    times.append(datetime.strptime(f, '%m/%d/%y %H:%M:%S'))

#Pick out temperature values and convert them to Celsius
tempsF = frame.loc[range(center_index[0] - 5760,center_index[0]+5760),["Temperature_1"]].Temperature_1.tolist()
temps = []
for f in tempsF:
    c = (f-32.)/1.8
    temps.append(c)
    
#Pick out relative humidity values
relhums = frame.loc[range(center_index[0] - 5760,center_index[0]+5760),["Relative_Humidity"]].Relative_Humidity.tolist()

#Pick out precipitation values and convert them to mm
rainsI = frame.loc[range(center_index[0] - 5760,center_index[0]+5760),["Rain_Today"]].Rain_Today.tolist()
rains = []
for rI in rainsI:
    rmm = rI * 25.4
    rains.append(rmm)

#STEP 3: Create the three plots for Temperature, Humidity, and Precipitation.

#Making the individual plots

#plt.style.use('_classic_test')
fig = plt.figure(figsize = (15.,15.))
x = times

#Temperature

ax = plt.subplot(311)
ax.set_xlabel("Date and Time [month-day hh UTC]")
ax.set_ylabel("Temperature [°C]")
ax.set_title("Temperature")
ax.axvspan(obs_dt,obs_dt+timedelta(hours=2.5), alpha=0.3)
y = temps
plt.plot(x,y,color='red')

#Humidity

ax = plt.subplot(312)
ax.set_xlabel("Date and Time [month-day hh UTC]")
ax.set_ylabel("Relative Humidity (%)")
ax.set_title("Relative Humidity")
ax.axvspan(obs_dt,obs_dt+timedelta(hours=2.5), alpha=0.3)
y = relhums
plt.plot(x,y,color='blue')

#Precipitation

ax = plt.subplot(313)
ax.set_xlabel("Date and Time [month-day hh UTC]")
ax.set_ylabel("Accumulated Rain Per Day (mm)")
ax.set_title("Accumulated Rain Per Day")
ax.axvspan(obs_dt,obs_dt+timedelta(hours=2.5), alpha=0.3)
y = rains
plt.plot(x,y,color='black')

#Final adjustments
fig.subplots_adjust(hspace=.5)

plt.show()













