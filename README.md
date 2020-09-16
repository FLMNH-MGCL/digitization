# Scripts for the FLMNH
This repository serves as a collection of library classes, scripts and other projects developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF.
<br/><br/>

### Installing Dependencies:
```sh
$ pip3 install --user -r requirements.txt
```
<br/>

### Usage:
Major tasks for the Digitization workflows are implemented as librareis to be used in ```digitization.py```. 

To see all options for starting the program: 
```sh
$ python3 digitization.py --help
```
This will display a help prompt containing information regarding all the arguments accepted by the program. By default, an empty argument list is accepted. In this case, you will be presented with a text-based menu to select a program to 'load' and run.

### Rename:
Rename.py replaces the Unix commands for renaming images that have been named via the physical barcode scanner 
```MGCL 0123456 (2).CR2 --> MGCL 0123456_V.CR2```

Rename.py is to be used as a temporary workflow optimization until the data matrix scanner software we are developing is completed. 
<br/><br/>


### LegacyUpgrade:
We have ran Legacy Upgrade on server data already, if you are a current volunteer you most likely do not need to run this script.
Legacy Upgrade is to be used to upgrade data to the new standards.

```MGCL__0123456__V__M.CR2 --> MGCL_0123456_V.CR2```

It also will find errors and duplicates.
<br/><br/>

### Aiello
This program is designed for a specific task, and should only be used accordingly. It will parse out a specifically formatted excel sheet to locate file references in the museum server and copy these files to another location with a different naming scheme to be used in a particular project. 
<br/><br/>


### Rescale
This will rescale images in a given directory (and subdirectories, if required by user) by a user provided proportion. This is to aid in the upload of images, as the hi-res images previously took up a large amount of space. This will allow for smaller file sizes without losing a noticeable amount of image quality. 
<br/><br/>


### Zipper
This will analyze a directory (and subdirectories, if required by user) and determine how many 1GB zip archives should be created. This is to aid in the upload of images, as well. Important notes: this script only looks inside folders entitled LOW-RES at all levels. This is because only the downscaled images will be grouped together for upload, as a means of saving cloud storage.
<br/><br/>


### Other Projects
[DataMatrix-Reader](https://github.com/FLMNH-MGCL/DataMatrix-Reader)  
[SpeSQL / Database-App](https://github.com/FLMNH-MGCL/Database-App)
