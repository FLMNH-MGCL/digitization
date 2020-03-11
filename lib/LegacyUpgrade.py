import os
import re
import time
import datetime

class LegacyUpgrader:
    def __init__(self):
        pass

    def run(self):
        pass

old_new_paths = []
duplicates = []
unknowns = []
digerrs = []
valid_imgs = ['JPG', 'jpg', 'jpeg', 'JPEG', 'CR2', 'cr2']

def Log(path):
    global old_new_paths
    d = datetime.datetime.today()
    date = str(d.year) + '_' + str(d.month) + '_' + str(d.day)
    filename = path + 'RENAMED_SCRIPT_LOG_' + date

    count = ''
    num = 0
    while os.path.exists(filename + count + '.csv'):
        if num == 0:
            filename += '_'
        num += 1
        count = str(num)

    if num == 0:
        filename = filename + '.csv'
    else:
        filename = filename + count + '.csv'

    csv_file = open(filename, mode='w')
    csv_file.write('Old Path,New Path\n')
    for old_path,new_path in old_new_paths:
        csv_file.write(old_path + ',' + new_path + '\n')
    for old_path,new_path in duplicates:
        csv_file.write(old_path + ',' + new_path + '\n')
    for old_path,new_path in unknowns:
        csv_file.write(old_path + ',' + new_path + '\n')
    for old_path,new_path in digerrs:
        csv_file.write(old_path + ',' + new_path + '\n')


def AskUsage():
    prompt = str(
            "\nThis program will upgrade the legacy server data to fit the new standardized filename structure. " \
            "It will first ask for you to input the directory containing the specimen images, alternatively " \
            "you may drag the folder into the terminal window on mac platforms. From there, the program will " \
            "attempt to rename all valid image files in the folder. When it is done, you will have the chance " \
            "to choose whether or not to: delete any duplicates found, undo changes or repeat program in a new " \
            "directory. 5 seconds after asking for this prompt you may begin. "
        )
    wanted = input("\nDo you want to see the usage information?\n [1]yes\n [2]no\n --> ")
    if wanted == '1' or wanted == 'y' or wanted == 'yes':
        print(prompt)
        time.sleep(5)


def IsValid(extension):
    if extension in valid_imgs:
        return True
    else: 
        return False


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


def GetDirs(path):
    dirs = []
    for folder in sorted(os.listdir(path)):
        if os.path.isdir(path + folder):
            dirs.append(folder)
    return dirs


def GetImages(path):
    imgs = []
    for img in sorted(os.listdir(path)):
        if os.path.isfile(path + img):
            img_vec = img.split('.')
            if len(img_vec) > 1 and IsValid(img_vec[1]):
                imgs.append(img)
    return imgs


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


def FixDateFormat(date, path):
    return date


def CountDigits(string):
    return sum(c.isdigit() for c in string)


def DeleteDupl():
    for old_name,new_name in duplicates:
        try:
            os.remove(new_name)
        except:
            print("Could not find file.")


def Undo():
    valid_choice = False
    ret_str = ""
    while not valid_choice:
        choice = input("Do you want to:\n [1]undo ALL changes\n [2]leave errors and duplicates renamed?\n --> ")
        if choice == '1' or choice == 'all':
            valid_choice = True
            for old_path,new_path in old_new_paths:
                os.rename(new_path, old_path)
            for old_path,new_path in unknowns:
                os.rename(new_path, old_path)
            for old_path,new_path in duplicates:
                os.rename(new_path, old_path)
            for old_path,new_path in digerrs:
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

    delete_dupl = input("Do you wish to delete any found duplicates?\n [1]yes\n [2]no\n --> ")
    if delete_dupl == '1' or delete_dupl == 'y' or delete_dupl == 'yes':
        double_check = input("Are you sure? This cannot be undone!!\n [1]yes\n [2]no\n --> ")
        if double_check == '1' or double_check == 'y' or double_check == 'yes':
            # DeleteDupl()
            print("Deleting will be functional after proper testing...")

    while wait == True:
        undo = input("Do you wish to undo?\n [1]yes\n [2]no\n --> ")
        if undo == '1' or undo == 'y' or undo =='yes':
            print(Undo())
            wait = False
        elif undo == '2' or undo == 'n' or undo == 'no':
            wait = False
            Log(path)
        else:
            print('Input error. Invalid option.')
            continue

    repeat = input ("Do you want to repeat program in a new parent directory?\n [1]yes\n [2]no\n --> ")
    if repeat == '1' or repeat == 'y' or repeat == 'yes':
        old_new_paths.clear()
        duplicates.clear()
        unknowns.clear()
        AskUsage()
        Upgrade(DirPrompt())
    else:
        print("Exiting...")
        time.sleep(2)


