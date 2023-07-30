# imports
import yaml

def readYaml(inputPath: str):
    '''
    inputs: path to yaml file
    outputs: output dictionary of the values in the yaml file
    
    The goal of this function is to open yaml configuration files for scripts.
    '''
    with open(inputPath, "r") as file: # open file
        dictionary = yaml.safe_load(file) # load yaml as a dictionary
    
    return dictionary