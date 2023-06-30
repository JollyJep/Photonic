import requests as rq
import win_precise_time as wpt
import sacn
import queue


class Communication_System:
    def __init__(self, devices, comms_queue, framerate=30, universes=(1,2)):
        self.devices = devices      #List of devices, contains local addresses, number of LEDS etc
        self.comms = comms_queue    #Threading queue for inter code communications
        self.framerate = framerate      # Maximum framerate for E1.13 protocol, irrelevent for other protocols. Also determines inter code comm check time
        self.air_dmx = sacn.sACNsender(fps=framerate)
        self.switch = 0     #Turns on/off each system, takes values of 1,2,3 when streaming data
        self.ledfx_url = "http://localhost:8888"
        response = rq.get(f"{self.ledfx_url}/api/devices")
        self.ledfx_devices = response.json()
        self.universes = universes
        self.initialise = True


    def inter_code_comms(self):
        live = True
        while live:
            frame_start = wpt.time()
            try:
                local_data = self.comms.get(block=False)
                if type(local_data) == bool:
                    live = False
                    break
                else:
                    self.protocol = local_data[0]
                    self.protocol_handler(local_data)
                    local_data = ""
                wpt.sleep(1 / self.framerate * self.mult - (wpt.time() - frame_start))
            except:
                wpt.sleep(1 / self.framerate * self.mult -(wpt.time()-frame_start))


    def protocol_handler(self, data):
        if self.protocol == "E1.31":
            if self.switch != 1:
                if self.switch == 2:
                    for device in self.ledfx_devices:
                        if device["config"]["type"] == "wled":
                            device_id = device["id"]
                            rq.delete(f"{self.ledfx_url}/api/devices/{device_id}/effects/active")
                self.switch = 1
                self.air_dmx.start()
                self.initialise = True
            self.wireless_DMX(data)
        elif self.protocol == "LEDfx":
            if self.switch != 2:
                if self.switch == 1:
                    self.air_dmx.deactivate_output(1)
                self.switch = 2
                self.

    def wireless_DMX(self, data):
        if self.initialise:
            self.initialise = False

