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
        dirs = self._get_direction()
        self.cube.move(dirs['forward'])

    def move_backward(self):
        dirs = self._get_direction()
        self.cube.move(dirs['backward'])

    def move_left(self):
        dirs = self._get_direction()
        self.cube.move(dirs['left'])

    def move_right(self):
        dirs = self._get_direction()
        self.cube.move(dirs['right'])

    def _get_direction(self):
        orientation = self.cube.direction
        dirs = {}

        if orientation[0] == 1:
            dirs = {'forward': 'forward', 'backward': 'backward',
                    'left': 'left', 'right': 'right'}
        elif orientation[0] == -1:
            dirs = {'forward': 'backward', 'backward': 'forward',
                    'left': 'right', 'right': 'left'}
        elif orientation[1] == 1:
            dirs = {'forward': 'right', 'backward': 'left',
                    'left': 'forward', 'right': 'backward'}
        elif orientation[1] == -1:
            dirs = {'forward': 'left', 'backward': 'right',
                    'left': 'backward', 'right': 'forward'}

        return dirs
