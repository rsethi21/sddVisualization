# imports
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
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
    breakSpecsHeaders = ["strand", "base", "identifier"] # default column headers for damage causes

    def __init__(self, sddPath: str):
        
        self.originalDF, self.volumes, self.damages = SDDReport.openNStore(sddPath)

    @classmethod
    def splitAny(cls, val: str, typ: any, sep: str):
        values = list(val.split(sep)) # list of separated values
        if len(values) != 0: # below converting data into proper types
            values = [value for value in values if value not in [" ", ""]]
            if type(values[0]) != typ:
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
        else:
            return None

    @classmethod
    def splitBoth(cls, val: str, typ: any, firstSplit = '/', secondSplit = ','):
        '''
        inputs: requires a string that has slashes and then commas as a delimiter, and final type of the split values
        outputs: return a list of values after delimitation
        
        The goal of this function is split values that are delimited by slashes then commas which is common in an sdd file. Class method since no need for instance specific changes.
        '''
        lst = SDDReport.splitAny(val, type(""), firstSplit) # split outer first
        vals = []
        for v in lst:
            vals.append(SDDReport.splitAny(v, typ, secondSplit))
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
        volumerow = list()

        file = open(path, "r") # opening file
        lines = file.readlines() # reading file lines as list

        tempfile = open("./temp.csv", "w")

        newLines = []
        for line in lines:
            if not line.isspace():
                newLines.append(line)
                tempfile.write(line)

        # add try except for space delimitation
        for i, line in enumerate(newLines): # iterating through list
            if "EndOfHeader" in line: # looking for end of header marker to determine where data rows begin
                skiprow = i+1 # assigning the index were data starts
            if "Data entries" in line: # looking for binary data list to determine which columns present
                columnrow = line[line.index("Data entries, ")+len("Data entries, "):-2].split(",") # finding string list with binary info. and spliting into list of ints
                columnrow = [True if int(item) == 1 else False for item in columnrow] # converting 1, 0s to booleans
            if "Volumes" in line:
                volumerow = line[line.index("Volumes, ")+len("Volumes, "):-2].split(",")
                volumerow = [float(item) for item in volumerow]
            if "Damage definition" in line:
                damage = line[line.index("Damage definition, ")+len("Damage definition, "):-2].split(",")
                damage = [str(item) for item in damage]


        with open("./temp.csv", "r") as file2: # opening file again to read sdd
            df = pd.read_csv(file2, sep=";", header = None, skiprows = skiprow) # opening sdd as a DF with appropriate skipping
            df.dropna(axis=1, how="all", inplace=True) # remove columns with all NAs if any present (separator is a bit odd)

            columns = list(compress(cls.originalColumnHeaders, columnrow)) # applying boolean list to default column headers
            df.columns = columns # setting default column headers

        os.remove("./temp.csv")

        return df, volumerow, damage
    
    def extractCol(self, colName: str):
        return self.originalDF[colName]

    def parseVizInfo(self, damagerow):
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
                if '/' in row:
                    try:
                        for l in SDDReport.splitBoth(str(row), type(0.0), secondSplit=','): # split values into floats
                            temp += l # extend temp list with values from row
                        dimensions.append(temp) # append values from row
                    except:
                        for l in SDDReport.splitBoth(str(row), type(0.0), secondSplit=' '): # split values into floats
                            temp += l # extend temp list with values from row
                        dimensions.append(temp) # append values from row
                else:
                    try:
                        temp = SDDReport.splitAny(str(row), type(0.0), ",") # split values into floats
                    except:
                        temp = SDDReport.splitAny(str(row), type(0.0), " ") # split values into floats
                    dimensions.append(temp) # append values from row
            length = len(dimensions[0]) # determine the number of columns (center, max, min)
            dimensions = pd.DataFrame(np.array(dimensions), columns=SDDReport.dimensionsHeaders[0:length]) # assign appropriate parsed column headers
        except ValueError:
            print("Either no positional information or missing extent of damage.")

        try:
            chromosomeInfo = [] # instantiating chromosomeInfo list
            for row2 in self.extractCol("chromosomeid"): # iterating through rows of the chromosomeID columns
                try:
                    chromosomeInfo.append(SDDReport.splitAny(str(row2), type(0), ",")) # split values into ints
                except:
                    chromosomeInfo.append(SDDReport.splitAny(str(row2), type(0), " ")) # split values into ints
            chromosomeInfo = pd.DataFrame(np.array(chromosomeInfo), columns=SDDReport.chromosomeInfoHeaders) # assign appropriate parsed column headers
        except:
            print("There is no chromosome information column in this file. Skipping...")
            chromosomeInfo = pd.DataFrame()

        try:
            breakSpecs = [] # instantiating damageInfo list
            for row5 in self.extractCol("breakspec"): # iterating through rows of the damageInfo columns
                indirect = 0
                direct = 0
                indirectNDirect = 0
                present = -1

                try:
                    temp = SDDReport.splitBoth(str(row5), type(0), secondSplit=' ') # split values into ints
                except:
                    temp = SDDReport.splitBoth(str(row5), type(0)) # split values into ints
                try:
                    temp.remove(None)
                except:
                    pass

                tempDF = pd.DataFrame(np.array(temp), columns=SDDReport.breakSpecsHeaders)

                singleNumber = len(tempDF[((tempDF["strand"] == 1) | (tempDF["strand"] == 4)) & (tempDF["identifier"] != 0)]["strand"])
                baseNumber = len(tempDF[((tempDF["strand"] == 2) | (tempDF["strand"] == 3)) & (tempDF["identifier"] != 0)]["base"])
                
                if len(tempDF["identifier"].unique()) == 1:
                    identifier = tempDF["identifier"].unique()[0]
                    if identifier == 1:
                        direct += 1
                    if identifier == 2:
                        indirect += 1
                    if identifier == 3:
                        indirectNDirect += 1
                elif 1 in tempDF["identifier"].unique() and 2 in tempDF["identifier"].unique():
                    identifier = 3
                    direct += len(tempDF[tempDF["identifier"] == 1])
                    indirect += len(tempDF[tempDF["identifier"] == 2])
                    indirectNDirect += len(tempDF[tempDF["identifier"] == 3])
                else:
                    identifier = max(tempDF["identifier"].unique())
                    direct += len(tempDF[tempDF["identifier"] == 1])
                    indirect += len(tempDF[tempDF["identifier"] == 2])
                    indirectNDirect += len(tempDF[tempDF["identifier"] == 3])

                if damagerow != None and int(damagerow[1]) == 0:
                    bps = float(damagerow[2])
                    strand1 = list(tempDF[(tempDF["strand"] == 1) & (tempDF["identifier"] != 0)]["base"])
                    strand4 = list(tempDF[(tempDF["strand"] == 4) & (tempDF["identifier"] != 0)]["base"])
                    distances = []
                    for base in strand1:
                        differences = np.array(strand4) - base
                        distances.extend(differences)

                    if len(distances) != 0:
                        if min(distances) <= bps:
                            present = 1
                        else:
                            present = 0

                else:
                    pass

                breakSpecs.append([baseNumber, singleNumber, identifier, direct, indirect, indirectNDirect, present])
            breakSpecs = pd.DataFrame(np.array(breakSpecs), columns=["numBases", "singleNumber", "identifier", "direct", "indirect", "directNIndirect", "dsbPresent"])
            if sum(breakSpecs["dsbPresent"] < 0):
                breakSpecs.drop(columns=["dsbPresent"], inplace=True)
        except:
            print("There is no break specification information column in this file. Skipping...")
            breakSpecs = pd.DataFrame()

        try:
            if len(list(breakSpecs.columns)) == 0:
                damageInfo = [] # instantiating damageInfo list
                for row3 in self.extractCol("damage"): # iterating through rows of the damageInfo columns
                    try:
                        damageInfo.append(SDDReport.splitAny(str(row3), type(0), ",")) # split values into ints
                    except:
                        damageInfo.append(SDDReport.splitAny(str(row3), type(0), " ")) # split values into ints
                length = len(damageInfo[0])
                damageInfo = pd.DataFrame(np.array(damageInfo), columns=SDDReport.damageInfoHeaders[0:length]) # assign appropriate parsed column headers
            else:
                damageInfo = [] # instantiating damageInfo list
                for row3 in self.extractCol("damage"): # iterating through rows of the damageInfo columns
                    try:
                        damageInfo.append(SDDReport.splitAny(str(row3), type(0), ",")) # split values into ints
                    except:
                        damageInfo.append(SDDReport.splitAny(str(row3), type(0), " ")) # split values into ints
                length = len(damageInfo[0])
                damageInfo = pd.DataFrame(np.array(damageInfo), columns=SDDReport.damageInfoHeaders[0:length]) # assign appropriate parsed column headers
                damageInfo = pd.DataFrame(damageInfo["dsbPresent"])
                if "dsbPresent" in list(breakSpecs.columns):
                    breakSpecs.drop(columns=["dsbPresent"], inplace=True)
        except:
            print("There is no damage information column in this file. Skipping...")
            damageInfo = pd.DataFrame()
            
        try:
            cause = [] # instantiating cause list
            for row4 in self.extractCol("cause"): # iterating through rows of then cause columns
                try:
                    cause.append(SDDReport.splitAny(str(row4), type(0), ",")) # split values into ints
                except:
                    cause.append(SDDReport.splitAny(str(row4), type(0), " ")) # split values into ints
            length = len(cause[0])
            if length == 1:
                cause = pd.DataFrame(np.array(cause), columns=["cause"])
            else:
                cause = pd.DataFrame(np.array(cause), columns=SDDReport.causeHeaders[0:length]) # assign appropriate parsed column headers
            if "identifier" in list(breakSpecs.columns) and "identifier" in list(cause.columns):
                cause.drop(columns=["identifier"], inplace = True)
            elif "identifier" not in list(breakSpecs.columns) and "identifier" in list(cause.columns):
                cause["identifier"] = cause["identifier"] + 1
            if "direct" in breakSpecs.columns:
                cause.drop(columns=["direct"], inplace=True)
            if "indirect" in breakSpecs.columns:
                cause.drop(columns=["indirect"], inplace=True)
        except:
            print("There is no cause information column in this file. Skipping...")
            cause = pd.DataFrame()

        # add lesion time parsing
        try:
            times = []
            for row6 in self.extractCol("lesiontime"):
                times.append(float(float(row6)))
            scaler = MinMaxScaler(feature_range=(1, 1200))
            scaledtimes = scaler.fit_transform(pd.DataFrame(np.array(times), columns=["lesiontimes"]))
            times = pd.DataFrame(scaledtimes, columns=["lesiontimes"])
            self.timescaler = scaler
        except:
            print("There is no cause information column in this file. Skipping...")
            times = pd.DataFrame()

        return dimensions, chromosomeInfo, damageInfo, cause, breakSpecs, times

    def saveParsed(self, df1: pd.DataFrame, *dfs: pd.DataFrame, path: str = None):
        '''
        inputs: single or and number of dataframes, path to output path (optional)
        outputs: final dataframe returned
        
        The goal of this function is to combine the parsed columns needed for the final visualization.
        '''

        finaldf = df1 # set the single dataframe

        for df in dfs: # iterating through each dataframe in the list
            finaldf = finaldf.join(df) # join the dataframe columns into one big dataframe

        if "numBases" and "singleNumber" in finaldf.columns:
            finaldf["totalDamages"] = finaldf["numBases"] + finaldf["singleNumber"]

        self.parsedDf = finaldf # set parsedDF as an value of the object
        if path != None: # if path is None then does not save to a file otherwise saves to path
            finaldf.to_csv(path) # saves to path

        return finaldf
