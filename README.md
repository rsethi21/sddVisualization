# sddVisualization

- This is a set of tools that allow for the visualization of DNA damage by radiation. This simulation requires an SDD file and optional configurations files (filtering and color coordinating).

## What is an SDD File?

- An SDD file is a standardized data file that stores information about DNA damage. This allows for a predictable data input and output for visualization.
- For an SDD file, Some fields are required and some are optional. These files also have a header with more information about what the files contain.
- For more information about SDD files, see this paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6407706/ 

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
move into this sddVisualization folder after installation complete
### Virtual Environment (only do this once)

create venv:
```
python3 -m pip3 install --user virtualenv
python3 -m venv [name of environment]
```
activate venv:
```
source [name of environment]/bin/activate # only in linux
[name of environment]\Scripts\activate.bat # only in windows
```
install packages:
```
pip3 install -r requirements.txt
```
Once installed, all you have to do is reactivate the environment after re-entering the command prompt/shell instance using the active venv command

### Scripts

- Helper Scripts:
    -  parser.py: opens the SDD file and creates an SDD object with the original SDD file and customized parsed SDD dataframes
    - normalize.py: takes columns of similar data and normalizes the data to the scale desired by a user
    - readYaml.py: opens yaml configuration files
- User Script:
    - draw.py: puts all the helper scripts together to read SDD file and yaml files to create images of the DNA damage

### Inputs for draw.py

```python3 draw.py [-h] -i INPUT [-w WIDTH] [-l LENGTH] [-f FILTER] [-c COORDINATE] [-s SAVE] [--points | --no-points]```

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
  --points, --no-points
                        plot as points rather than lines of the DNA extent

### Outputs for draw.py

- points
    - one unlabelled, unfiltered centers of DNA damage
    - labelled and/or filtered centers of DNA damage plotted (multiple images if multiple columns selected for labelling by user)
    - size of centers based upon the total number of damages (direct/indirect) if this information is present, otherwise a single size for all damage; this represent the extent of damage
- lines
    - one unlabelled, unfiltered lines between min and max coordinates of DNA damage
    - labelled and/or filtered lines between min and max coordinates of DNA damage plotted (multiple images if multiple columns selected for labelling by user)
    - extent of damage within DNA encoded by lengths of lines

### Example for draw.py

```python3 draw.py -i ./data/NucleusDNADamage-0.5_sdd.csv -w 10 -l 10 -f ./data/filter.yaml -c ./data/label.yaml -s . --points```

## What are filter/label.yaml files?

- These are extra user adjustable configuration files to filter and label the data as desired
- Information about each field of the yaml file commented within the file

## What are next steps?

- make the labelling and filtering available for all columns types (challenging in the sense that SDD files have many fields as optional and so much complex logic required)
    - breakspec is really the only one not yet used in this tool
    - lesion time is present but need an SDD example that has this field present
