import argparse
import pandas as pd
import mpld3
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.colors as mcolors
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from parser import SDDReport
from normalize import trainScaling, ScalePos
from readYaml import readYaml

parseIt = argparse.ArgumentParser()
parseIt.add_argument('-i', '--input', help='path to ssd file', required=True)
parseIt.add_argument('-w', '--width', help='width of output image', required=False, default=10)
parseIt.add_argument('-l', '--length', help='length of output image', required=False, default=10)

def openSSD(pathSSD, outpath = None):

  sdd = SDDReport(pathSSD)
  dimensions, chromosomeInfo, damageInfo, cause = sdd.parseVizInfo()
  parsedSdd = sdd.saveParsed(dimensions, chromosomeInfo, damageInfo, cause, path=outpath)

  return parsedSdd

def scalePositionalData(df, width, length):
  
  if "xmax" not in df.columns:
    x = ScalePos(df['xcenter'], trainScaling(width, length, df['xcenter']))
    y = ScalePos(df['ycenter'], trainScaling(width, length, df['ycenter']))
    z = ScalePos(df['zcenter'], trainScaling(width, length, df['zcenter']))
    df["xcenter"] = x
    df["ycenter"] = y
    df["zcenter"] = z
  
  else:
    sx = trainScaling(width, length, df['xcenter'], df['xmax'], df['xmin'])
    sy = trainScaling(width, length, df['ycenter'], df['ymax'], df['ymin'])
    sz = trainScaling(width, length, df['zcenter'], df['zmax'], df['zmin'])
    df["xcenter"], df["ycenter"], df["zcenter"] = ScalePos(df["xcenter"], sx), ScalePos(df["ycenter"], sy), ScalePos(df["zcenter"], sz)
    df["xmax"], df["ymax"], df["zmax"] = ScalePos(df["xmax"], sx), ScalePos(df["ymax"], sy), ScalePos(df["zmax"], sz)
    df["xmin"], df["ymin"], df["zmin"] = ScalePos(df["xmin"], sx), ScalePos(df["ymin"], sy), ScalePos(df["zmin"], sz)

if __name__ == '__main__':

  args = parseIt.parse_args()

  df = openSSD(args.input)
  scalePositionalData(df, int(args.width), int(args.length))
  print(df.columns)
