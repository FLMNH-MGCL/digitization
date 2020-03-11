# Scripts for the FLMNH
This repository serves as a collection of library classes developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF.
<br/><br/>

### Installing Dependencies:
If you are on a unix-based operating system (i.e. Linux distributions or MacOS), then you
can use the install script provided.
```sh
$ ./install_requirements.sh
```
In addition to install the requirements, this will check that the correct python version is 
installed. If you are on windows, you will have to manually run the install command through pip, which will not include these extra checks.

```sh
$ pip3 install --user -r requirements.txt
```
<br/>

### Basic Usage:
I have removed the 'scripting' aspect of these programs. Initially, each script was a separate entity, however I have since converted all the scripts into a collection of classes to serve as a library for the wrapper program ```Digitization.py```. Now, you will only need to launch this file and select which program to run; there is no more need for running individual scripts manually. <br /><br />
Additionally, I have abstracted out some common functions between the programs into a Helper class as static functions. This reduces some redundancy in the code. I have also created a dedicated Logger class to keep track of each individual program's logging requirements.<br/><br/>

To start the program: 
```sh
$ ./install_requirements.sh (or the windows pip command)
$ python3 Digitization.py
```
<br/>

### Rename (Legacy):
Rename.py replaces the Unix commands for renaming images that have been named via the physical barcode scanner (e.g. ```MGCL 0123456 (2).CR2 --> MGCL 0123456_V.CR2```)

Rename.py is to be used as a temporary workflow optimization until the data matrix scanner software we are developing is completed.
<br/><br/>


### LegacyUpgrade (Legacy):
We have ran Legacy Upgrade on server data already, if you are a current volunteer you most likely do not need to run this script.
Legacy Upgrade is to be used to upgrade data to the new standards   

```MGCL__0123456__V__M.CR2 --> MGCL_0123456_V.CR2```

It also will find errors and duplicates.
<br/><br/>

### Aiello Project
This program is designed for a specific task, and should only be used accordingly. It will parse out a specifically formatted excel sheet to locate file references in the museum server and copy these files to another location with a different naming scheme to be used in a particular project. 
<br/><br/>


### Rescale Script
This will rescale images in a given directory (and subdirectories, if required by user) by a user provided proportion. This is to aid in the upload of images, as the hi-res images previously took up a large amount of space. This will allow for smaller file sizes without losing a noticeable amount of image quality. 
<br/><br/>


### Zipper Script
This will analyze a directory (and subdirectories, if required by user) and determine how many 1GB zip archives should be created. This is to aid in the upload of images, as well. Important notes: this script only looks inside folders entitled LOW-RES at all levels. This is because only the downscaled images will be grouped together for upload, as a means of saving cloud storage.
<br/><br/>


### Other Projects
[DataMatrix-Reader](https://github.com/FLMNH-MGCL/DataMatrix-Reader)  
[SpeSQL / Database-App](https://github.com/FLMNH-MGCL/Database-App)
