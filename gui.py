from Tkinter import *

class App:

    def __init__(self, master, cube):
        frame = Frame(master)
        frame.pack()

        self._up_arrow = PhotoImage(file="img/arrow-up.png")
        self._down_arrow = PhotoImage(file="img/arrow-down.png")
        self._left_arrow = PhotoImage(file="img/arrow-left.png")
        self._right_arrow = PhotoImage(file="img/arrow-right.png")

        forward = Button(
            frame, image=self._up_arrow, command=self.move_forward
        )
        backward = Button(
            frame, image=self._down_arrow, command=self.move_backward
        )
        left = Button(
            frame, image=self._left_arrow, command=self.move_left
        )
        right = Button(
            frame, image=self._right_arrow, command=self.move_right
        )
        forward.pack(side=TOP)
        backward.pack(side=BOTTOM)
        left.pack(side=LEFT)
        right.pack(side=RIGHT)

        self.cube = cube

    def move_forward(self):
        self.cube.move('forward')

    def move_backward(self):
        self.cube.move('backward')

    def move_left(self):
        self.cube.move('left')

    def move_right(self):
        self.cube.move('right')
