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
import math

# parser arguments to allow for customized drawing
parseIt = argparse.ArgumentParser() # create argument parser object
parseIt.add_argument('-i', '--input', help='path to ssd file', required=True) # input path to sdd
parseIt.add_argument('-w', '--width', help='width of output image', required=False, default=10) # width of frame defaults to 10
parseIt.add_argument('-l', '--length', help='length of output image', required=False, default=10) # length of frame defaults to 10
parseIt.add_argument('-f', '--filter', help='yaml file with filter configurations', required=False, default=None) # filter.yaml path to help filter the dataset
parseIt.add_argument('-c', '--coordinate', help='yaml file with labelling configurations', required=False, default=None) # coordinate.yaml to help plot the data with color coordination
parseIt.add_argument('-s', '--save', help='output folder path', required=False, default='.') # output folder path for png files

def openSSD(pathSSD: str, outpath: str = None):
  '''
  inputs: path to SDD, optional outpath to save parsed sdd file
  outputs: parsedSDD dataframe object
  
  The goal of this function is use the SDDReport object to save the parsed SDD.
  '''
  sdd = SDDReport(pathSSD) # create SDD object
  dimensions, chromosomeInfo, damageInfo, cause = sdd.parseVizInfo() # create parsed dataframes of important data
  parsedSdd = sdd.saveParsed(dimensions, chromosomeInfo, damageInfo, cause, path=outpath) # create a dataframe with parsed SDD data for visualization

  return parsedSdd, sdd.volumes

def scalePositionalData(originaldf: pd.DataFrame, width: int, length: int):
  '''
  inputs: parsedSDD dataframe, width and length of frame
  outputs: None; changes dataframe to normalized values
  
  The goal of this function is to scale the xyz data from the parsedSDD dataframe to the desired scale.
  '''
  df = originaldf.copy() # create a copy of the dataframe to ensure returning back the original
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

  return df, sx, sy, sz

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

def label(df: pd.DataFrame, labelFilePath: str):
  '''
  inputs: pandas dataframe, path to color coordination file path
  outputs: list of columns to color coordinate charts by and dataframe with proper labels applied to the unique values of the columns
  
  The goal of this function is to determine columns to plot colors by and finalized dataframe for plotting.
  '''
  filterDict = readYaml(labelFilePath) # open dictionary of color coordination configurations
  newDict = {} # instantiate a new processed dictionary for configurations
  for col in list(filterDict.keys()): # iterate through each key in the yaml which is a column in the dataframe
    if col in list(df.columns): # check if the column exists in the dataframe
      newDict[col] = filterDict[col] # add the configuration to the new dictionary
    else:
      print(f"Cannot label by values in column {col} because it is not in the provided sdd.") # if not in the dataframe then skip

  plotBy = [] # instantiate a list to store which columns to color coordinate by
  outfiles = {}
  for key in list(newDict.keys()): # iterate through each key in the color coordination dictionary
    if newDict[key]['labelby']: # check if user wants to coordinate by this key
      plotBy.append(key) # add the key to the list
      outfiles[key] = newDict[key]['outfile']
      for i in df.index: # iterate through each row in the dataframe
        # try except in case user does not include labels
        try:
          df[key][i] = newDict[key]['labels'][df[key][i]] # apply user desired labels to the unique values of the column the key represents
        except:
          pass

  return plotBy, outfiles, df

def graphNucleus(ax, volumes):

  if len(volumes) == 7 and int(volumes[0]) == 1:
      
      rx, ry, rz = abs(volumes[1] - volumes[4]), abs(volumes[2] - volumes[5]), abs(volumes[3] - volumes[6])

      # Set of all spherical angles:
      u = np.linspace(0, 2 * np.pi, 256).reshape(256, 1)
      v = np.linspace(0, np.pi, 256).reshape(-1, 256)

      # Cartesian coordinates that correspond to the spherical angles:
      # (this is the equation of an ellipsoid):
      x = rx * np.sin(v) * np.cos(u)
      y = ry * np.sin(v) * np.sin(u)
      z = rz * np.cos(v)

      ax.plot_surface(x, y, z, alpha=0.20, color='m')

