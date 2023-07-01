import queue
import threading as th
import time
import sacn
import win_precise_time as wpt
from Lighting_Modules_Air_DMX import Background as bg

def Communication_Daemon(comms_queue_1, comms_queue_2, comms_queue_3, comms_queue_4, kill_switch, protocol, next_prot_queue, event):
    while len(kill_switch.qsize()) == 0:
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

def Air_DMX (comms_queue_2, comms_queue_4, kill_switch, framerate):
    start = True
    is_active = False
    sender = sacn.sACNsender(fps=framerate)
    sender.start()
    sender[1].destination = "192.168.0.10"
    sender[2].destination = "192.168.0.10"
    data_1 = [0, 0, 0] * 150
    data_2 = [0, 0, 0] * 50
    while len(kill_switch.qsize()) == 0:
        try:
            protocol = comms_queue_2.get(blocking=False)
        except:
            protocol = "null"
            wpt.sleep(0.2)
        if protocol != "E1.31" or protocol !="null":
            start = True
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
                data_1 = [0, 0, 0] * 150
                data_2 = [0, 0, 0] * 50
                sender[1].dmx_data = data_1
                sender[2].dmx_data = data_2
                for x in range(2*framerate):
                    init_time = wpt.time()
                    data_1 = [0, 0, int(255 * (x /255)/(120/255))] * 150
                    data_2 = [0, 0, int(255 * (x /255)/(120/255))] * 50
                    sender[1].dmx_data = data_1
                    sender[2].dmx_data = data_2
                    wpt.sleep(1/framerate - (wpt.time()-init_time))
                comms_queue_4.put(True)


def Air_DMX_Streamer (comms_queue_4, kill_switch):
    status = False
    pattern = "Bg"
    while len(kill_switch.qsize()) == 0:
        if not status:
            status = comms_queue_4.get()
        else:
            try:
                status = comms_queue_4.get(blocking=False)
            except:
                status = True
            if status:



event = th.Event()