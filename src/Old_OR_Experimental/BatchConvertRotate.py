import os
import sys
import rawpy
import imageio

def GetSubDirs(path):
    subdirectories = []
    for img in os.listdir(path):
        if os.path.isdir(path + img):
            subdirectories.append(img)
    return subdirectories

def GetDirFiles(path):
    files = []
    for img in os.listdir(path):
        if os.path.isfile(path + img) and img.endswith('.CR2'):
            files.append(img)
    return files

def ConvertAndRotate(path):
    #ext = '.CR2'
    print("\nWorking in... {}\n".format(path))

    for img in GetDirFiles(path):
        
        # how to read image
        with rawpy.imread(path) as raw:
            #newImage = raw.postprocess(use_camera_wb = True, user_flip = 5, auto_bright_thr = 0.000015)
            newImage = raw.postprocess(use_camera_wb = True, user_flip = 5, dcb_enhance = True, exp_preserve_highlights = 1, bright = .75)
        
        # save image
        imageio.imsave(path + img.splitext('.')[0] + ".jpg", newImage, quality = 100, dpi = tuple((300,300)))
        
        print('\n{} has been converted / rotated.'.format(img))

def RecursiveConvertAndRotate(path):
    subdirectories = GetSubDirs(path)
    for dir in subdirectories:
        RecursiveConvertAndRotate(path + dir + '/')
    ConvertAndRotate(path)
    print('\n')

def main():
    ext = '.CR2'
    print('\nThis script will convert any CR2 files and rotate them to proper orientation from any given directory')
    path = input('Please enter the path to the target parent directory: ')
    if not path.endswith('/'):
        path += '/'

    method = input("\nChoose 1 of the following: \n [1]Standard (All " + ext + " files in this directory level) \n [2]Recursive (All " + ext + " files in this directory level and every level below) \n--> ")
    
    if method == '1':
        ConvertAndRotate(path)

    elif method == '2':
        # Recursive
        RecursiveConvertAndRotate(path)

    else:
        print("Input error.")
        sys.exit(1)

    print("\nProgram completed.\n")

# Driver
if __name__ == '__main__':
    main()
