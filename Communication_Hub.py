import queue
import threading as th
import time

import numpy as np
import sacn
import win_precise_time as wpt
from Lighting_Modules_Air_DMX import Background as bg

def Communication_Daemon(comms_queue_1, comms_queue_2, comms_queue_3, comms_queue_4, kill_switch, protocol, next_prot_queue, event):
    while kill_switch.qsize() == 0:
        if len(next_prot_queue) != 0:
            protocol_new = next_prot_queue.get()
            if protocol_new != protocol:
                comms_queue_1.put(protocol)
                comms_queue_2.put(protocol)
                comms_queue_3.put(protocol)
        event.wait(0.05)
    exit()

def WLED (comms_queue_1, kill_switch):
    pass

def Air_DMX (comms_queue_2, comms_queue_4, kill_switch, framerate, universes):
    start = True
    is_active = False
    sender = sacn.sACNsender(fps=framerate)
    sender.start()
    sender.activate_output(1)
    sender.activate_output(2)
    sender[1].destination = "127.0.0.1"
    sender[2].destination = "127.0.0.1"
    while kill_switch.qsize() == 0:
        try:
            #protocol = comms_queue_2.get(blocking=False)
            protocol = "E1.31"
        except:
            protocol = "null"
            wpt.sleep(0.2)
        if protocol != "E1.31" and protocol !="null":
            print("here")
            if is_active:
                comms_queue_4.put(False)
                wpt.sleep(0.1)
                sender.deactivate_output(1)
                sender.deactivate_output(2)
                is_active = False
        else:
            if start:
                sender.activate_output(1)
                sender.activate_output(2)
                start = False
                is_active = True
                RGB_data, RGBW_data = Flat_Colour_Operator(universes)
                Air_DMX_Output(sender, universes, RGB_data, RGBW_data)
                for x in range(2 * framerate):
                    init_time = wpt.time()
                    colour_RGB = np.array([0, 0, int(255 * (x /255)/(2 * framerate/255))])
                    colour_RGBW = np.array([0, 0, int(255 * (x / 255) / (2 * framerate / 255)), 0])
                    RGB_data, RGBW_data = Flat_Colour_Operator(universes, colour_RGB, colour_RGBW)
                    #print(RGB_data)
                    Air_DMX_Output(sender, universes, RGB_data, RGBW_data)
                    wpt.sleep(1/framerate - (wpt.time()-init_time))
                comms_queue_4.put(True)
                #exit()


def Flat_Colour_Operator(universes, colour_RGB=np.array([0,0,0],dtype=np.uint8), colour_RGBW=np.array([0,0,0,0],dtype=np.uint8)):   # Also used for universe initialisation
    RGB_data = np.zeros((0,3),dtype=np.uint8)
    RGBW_data = np.zeros((0,4),dtype=np.uint8)
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




def Air_DMX_Output(sender, universes, RGB_data, RGBW_data):
    last_index_RGB = 0
    last_index_RGBW = 0
    for count, target in enumerate(universes):
        if target[1] == "RGB":
            sender[count + 1].dmx_data = RGB_data[last_index_RGB:last_index_RGB + int(target[0])].flatten().tolist()
        elif target[1] == "RGBW":
            sender[count + 1].dmx_data = RGBW_data[last_index_RGBW:last_index_RGBW + int(target[0])].flatten().tolist()




def Air_DMX_Streamer (comms_queue_4, kill_switch):
    status = False
    pattern = "Bg"
    while kill_switch.qsize() == 0:
        if not status:
            status = comms_queue_4.get()
        else:
            try:
                status = comms_queue_4.get(blocking=False)
            except:
                status = True
            #if status:


if __name__ == "__main__":
    comms_queue_1 = queue.Queue()
    comms_queue_2 = queue.Queue()
    comms_queue_3 = queue.Queue()
    comms_queue_4 = queue.Queue()
    kill_switch = queue.Queue()
    framerate = 60
    comms_queue_2.put("E1.31")
    universes = np.array([[150, "RGB", 1], [50, "RGB", 2]])
    th.Thread(target=Air_DMX, args=(comms_queue_2, comms_queue_4, kill_switch, framerate, universes)).start()
