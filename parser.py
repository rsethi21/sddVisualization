import argparse
import pandas as pd
import csv
import os
from itertools import compress

parser = argparse.ArgumentParser(description='custom parser for sdd file')
parser.add_argument('-i', '--input', help='input path to sdd file', required=True)
parser.add_argument('-s', '--save', help='path to save parsed csv', required=False, default=None)

class SDDReport:

    originalColumnHeaders = ["class", "xyz", "chromosomeid", "chromosomepos", \
                              "cause", "damage", "breakspec", "sequence", \
                                "lesiontime", "particletype", "particleenergy", \
                                    "particletranslation", "particledirection", "particletime"]
    parsedColumnHeaders = []

    def __init__(self, sddPath, parsedPath):
        
        self.sdd = SDDReport.openNStore(sddPath)

    @classmethod
    def openNStore(cls, path, columns=None):
        
        skiprow = 0
        columnrow = list()

        file = open(path, "r")
        lines = file.readlines()
        for i, line in enumerate(lines):
            if "EndOfHeader" in line:
                skiprow = i+1
            elif "Data entries" in line:
                columnrow = line[line.index("Data entries")+len("Data entries")+2:-2].split(", ")
                columns = [True if item == "1" else False for item in columnrow]

        with open(path, "r") as file2:
            df = pd.read_csv(file2, sep=";", header = None, skiprows = skiprow)
            df.dropna(axis=1, how="all", inplace=True)
            if columns != None:
                columns = list(compress(cls.originalColumnHeaders, columns))
                df.columns = columns
        print(df)
        return df

if __name__ == '__main__':
    args = parser.parse_args()
    SDDReport.openNStore(args.input)

