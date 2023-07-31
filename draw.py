# imports
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
import random

# parser arguments to allow for customized drawing
parseIt = argparse.ArgumentParser() # create argument parser object
parseIt.add_argument('-i', '--input', help='path to ssd file', required=True) # input path to sdd
parseIt.add_argument('-w', '--width', help='width of output image', required=False, default=10) # width of frame defaults to 10
parseIt.add_argument('-l', '--length', help='length of output image', required=False, default=10) # length of frame defaults to 10
parseIt.add_argument('-f', '--filter', help='yaml file with filter configurations', required=False, default=None) # filter.yaml path to help filter the dataset
parseIt.add_argument('-c', '--coordinate', help='yaml file with labelling configurations', required=False, default=None) # coordinate.yaml to help plot the data with color coordination
parseIt.add_argument('-s', '--save', help='output folder path', required=True) # output folder path for png files
parseIt.add_argument('--points', help='plot as points', default=False, action=argparse.BooleanOptionalAction) # boolean flag to determine if plot has points or lines

def openSSD(pathSSD: str, outpath: str = None):
  '''
  inputs: path to SDD, optional outpath to save parsed sdd file
  outputs: parsedSDD dataframe object
  
  The goal of this function is use the SDDReport object to save the parsed SDD.
  '''
  sdd = SDDReport(pathSSD) # create SDD object
  dimensions, chromosomeInfo, damageInfo, cause = sdd.parseVizInfo() # create parsed dataframes of important data
  parsedSdd = sdd.saveParsed(dimensions, chromosomeInfo, damageInfo, cause, path=outpath) # create a dataframe with parsed SDD data for visualization

  return parsedSdd

def scalePositionalData(df: pd.DataFrame, width: int, length: int):
  '''
  inputs: parsedSDD dataframe, width and length of frame
  outputs: None; changes dataframe to normalized values
  
  The goal of this function is to scale the xyz data from the parsedSDD dataframe to the desired scale.
  '''
  if "xmax" not in df.columns: # if no xmax in dataframe, then assume only center data so only scale those
    # trainScaling return a scaler from the data inputted and ScalePos actually scales all the values
    x = ScalePos(df['xcenter'], trainScaling(width, length, df['xcenter']))
    y = ScalePos(df['ycenter'], trainScaling(width, length, df['ycenter']))
    z = ScalePos(df['zcenter'], trainScaling(width, length, df['zcenter']))
    df["xcenter"] = x
    df["ycenter"] = y
    df["zcenter"] = z
  
  else: # else scale all max and mins and centers
    # trainScaling return a scaler from the data inputted and ScalePos actually scales all the values
    sx = trainScaling(width, length, df['xcenter'], df['xmax'], df['xmin'])
    sy = trainScaling(width, length, df['ycenter'], df['ymax'], df['ymin'])
    sz = trainScaling(width, length, df['zcenter'], df['zmax'], df['zmin'])
    df["xcenter"], df["ycenter"], df["zcenter"] = ScalePos(df["xcenter"], sx), ScalePos(df["ycenter"], sy), ScalePos(df["zcenter"], sz)
    df["xmax"], df["ymax"], df["zmax"] = ScalePos(df["xmax"], sx), ScalePos(df["ymax"], sy), ScalePos(df["zmax"], sz)
    df["xmin"], df["ymin"], df["zmin"] = ScalePos(df["xmin"], sx), ScalePos(df["ymin"], sy), ScalePos(df["zmin"], sz)

