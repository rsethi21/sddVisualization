import draw
import argparse
import warnings
import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.colors as mcolors
import random
from concurrent.futures import ProcessPoolExecutor as ppe
from itertools import repeat
from createVideo import createVideo

# parser arguments to allow for customized drawing
parseIt = argparse.ArgumentParser() # create argument parser object
parseIt.add_argument('-i', '--input', help='path to ssd file', required=True) # input path to sdd
parseIt.add_argument('-w', '--width', help='width of output images', required=False, default=10) # width of frame defaults to 10
parseIt.add_argument('-l', '--length', help='length of output images', required=False, default=10) # length of frame defaults to 10
parseIt.add_argument('-f', '--filter', help='yaml file with filter configurations', required=False, default=None) # filter.yaml path to help filter the dataset
parseIt.add_argument('-c', '--coordinate', help='yaml file with labelling configurations', required=False, default=None) # coordinate.yaml to help plot the data with color coordination
parseIt.add_argument('-s', '--save', help='output folder path', required=False, default='.') # output folder path for png files
parseIt.add_argument('-p', '--workers', help='number of processes to use', required=False, default=1) # output folder path for png files
parseIt.add_argument('-t', '--fps', help='frames per second for video speed; max is 60 will automatically default to this if greater than this', required=False, default=60) # output folder path for png files
parseIt.add_argument('--size', help='boolean flag to allow for size modulation of damage centroids', required=False, default=False, action=argparse.BooleanOptionalAction)

def graph(df: pd.DataFrame, unfilteredDF: pd.DataFrame, labelCoordinateList: list, outputDirs: list, basicOutputDir: str, volumes: list, size: bool, ind: int):
  '''
  inputs: dataframe to plot, list to color coordinate data by, output directory to store images, flag to override and plot points
  outputs: plots saved to output directory (labelled and unlablled)
  
  The goal of this function is to plot the graph with points/lines of damage and labelled/filtered as desired by the user. The png files will be labelled by filtration criteria and a basic one without labels
  '''
  colorlist = sorted(list(mcolors.CSS4_COLORS)) # various matplotlib colors

  for key, f in zip(labelCoordinateList, outputDirs): # iterate through list of labels
    fig = plt.figure() # create new fig object
    ax = fig.add_subplot(111, projection="3d") # create a 3D plot in figure
    uniqueVals = list(unfilteredDF[key].unique()) # find unique values of the column
    left = uniqueVals.copy() # copy a index tracker for which labels used
    draw.graphNucleus(ax, volumes)
    for x, y, z, l, i in zip(df['xcenter'], df['ycenter'], df['zcenter'], df[key], df.index): # iterate through centers, labelled column and index in dataframe
      if l in left: # if label still in index tracker (meaning no labelled values by this unique value)
        if "totalDamages" in df.columns and size: # if direct and indirect (changing size of damage on plot since basically the number of damages)
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=(df["totalDamages"][i]), label = l) # plot point with label, its own unique color, and size
          left.remove(l) # remove from index to not reuse and create a large legend (weird workaround pyplot)
        else: # if direct and indirect not in dataframe
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=1, label = l) # cannot change size of points
          left.remove(l) # remove since first time using this label in legend
      
      else: # if label not in index list for unique values
        if "totalDamages" in df.columns and size:# if direct and indirect (changing size of damage on plot since basically the number of damages)
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=(df["totalDamages"][i])) # plot point without label since already applied but color will be unique to label
        else: # if no direct, indirect
          ax.plot3D(x, y, z, marker=".", color=colorlist[uniqueVals.index(l)], markersize=1) # size not modulated by number of damages in the center damage point

    plt.legend(loc="upper right", ncol = 5, fontsize = "xx-small") # apply legend
    fig.savefig(os.path.join(f, f"damage_{key}_{ind}.png")) # save figure based on labelled column
    plt.close(fig) # close to avoid overlaps

  fig = plt.figure() # create new figure
  ax = fig.add_subplot(111, projection="3d") # add 3D component
  draw.graphNucleus(ax, volumes)
  if "totalDamages" in df.columns and size: # if direct and indirect (changing size of damage on plot since basically the number of damages)
    for x, y, z, i in zip(df['xcenter'], df['ycenter'], df['zcenter'], df.index): # iterate through centers, labelled column and index in dataframe
      ax.plot3D(x, y, z, marker=".", color='k', markersize=(df["totalDamages"][i])) # graph with size modulation and no labels
  else: # if no direct/indirect
    for x, y, z, i in zip(df['xcenter'], df['ycenter'], df['zcenter'], df.index): # iterate through centers, labelled column and index in dataframe
      ax.plot3D(x, y, z, marker=".", markersize=1, color='k') # same size for all points

  fig.savefig(os.path.join(basicOutputDir, f"damage_{ind}.png")) # save basic image

  plt.close(fig) # close to avoid overlaps

