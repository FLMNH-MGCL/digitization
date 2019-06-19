import os
import re
import csv
import pandas as pd
import numpy as np

def WriteCSV(old_new_names):
    df = pd.DataFrame.from_dict(list(old_new_names.items()))
    df.columns = ['Old name', 'New name']
    df.to_csv('changed_filenames.csv', index=False, encoding='utf-8')


def GetDirs(path):
    dirs = []
    for folder in os.listdir(path):
        if os.path.isdir(path + folder):
            dirs.append()
    return dirs


def NewName(old_name):
    # remove male/female distinction
    new_name = old_name
    new_name = new_name.replace("_M", "")
    new_name = new_name.replace("_F", "")

    # substitute repeating underscores with single underscore
    new_name = re.sub("\_+", "_", new_name)
    return new_name


def CountDigits(string):
	return sum(c.isdigit() for c in string)


def main():
    # get directory containing genus folders    
    parent_path = input('\nPlease input the path to the directory that contains the Genus folders: ')
    genuses = GetDirs(parent_path)
    old_new_names = dict()

    for genus in genuses:
        species = GetDirs(parent_path + genus)
        for spec in species:
            collection = GetDirs(parent_path + genus + '/' + spec)
            visited = dict()
            duplicates = []
            for img in collection:
                # parse and rename image name
                new_name = NewName(img.split('.')[0])
                print(new_name)

                # check digits for error
                num = CountDigits(new_name)
                if num != 7:
                    # mark as DIGERROR
                    new_name += 'DIGERROR'

                # extract file name w/o extension
                ext = img.split('.')[1]

                # 'visit' the picture id and check for duplicate
                id = new_name.split('_')[1]
                if id in visited.keys():
                    if visited[id] == 2:
                        duplicates.append(new_name + ext)
                    else:
                        visited[id] += 1
                else:
                    visited[id] = 0

                # rename photo
                working_path = parent_path + genus + '/' + spec + '/' + collection + '/'
                os.rename(working_path + img, working_path + (new_name + ext))

                # store old vs new filename pairs
                old_new_names[str(img)] = str(new_name + ext)

            # store duplicate paths somewhere

    # write old vs new filename pairs to CSV file
    for x in old_new_names:
        print(x)
        for y in old_new_names[x]:
            print(y, ':', old_new_names[x][y])
    #WriteCSV(old_new_names)


# Driver
if __name__ == '__main__':
    main()
