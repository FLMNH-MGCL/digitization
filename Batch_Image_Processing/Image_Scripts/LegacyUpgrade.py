import os
import re
#import csv
#import pandas as pd
#import numpy as np

#def WriteCSV(old_new_names):
#    df = pd.DataFrame.from_dict(list(old_new_names.items()))
#    #df.columns = ['Old name', 'New name', 'third']
#    df.to_csv('changed_filenames.csv', index=False, encoding='utf-8')

def WriteCSV(old_new_names):
    f = open("test_csv.csv", "w+")
    f.write("Old filenames,New filenames\n")
    for old_name,new_name in old_new_names:
        f.write(old_name + ',' + new_name + '\n')


def GetDirs(path):
    dirs = []
    for folder in os.listdir(path):
        if os.path.isdir(path + folder):
            dirs.append(folder)
    return dirs


def GetPics(path):
    imgs = []
    for img in os.listdir(path):
        if os.path.isfile(path + img):
            imgs.append(img)
    return imgs


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
    
    # ask user where they would like to store the changed file names CSV file and what to save it as
    # filename = input('\nPlease privde the path (including the desired name) to save a CSV file of filename changes: ')
    
    # add trailing slash if not present
    if not parent_path.endswith('/'):
        parent_path += '/'

    genuses = GetDirs(parent_path)

    print (parent_path)
    old_new_names = list()

    for genus in genuses:
        print(genus)
        species_path = parent_path + genus + '/'
        species = GetDirs(species_path)
        for spec in species:
            print (spec)
            date_path = species_path + spec + '/'
            dates = GetDirs(date_path)
            for date in dates:
                collection_path = date_path + date + '/'
                collection = GetPics(collection_path)
                visited = dict()
                duplicates = []
                for img in collection:
                    # parse and rename image name
                    new_name = NewName(img.split('.')[0])

                    # check digits for error
                    num = CountDigits(new_name)
                    if num != 7:
                        # mark as DIGERROR
                        new_name += '_DIGERROR'

                    # extract file name w/o extension
                    ext = '.' + img.split('.')[1]

                    # 'visit' the picture id and check for duplicate
                    id = new_name.split('_')[1]
                    if id in visited.keys():
                        if visited[id] == 2:
                            duplicates.append(new_name + ext)
                        else:
                            visited[id] += 1
                    else:
                        visited[id] = 0

                    print("Old name: {0} New name: {1}".format(img, (new_name + ext)))

                    # rename photo
                    # working_path = collection_path
                    # os.rename(working_path + img, working_path + (new_name + ext)) UNCOMMENT WHEN TESTING COMPLETE

                    # store old vs new filename pairs
                    old_new_names.append(tuple((img, (new_name + ext))))

            # store duplicate paths somewhere

    # write old vs new filename pairs to CSV file
    WriteCSV(old_new_names)


# Driver
if __name__ == '__main__':
    main()
