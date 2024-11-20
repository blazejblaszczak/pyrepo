from PIL import Image, ImageDraw, ImageFont
from os.path import join

# images 
image = Image.new('RGBA', (800,400), (255,255,255))
bird = Image.open(join('resources', 'card', 'bird.png'))
logo = Image.open(join('resources', 'card', 'logo.png'))

# data
draw = ImageDraw.Draw(image)

font_large = ImageFont.truetype(
  font = join('resources', 'RabbidHighway.otf'), 
  size = 60
)

font_small = ImageFont.truetype(
  font = join('resources', 'RabbidHighwayOblique.otf'), 
  size = 24
)

name = 'Mr B'
jobs = [
  'Senior developer', 
  'python expert', 
  'data expert'
]

company = 'BB Inc.'
color = (50,50,50)
padding = 20
logo_padding = 4
logo_top = 280

# name
draw.text(
  xy = (padding, padding),
  text = name, 
  font = font_large,
  fill = color)

y = draw.textbbox(
  xy = (padding, padding),
  text = name, 
  font = font_large)[-1] + logo_padding

text_length = font_large.getlength(name)

draw.line(
  xy = ((padding,y), (padding + text_length, y)),
  fill = color,
  width = 5)

# jobs 
draw.multiline_text(
  xy = (padding, y + 20),
  text = '\n'.join(jobs),
  fill = color, 
  font = font_small,
  spacing = 15)

# company
image.paste(logo, (padding,logo_top), logo)

x = padding + logo.size[0] + 10
y = logo_top + logo.size[1] / 2

text_size = draw.textbbox(
  xy = (x,y),
  text = company,
  font = font_small, 
  anchor = 'lm')

text_size_padded = (
  text_size[0] - logo_padding,
  text_size[1] - logo_padding,
  text_size[2] + logo_padding,
  text_size[3] + logo_padding,
  )

draw.rectangle(
  xy = text_size_padded,
  fill = color)

draw.text(
  xy = (x, y),
  text = company,
  fill = (255,255,255), 
  font = font_small,
  anchor = 'lm')

# bird image 
image.paste(bird, (500,padding), bird)

image.show()
