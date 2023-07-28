import pandas as pd
import numpy as np
import csv
import os
from itertools import compress

class SDDReport:

    originalColumnHeaders = ["class", "xyz", "chromosomeid", "chromosomepos", \
                              "cause", "damage", "breakspec", "sequence", \
                                "lesiontime", "particletype", "particleenergy", \
                                    "particletranslation", "particledirection", "particletime"]
    dimensionsHeaders = ["xcenter", "ycenter", "zcenter", "xmax", "ymax", "zmax", "xmin", "ymin", "zmin"]
    chromosomeInfoHeaders = ["structure", "chromsomeNumber", "chromatidNumber", "arm"]
    damageInfoHeaders = ["numBases", "singleNumber", "dsbPresent"]
    causeHeaders = ["identifier", "direct", "indirect"]

    def __init__(self, sddPath):
        
        self.originalDF = SDDReport.openNStore(sddPath)

    @classmethod
    def splitSlashes(cls, val, typ):

        sep = " / "
        values = list(val.split(sep))
        if type(values[0]) != typ:
            if typ == type(0):
                values = [int(value) for value in values]
            elif typ == type(""):
                values = [str(value) for value in values]
            elif typ == type(0.0):
                values = [float(value) for value in values]
            else:
                output = f"Unknown type for entry {val}. Defaulted to existing type: {type(val)}"
                print(output)
                print()
        
        return values
    
    @classmethod
    def splitCommas(cls, val, typ):
        
        sep = ", "
        values = list(val.split(sep))
        if type(values[0]) != typ:
            if typ == type(0):
                values = [int(value) for value in values]
            elif typ == type(""):
                values = [str(value) for value in values]
            elif typ == type(0.0):
                values = [float(value) for value in values]
            else:
                output = f"Unknown type for entry {val}. Defaulted to existing type: {type(val)}"
                print(output)
                print()
        
        return values

    @classmethod
    def splitBoth(cls, val, typ):
        
        lst = SDDReport.splitSlashes(val, type(""))
        vals = []
        for v in lst:
            vals.append(SDDReport.splitCommas(v, typ))
        return vals

    @classmethod
    def openNStore(cls, path):
        
        skiprow = 0
        columnrow = list()

        file = open(path, "r")
        lines = file.readlines()

        for i, line in enumerate(lines):
            if "EndOfHeader" in line:
                skiprow = i+1
            if "Data entries" in line:
                columnrow = line[line.index("Data entries")+len("Data entries")+2:-2].split(", ")
                columnrow = [True if item == "1" else False for item in columnrow]

        with open(path, "r") as file2:
            df = pd.read_csv(file2, sep=";", header = None, skiprows = skiprow)
            df.dropna(axis=1, how="all", inplace=True)

            columns = list(compress(cls.originalColumnHeaders, columnrow))
            df.columns = columns
        
        return df
    
    def extractCol(self, colName):

        return self.originalDF[colName]

    def parseVizInfo(self):

        try:
            dimensions = []
            for row in self.extractCol("xyz"):
                temp = []
                for l in SDDReport.splitBoth(row, type(0.0)):
                    temp += l
                dimensions.append(temp)
            length = len(dimensions[0])
            dimensions = pd.DataFrame(np.array(dimensions), columns=SDDReport.dimensionsHeaders[0:length])
        except ValueError:
            print("Either no positional information or missing extent of damage.")

        try:
            chromosomeInfo = []
            for row2 in self.extractCol("chromosomeid"):
                chromosomeInfo.append(SDDReport.splitCommas(row2, type(0)))
            chromosomeInfo = pd.DataFrame(np.array(chromosomeInfo), columns=SDDReport.chromosomeInfoHeaders)
        except:
            print("There is no damage information column in this file. Skipping...")
            chromosomeInfo = None

        try:
            damageInfo = []
            for row3 in self.extractCol("damage"):
                damageInfo.append(SDDReport.splitCommas(row3, type(0)))
            damageInfo = pd.DataFrame(np.array(damageInfo), columns=SDDReport.damageInfoHeaders)
        except:
            print("There is no damage information column in this file. Skipping...")
            damage = None

        try:
            cause = []
            for row4 in self.extractCol("cause"):
                cause.append(SDDReport.splitCommas(row4, type(0)))
            cause = pd.DataFrame(np.array(cause), columns=SDDReport.causeHeaders)
        except:
            print("There is no cause information column in this file. Skipping...")
            cause = None

        return dimensions, chromosomeInfo, damageInfo, cause

    def saveParsed(self, df1, *dfs, path = None):

        finaldf = df1
        for df in dfs:
            finaldf = finaldf.join(df)
        
        self.parsedDf = finaldf
        if path != None:
            finaldf.to_csv(path)

        return finaldf