def graph(df: pd.DataFrame, labelCoordinateList: list, outfiles: dict, outputDir: str, volumes: list):
  '''
  inputs: dataframe to plot, list to color coordinate data by, output directory to store images, flag to override and plot points
  outputs: plots saved to output directory (labelled and unlablled)
  
  The goal of this function is to plot the graph with points/lines of damage and labelled/filtered as desired by the user. The png files will be labelled by filtration criteria and a basic one without labels
  '''
  colorlist = list(mcolors.CSS4_COLORS) # various matplotlib colors
  random.shuffle(colorlist) # shuffling to get better color selections in the beginning of the list

  for key in labelCoordinateList: # iterate through list of labels
    fig = plt.figure() # create new fig object
    ax = fig.add_subplot(111, projection="3d") # create a 3D plot in figure
    uniqueVals = list(df[key].unique()) # find unique values of the column
    left = uniqueVals.copy() # copy a index tracker for which labels used
    for x, y, z, l, i in tqdm(zip(df['xcenter'], df['ycenter'], df['zcenter'], df[key], df.index)): # iterate through centers, labelled column and index in dataframe
      if l in left: # if label still in index tracker (meaning no labelled values by this unique value)
        if "direct" in df.columns and "indirect" in df.columns: # if direct and indirect (changing size of damage on plot since basically the number of damages)
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2*(df["direct"][i] + df["indirect"][i]), label = l) # plot point with label, its own unique color, and size
          left.remove(l) # remove from index to not reuse and create a large legend (weird workaround pyplot)
        else: # if direct and indirect not in dataframe
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2, label = l) # cannot change size of points
          left.remove(l) # remove since first time using this label in legend
      
      else: # if label not in index list for unique values
        if "direct" in df.columns and "indirect" in df.columns: # if direct and indirect (changing size of damage on plot since basically the number of damages)
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2*(df["direct"][i] + df["indirect"][i])) # plot point without label since already applied but color will be unique to label
        else: # if no direct, indirect
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=2) # size not modulated by number of damages in the center damage point
    
    graphNucleus(ax, volumes)

    plt.legend(loc="upper right", ncol = 5, fontsize = "xx-small") # apply legend
    try:
      fig.savefig(os.path.join(outputDir, outfiles[key])) # save figure based on labelled column
    except:
      fig.savefig(os.path.join(outputDir, f"dsb_{key}.png")) # save figure based on labelled column
    plt.close(fig) # close to avoid overlaps
    
  fig = plt.figure() # create new figure
  ax = fig.add_subplot(111, projection="3d") # add 3D component

  if "direct" in df.columns and "indirect" in df.columns: # if direct and indirect (changing size of damage on plot since basically the number of damages)
    for x, y, z, i in tqdm(zip(df['xcenter'], df['ycenter'], df['zcenter'], df.index)): # iterate through centers, labelled column and index in dataframe
      ax.plot3D(x, y, z, marker=".", color='k', markersize=2*(df["direct"][i] + df["indirect"][i])) # graph with size modulation and no labels
  else: # if no direct/indirect
    for x, y, z, i in tqdm(zip(df['xcenter'], df['ycenter'], df['zcenter'], df.index)): # iterate through centers, labelled column and index in dataframe
      ax.plot3D(x, y, z, marker=".", markersize=2, color='k') # same size for all points
  
  graphNucleus(ax, volumes)

  fig.savefig(os.path.join(outputDir, f"dsb.png")) # save basic image
  plt.close(fig) # close to avoid overlaps
  
  

if __name__ == '__main__': # if script run directly

  args = parseIt.parse_args() # creating an args object to extract user input

  df, volumes = openSSD(args.input) # original unprocessed dataframe; remains untouched
  newdf, sx, sy, sz = scalePositionalData(df, int(args.width), int(args.length)) # scaling the positional data; return new dataframe object in memory
  
  nucleusAxes = []
  if len(volumes) > 7:
    nucleusAxes = [int(volumes[7]), sx.transform([[volumes[8]]]).item(), sy.transform([[volumes[9]]]).item(), sz.transform([[volumes[10]]]).item(), sx.transform([[volumes[11]]]).item(), sy.transform([[volumes[12]]]).item(), sz.transform([[volumes[13]]]).item()]
  elif len(volumes) == 7:
    nucleusAxes = [int(volumes[0]), sx.transform([[volumes[1]]]).item(), sy.transform([[volumes[2]]]).item(), sz.transform([[volumes[3]]]).item(), sx.transform([[volumes[4]]]).item(), sy.transform([[volumes[5]]]).item(), sz.transform([[volumes[6]]]).item()]

  if args.filter != None: # ensuring this is inputed, else basic plot
    newdf = filter(newdf, args.filter) # applies filter to new dataframe object in memory
  pb = [] # instantiating empty variable incase labels not applied
  outfiles = {}
  if args.coordinate != None: # ensuring this is inputed, else basic plot
    pb, outfiles, newdf = label(newdf, args.coordinate) # applies labels to the same dataframe in memory as filter
  graph(newdf, pb, outfiles, args.save, nucleusAxes) # create and save plots