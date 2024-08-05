from turtle import *


speed(0)

# set the background color
bgcolor("black")

# create the ORANGE planet
color("orange")
begin_fill()
circle(60)
end_fill()

# move down
right(90)
penup()
forward(70)
pendown()
left(90)

# create the GRAY planet
color("gray")
begin_fill()
circle(20)
end_fill()

# move down
right(90)
penup()
forward(100)
pendown()
left(90)

# create the RED planet
color("red")
begin_fill()
circle(40)
end_fill()

# move down
right(90)
penup()
forward(100)
pendown()
left(90)

# create the GREEN planet
color("green")
begin_fill()
circle(30)
end_fill()