def filter(df: pd.DataFrame, filterFilePath: str):
  '''
  inputs: parsedSDD and file path to filtering configurations
  outputs: filtered parsedSDD
  
  The goal of this function is to filter the dataframe based off of the desired configurations by the user.
  '''
  newdf = df.copy() # create a copy of the dataframe to ensure returning back the original

  filterDict = readYaml(filterFilePath) # opening up the yaml file as a dictionary
  newDict = {} # instantiating a new yaml dict
  for col in list(filterDict.keys()): # checking all keys in the yaml (each key is a column header)
    if col in list(df.columns): # determining if those keys are in the actual dataframe
      newDict[col] = filterDict[col] # adding to new yaml dict if present
    else: # else skips this key and any filtration user desires
      print(f"Cannot filter by values in column {col} because it is not in the provided sdd.")
  
  for key in list(newDict.keys()): # iterating through selected filter keys/columns
    filters = [] # instantiating a list that will house the desired values from the specific column of interest
    if key == 'structure' or key == 'identifier' or key == 'dsbPresent': # these keys/columns are of a specific format in the yaml
      for i in newDict[key].keys(): # iterate each unique entry in the column of interest
        if newDict[key][i]['include']: # check is user desires this entry
          filters.append(i) # if so, add to filter as one to keep
    elif key == "direct" or key == "indirect" or key == "numBases" or key == "singleNumber": # these keys/columns are of another specific format in the yaml
      # the set of if else statements below are checks to ensure user requests are valid
      if newDict[key]['less'] == None and newDict[key]['greater'] == None and newDict[key]['equal'] == None: # checking if any are none, if so skip this condition
        pass
      elif (newDict[key]['less'] != None and newDict[key]['greater'] != None) and (newDict[key]['less'] > newDict[key]['greater'] or newDict[key]['less'] == newDict[key]['greater']): # checking to see if less and greater are appropriately selected
        print(f"Invalid arguments for {key} in {filterFilePath}. The less than value is larger than the greater than value or is equal to it.")
      elif newDict[key]['equal'] != None and newDict[key]['equal'] not in newdf[key]: # checking to see if the equal selection is even present
        print(f"Invalid arguments for {key} in {filterFilePath}. {newDict[key]['equal']} is not in this dataframe.")
      elif newDict[key]['greater'] != None and len(newdf[newdf[key] > newDict[key]['greater']]) == 0: # checking to see if the greater than selection is even present
        print(f"Invalid arguments for {key} in {filterFilePath}. There is no value in the dataframe greater than {newDict[key]['greater']}.")
      elif newDict[key]['less'] != None and len(newdf[newdf[key] < newDict[key]['less']]) == 0: # checking to see if the less than selection is even present
        print(f"Invalid arguments for {key} in {filterFilePath}. There is no value in the dataframe less than {newDict[key]['less']}.")
      else:
        # try except clauses to catch any other issues not addressed and/or apply conditions without more complex logic
        try:
          greater = newdf[key][newdf[key] > newDict[key]['greater']].values # selecting greater than values if present
        except:
          greater = []
        try:
          less = newdf[key][newdf[key] < newDict[key]['less']].values # selecting less than values if present
        except:
          less = []
        try:
          equal = newdf[key][newdf[key] == newDict[key]['equal']].values # selecting equal to values if present
        except:
          equal = []
        # adding the combination of any of these conditions to the filters
        filters.extend(greater)
        filters.extend(less)
        filters.extend(equal)
    elif key == 'chromsomeNumber': # if chromosomenumber is a criteria for the user
      filters.extend(newDict[key]) # append all numbers the user desires
    else:
      print("Unknown filter criteria. Defaulting to all damages.")

    # apply filter for every key on the dataframe if present
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

def graph(df, labelCoordinateList, outputDir, points):
  colorlist = list(mcolors.CSS4_COLORS)
  random.shuffle(colorlist)
  if 'xmax' not in list(df.columns) or points:
    for key in labelCoordinateList:
      fig = plt.figure()
      ax = fig.add_subplot(111, projection="3d")
      uniqueVals = list(df[key].unique())
      left = uniqueVals.copy()
      for x, y, z, l, i in tqdm(zip(df['xcenter'], df['ycenter'], df['zcenter'], df[key], df.index)):
        if l in left:
          if "direct" in df.columns and "indirect" in df.columns:
            ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2*(df["direct"][i] + df["indirect"][i]), label = l)
            left.remove(l)
          else:
            ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2, label = l)
            left.remove(l)
        else:
          if "direct" in df.columns and "indirect" in df.columns:
            ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2*(df["direct"][i] + df["indirect"][i]))
          else:
            ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2)
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
  scalePositionalData(df, int(args.width), int(args.length))
  newdf = filter(df, args.filter)
  pb, newdf = label(newdf, args.coordinate)
  graph(newdf, pb, args.save, points=args.points)