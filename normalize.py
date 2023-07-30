# imports
import argparse
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def trainScaling(scale: int, *arr: pd.Series):
    '''
    inputs: scale of frame, any number of pandas series objects
    outputs: scaler to fit the data with

    The goal of this function is to design a scaler that can be used for all values of the same variable (i.e. xcenter, xmax, xmin).
    By default uses the MinMaxScaler. The scale is used to determine what values to scale the arrays to (i.e. 10 scales data to -10, 10).
    '''
    arrs = pd.DataFrame(pd.concat(arr, axis=0)) # combine all arrays under the same series obj
    scaler = MinMaxScaler(feature_range = (-1*scale, scale)) # design scaler to fit values into the desired scale
    scaler.fit(arrs) # fit scaler to data
    return scaler

def ScalePos(arr: pd.Series, scaler: MinMaxScaler):
    '''
    inputs: pandas series obj, scikit learn scaler object
    outputs: numpy array of the series object (shape = (1 x numRows))

    The goal of this function is to scale any data array to the specific scaler desired.
    '''
    return scaler.transform(pd.DataFrame(arr)) # scale data
