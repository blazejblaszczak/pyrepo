from PIL import Image 
from os.path import join, exists
from glob import glob
from os import mkdir


# This code is used to add a watermark to a collection of images.
# The watermark is positioned at the bottom right corner with a specified padding,
# and the watermarked images are saved into a new “watermarked” directory.

logo = Image.open(join('resources', 'watermark.png'))
paths = glob(join('resources', 'images', '*.jpg'))
images = [Image.open(path) for path in paths]
padding = 10

if not exists('watermarked'):
  mkdir('watermarked')
  
for image in images:
  x = image.width - padding - logo.width
  y = image.height - padding - logo.height
  name = image.filename.split('\\')[-1][:-4] + '_watermark.jpg'
  image.paste(logo, (x,y), logo)
  image.save(f'watermarked/{name}', 'JPEG')
