#    MGCL 3947933    --> MGCL_3947933_D
#    MGCL 3947933(2) --> MGCL_3947933_V
#    MGCL 3947933_L  --> MGCL_3947933_L

import os
import sys
import platform

def GetSubDirs(path):
    subdirectories = []
    for img in os.listdir(path):
        if os.path.isdir(path + img):
            subdirectories.append(img)
    return subdirectories

def GetDirFiles(path):
    files = []
    for img in os.listdir(path):
        if not os.path.isdir(path + img):
            files.append(img)
    return files

def RecursiveRename(path):
    subdirectories = GetSubDirs(path)
    for dir in subdirectories:
        RecursiveRename(path + dir + '\\')
    Rename(path)

def Rename(path):
    ext = ".CR2"
    print("\nWorking in... {}\n".format(path))

    for filename in GetDirFiles(path):
        if filename.split('.')[1] != ext:
            continue

        # Separate ext and filename
        new_name = filename.split('.')[0]

        # instances of ' (2)' become _V
        new_name = new_name.replace("(2)", "_V")

        # Spaces replaced with '_'
        new_name = new_name.replace(' ', '_')

        # If not _V nor _L nor _D, add _D 
        if (new_name.find("_V") == -1 and new_name.find("_L") == -1 and new_name.find("_D") == -1):
            new_name += "_D"

        if filename != new_name + ext:
            os.rename(path + filename, path + (new_name + ext))

    print("Directory completed.")


def main():
    # target files = .CR2
    ext = ".CR2"

    # Trailing slash default to unix systems
    trailing_slash = '/'
    if platform.system().find("Windows"):
        trailing_slash = '\\'

    print("\nThis program will help you rename " + ext + " files in a directory")
    path = input("Please type the path of the directory: ")
    if not path.endswith(trailing_slash):
        path += trailing_slash

    method = input("\nChoose 1 of the following: \n [1]Standard (All " + ext + " files in this directory level) \n [2]Recursive (All " + ext + " files in this directory level and every level below) \n--> ")
    
    if method == '1':
        Rename(path)

    elif method == '2':
        # Recursive
        RecursiveRename(path)

    else:
        print("Input error.")
        sys.exit(1)

    print("\nProgram completed.\n")

# Driver Code
if __name__ == '__main__':
    main()
