import argparse
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def trainScaling(width, length, *arr):

    arrs = pd.DataFrame(pd.concat(arr, axis=0))
    scale = min(int(width), int(length))
    scaler = MinMaxScaler(feature_range = (-1*scale, scale))
    scaler.fit(arrs)
    return scaler

def ScalePos(arr, scaler):

    return scaler.transform(pd.DataFrame(arr))