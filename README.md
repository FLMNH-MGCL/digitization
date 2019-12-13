# Scripts for the FLMNH
This repository serves as a collection of scripts developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF.

### Installing Dependencies without Admin Privelage:
https://docs.google.com/document/d/1cK4l-3mDBV_ln4ZRwAdSnh5nq-eYyI0gnzdLB0itrqA/edit

### Rename Usage:
Rename.py replaces the Unix commands for renaming images that have been named via barcode i.e. "MGCL 0123456 (2)" --> "MGCL 0123456_V"

Rename.py is to be used as a temporary workflow optimization until the dependencies for data-matrix renaming are met, when dmtxread is installed, we will link it here and move rename to Old/Experimental scripts.

```sh
$ cd FLMNH/scripts/
$ python3 Rename.py
```

### LegacyUpgrade Usage:
We have ran Legacy Upgrade on server data already, if you are a current volunteer you most likely do not need to run this script.
Legacy Upgrade is to be used to upgrade data to the new standards "MGCL__0123456__V__M" --> "MGCL_0123456_V". It also will find errors and duplicates.

```sh
$ cd FLMNH/scripts/
$ python3 LegacyUpgrade.py
```

### Aiello Script
This script was designed for a specific task, and should only be used accordingly. It will parse out a specifically formatted excel sheet to locate file references in the museum server and copy these files to another location with a different naming scheme to be used in a particular project. 

```sh
$ cd FLMNH/scripts/
$ python3 Aiello.py
```


### Other Projects
[DataMatrix-Reader](https://github.com/FLMNH-MGCL/DataMatrix-Reader)
[Database-App](https://github.com/FLMNH-MGCL/Database-App)
