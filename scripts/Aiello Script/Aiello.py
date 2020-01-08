import os
import pandas as pd
from shutil import copyfile
import time

old_new_paths = []
mgcl_nums = dict()
destination = ''
error_log = []

def AskUsage():
    prompt = str(
            "" \
            ""
        )
    wanted = input("\nDo you want to see the usage information?\n [1]yes\n [2]no\n --> ")
    if wanted == '1' or wanted == 'y' or wanted == 'yes':
        print(prompt)
        time.sleep(5)


def DirPrompt():
    parent_directory = input('\nPlease input the path to the directory that contains the images: ')
    parent_directory = parent_directory.strip()

    if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
        parent_directory += '/'

    while not os.path.exists(parent_directory) or not os.path.isdir(parent_directory):
        print("\nCould not find path in filesystem or is not a directory...")
        parent_directory = input('\nPlease input the path to the directory that contains the images: ')
        parent_directory = parent_directory.strip()

        if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
            parent_directory += '/'

    return parent_directory


def DestinationDirPrompt():
    destination = input('\nPlease input the path you would like the copies to go: ')
    destination = destination.strip()

    if not destination.endswith('/') or not destination.endswith('\\'):
        destination += '/'

    while not os.path.exists(destination) or not os.path.isdir(destination):
        print("\nCould not find path in filesystem or is not a directory...")
        destination = input('\nPlease input the path to the directory that contains the images: ')
        destination = destination.strip()

        if not destination.endswith('/') or not destination.endswith('\\'):
            destination += '/'

    return destination


def GetDirs(path):
    dirs = []
    for dir in sorted(os.listdir(path)):
        if os.path.isdir(path + dir):
            dirs.append(dir)
    return dirs

def GetNewName(old_name):
    # remove male / female distinction
    new_name = old_name
    new_name = new_name.replace("-", "_") # replace hyphens
    if not new_name.startswith("MGCL_") and new_name.startswith("MGCL"):
        new_name = new_name.replace("MGCL", "MGCL_")
    new_name = new_name.replace("_M", "")
    new_name = new_name.replace("_F", "")
    # new_name = new_name.replace("_C", "_CROPPED")

    # sub repeating underscores with single underscore
    new_name = re.sub("\_+", "_", new_name)

    return new_name


def Undo():
    valid_choice = False
    ret_str = ""
    while not valid_choice:
        choice = input("Do you want to:\n [1]undo ALL changes\n [2]leave errors and duplicates renamed?\n --> ")
        if choice == '1' or choice == 'all':
            valid_choice = True
            for old_path,new_path in old_new_paths:
                os.rename(new_path, old_path)

            ret_str = "All changes undone. Original state restored."

        elif choice == '2':
            valid_choice = True
            for old_path,new_path in old_new_paths:
                os.rename(new_path, old_path)

            ret_str = "Only valid images were reverted to original state. All others left as is."
        else:
            print("Invalid choice.")

    return ret_str


def Wait(path):
    time.sleep(5)

    wait = True
    print("Program completed... Please review changes.")

    # while wait == True:
    #     undo = input("Do you wish to undo?\n [1]yes\n [2]no\n --> ")
    #     if undo == '1' or undo == 'y' or undo =='yes':
    #         print(Undo())
    #         wait = False
    #     elif undo == '2' or undo == 'n' or undo == 'no':
    #         wait = False
    #         # Log(path)
    #     else:
    #         print('Input error. Invalid option.')
    #         continue

    # repeat = input ("Do you want to repeat program in a new parent directory?\n [1]yes\n [2]no\n --> ")
    # if repeat == '1' or repeat == 'y' or repeat == 'yes':
    #     old_new_paths.clear()
    #     AskUsage()
    #     Run(DirPrompt())
    # else:
    #     print("Exiting...")
    #     time.sleep(2)


def GenerateName(found, item):
    ext = found.split('.')[1]
    viewarr = found.split('_')
    view = viewarr[len(viewarr) - 1]
    new_name = item['Genus'] + '_' + item['species'] + '_' + item['cat#'] + '_' + item['sex'] + '_' + view
    # print(new_name)
    return new_name

def HandleFind(target, found, path, item):
    global mgcl_nums
    global destination

    new_name = GenerateName(found, item)
    print('\nCopying and moving {} as {} to {}'.format(found, new_name, destination))
    copyfile(path, destination + new_name)


def FindItem(path, item):
    global mgcl_nums
    global old_new_paths
    found = False

    target = item['cat#']
    for image in sorted(os.listdir(path)):
        if target in image:
            HandleFind(target, image, path + image, item)

    if not found:
        print('Could not find {}'.format(target))
        error_log.append(item)


def RecursiveFindItem(path, item):
    subdirs = GetDirs(path)
    for subdir in subdirs:
        RecursiveFindItem(path + subdir + '/', item)
    FindItem(path, item)



"""
    1). specify folder to run
    2). find folder 'genus' and search for duplicate mgcl numbers
    3). on dupl, send file to ../LepNet/SpecialProjects/Aillo_Saturniidae_Summer_2019_present
    4). for copy of the file, add genus, species and sex from excel sheet
"""
def Run(path):
    global mgcl_nums
    global old_new_paths
    global destination

    destination = DestinationDirPrompt()

    excel_path = input('\nPlease enter the path to the properly formatted CSV file: ')

    data = pd.read_csv(excel_path, header=0)

    for id,item in data.iterrows():
        RecursiveFindItem(path + item['Genus'] + '/', item)


def main():
    AskUsage()
    Run(DirPrompt())


# Driver Code
if __name__ == '__main__':
    main()