# Scripts for the FLMNH

This repository serves as a collection of scripts, library classes, and other projects developed to help improve the digitization workflow at the Florida Museum of Natural History at UF.

## Installing Dependencies:

```sh
$ pip3 install --user -r requirements.txt
```

## Scripts

There is a selection of scripts available in the [`scripts`](https://github.com/FLMNH-MGCL/digitization/tree/main/scripts) directory. They all have unique CLI structures, so be sure to run whichever is needed with the `--help` flag to get started. The below table provides a brief overview for each script:

| Script               | Description                                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------------------------- |
| `dynaiello.py`       | A version of the Aiello script with less column restrictions. Copy and rename entries based on a CSV file. |
| `gene_copy.py`       | Removes divergent consensus sequences (IBA pipeline) from .fas/.fasta files                                |
| `gene_parser.py`     | Parses .fa/.fasta files to extract accession numbers and gene names                                        |
| `mgcl_tracker.py`    | Tracks the used catalog numbers in the filesystem against a range/csv of numbers                           |
| `protein_combine.py` | Combines separated protein/nucleotide files into one combined file                                         |
| `relocate.py`        | _(deprecated)_ Relocates 'troublesome' images based on the log output of other scripts                     |
| `suspect_numbers.py` | Agreggates 'suspect' catalog numbers in a filesystem                                                       |
| `unique_values.py`   | Outputs all the unique values in the columns of a CSV or XLSX file                                         |
| `wls.py`             | _(deprecated)_ Generates CSV of specimen at current working directory                                      |
| `wrangler.py`        | Assigns BOMBID numbers to collection specimen                                                              |

## Digitization Program

Although a little dated, a few major workflow tasks for were implemented as libraries used by the wrapper [`digitization.py`](https://github.com/FLMNH-MGCL/digitization/blob/main/digitization.py) file.

### Usage:

A text-based list of programs to load will show on launch. Each program has a unique help prompt once loaded that will be available once selected.

### Programs

This is not an exhaustive list:

| Name                  | Description                                                                                                                                                                                                                                                                                                                                                                                    | Example(s)                                       |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| <b>Rename</b>         | Replaces the existing bash scripts previously for renaming images that have been named via the physical barcode scanner:                                                                                                                                                                                                                                                                       | `MGCL 0123456 (2).CR2 --> MGCL 0123456_V.CR2`    |
| <b>Legacy Upgrade</b> | We have ran Legacy Upgrade on server data already, if you are a current volunteer you most likely do not need to run this script. Legacy Upgrade is to be used to upgrade data to the new standards.                                                                                                                                                                                           | `MGCL__0123456__V__M.CR2 --> MGCL_0123456_V.CR2` |
| <b>Aiello</b>         | This program is designed for a specific task, and should only be used accordingly. It will parse out a specifically formatted excel sheet to locate file references in the museum server and copy these files to another location with a different naming scheme to be used in a particular project.                                                                                           |                                                  |
| <b>Rescale</b>        | This will rescale images in a given directory (and subdirectories, if required by user) by a user provided proportion. This is to aid in the upload of images, as the hi-res images previously took up a large amount of space. This will allow for smaller file sizes without losing a noticeable amount of image quality.                                                                    |                                                  |
| <b>Zipper</b>         | This will analyze a directory (and subdirectories, if required by user) and determine how many 1GB zip archives should be created. This is to aid in the upload of images, as well. Important notes: this script only looks inside folders entitled LOW-RES at all levels. This is because only the downscaled images will be grouped together for upload, as a means of saving cloud storage. |                                                  |

### Other Projects

- [spesql](https://github.com/FLMNH-MGCL/spesql)
- [datamatrix-reader](https://github.com/FLMNH-MGCL/datamatrix-reader)
- [imageconverter](https://github.com/FLMNH-MGCL/imageconverter)
