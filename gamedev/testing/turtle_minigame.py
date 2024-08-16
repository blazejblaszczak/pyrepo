from turtle import *


speed(0)
move_distance = 20

# create beach
bgcolor("#D2691E")

# draw ocean
penup()
goto(100, 200)
pendown()
color("blue")
begin_fill()
goto(300, 200)
goto(300, -200)
goto(100, -200)
goto(100, 200)
end_fill()

# set turtle starting position
penup()
goto(-200, 0)
shape("turtle")
color("green")


def move_up ():
    setheading(90)
    forward(move_distance)
    check_goal()


def move_down ():
    setheading(270)
    forward(move_distance)
    check_goal()


def move_left ():
    setheading(180)
    forward(move_distance)
    check_goal()


def move_right ():
    setheading(0)
    forward(move_distance)
    check_goal()

# called when we move the turtle
def check_goal ():
    if xcor() > 100:
        hideturtle()


color("white")
write("YOU WIN!")
onkey(None, "Up")
onkey(None, "Down")
onkey(None, "Left")
onkey(None, "Right")

# key press events
onkey(move_up, "Up")
onkey(move_down, "Down")
onkey(move_left, "Left")
onkey(move_right, "Right")

# listen for key presses
listen()
