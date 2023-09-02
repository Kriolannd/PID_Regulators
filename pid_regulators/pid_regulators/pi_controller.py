import os
import time
import numpy as np
import datetime
import logging


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


class StreamProcessing:
    def __init__(self, file_path, regulator, dt):
        self.logfile = open(file_path, "r")
        self.regulator = regulator
        self.dt = dt

        lines = self.logfile.read().strip("\n").split("\n")
        if len(lines) > 1:
            self.historic_info = list(map(self._process_line, lines[1:]))
        else:
            self.historic_info = []
        print(self.historic_info)

        # self.logger = logging.getLogger('logger')
        # if self.logger.hasHandlers():
        #     self.logger.handlers.clear()
        # self.logger.addHandler(logging.FileHandler('F6.txt'))
        # self.logger.info("qwe")

    def _process_line(self, line):
        return float(line.split(";")[1])

    def _follow(self, thefile):
        thefile.seek(0, os.SEEK_END)
        while True:
            line = thefile.readline()
            if not line or line == "\n":
                time.sleep(self.dt)
                continue
            yield line

    def start(self):
        loglines = self._follow(self.logfile)
        for line in loglines:
            self.historic_info.append(self._process_line(line))
            switch = self.regulator.switch(self.historic_info)

            if switch == 1:
                print(1)
                logging.info(str(datetime.datetime.now().strftime("%m.%d.%Y %H:%M:%S.%f")) + ";" + str(switch))


if __name__ == "__main__":
    with open("F3.txt", "r") as f:
        params = f.read().split(";")
        dt = float(params[0])
        t_max, t_min = map(int, params[2:4])

    logging.basicConfig(level=logging.INFO, filename="F6.txt", filemode="a", format="%(message)s")
    StreamProcessing("F4.txt", Regulator(t_min, t_max, (t_max - t_min) * 0.3), dt).start()
