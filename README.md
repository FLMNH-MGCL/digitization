# Scripts for the FLMNH
This reposity serves as a collection of scripts developed to help improve the workflow for some of the post processesing tasks of the digitization group here at the Florida Museum of Natural History at UF (e.g. batch file renaming / transcription, batch .cr2 to jpg file conversion and image rotation, and upgrading the legacy data to conform to the current filename formatting)

### Installation

Although they are not quite ready for deployment, these scripts will require [Python3](https://www.python.org/downloads/release/python-373/) to run, as well as a few extra Python modules. We are in the process of creating a script to auto-install these dependencies for you, however, so the process will be as simple as: 

```sh
$ cd FLMNH/Batch_Image_Processing/Image_Scripts/
$ pip install -r requirements.txt
$ pyhton name_of_script.py
```
