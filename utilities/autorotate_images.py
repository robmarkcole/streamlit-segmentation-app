# a simple script to detect and correct rotated images and resave them out to a different folder
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageDraw, ExifTags
import os

root = Tk()
root.filename =  filedialog.askdirectory(initialdir = "./",title = "Select directory of image files")
image_direc = root.filename
print(image_direc)
root.withdraw()

root = Tk()
root.filename =  filedialog.askdirectory(initialdir = "./",title = "Select output directory")
out_direc = root.filename
print(out_direc)
root.withdraw()

# all_files = []
for root, dirs, files in os.walk(image_direc, topdown=False):

    ## if you need to rotate images before labeling them on makesense.ai
    for rawfile in files:
        try:
            image = Image.open(root+os.sep+rawfile)
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif=dict(image._getexif().items())

            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)

            if 'jpg' in rawfile:  
                image.save(out_direc+os.sep+rawfile, format='JPEG')	
            else:     
                image.save(out_direc+os.sep+rawfile, format='PNG')

        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            pass
                	
