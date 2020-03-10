import sys
import os
import time
import imageio
import rawpy

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
    dirs = []
    for dir in sorted(os.listdir(path)):
        if os.path.isdir(path + dir):
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
    if len(imgs_all) / 2 != len(imgs_jpg):
        return False
    else:
        return True


def recurse(path):
    subdirs = GetDirs(path)
    for subdir in subdirs:
        recurse(path + subdir + '/')
    run(path)


def run(path):
    print('Currently working in {}'.format(path))
    images = GetImgs(path)

    if CheckCompleted(path):
        print('Directory already handled... Continuing')
        return

    else:
        for image in images:
            if 'mgcl' in image.lower():
                continue
            else:
                print('Converting {}'.format(path + image))
                with rawpy.imread(path + image) as raw:
                    rgb = raw.postprocess(user_wb=[1, 0.5, 1, 0])
                    name = image.split('.')[0] + '.jpg'
                    imageio.imsave(path + name, rgb)


def main():
    recurse(DirPrompt())


if __name__ == '__main__':
    main()
