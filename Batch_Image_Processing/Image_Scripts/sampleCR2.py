import rawpy
import imageio
import exifread
from PIL import Image
import piexif

path = 'MGCL_1085340_L.JPG' 

def ConvertAndRotate(path):
    # get metadata
    f = open(path, 'rb')
    
    exif_dict = exifread.process_file(f)
    
    for tag in exif_dict.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print("Key: %s, value %s" % (tag, exif_dict[tag]))
    
    # process im and exif_dict to store as bytes
    #w, h = f.size
    #exif_dict["0th"][piexif.ImageIFD.XResolution] = (w, 1)
    #exif_dict["0th"][piexif.ImageIFD.YResolution] = (h, 1)
    
    exif_bytes = piexif.dump(exif_dict)
    
    # Read and save image   
    #with rawpy.imread(path) as raw:
    #    newImage = raw.postprocess(use_camera_wb = True, user_flip = 5, dcb_enhance = True, exp_preserve_highlights = 1, bright = .75)
    #    imageio.imsave('default' + '.jpg', newImage, quality = 100, dpi = tuple((300,300)))
    
    # insert metadata
    # piexif.insert(exif_bytes,'default.jpg')

ConvertAndRotate(path)


