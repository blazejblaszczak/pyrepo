import turtle as t


diameter = 40
pop_diameter = 100

# draws the balloon on screen

def draw_balloon ():
    t.color("red")
    t.dot(diameter)


# called when we press the Up arrow key
def inflate_balloon ():
    global diameter
    diameter = diameter + 10
    draw_balloon()
    # are we ready to pop?
    if diameter >= pop_diameter:
        t.clear()
        diameter = 40
        t.write("POP!")
    

draw_balloon()

# call inflate_balloon when we press the Up arrow key
t.onkey(inflate_balloon, "Up")
t.listen()
