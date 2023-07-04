import win_precise_time
import colorsys
import numpy as np
import colorutils
import random
from lib import Lighting_Funcs as lf
class Background:
    def __init__(self, fps, bar_length, speed, colour_RGB, colour_RGBW, bar_col_RGB, bar_col_RGBW, universes, selected, multi_strip=True, random_start=True, direction=0):
        """
        :param fps: For time management, from Air_DMX initialisation (int/float)
        :param bar_length: Length of coloured bar in pixels (int)
        :param speed: Speed of bar in pixels / second (float/int)
        :param colour_RGB: Base colour (RGB Numpy array)
        :param colour_RGBW: Base colour (RGBW Numpy array)
        :param bar_col_RGB: Bar colour (RGB Numpy array)
        :param bar_col_RGBW: Bar colour (RGBW Numpy array)
        :param universes: Universe data, from Air_DMX initialisation
        :param selected: Which universes are being used (index numpy array)
        :param multi_strip: Should effect be across many strips? (Bool)
        :param random_start: Random starting position or start of first strip (Bool)
        :param direction: Indicates direction of head, 0 is right (from start to end of strips), 1 is left (from end to start of strips) and 2 is random
        """
        self.fps = fps
        self.frame = 0
        self.bar_length = bar_length
        self.speed = speed
        self.colour_RGB = colour_RGB
        self.colour_RGBW = colour_RGBW
        self.bar_col_RGB = bar_col_RGB
        self.bar_col_RGBW = bar_col_RGBW
        self.universes = universes
        self.selected = selected
        self.total = 0
        self.active_universes = np.zeros((0, 4))
        last_index_RGB = 0
        last_index_RGBW = 0
        running_count = 0
        for count, target in enumerate(universes):

            if target[1] == "RGB":
                if count in selected:
                    running_count += universes[count, 0]
                    self.active_universes = np.append(self.active_universes, np.array([[last_index_RGB], [last_index_RGB + int(target[0])], [running_count], ["RGB"]]))
                last_index_RGB += int(target[0])
            elif target[1] == "RGBW":
                if count in selected:
                    running_count += universes[count, 0]
                    self.active_universes = np.append(self.active_universes, np.array([[last_index_RGBW], [last_index_RGBW + int(target[0])], [running_count], ["RGBW"]]))
                last_index_RGBW += int(target[0])

        self.multi_strip = multi_strip
        if random_start:
            self.index = float(random.randint(1, self.total) - 1)
        else:
            self.index = 0.0
        if direction != 2:
            self.direction = direction
        else:
            self.direction = random.randint(0, 1)

    def run(self):
        RGB_data, RGBW_data = lf.Flat_Colour_Operator(self.universes, self.colour_RGB, self.colour_RGBW)
        pixel_positions = []
        for pixels in range(0, self.bar_length):
            if self.direction == 1:
                position = self.index - float(pixels)
                if position < 0:
                    position += float(self.total)

            else:
                position = self.index + float(pixels)
                if position > self.total - 1:
                    position -= float(self.total)
            for active in self.active_universes:
                if 0 <= position < active[2]:
                    if active[3] == "RGB":
                        RGB_data[active[1]-int(round(active[2] - position))] = self.bar_col_RGB
                    else:
                        RGBW_data[active[1]-int(round(active[2] - position))] = self.bar_col_RGBW
        return RGB_data, RGBW_data