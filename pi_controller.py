import json
import sys
import time
from threading import Thread

import numpy as np

import requests
from sseclient import SSEClient

import os


class Regulator:
    def __init__(self, t_min, t_max, dt):
        self.t_min = t_min
        self.t_max = t_max
        self.dt = dt
        self.current_state = 1

    def _count_signal(self, t):
        first_idx = next((el for el in enumerate(t) if el[1] > self.t_min), (-1, None))[0]
        res = 0.9 * t[-1] + 0.1 * np.mean(t[first_idx:])
        print("count_signal " + str(res))
        return res

    def _to_work(self, t):
        out_signal = self._count_signal(t)
        if out_signal < self.t_min + self.dt: return 1
        if out_signal > self.t_max - self.dt: return 0
        return self.current_state

    def switch(self, t):
        print("current", self.current_state, "to_work", self._to_work(t))
        if self._to_work(t) == self.current_state:
            return 0
        else:
            self.current_state = self._to_work(t)
            return 1


class ListeningProcess(Thread):
    def __init__(self, regulator, events_url, switch_url):
        super().__init__()

        self.regulator = regulator
        self.events_url = events_url
        self.switch_url = switch_url

        self.historic_info = []

    def run(self):
        while True:
            try:
                events = SSEClient(self.events_url)
                break
            except requests.exceptions.ConnectionError:
                print("Error connecting to " + self.events_url)
                time.sleep(1)

        for event in events:
            if not event.data: continue

            data = json.loads(event.data)
            if "temp_apparent" not in data: continue

            self.historic_info.append(data["temp_apparent"])
            switch = self.regulator.switch(self.historic_info)

            if switch == 1:
                requests.post(self.switch_url)


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(sys.executable), "config.json"), "r") as f:
        config = json.loads(f.read())

    settings = config["settings"]
    connection_params = config["connection"]

    ListeningProcess(Regulator(settings["tMin"], settings["tMax"], (settings["tMax"] - settings["tMin"]) * 0.3),
                     connection_params["eventsUrl"],
                     connection_params["switchUrl"]).start()
