# Scripts for the FLMNH
This repository serves as a collection of scripts developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF (e.g. batch file renaming / transcription, batch .cr2 to jpg file conversion and image rotation, and upgrading the legacy data to conform to the current filename formatting)

### Installing Dependencies without Admin Privelage:
https://docs.google.com/document/d/1cK4l-3mDBV_ln4ZRwAdSnh5nq-eYyI0gnzdLB0itrqA/edit

### Rename Usage:
Rename.py replaces the Unix commands for renaming images that have been named via barcode i.e. "MGCL 0123456 (2)" --> "MGCL 0123456_V"

Rename.py is to be used as a temporary workflow optimization until the dependencies for data-matrix renaming are met, when dmtxread is installed, we will link it here and move rename to Old/Experimental scripts.

```sh
$ cd FLMNH/src/
$ python3 Rename.py
```

### Legacy_Upgrade Usage:
We have ran Legacy Upgrade on server data already, if you are a current volunteer you most likely do not need to run this script.
Legacy Upgrade is to be used to upgrade data to the new standards "MGCL__0123456__V__M" --> "MGCL_0123456_V". It also will find errors and duplicates.

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

Below is the link to the DataMatrix-Reader, the python version is pretty much complete.
We are waiting on dependencies to be installed on the Macs. 
[DataMatrix-Reader](https://github.com/aaronleopold/DataMatrix-Reader)
