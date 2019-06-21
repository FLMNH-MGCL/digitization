import rawpy
import imageio
import exifread

path = 'MGCL_1085284_L.CR2' 

def ConvertAndRotate(path):
    # how to read image    
    with rawpy.imread(path) as raw:
        newImage = raw.postprocess(use_camera_wb = True, user_flip = 5, dcb_enhance = True, exp_preserve_highlights = 1, bright = .75)
        imageio.imsave('default' + '.jpg', newImage, quality = 92, dpi = tuple((300,300)))
        
    #imageio.help(name = 'jpg')

        #, auto_bright_thr = 0.0000135 
        # 0 
    # get metadata
    #f = open(path, 'rb')
    
    #tags = exifread.process_file(f)
    
    #for tag in tags.keys():
    #    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
    #        print("Key: %s, value %s" % (tag, tags[tag]))
    
    # save image
    

ConvertAndRotate(path)


