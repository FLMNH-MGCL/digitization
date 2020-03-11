import os
import shutil
from PIL import Image
from PIL import ExifTags

class Rescaler:
    def __init__(self):
        pass

    def run(self):
        pass


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


def scale_prompt():
    scale_amount = input('\nPlease input the amount to rescale the image. For example, if you want it scaled to half the size, enter \'2\'. If you wanted it a quarter of the size, enter \'4\'.\n --> ')
    scale = 1

    valid = False
    while not valid:
        try:
            scale = int(scale_amount)
        except:
            scale_amount = input('Invalid input. Please enter a non-negative, integer value:\n --> ')

        if scale <= 0:
            scale_amount = input('Invalid input. Please enter a non-negative, integer value:\n --> ')
        else:
            print('Program will scale to 1/{}'.format(scale))
            valid = True
            break

    return scale


def rescurse_prompt():
    recurse = input("\nChoose 1 of the following: \n [1]Standard (All image files in this directory level) \n [2]Recursive " \
            "(All image files in this directory level and every level below) \n--> ")
    valid = False
        
    if recurse in ['1', '2', '[1]', '[2]']:
        valid = True

    while not valid:
        recurse = input("\nInvalid input. Choose 1 of the following: \n [1]Standard (All image files in this directory level) \n [2]Recursive " \
            "(All image files in this directory level and every level below) \n--> ")

    if recurse is '1' or recurse is '[1]':
        return False
    
    else: return True


def get_subdirs(path):
    subdirs = []
    for item in sorted(os.listdir(path)):
        if os.path.isdir(path + item):
            subdirs.append(item)

    return subdirs


def moveCR2(path, img):
    pass
    shutil.move(path + img, path + 'CR2/' + img)

def getRotation(orientation):
    if orientation in [1, 2]:
        return 0
    elif orientation in [3, 4]:
        return 180
    elif orientation in [5, 6]:
        return 270
    elif orientation in [7, 8]:
        return 90
    else:
        return -1

def isMirrored(orientation):
    if orientation in [2, 7, 4, 5]:
        return True
    else: return False

def rescale(path, name, scale):
    img = Image.open(path + name)
    width, height = img.size
    ext = name.split('.')[1]

    new_width = int(width / scale)
    new_height = int(height / scale)
    new_size = (new_width, new_height)
    new_name = name.split('.')[0] + '_downscaled.' + ext

    # grab exif data
    try:
        exif = dict((ExifTags.TAGS[k], v) for k, v in new_image._getexif().items() if k in ExifTags.TAGS)
        # rotate / mirror if applicable
        if exif['Orientation']:
            rotation = getRotation(exif['Orientation'])
            mirrored = isMirrored(exif['Orientation'])
            if mirrored:
                new_image = new_image.transpose(Image.FLIP_LEFT_RIGHT)
            new_image = new_image.rotate(rotation, expand=True)
    except:
        print('no exif data could be loaded for rotation information...')

    new_image = img.resize(new_size)

    print('{}: Original width and height {} by {}. New width and height {} by {}'.format(path, width, height, new_width, new_height))

    print('Saving downscaled image...')
    print('Moving downscaled image {} to LO-RES folder...'.format(new_name))

    # save downscaled to low-res folder
    new_image.save(path + 'LOW-RES/' + new_name, 'JPEG')

    print('Moving original {} to HI-RES folder'.format(name))

    # move original jpg to hi-res folder
    shutil.move(path + name, path + 'HI-RES/' + name)

    


def recursive_run(path, scale):
    for subdir in get_subdirs(path):
        recursive_run(path + subdir + '/', scale)
    run(path, scale)


def run(path, scale):
    print('Working in: {}'.format(path))
    # create the CR2, HIRES, LOWRES folders at this pathway. 
    if not os.path.exists(os.path.join(path, 'CR2')):
        os.mkdir(os.path.join(path, 'CR2'))

    if not os.path.exists(os.path.join(path, 'HI-RES')):
        os.mkdir(os.path.join(path, 'HI-RES'))

    if not os.path.exists(os.path.join(path, 'LOW-RES')):
        os.mkdir(os.path.join(path, 'LOW-RES'))


    for img in sorted(os.listdir(path)):
        if img.lower().endswith('.cr2'):
            moveCR2(path, img)
        elif img.lower().endswith('.jpg') or img.lower().endswith('.jpeg'):    
            rescale(path, img, scale)
        else:
            print('invalid file type. skipping...')


def main():
    path = DirPrompt()
    scale = scale_prompt()
    recurse = rescurse_prompt()

    if recurse:
        recursive_run(path, scale)
    else:
        run(path, scale)



if __name__ == '__main__':
    main()