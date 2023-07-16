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

def convert_RGB_RGBW(colour_RGB):   # Converts base RGB to an RGBW array, no colour change
    return np.append(colour_RGB, 0)

def convert_RGBW_RGB(colour_RGBW):  # Approximation to convert from RGBW to RGB
    red = int(colour_RGBW[0])+ int(colour_RGBW[3])
    blue = int(colour_RGBW[1]) + int(colour_RGBW[3])
    green = int(colour_RGBW[2]) + int(colour_RGBW[3])
    if red >= blue and red > green:
        blue_index = blue / red
        green_index = green / red
        if red > 255:
            red = 255
        blue = int(blue_index * red)
        green = int(green_index * red)
    elif blue > red and blue >= green:
        red_index = red / blue
        green_index = green / blue
        if blue > 255:
            blue = 255
        red = int(red_index * blue)
        green = int(green_index * blue)
    elif green >= red and green > blue:
        red_index = red / green
        blue_index = blue / green
        if green > 255:
            green = 255
        red = int(red_index * green)
        blue = int(blue_index * green)
    else:
        if red > 255:
            red = 255
            blue = 255
            green = 255
    return np.array([red, blue, green], dtype=np.uint8)

