# Scripts for the FLMNH
This repository serves as a collection of scripts developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF (e.g. batch file renaming / transcription, batch .cr2 to jpg file conversion and image rotation, and upgrading the legacy data to conform to the current filename formatting)

### LegacyUpgrade Usage:
```sh
$ cd FLMNH/src/
$ python3 LegacyUpgrade.py
```

### Old/Experimental Scripts:

Although these scripts are not quite ready for deployment, these scripts will require [Python3](https://www.python.org/downloads/release/python-373/) to run, as well as a few extra Python modules. We are in the process of creating a script to auto-install these dependencies for you, however, so the process will be as simple as: 

```sh
$ cd FLMNH/src/Old_OR_Experimental
$ pip3 install -r requirements.txt
$ python3 name_of_script.py
```

### Other Projects
More robust projects for the museum will be separated from this script collection repository and linked here!  
[DataMatrix-Reader](https://github.com/aaronleopold/DataMatrix-Reader)
