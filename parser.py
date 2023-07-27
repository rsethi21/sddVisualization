import argparse
import pandas as pd
import numpy as np
import csv
import os
from itertools import compress

parser = argparse.ArgumentParser(description='custom parser for sdd file')
parser.add_argument('-i', '--input', help='input path to sdd file', required=True)
parser.add_argument('-s', '--save', help='path to save csv', required=False, default='./output.csv')
parser.add_argument('-p', '--parse', help='whether to parse out values needed for visualization tool', default=True, action=argparse.BooleanOptionalAction)

class SDDReport:

    originalColumnHeaders = ["class", "xyz", "chromosomeid", "chromosomepos", \
                              "cause", "damage", "breakspec", "sequence", \
                                "lesiontime", "particletype", "particleenergy", \
                                    "particletranslation", "particledirection", "particletime"]
    dimensionsHeaders = ["xcenter", "ycenter", "zcenter", "xmax", "ymax", "zmax", "xmin", "ymin", "zmin"]
    chromosomeInfoHeaders = ["structure", "chromsomeNumber", "chromatidNumber", "arm"]
    damageInfoHeaders = ["numBases", "singleNumber", "dsbPresent"]

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

    def saveParsed(self, path, df1, *dfs):

        finaldf = df1
        for df in dfs:
            finaldf = finaldf.join(df)
        
        self.parsedDf = finaldf
        finaldf.to_csv(path)

        return finaldf

if __name__ == '__main__':
    
    args = parser.parse_args()
    sdd = SDDReport(args.input)
    
    if not args.parse:
        sdd.to_csv(args.save)

    else:
        dimensions = []
        for row in sdd.extractCol("xyz"):
            temp = []
            for l in SDDReport.splitBoth(row, type(0.0)):
                temp += l
            dimensions.append(temp)
        dimensions = pd.DataFrame(np.array(dimensions), columns=SDDReport.dimensionsHeaders)

        chromosomeInfo = []
        for row2 in sdd.extractCol("chromosomeid"):
            chromosomeInfo.append(SDDReport.splitCommas(row2, type(0)))
        chromosomeInfo = pd.DataFrame(np.array(chromosomeInfo), columns=SDDReport.chromosomeInfoHeaders)

        damageInfo = []
        for row3 in sdd.extractCol("damage"):
            damageInfo.append(SDDReport.splitCommas(row3, type(0)))
        damageInfo = pd.DataFrame(np.array(damageInfo), columns=SDDReport.damageInfoHeaders)

        parsedSdd = sdd.saveParsed(args.save, dimensions, chromosomeInfo, damageInfo)
        print(parsedSdd)