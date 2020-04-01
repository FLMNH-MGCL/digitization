import os
import shutil
from PIL import Image
from PIL import ExifTags
from lib.Logger import Logger
from lib.Helpers import Helpers

class Rescaler:
    def __init__(self):
        self.target_directory = ""
        self.scale = 0

    def scale_prompt(self):
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
                print('\nProgram will scale to 1/{}'.format(scale))
                valid = True
                break

        self.scale = scale

    def getRotation(self, orientation):
        if orientation is 1 or orientation is 2:
            return 0
        elif orientation is 3 or orientation is 4:
            return 180
        elif orientation is 5 or orientation is 6:
            return 270
        elif orientation is 7 or orientation is 8:
            return 90
        else:
            return -1

    def isMirrored(self, orientation):
        if orientation in [2, 7, 4, 5]:
            return True
        else: return False

    def rescale(self, path, name):
        img = Image.open(path + name)
        width, height = img.size
        ext = name.split('.')[1]

        new_width = int(width / self.scale)
        new_height = int(height / self.scale)
        new_size = (new_width, new_height)
        new_name = name.split('.')[0] + '_downscaled.' + ext

        raw_rotation = None
        rotation = None
        mirrored = None
        new_image = img

        # grab exif data
        try:
            exif = dict((ExifTags.TAGS[k], v) for k, v in new_image._getexif().items() if k in ExifTags.TAGS)
            # rotate / mirror if applicable
            if exif['Orientation']:
                raw_rotation = int(exif['Orientation'])
                rotation = self.getRotation(raw_rotation)
                mirrored = self.isMirrored(rotation)
                if mirrored:
                    print("Detected mirrored image: flipping left to right")
                    new_image = new_image.transpose(Image.FLIP_LEFT_RIGHT)
                
        except:
            print('No exif data could be loaded for rotation information...')

        if rotation is not None and raw_rotation is not None:
            print("Rotating image {} degrees (raw metadata value: {})".format(rotation, raw_rotation))
            new_image = new_image.rotate(rotation, expand=True)
            new_size = (new_size[1], new_size[0])

        new_image = new_image.resize(new_size)

        print('{}: Original width and height {} by {}. New width and height {} by {}'.format(path, width, height, new_width, new_height))

        print('Saving downscaled image...')
        print('Moving downscaled image {} to LO-RES folder...'.format(new_name))

        # save downscaled to low-res folder
        new_image.save(path + 'LOW-RES/' + new_name, 'JPEG')

        print('Moving original {} to HI-RES folder'.format(name))

        # move original jpg to hi-res folder
        shutil.move(path + name, path + 'HI-RES/' + name)

    def moveCR2(self, path, img):
        shutil.move(path + img, path + 'CR2/' + img)

    def standard_run(self, path):
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
                self.moveCR2(path, img)
            elif img.lower().endswith('.jpg') or img.lower().endswith('.jpeg'):    
                self.rescale(path, img)
            else:
                print('invalid file type. skipping...')
        
        print()

    def recursive_run(self, path):
        for subdir in Helpers.get_dirs(path):
            self.recursive_run(path + subdir + '/')
        self.standard_run(path)

    def run(self):
        print('### RESCALER PROGRAM ###\n')
        help_prompt = str(
            "This doesn't have help right now..."
        )
        Helpers.ask_usage(help_prompt)

        path_prompt = "\nPlease input the path to the directory that contains the images:\n--> "
        self.target_directory = Helpers.get_existing_path(Helpers.path_prompt(path_prompt), True)

        self.scale_prompt()

        recurse_prompt = str("\nChoose 1 of the following: \n [1]Standard (All files in this directory level) \n [2]Recursive " \
            "(All files in this directory level and every level below) \n\n--> ")
        recurse = Helpers.rescurse_prompt(recurse_prompt)
        print()

        if recurse:
            self.recursive_run(self.target_directory)
        else:
            self.standard_run(self.target_directory)

        print('\nProgram complete.\n')