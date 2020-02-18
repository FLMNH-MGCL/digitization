# Scripts for the FLMNH
This repository serves as a collection of scripts developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF.

### Installing Dependencies without Admin Privelage:
To install any dependencies of any of the scripts on a museum computer, you must only install them with user scope/privileges (I.e. the default is admin scope).

To do so, you will need the argument --user in any install commands. For example: ```pip3 install --user [package_name]```

### Rename Usage:
Rename.py replaces the Unix commands for renaming images that have been named via the physical barcode scanner (e.g. ```MGCL 0123456 (2).CR2 --> MGCL 0123456_V.CR2```)

```sh
$ cd FLMNH/scripts/Rename
$ python3 Rename.py
```

Rename.py is to be used as a temporary workflow optimization until the data matrix scanner software we are developing is completed.

### LegacyUpgrade Usage:
We have ran Legacy Upgrade on server data already, if you are a current volunteer you most likely do not need to run this script.
Legacy Upgrade is to be used to upgrade data to the new standards   

```MGCL__0123456__V__M.CR2 --> MGCL_0123456_V.CR2```

```sh
$ cd FLMNH/scripts/LegacyUpgrade
$ python3 LegacyUpgrade.py
```

It also will find errors and duplicates.

### Aiello Script
This script was designed for a specific task, and should only be used accordingly. It will parse out a specifically formatted excel sheet to locate file references in the museum server and copy these files to another location with a different naming scheme to be used in a particular project. 

```sh
$ cd FLMNH/scripts/Aiello
$ python3 Aiello.py
```

### Rescale Script
This will rescale images in a given directory (and subdirectories, if required by user) by a user provided proportion. This is to aid in the upload of images, as the hi-res images previously took up a large amount of space. This will allow for smaller file sizes without losing a noticeable amount of image quality. 

```sh
$ cd FLMNH/scripts/Rescale
$ python3 rescale.py
```


### Zipper Script
This will analyze a directory (and subdirectories, if required by user) and determine how many 1GB zip archives should be created. This is to aid in the upload of images, as well. Important notes: this script only looks inside folders entitled LOW-RES at all levels. This is because only the downscaled images will be grouped together for upload, as a means of saving cloud storage.

```sh
$ cd FLMNH/scripts/Zipper
$ python3 zipper.py
```


### Other Projects
[DataMatrix-Reader](https://github.com/FLMNH-MGCL/DataMatrix-Reader)  
[SpeSQL / Database-App](https://github.com/FLMNH-MGCL/Database-App)
