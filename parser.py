import argparse
import pandas as pd
import csv
import os
from itertools import compress

parser = argparse.ArgumentParser(description='custom parser for sdd file')
parser.add_argument('-i', '--input', help='input path to sdd file', required=True)
parser.add_argument('-s', '--save', help='path to save parsed csv', required=False, default=None)
parser.add_argument('-c', '--columns', nargs='*', help='multiple columns headers must match that of', required=False, default=None)

class SDDReport:

    originalColumnHeaders = ["class", "xyz", "chromosomeid", "chromosomepos", \
                              "cause", "damage", "breakspec", "sequence", \
                                "lesiontime", "particletype", "particleenergy", \
                                    "particletranslation", "particledirection", "particletime"]
    parsedColumnHeaders = []

    def __init__(self, sddPath, column_headers):
        
        self.originalDF = SDDReport.openNStore(sddPath, column_headers)

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
    def openNStore(cls, path, columns):
        
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
            try:
                df.columns = columns
            except:
                print("Column headers not provided or of incorrect size. Defaulting to standard column names based on file...")
                print()    
                columns = list(compress(cls.originalColumnHeaders, columnrow))
                df.columns = columns

        return df
    
    def separateVals(self):
        return

if __name__ == '__main__':
    
    args = parser.parse_args()
    sdd = SDDReport(args.input, args.columns)
    print(sdd.originalDF)
