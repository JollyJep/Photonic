import requests as rq
import sacn
import queue


class Communication_System:
    def __init__(self, devices, comms_queue, initial_protocol="E1.13", framerate=60):
        self.devices = devices      #List of devices, contains mac addresses, number of LEDS etc
        self.comms = comms_queue    #Threading queue for inter code communications
        self.protocol = initial_protocol    #E1.13 or WLED or LEDfx
        self.framerate = framerate      # Maximum framerate for E1.13 protocol, irrelevent for other protocols


    def inter_code_comms(self):
        live = True
        while live:
            local_data = self.comms.get()
            if type(local_data) == bool:
                live = False
                break
            else:
                self.protocol_handler(local_data)


    def protocol_handler(self, data):
