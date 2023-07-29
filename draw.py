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
parseIt.add_argument('-f', '--filter', help='yaml file with filter configurations', required=False, default=None)
parseIt.add_argument('-c', '--coordinate', help='yaml file with labelling configurations', required=False, default=None)
parseIt.add_argument('-s', '--save', help='output folder path', required=True)

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

def filter(df, filterFilePath):

  newdf = df.copy()

  filterDict = readYaml(filterFilePath)
  newDict = {}
  for col in list(filterDict.keys()):
    if col in list(df.columns):
      newDict[col] = filterDict[col]
    else:
      print(f"Cannot filter by values in column {col} because it is not in the provided sdd.")
  
  for key in list(newDict.keys()):
    filters = []
    if key == 'structure' or key == 'identifier' or key == 'dsbPresent':
      for i in newDict[key].keys():
        if newDict[key][i]['include']:
          filters.append(i)
    elif key == "direct" or key == "indirect" or key == "numBases" or key == "singleNumber":
      if newDict[key]['less'] == None and newDict[key]['greater'] == None and newDict[key]['equal'] == None:
        pass
      elif (newDict[key]['less'] != None and newDict[key]['greater'] != None) and (newDict[key]['less'] > newDict[key]['greater'] or newDict[key]['less'] == newDict[key]['greater']):
        print(f"Invalid arguments for {key} in {filterFilePath}. The less than value is larger than the greater than value or is equal to it.")
      elif newDict[key]['equal'] != None and newDict[key]['equal'] not in newdf[key]:
        print(f"Invalid arguments for {key} in {filterFilePath}. {newDict[key]['equal']} is not in this dataframe.")
      elif newDict[key]['greater'] != None and len(newdf[newdf[key] > newDict[key]['greater']]) == 0:
        print(f"Invalid arguments for {key} in {filterFilePath}. There is no value in the dataframe greater than {newDict[key]['greater']}.")
      elif newDict[key]['less'] != None and len(newdf[newdf[key] < newDict[key]['less']]) == 0:
        print(f"Invalid arguments for {key} in {filterFilePath}. There is no value in the dataframe less than {newDict[key]['less']}.")
      else:
        try:
          greater = newdf[key][newdf[key] > newDict[key]['greater']].values
        except:
          greater = []
        try:
          less = newdf[key][newdf[key] < newDict[key]['less']].values
        except:
          less = []
        try:
          equal = newdf[key][newdf[key] == newDict[key]['equal']].values
        except:
          equal = []
        filters.extend(greater)
        filters.extend(less)
        filters.extend(equal)
    elif key == 'chromsomeNumber':
      filters.extend(newDict[key])
    else:
      print("Unknown filter criteria. Defaulting to all damages.")

    if len(filters) != 0:
      newdf = newdf[newdf[key].isin(filters)]
    else:
      pass

  return newdf

def label(df, labelFilePath):

  filterDict = readYaml(labelFilePath)
  newDict = {}
  for col in list(filterDict.keys()):
    if col in list(df.columns):
      newDict[col] = filterDict[col]
    else:
      print(f"Cannot label by values in column {col} because it is not in the provided sdd.")

  plotBy = []
  for key in list(filterDict.keys()):
    if filterDict[key]['include']:
      plotBy.append(key)
      for i in df.index:
        try:
          df[key][i] = filterDict[key]['labels'][df[key][i]]
        except:
          pass

  return plotBy, df

def graph(df, labelCoordinateList, outputDir):
  colorlist = list(mcolors.CSS4_COLORS)
  if 'xmax' not in list(df.columns):
    for key in labelCoordinateList:
      fig = plt.figure()
      ax = fig.add_subplot(111, projection="3d")
      uniqueVals = list(df[key].unique())
      left = uniqueVals.copy()
      for x, y, z, l in tqdm(zip(df['xcenter'], df['ycenter'], df['zcenter'], df[key])):
        if l in left:
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=10, label = l)
          left.remove(l)
        else:
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=10)
      plt.legend(loc="upper right", ncol = 5, fontsize = "xx-small")
      fig.savefig(os.path.join(outputDir, f"dsb_{key}.png"))
      plt.close(fig)
  else:
    for key in labelCoordinateList:
      fig = plt.figure()
      ax = fig.add_subplot(111, projection="3d")
      uniqueVals = list(df[key].unique())
      left = uniqueVals.copy()
      for x1, y1, z1, x2, y2, z2, l in tqdm(zip(df['xmin'], df['ymin'], df['zmin'], df['xmax'], df['ymax'], df['zmax'], df[key])):
        if l in left:
          ax.plot3D([x1, x2], [y1, y2], [z1, z2], linestyle='-', linewidth = 2, color=colorlist[uniqueVals.index(l)], label = l)
          left.remove(l)
        else:
          ax.plot3D([x1, x2], [y1, y2], [z1, z2], linestyle='-', linewidth = 2, color=colorlist[uniqueVals.index(l)])
      plt.legend(loc="upper right", ncol = 5, fontsize = "xx-small")
      fig.savefig(os.path.join(outputDir, f"dsb_{key}.png"))
      plt.close(fig)

if __name__ == '__main__':

  args = parseIt.parse_args()

  df = openSSD(args.input)
  # scalePositionalData(df, int(args.width), int(args.length))
  newdf = filter(df, args.filter)
  pb, newdf = label(newdf, args.coordinate)
  graph(newdf, pb, args.save)