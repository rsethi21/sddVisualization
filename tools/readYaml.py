import yaml
from yaml import load

def readYaml(inputPath):
    with open(inputPath, "r") as file:
        dictionary = yaml.safe_load(file)
    
    return dictionary