import queue
import threading as th
import time

import numpy as np
import sacn
import win_precise_time as wpt
from lib import Lighting_Funcs as lf
from Lighting_Modules_Air_DMX import Background as bg

def Communication_Daemon(comms_queue_1, comms_queue_2, comms_queue_3, comms_queue_4, kill_switch, protocol, next_prot_queue, event):
    while kill_switch.qsize() == 0:
        if len(next_prot_queue) != 0:
            protocol_new = next_prot_queue.get()
            if protocol_new != protocol:
                comms_queue_1.put(protocol)
                comms_queue_2.put(protocol)
                comms_queue_3.put(protocol)
        wpt.sleep(0.05)
    exit()

def WLED (comms_queue_1, kill_switch):
    pass

def Air_DMX (comms_queue_2, comms_queue_4, kill_switch, framerate, universes):
    start = True
    is_active = False
    sender = sacn.sACNsender(fps=framerate)
    sender.start()
    sender.activate_output(1)           # Needs to be made variable. Only hard coded for now
    sender.activate_output(2)
    sender[1].destination = "dans_bedroom.local"
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
                RGB_data, RGBW_data = lf.Flat_Colour_Operator(universes)
                Air_DMX_Output(sender, universes, RGB_data, RGBW_data)
                for x in range(2 * framerate):
                    init_time = wpt.time()
                    colour_RGB = np.array([0, 0, int(255 * (x /255)/(2 * framerate/255))])
                    colour_RGBW = np.array([0, 0, int(255 * (x / 255) / (2 * framerate / 255)), 0])
                    RGB_data, RGBW_data = lf.Flat_Colour_Operator(universes, colour_RGB, colour_RGBW)
                    Air_DMX_Output(sender, universes, RGB_data, RGBW_data)
                    wpt.sleep(1/framerate - (wpt.time()-init_time))
                comms_queue_4.put(True)
                #exit()


def Air_DMX_Output(sender, universes, RGB_data, RGBW_data):
    last_index_RGB = 0
    last_index_RGBW = 0
    for count, target in enumerate(universes):
        if target[1] == "RGB":
            sender[count + 1].dmx_data = RGB_data[last_index_RGB:last_index_RGB + int(target[0])].flatten().tolist()
            last_index_RGB += int(target[0])
        elif target[1] == "RGBW":
            sender[count + 1].dmx_data = RGBW_data[last_index_RGBW:last_index_RGBW + int(target[0])].flatten().tolist()
            last_index_RGB += int(target[1])




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
