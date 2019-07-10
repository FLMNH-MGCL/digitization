# EARLY TESTING NOT YET FOR PRACTICAL USE!!

from PIL import Image
import pytesseract
import os
import sys
import time
from statistics import mean

# using the following tutorial:
# https://www.tensorscience.com/ocr/optical-character-recognition-ocr-with-python-and-tesseract-4-an-introduction


def GetDirFiles(path):
    files = []
    for img in os.listdir(path):
        if not os.path.isdir(path + img):
            files.append(img)
    return files

def GetCatalogueNumber(imPath): 
    # Convert to Greyscale

    im = Image.open(imPath)

    # im = im.convert('L')
    
    # Binarization
    # im = im.point(lambda x: 0 if x<128 else 255, '1') 

    imStr = pytesseract.image_to_string(im)

    return imStr

def main():

    tlst = list()

    # hardcode your path for testing here
    path = 'C:/Users/ryuoo/Documents/FLMNH/Batch_Image_Processing/Image_Scripts/JPG/'

    for filename in GetDirFiles(path):
        start = time.time()
        imPath = path + filename
        print(GetCatalogueNumber(imPath))
        end = time.time()
        tlst.append(end - start)
    
    print('Average Time=', round(mean(tlst)), 2)

# Driver Code
if __name__ == '__main__':
    main()