# main upgrading code
"""
This assumes the following folder structure:
    ../families/genera/collection_dates/*specimen images here*
"""
def Upgrade(parent_directory):
    global old_new_paths
    global duplicates
    global unknowns
    global digerrs

    print("\nProgram starting...")
    time.sleep(1)
    families = GetDirs(parent_directory) # all the family folders
    for family in families:
        genera = GetDirs(parent_directory + family + '/') # all the genus folders
        for genus in genera:
            collection = GetDirs(parent_directory + family + '/' + genus + '/') # all the date folders
            for date in collection:
                # ensures proper dating of collection folder
                # date = FixDateFormat(date, parent_directory + family + '/' + genus + '/')

                working_directory = parent_directory + family + '/' + genus + '/' + date + '/'
                specimens = GetImages(working_directory)
                visited = []
                for specimen in specimens:
                    is_unknown = False
                    has_digerror = False
                    is_duplicate = False
                    extension = '.' + specimen.split('.')[1]
                    old_name = specimen.split('.')[0]
                    new_name = GetNewName(old_name)

                    if new_name.startswith("MGCL_"):
                        img_vec = new_name.split('_')

                        # check for duplicates
                        if len(img_vec) > 1:
                            # check for duplicate
                            if new_name in visited:
                                is_duplicate = True
                                new_name += '_DUPL'
                            else:
                                visited.append(new_name)

                            # check digits for error (requires exactly 7 digits)
                            if CountDigits(img_vec[1]) != 7:
                                print(specimen + ': File has digit error.')
                                new_name += '_DIGERROR'
                                has_digerror = True

                        else:
                            print(specimen + ': Unknown file formatting.')
                            new_name += 'UNKNOWN'
                            is_unknown = True

                    else:
                        print(specimen + ': Unknown file formatting.')
                        new_name += 'UNKNOWN'
                        is_unknown = True

                    new_name += extension
                    old_path = working_directory + specimen
                    new_path = working_directory + new_name
                    if is_unknown:
                        unknowns.append(tuple((old_path, new_path)))
                    elif has_digerror:
                        digerrs.append(tuple((old_path, new_path)))
                    elif is_duplicate:
                        duplicates.append(tuple((old_path, new_path)))
                    else:
                        old_new_paths.append(tuple((old_path, new_path)))

                    os.rename(old_path, new_path)
                    print("\nRenaming {} as {}\n".format(old_path, new_path))

    print("All images handled. Please hold...\n")
    Wait(parent_directory)


def main():
    AskUsage()
    parent_directory = DirPrompt()
    Upgrade(parent_directory)

if __name__ == '__main__':
    main()

"""
KNOWN BUGS:
    (2) counted as dig error (should be fixed)
        fixed on personal computer, not museum. cannot repeat bug as of yet for testing.
    _2 counted as dig error (should be fixed)
    not duplicates if diff orientations ? (fixed)
    fix duplicate calc, eg Dorsal Dorsal Ventral not counted (fixed)
    MGCL- "MGCL hyphen" #Replace w/ underscores
    MGCL# (no separation)   #Replace MGCL w/ MGCL_
"""
