import sys
import os
import time
import imageio
import rawpy

skipping = ["EREBIDAE_partial_rename", "SPHINGIDAE_partial_rename" ]

def DirPrompt():
    parent_directory = input('\nPlease input the path to the target directory: ')
    parent_directory = parent_directory.strip()

    if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
        parent_directory += '/'

    while not os.path.exists(parent_directory) or not os.path.isdir(parent_directory):
        print("\nCould not find path in filesystem or is not a directory...")
        parent_directory = input('\nPlease input the path to the target directory that contains the folder of the folders of images: ')
        parent_directory = parent_directory.strip()

        if not parent_directory.endswith('/') or not parent_directory.endswith('\\'):
            parent_directory += '/'

    return parent_directory

def GetDirs(path):
    global skipping
    dirs = []
    for dir in sorted(os.listdir(path)):
        if os.path.isdir(path + dir):
            if ("partial" in dir or "rename_all" in dir) and dir not in skipping:
                dirs.append(dir)

    return dirs


def GetSubDirs(path):
    dirs = []
    for dir in sorted(os.listdir(path)):
        if os.path.isdir(path + dir):
            #if "partial" in dir or "rename_all" in dir:
            whats_done = ['Actias_rename_all', 'Automeris_rename_partial', 'Coloradia_rename_all']
            if dir in whats_done:
                continue
            else:
                dirs.append(dir)
    return dirs


def GetImgs(path):
    imgs = []
    for img in sorted(os.listdir(path)):
        if os.path.isfile(path + img) and img.split('.')[1] == 'CR2':
            imgs.append(img)
    return imgs


def GetJPGS(path):
    jpgs = []
    for jpg in sorted(os.listdir(path)):
        if os.path.isfile(path + jpg) and (jpg.split('.')[1] == 'JPG' or jpg.split('.')[1] == 'jpg' or jpg.split('.')[1] == 'JPEG' or jpg.split('.')[1] == 'jpeg'):
            jpgs.append(jpg)
    return jpgs


def CheckCompleted(path):
    imgs_all = [img for img in sorted(os.listdir(path)) if os.path.isfile(path + img)]
    imgs_jpg = [img for img in imgs_all if img.split('.')[1] == 'jpg']
    #print(len(imgs_jpg))
    #print(len(imgs_all) / 2)
    if len(imgs_all) / 2 != len(imgs_jpg):
        return False
    else:
        return True



def main():
    # path = r"M:\\NaturalHistory\\Lepidoptera\\Kawahara\\Digitization\\LepNet\\PINNED_COLLECTION\\IMAGES_UPLOADED\\IMAGES_CR2_editing_complete\\"
    path = input("Input path")
    families = GetDirs(path)
    for family in families:
        genera = GetSubDirs(path + family + '/')
        for genus in genera:
            dates = GetSubDirs(path + family + '/' + genus + '/')
            for date in dates:
                images = GetImgs(path + family + '/' + genus + '/' + date + '/')
                current_path = path + family + '/' + genus + '/' + date + '/'
                print("Current Path: " + current_path)
                if CheckCompleted(current_path):
                    print('All images converted...\n')
                    continue
                #old_new_paths = []
                for image in images:
                    if "MGCL" in image:
                        continue
                    print (image)
                    #time.sleep(4)
                    with rawpy.imread(current_path + image) as raw:
                        rgb = raw.postprocess(user_wb=[1, 0.5, 1, 0])
                        name = image.split('.')[0] + '.jpg'
                        imageio.imsave(current_path + name, rgb)
                    #time.sleep(10)


if __name__ == '__main__':
    main()