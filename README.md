# sddVisualization

- This is a set of tools that allow for the visualization of DNA damage by radiation. This simulation requires an SDD file and optional configurations files (filtering and color coordinating).

## What is an SDD File?

- An SDD file is a standardized data file that stores information about DNA damage. This allows for a predictable data input and output for visualization.
- For an SDD file, Some fields are required and some are optional. These files also have a header with more information about what the files contain.
- For more information about SDD files, see this paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6407706/
- There is test data in the following website that documents SDD file format: https://standard-for-dna-damage.readthedocs.io/en/latest/index.html
    - This test data is provided in the ./data folder with a complete and minimal SDD example

## What is the goal for this tool?

- The purpose of this tool is to create 3D images of the DNA damage from radiation simulations in the SDD format
- The tool provides the flexibility, customization, and standardization allowing for ease of visualization

## What is needed to run this tool?

### Install Python (only do this once)
Go to python on google and install proper sdk for your machine

### Install Git (only do this once)
Go to git on google and install proper sdk for your machine

### Install PIP (only do this once)
```
python3 -m pip3 install --upgrade pip
```
### Clone this repository (only do this once)
```
git clone https://github.com/rsethi21/sddVisualization.git
```
move into this sddVisualization folder after installation is complete
### Virtual Environment

create venv: # only do this once
```
python3 -m pip3 install --user virtualenv
python3 -m venv [name of environment]
```
activate venv: # do this everytime you open a new shell session and want to run this tool
```
source [name of environment]/bin/activate # only in linux
[name of environment]\Scripts\activate.bat # only in windows
```
install packages: # only do this once
```
pip3 install -r requirements.txt
```

### Scripts

- Helper Scripts:
    - parser.py: opens the SDD file and creates an SDD object with the original SDD file and customized parsed SDD dataframes
    - normalize.py: takes columns of similar data and normalizes the data to the scale desired by a user
    - readYaml.py: opens yaml configuration files
    - draw.py: puts all the helper scripts together to read SDD file and yaml files to create images of the DNA damage
- User Script:
    - runImage.py: allows user to create images of damage based on desired labels
    - runVideo.py: create video of damage in which damage arises when listed in lesion time column; runs for maximum of 20 seconds

### Inputs for runImage.py

```python3 runImage.py [-h] -i INPUT [-w WIDTH] [-l LENGTH] [-f FILTER] [-c COORDINATE] [-s SAVE] [--size | --no-size]```
```
- options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to ssd file
  -w WIDTH, --width WIDTH
                        width of output image
  -l LENGTH, --length LENGTH
                        length of output image
  -f FILTER, --filter FILTER
                        yaml file with filter configurations
  -c COORDINATE, --coordinate COORDINATE
                        yaml file with labelling configurations
  -s SAVE, --save SAVE  output folder path
  --size  whether to modulate size of points by number of confirmed damages
```
### Outputs for runImage.py

- points representing center of damage extent
    - one unlabelled, unfiltered centers of DNA damage
    - labelled and/or filtered centers of DNA damage plotted (multiple images if multiple columns selected for labelling by user)
    - size of centers based upon the total number of damages (direct/indirect) if this information is present, otherwise a single size for all damage; this represent the extent of damage
- saves images to the desired directory specified under the save argument; if none supplied uses current directory, if does not exist it will be created, if not empty it will warn you and ask you to clear the folder

### Example for runImage.py

Make sure you are in the sddVisualization folder in order to run the script (you must have your own test data)
```python3 runImage.py -i ./data/completeSDDExample.csv -w 10 -l 10 -f ./data/filter.yaml -c ./data/label.yaml -s . --size```

### Inputs for runVideo.py

```python3 runVideo.py [-h] -i INPUT [-w WIDTH] [-l LENGTH] [-f FILTER] [-c COORDINATE] [-s SAVE] [-p WORKERS] [-t FPS] [--size | --no-size]```
```
- options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to ssd file
  -w WIDTH, --width WIDTH
                        width of output image
  -l LENGTH, --length LENGTH
                        length of output image
  -f FILTER, --filter FILTER
                        yaml file with filter configurations
  -c COORDINATE, --coordinate COORDINATE
                        yaml file with labelling configurations
  -s SAVE, --save SAVE
                        output folder path
  -p WORKERS, --workers
                        processing needed to create the frames for video
  -t FPS, --fps
                        frames per second for video speed; max is 60 will automatically default to this if greater than this
  --size  whether to modulate size of points by number of confirmed damages
```
### Outputs for runVideo.py

- points representing center of damage extent
    - one unlabelled, unfiltered centers of DNA damage
    - labelled and/or filtered centers of DNA damage plotted (multiple images if multiple columns selected for labelling by user)
    - size of centers based upon the total number of damages (direct/indirect) if this information is present, otherwise a single size for all damage; this represent the extent of damage
- saves images of frames and videos to the desired directory specified under the save argument; if none supplied uses current directory, if does not exist it will be created, if not empty it will warn you and ask you to clear the folder
    - within the directory folders are created with the associated label name where the frames are saved and a separate videos folder with the frames put together as a video for each label

### Example for runVideo.py

Make sure you are in the sddVisualization folder in order to run the script (you must have your own test data)
```python3 runVideo.py -i ./data/completeSDDExample.csv -w 10 -l 10 -f ./data/filter.yaml -c ./data/label.yaml -s . -p 1 -t 60 --size```

## What are filter/label.yaml files?

- These are extra user adjustable configuration files to filter and label the data as desired
- Information about each field of the yaml file commented within the file

## What are next steps?
- apply test/end cases for the tool
