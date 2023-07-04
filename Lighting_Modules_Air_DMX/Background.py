import win_precise_time
import colorsys
import numpy as np
import colorutils
import random

class Background:
    def __init__(self, fps, bar_length, speed, colour, bar_col, universes, selected, order, multi_strip=True, random_start=True, direction=0):
        """
        :param fps: For time management, from Air_DMX initialisation (int/float)
        :param bar_length: Length of coloured bar in pixels (int)
        :param speed: Speed of bar in pixels / second (float/int)
        :param colour: Base colour (RGB Numpy array)
        :param bar_col: Bar colour (RGB Numpy array)
        :param universes: Universe data, from Air_DMX initialisation
        :param selected: Which universes are being used (index numpy array)
        :param order: Strip order (Numpy array)
        :param multi_strip: Should effect be across many strips? (Bool)
        :param random_start: Random starting position or start of first strip (Bool)

        """
        self.fps = fps
        self.frame = 0
        self.bar_length = bar_length
        self.speed = speed
        self.colour = colour
        self.bar_col = bar_col
        self.universes = universes
        self.selected = selected
        self.total = 0
        for index in selected:
            self.total += int(universes[index,0])
        self.order = order
        self.multi_strip = True
        if random_start:
            self.index = random.randint(1, self.total)
        else:
            self.index = 0

    #def main(self):

