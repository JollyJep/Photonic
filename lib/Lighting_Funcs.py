import queue
import threading as th
import time

import numpy as np
import sacn
import win_precise_time as wpt



def Flat_Colour_Operator(universes, colour_RGB=np.array([0, 0, 0], dtype=np.uint8),colour_RGBW=np.array([0, 0, 0, 0],dtype=np.uint8)):  # Also used for universe initialisation
    RGB_data = np.zeros((0, 3), dtype=np.uint8)
    RGBW_data = np.zeros((0, 4), dtype=np.uint8)
    for count, universe in enumerate(universes):
        if universe[1] == "RGB":
            RGB_data = np.append(RGB_data, np.full((int(universe[0]), 3), colour_RGB), axis=0)
        elif universe[1] == "RGBW":
            RGBW_data = np.append(RGBW_data, np.full((int(universe[0]), 4), colour_RGBW), axis=0)
    return RGB_data, RGBW_data


def Universe_Masker(universes, keep_list, RGB_data, RGBW_data): #Works similar to boolean alpha channel (Either 0 light output or previous data, allows for universe separation)
    RGB_universes = universes[universes[:, 1] == "RGB"]
    RGBW_universes = universes[universes[:, 1] == "RGBW"]

    for keep in keep_list:  #indexes
        number = 0
        if universes[keep, 1] == "RGB":
            pos = np.where(RGB_universes[:,2] == keep + 1)
            for x in range(0, pos[0]):
                number += RGB_universes[x, 0]
            RGB_data[number:number + RGB_universes[pos, 0]] = np.zeros((RGB_universes[pos, 0], 3))
        elif universes[keep, 1] == "RGBW":
            pos = np.where(RGBW_universes[:,2] == keep + 1)
            for x in range(0, pos[0]):
                number += RGBW_universes[x, 0]
            RGBW_data[number:number + RGBW_universes[pos, 0]] = np.zeros((RGBW_universes[pos, 0], 4))
    return RGB_data, RGBW_data