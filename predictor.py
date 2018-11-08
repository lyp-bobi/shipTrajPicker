import pandas as pd
import numpy as np

#currently not used

def MAPredict(df:pd.DataFrame):
    #the df should be the 10 previous and 10 next element in the sequence
    #so it should be 20rows and multiple columns
    return df.mean()

#todo: GaussianMAPredict, NNPredict, attributesPredict