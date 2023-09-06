import warnings
import argparse
import draw
import os

# parser arguments to allow for customized drawing
parseIt = argparse.ArgumentParser() # create argument parser object
parseIt.add_argument('-i', '--input', help='path to ssd file', required=True) # input path to sdd
parseIt.add_argument('-w', '--width', help='width of output image', required=False, default=10) # width of frame defaults to 10
parseIt.add_argument('-l', '--length', help='length of output image', required=False, default=10) # length of frame defaults to 10
parseIt.add_argument('-f', '--filter', help='yaml file with filter configurations', required=False, default=None) # filter.yaml path to help filter the dataset
parseIt.add_argument('-c', '--coordinate', help='yaml file with labelling configurations', required=False, default=None) # coordinate.yaml to help plot the data with color coordination
parseIt.add_argument('-s', '--save', help='output folder path', required=False, default='.') # output folder path for png files
parseIt.add_argument('--size', help='boolean flag to allow for size modulation of damage centroids', required=False, default=False, action=argparse.BooleanOptionalAction)


if __name__ == '__main__': # if script run directly

  warnings.filterwarnings("ignore")

  args = parseIt.parse_args() # creating an args object to extract user input

  if not os.path.isdir(args.save):
      os.mkdir(args.save)
  else:
      if len(os.listdir(args.save)) == 0:
        pass
      else:
        raise ValueError("Please empty desired output directory")

  start = "\033[1;3m"
  end = "\033[0m"
  print(start + "Extracting SDD Information..." + end)
  df, volumes, obj = draw.openSSD(args.input, outpath=args.save) # original unprocessed dataframe; remains untouched
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
  outfiles = {}

  if args.coordinate != None: # ensuring this is inputed, else basic plot
    print(start + "Applying labels to SDD..." + end)
    pb, newdf = draw.label(newdf, args.coordinate) # applies labels to the same dataframe in memory as filter
  draw.graph(newdf, pb, args.save, nucleusAxes, args.size) # create and save plots
  print(start + "Graphing Successful!" + end)
