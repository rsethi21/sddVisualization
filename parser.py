# imports
import pandas as pd
import numpy as np
import csv
import os
from itertools import compress

class SDDReport:
    '''
    inputs: path to sdd file
    
    The goal of this object is to provide a set of custom tools to parse an sdd file.
    This also provides a default parser to generate an image of damage across the nucleus.
    The reason for making this an object is to be able to store the old sdd, parsed sdd, and organize functions.
    '''
    originalColumnHeaders = ["class", "xyz", "chromosomeid", "chromosomepos", \
                              "cause", "damage", "breakspec", "sequence", \
                                "lesiontime", "particletype", "particleenergy", \
                                    "particletranslation", "particledirection", "particletime"]
    dimensionsHeaders = ["xcenter", "ycenter", "zcenter", "xmax", "ymax", "zmax", "xmin", "ymin", "zmin"] # default column headers for sdd dimensions
    chromosomeInfoHeaders = ["structure", "chromsomeNumber", "chromatidNumber", "arm"] # default column headers for chromosome information
    damageInfoHeaders = ["numBases", "singleNumber", "dsbPresent"] # default column headers for damage information
    causeHeaders = ["identifier", "direct", "indirect"] # default column headers for damage causes
    
    def __init__(self, sddPath: str):
        
        self.originalDF = SDDReport.openNStore(sddPath)

    @classmethod
    def splitSlashes(cls, val: str, typ: any):
        '''
        inputs: requires a string that has slashes as a delimiter, and final type of the split values
        outputs: return a list of values after delimitation
        
        The goal of this function is to split the string and convert to desired output.  Class method since no need for instance specific changes.
        '''
        sep = " / " # common outer header for sdd file
        values = list(val.split(sep)) # list of separated values
        if type(values[0]) != typ: # below converting data into proper types
            if typ == type(0): # converting to int
                values = [int(value) for value in values]
            elif typ == type(""): # converting to str
                values = [str(value) for value in values]
            elif typ == type(0.0): # converting to float
                values = [float(value) for value in values]
            else: # unknown data type skip
                output = f"Unknown type for entry {val}. Defaulted to existing type: {type(val)}"
                print(output)
                print()
        
        return values
    
    @classmethod
    def splitCommas(cls, val: str, typ: any):
        '''
        inputs: requires a string that has commas as a delimiter, and final type of the split values
        outputs: return a list of values after delimitation
        
        The goal of this function is to split the string and convert to desired output. Class method since no need for instance specific changes.
        '''
        sep = ", " # common inner header for sdd file
        values = list(val.split(sep)) # list of separated values
        if type(values[0]) != typ: # below converting data into proper types
            if typ == type(0): # converting to int
                values = [int(value) for value in values]
            elif typ == type(""): # converting to str
                values = [str(value) for value in values]
            elif typ == type(0.0): # converting to float
                values = [float(value) for value in values]
            else: # unknown data type skip
                output = f"Unknown type for entry {val}. Defaulted to existing type: {type(val)}"
                print(output)
                print()
        
        return values

    @classmethod
    def splitBoth(cls, val: str, typ: any):
        '''
        inputs: requires a string that has slashes and then commas as a delimiter, and final type of the split values
        outputs: return a list of values after delimitation
        
        The goal of this function is split values that are delimited by slashes then commas which is common in an sdd file. Class method since no need for instance specific changes.
        '''
        lst = SDDReport.splitSlashes(val, type("")) # split outer first
        vals = []
        for v in lst:
            vals.append(SDDReport.splitCommas(v, typ)) # split inner second
        return vals

    @classmethod
    def openNStore(cls, path: str):
        '''
        inputs: path for sdd
        outputs: opened DF
        
        The goal of this function is to open an SDD and separate into its individuals columns unparsed and without header. Class method since no need for instance specific changes.
        '''
        skiprow = 0 # determining row at which the actual data starts
        columnrow = list() # boolean list for which columns are present in the SDD file

        file = open(path, "r") # opening file
        lines = file.readlines() # reading file lines as list

        for i, line in enumerate(lines): # iterating through list
            if "EndOfHeader" in line: # looking for end of header marker to determine where data rows begin
                skiprow = i+1 # assigning the index were data starts
            if "Data entries" in line: # looking for binary data list to determine which columns present
                columnrow = line[line.index("Data entries")+len("Data entries")+2:-2].split(", ") # finding string list with binary info. and spliting into list of ints
                columnrow = [True if item == "1" else False for item in columnrow] # converting 1, 0s to booleans
            if "Volumes" in line:
                try:
                    int(line[line.index("Volumes, ")+len("Volumes, ")+14])
                columnrow = line[line.index("Volumes, ")+len("Volumes, ")+2:-2].split(", ")

        with open(path, "r") as file2: # opening file again to read sdd
            df = pd.read_csv(file2, sep=";", header = None, skiprows = skiprow) # opening sdd as a DF with appropriate skipping
            df.dropna(axis=1, how="all", inplace=True) # remove columns with all NAs if any present (separator is a bit odd)

            columns = list(compress(cls.originalColumnHeaders, columnrow)) # applying boolean list to default column headers
            df.columns = columns # setting default column headers
        
        return df
    
    def extractCol(self, colName: str):
        '''
        inputs: colName as assigned in DF
        outputs: pandas series object with specified column
        
        The goal of this function is basic function to get column info. Instance method because specific parsed SDD
        '''
        return self.originalDF[colName]

    def parseVizInfo(self):
        '''
        inputs: none
        outputs: dataframes of dimensions, chromosomeInfo, damageInfo, cause
        
        The goal of this function is is to extract plotting specific information for visualization.
        '''
        # each try and except below is in case the column does not exist
        try:
            dimensions = [] # instantiating dimensions list
            for row in self.extractCol("xyz"): # iterating through rows of the coordinate columns
                temp = [] # temporary list to store values from each row
                for l in SDDReport.splitBoth(row, type(0.0)): # split values into floats
                    temp += l # extend temp list with values from row
                dimensions.append(temp) # append values from row
            length = len(dimensions[0]) # determine the number of columns (center, max, min)
            dimensions = pd.DataFrame(np.array(dimensions), columns=SDDReport.dimensionsHeaders[0:length]) # assign appropriate parsed column headers
        except ValueError:
            print("Either no positional information or missing extent of damage.")

        try:
            chromosomeInfo = [] # instantiating chromosomeInfo list
            for row2 in self.extractCol("chromosomeid"): # iterating through rows of the chromosomeID columns
                chromosomeInfo.append(SDDReport.splitCommas(row2, type(0))) # split values into ints
            chromosomeInfo = pd.DataFrame(np.array(chromosomeInfo), columns=SDDReport.chromosomeInfoHeaders) # assign appropriate parsed column headers
        except:
            print("There is no damage information column in this file. Skipping...")
            chromosomeInfo = None

        try:
            damageInfo = [] # instantiating damageInfo list
            for row3 in self.extractCol("damage"): # iterating through rows of the damageInfo columns
                damageInfo.append(SDDReport.splitCommas(row3, type(0))) # split values into ints
            damageInfo = pd.DataFrame(np.array(damageInfo), columns=SDDReport.damageInfoHeaders) # assign appropriate parsed column headers
        except:
            print("There is no damage information column in this file. Skipping...")
            damage = None

        try:
            cause = [] # instantiating cause list
            for row4 in self.extractCol("cause"): # iterating through rows of then cause columns
                cause.append(SDDReport.splitCommas(row4, type(0))) # split values into ints
            cause = pd.DataFrame(np.array(cause), columns=SDDReport.causeHeaders) # assign appropriate parsed column headers
        except:
            print("There is no cause information column in this file. Skipping...")
            cause = None

        return dimensions, chromosomeInfo, damageInfo, cause

    def saveParsed(self, df1: pd.DataFrame, *dfs: pd.DataFrame, path: str = None):
        '''
        inputs: single or and number of dataframes, path to output path (optional)
        outputs: final dataframe returned
        
        The goal of this function is to combine the parsed columns needed for the final visualization.
        '''
        finaldf = df1 # set the single dataframe
        for df in dfs: # iterating through each dataframe in the list
            finaldf = finaldf.join(df) # join the dataframe columns into one big dataframe
        
        self.parsedDf = finaldf # set parsedDF as an value of the object
        if path != None: # if path is None then does not save to a file otherwise saves to path
            finaldf.to_csv(path) # saves to path

        return finaldf
