import pandas as pd
import numpy as np
import picker
import matplotlib.pyplot as plt
import matplotlib

pointData = pd.read_csv('./AIS_2017_01_Zone03.csv')
grouped=pointData.groupby("MMSI")
i=0
spatialAxes=["LON","LAT"]
timeAxis="BaseDateTime"
numAttris=["SOG","COG","Heading","Length","Width","Draft","Cargo"]
dscAttris=["VesselName","IMO","CallSign","VesselType","Status"]
for name,group in grouped:
    print(group)
    i+=1
    picker.test(group)
    #picker.pick(100,group,spatialAxes,timeAxis,numAttris,dscAttris)
    if i>20:
        break

    #output as .csv, DON'T use this line while not testing!
    #group.to_csv(str(name)+".csv",sep=",",header=True)