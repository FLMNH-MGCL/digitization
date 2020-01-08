import os
from PIL import Image


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


def rescale(path, name, scale):
    img = Image.open(path + name)
    width, height = img.size
    ext = name.split('.')[1]

    new_width = int(width / scale)
    new_height = int(height / scale)
    new_size = (new_width, new_height)
    new_name = name.split('.')[0] + '_downscaled.' + ext

    new_image = img.resize(new_size)
    new_image.save(path + new_name, 'JPEG')

    print('{}: {} by {}'.format(path, width, height))


def main():
    path = DirPrompt()

    scale = scale_prompt()

    for img in sorted(os.listdir(path)):
        rescale(path, img, scale)


if __name__ == '__main__':
    main()