def plot(df, i, pb, folders, outFold, nucleusAxes, sizeBool):
   
   tempDF = df[df["lesiontimes"] <= int(i)]
   graph(tempDF, df, pb, folders, outFold, nucleusAxes, sizeBool, int(i)) # create and save plots
   print(f"Completed {int(100 * (i/1200))}% of Frames", end="\r") # 1200

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    args = parseIt.parse_args() # creating an args object to extract user input

    start = "\033[1;3m"
    end = "\033[0m"
    print(start + "Extracting SDD Information..." + end)
    df, volumes = draw.openSSD(args.input) # original unprocessed dataframe; remains untouched
    
    if "lesionTimes" not in df.columns:
       pass
    else:
       raise ValueError("Input an SDD with lesion times.")
    
    newdf, sx, sy, sz = draw.scalePositionalData(df, int(args.width), int(args.length)) # scaling the positional data; return new dataframe object in memory
    print()

    nucleusAxes = []
    if len(volumes) > 7:
        nucleusAxes = [int(volumes[7]), sx.transform([[volumes[8]]]).item(), sy.transform([[volumes[9]]]).item(), sz.transform([[volumes[10]]]).item(), sx.transform([[volumes[11]]]).item(), sy.transform([[volumes[12]]]).item(), sz.transform([[volumes[13]]]).item()]
    elif len(volumes) == 7:
        nucleusAxes = [int(volumes[0]), sx.transform([[volumes[1]]]).item(), sy.transform([[volumes[2]]]).item(), sz.transform([[volumes[3]]]).item(), sx.transform([[volumes[4]]]).item(), sy.transform([[volumes[5]]]).item(), sz.transform([[volumes[6]]]).item()]

    if args.filter != None: # ensuring this is inputed, else basic plot
        print(start + "Filtering SDD..." + end)
        newdf = draw.filter(newdf, args.filter) # applies filter to new dataframe object in memory
        print()
    pb = [] # instantiating empty variable incase labels not applied

    if args.coordinate != None: # ensuring this is inputed, else basic plot
        print(start + "Plotting against each frame..." + end)
        pb, newdf = draw.label(newdf, args.coordinate) # applies labels to the same dataframe in memory as filter
    
    if not os.path.isdir(args.save):
       os.mkdir(args.save)
    else:
       if len(list(os.listdir(args.save))) == 0:
          pass
       else:
          raise ValueError("Please empty output directory")

    folders = []
    for f in pb:
        if f not in os.listdir(args.save):
            os.mkdir(f"./{args.save}/{f}")
        folders.append(f"./{args.save}/{f}")
    os.mkdir(f"./{args.save}/unlabeled")

    with ppe(max_workers=int(args.workers)) as executor:
        indices = [i for i in range(1, 1201)]
        results = executor.map(plot, repeat(newdf), indices, repeat(pb), repeat(folders), repeat(f"./{args.save}/unlabeled"), repeat(nucleusAxes), repeat(args.size))

    print()
    print(start + "Creating videos from frames" + end)
    folders.append(f"./{args.save}/unlabeled")
    os.mkdir(os.path.join(args.save, "videos"))
    for f in tqdm(folders):
       createVideo(f, os.path.join(args.save, "videos"), f"{f}.avi", int(args.fps))
