from turtle import *
from random import *


speed(0)
bgcolor("black")
hideturtle()

# get the width and height of the window
width = window_width()
height = window_height()


# draws a star at a given position
def draw_star(xpos, ypos):
    # set a random size for the star
    size = randrange(4, 10)


# goto the desired position
penup()
goto(xpos, ypos)
pendown()

# draw the star
dot(size, "white")

for x in range(100):
    # create a random X & Y position
    xpos = randrange(round(-width / 2), round(width / 2))
    ypos = randrange(round(-height / 2), round(height / 2))

# draw the star at that position
draw_star(xpos, ypos)
