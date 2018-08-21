# Animation Starter Code, Focus on timerFired

from tkinter import *

####################################
# customize these functions
####################################

def init(d):
    # load d.xyz as appropriate
    pass

def mousePressed(event, d):
    # use event.x and event.y
    pass

def keyPressed(event, d):
    # use event.char and event.keysym
    pass

def timerFired(d):
    pass

def redrawAll(canvas, d):
    # draw in canvas
    pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, d):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, d.width, d.height,
                                fill='white', width=0)
        redrawAll(canvas, d)
        canvas.update()

    def mousePressedWrapper(event, canvas, d):
        mousePressed(event, d)
        redrawAllWrapper(canvas, d)

    def keyPressedWrapper(event, canvas, d):
        keyPressed(event, d)
        redrawAllWrapper(canvas, d)

    def timerFiredWrapper(canvas, d):
        timerFired(d)
        redrawAllWrapper(canvas, d)
        # pause, then call timerFired again
        canvas.after(d.timerDelay, timerFiredWrapper, canvas, d)
    # Set up d and call init
    class Struct(object): pass
    d = Struct()
    d.width = width
    d.height = height
    d.timerDelay = 100 # milliseconds
    root = Tk()
    init(d)
    # create the root and the canvas
    canvas = Canvas(root, width=d.width, height=d.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, d))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, d))
    timerFiredWrapper(canvas, d)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(400, 200)