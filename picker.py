import pandas as pd
import numpy as np
import time, datetime
import matplotlib.pyplot as plt
import matplotlib


def pick(numpicked:int,df:pd.DataFrame, spatialAxes=[], timeAxis="", numAttris=[], dscAttris=[]):
    #DataFrame is necessary, other is not necessary
    #if not used, leave it as [] or just skip it
    #only supported one time axis. other attributes
    df=df.copy()
    #configurations of significance

    spatialSig=0.35
    timeSig=0.1
    stSig=0
    numSig=0.35
    dscSig=0.2
    #dynamic set maWindow between 20 and 100
    #the actual window size is maWindow*2
    maWindow = int(min(100,max(df.shape[0]/40,20))/2)
    print("dynamical setted maWindow as "+str(maWindow))


    pd.set_option('display.max_columns',15)
    pd.set_option('display.max_rows', 100)


    score=pd.DataFrame()

    #if we can store all points,return the dataframe
    if df.shape[0]<numpicked:
        print("picked " + str(df.shape[0]) + " points from "
              + str(df.shape[0]) + "points ,and preserved 100% of information")
        return df

    # #numpicked should at least larger than maWindow
    # if numpicked<maWindow:
    #     print("numpicked should at least larger than "+str(maWindow))
    #     return df

    #sort all data by time
    if timeAxis!="":
        df=df.sort_values(timeAxis).reset_index(drop=True)


    #ranking spatial axis information based on moving average
    #todo: now the angular are included in numerical values
    #todo: but maybe we could calculate it by ourselves
    if spatialSig!=0:
        locC = df[spatialAxes].copy(deep=True)
        #extend it
        zerodf = pd.DataFrame(columns=locC.columns)
        for i in range(maWindow):
            zerodf=zerodf.append(locC.head(1))
        zerodf[:]=0
        #print(zerodf)
        locCExt = zerodf.append(locC).append(zerodf)
        ma=locCExt.rolling(maWindow,center=True).mean()[maWindow:-maWindow]
        prediction=ma
        #print(prediction)
        #rank the normalized(fake) spatial distance
        sDiff=locC-prediction
        #print(sDiff)
        sDiffAbs=sDiff.abs().apply(lambda x:x.sum(),axis=1)
        avSDiff=sDiffAbs.sum()/(sDiffAbs.shape[0]-maWindow)
        #print(avSDiff)
        #refill the first and last part as 2*avr
        if df.shape[0]>maWindow:
            sDiffAbs[0:maWindow]=sDiffAbs[0:maWindow].apply(lambda x:2*avSDiff)
            sDiffAbs[-maWindow:] = sDiffAbs[-maWindow:].apply(lambda x: 2 * avSDiff)
        else:
            sDiffAbs[:]=1
        tmpvalue=spatialSig/avSDiff
        score['spatial']=sDiffAbs.apply(lambda x:x*tmpvalue)

    #rank the time
    if timeSig!= 0:
        timeC=df[timeAxis].copy(deep=True)
        timeCnext=timeC.shift(-1)
        tDiff = timeCnext-timeC
        avTDiff=tDiff.mean()
        tmpvalue = timeSig / avTDiff
        score['time']= tDiff.apply(lambda x:x*tmpvalue)

    #todo: support the time-spatial Score calculation
    if stSig !=0:
        pass
        #currently not implemented

    #other numerical value
    if numSig!=0:
        numC=df[numAttris].copy(deep=True)
        numCnext = numC.shift(-1)
        numDiff = numCnext - numC
        numLen=len(numAttris)
        numDiffAbs=numDiff.abs()
        numDiffAbsMean=numDiffAbs.mean()
        for colnum in range(0,numLen):
            if(numDiffAbsMean[numAttris[colnum]]!=0):
                numDiffAbs[numAttris[colnum]]=\
                    numDiffAbs[numAttris[colnum]].apply(lambda x:x/numDiffAbsMean[numAttris[colnum]])
        tmpvalue=numSig/numLen
        score['numericalAttributes'] = numDiffAbs.apply(lambda x: x.sum()*tmpvalue,axis=1)

    #other non-numerical values, aka Description values
    if dscSig!=0:
        dscLen = len(dscAttris)
        dscC=df[dscAttris].copy(deep=True)
        for colnum in range(0,dscLen):
            col = dscC[dscAttris[colnum]].copy(deep=True)
            #only consider the change
            colpast=col.shift(1)
            dscDiff=col.copy(deep=True)
            for rownum in range(df.shape[0]):
                if col[rownum]!=colpast[rownum]:
                    dscDiff[rownum]=1
                else:
                    dscDiff[rownum]=0.5
            #the rare descriptions matters more
            map={}
            dscCount=pd.value_counts(col)
            for dscKey in dscCount.index:
                dscValue=dscCount[dscKey]
                rev=df.shape[0]/dscValue
                map[dscKey]=rev
            col=col.apply(lambda x: map[x])
            colMean=col.mean()
            col=col.apply(lambda x:x/colMean)*dscDiff
            #print(col)
            dscC.loc[:,dscAttris[colnum]]=col

        tmpvalue=dscSig/dscLen
        score['descriptionAttributes']=dscC.apply(lambda x:x.sum()*tmpvalue,axis=1)

    #print("score is \n"+str(score))
    #todo:don't pick two points when they are too near
    #hint:get 10 more points and calculate distance, and then
    #remove the 10 minist distance
    df['totalScore']=score.apply(lambda x:x.sum(),axis=1)
    totalSorted=df.sort_values('totalScore',ascending=False)
    picked=totalSorted[0:numpicked-2]
    picked=picked.append(df[:1]).append(df[-1:])\
        .sort_values('BaseDateTime').reset_index(drop=True)
    #print(picked)
    info=picked['totalScore'].sum()/totalSorted['totalScore'].sum()
    print("picked "+str(numpicked)+" points from "
          +str(df.shape[0])+"points ,and preserved "+format(info, '.0%')+" of information")
    return picked


def test(df:pd.DataFrame,id:int):
    df=df.copy()
    df.loc[:,["BaseDateTime"]] = df["BaseDateTime"].apply(
        lambda x: int(time.mktime(time.strptime(x, "%Y-%m-%dT%H:%M:%S")))
    )
    spatialAxes = ["LON", "LAT"]
    timeAxis = "BaseDateTime"
    numAttris = ["SOG", "COG", "Heading", "Length", "Width", "Draft", "Cargo"]
    dscAttris = ["VesselName", "IMO", "CallSign", "VesselType", "Status"]
    picked = pick(int(max(10,df.shape[0]/20)), df, spatialAxes, timeAxis, numAttris, dscAttris)
    tmpdf = df.sort_values("BaseDateTime")[["LON", "LAT"]]
    plt.figure(1)
    plt.title(str(id)+"ori")
    plt.scatter(tmpdf["LON"], tmpdf["LAT"], marker=".")
    plt.figure(2)
    plt.title(str(id)+"pkd")
    plt.scatter(picked["LON"], picked["LAT"], marker=".")
    plt.show()

if __name__ == '__main__':
    df=pd.read_csv("43676060.csv")
    #df=pd.read_csv("205700000.csv")
    test(df)