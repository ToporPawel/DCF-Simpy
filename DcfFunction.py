import random
import simpy
import Colors
import logging
import time
import pandas as pd
import matplotlib.pyplot as plt
import threading
import Times as t
from CompareResults import *
from sklearn import preprocessing

FRAME_LENGTH = 10
DATA_SIZE = 1472
CW_MIN = 3
CW_MAX = 1023
SIMULATION_TIME = 50000000
R_limit = 4

MIN_STATIONS = 5
MAX_STATIONS = 5
SIMS_PER_STATION_NUM = 10

big_num = 10000000


logging.basicConfig(format="%(message)s", level=logging.ERROR)


def log(station, mes):
    logging.info(
        station.col
        + f"Time: {station.env.now} Station: {station.name} Message: {mes}"
        + Colors.get_normal()
    )

class Frame:
    def __init__(self, frame_time, station_name, output_color, env, data_size):
        self.frame_time = frame_time
        self.number_of_retransmissions = 0
        self.t_start = env.now
        self.t_end = None
        self.t_to_send = None
        self.station_name = station_name
        self.col = output_color
        self.data_size = data_size

    def __repr__(self):
        return (
            self.col
            + "Frame: start=%d, end=%d, frame_time=%d, retransmissions=%d"
            % (self.t_start, self.t_end, self.t_to_send, self.number_of_retransmissions)
        )


class Station(object):
    def __init__(self, env, name, channel, cw_min=CW_MIN, cw_max=CW_MAX):
        self.name = name
        self.env = env
        self.col = Colors.get_color()
        self.frame_to_send = None
        self.succeeded_transmissions = 0
        self.failed_transmissions = 0
        self.failed_transmissions_in_row = 0
        self.cw_min = cw_min
        self.cw_max = cw_max
        self.mac_retry_drop = 0
        self.channel = channel
        env.process(self.start())
        self.process = None
        self.event = env.event()
        # self.bytes_sent = 0

    def start(self):
        while True:
            self.frame_to_send = self.generate_new_frame()
            was_sent = False
            while not was_sent:
                self.process = self.env.process(self.wait_back_off())
                yield self.process
                was_sent = yield self.env.process(self.send_frame())

    def wait_back_off(self):
        back_off = self.generate_new_back_off(self.failed_transmissions_in_row)
        while back_off > -1:
            try:
                with self.channel.tx_lock.request() as req:
                    yield req
                back_off += t.t_difs
                log(self, f"Starting to wait backoff: ({back_off})u...")
                start = self.env.now
                self.channel.join_back_off(self)
                yield self.env.timeout(back_off)
                log(self, f"Backoff waited, sending frame...")
                back_off = -1
                self.channel.leave_back_off(self)
            except simpy.Interrupt:
                log(self, "Waiting was interrupted, waiting to resume backoff...")
                back_off -= self.env.now - start
                back_off -= 9
                # self.env.timeout(1)

    def send_frame(self):
        self.channel.join_tx_list(self)
        res = self.channel.tx_queue.request(
            priority=(big_num - self.frame_to_send.frame_time)
        )
        try:
            result = yield res | self.env.timeout(0)
            if res not in result:
                raise simpy.Interrupt("There is a longer frame...")
            with self.channel.tx_lock.request() as lock:
                yield lock
                log(self, self.channel.back_off_list)
                for station in self.channel.back_off_list:
                    station.process.interrupt()
                log(self, self.frame_to_send.frame_time)
                yield self.env.timeout(self.frame_to_send.frame_time)
                self.channel.back_off_list.clear()
                was_sent = self.check_collision()
                if was_sent:
                    # log(self, "master")
                    yield self.env.timeout(t.get_ack_frame_time())
                    self.channel.tx_list.clear()
                    self.channel.tx_queue.release(res)
                    return was_sent
            # log(self, "waiting wck timeout master")
            self.channel.tx_list.clear()
            self.channel.tx_queue.release(res)
            self.channel.tx_queue = simpy.PreemptiveResource(self.env, capacity=1)
            yield self.env.timeout(t.get_ack_timeout())
            return was_sent
        except simpy.Interrupt:
            yield self.env.timeout(self.frame_to_send.frame_time)
        was_sent = self.check_collision()
        if was_sent:
            yield self.env.timeout(t.t_sifs + t.get_ack_frame_time())
        else:
            log(self, "waiting wck timeout slave")
            yield self.env.timeout(t.get_ack_timeout())
        return was_sent

    def check_collision(self):
        if len(self.channel.tx_list) > 1:
            self.sent_failed()
            return False
        else:
            self.sent_completed()
            return True

    def generate_new_back_off(self, n):
        upper_limit = pow(2, n) * (self.cw_min + 1) - 1
        upper_limit = upper_limit if upper_limit <= self.cw_max else self.cw_max
        return random.randint(0, upper_limit) * t.t_slot

    def generate_new_frame(self):
        # data_size = random.randrange(0, 2304)
        data_size = DATA_SIZE
        frame_length = t.get_ppdu_frame_time(data_size)
        return Frame(frame_length, self.name, self.col, self.env, data_size)

    def sent_failed(self):
        log(self, "There was a collision")
        self.frame_to_send.number_of_retransmissions += 1
        self.channel.failed_transmissions += 1
        self.failed_transmissions += 1
        self.failed_transmissions_in_row += 1
        log(self, self.channel.failed_transmissions)
        if self.frame_to_send.number_of_retransmissions > R_limit:
            self.mac_retry_drop += 1
            self.frame_to_send = self.generate_new_frame()
            self.failed_transmissions_in_row = 0

    def sent_completed(self):
        log(self, f"Successfully sent frame, waiting ack: {t.get_ack_frame_time()}")
        self.frame_to_send.t_end = self.env.now
        self.frame_to_send.t_to_send = (
            self.frame_to_send.t_end - self.frame_to_send.t_start
        )
        self.channel.succeeded_transmissions += 1
        self.succeeded_transmissions += 1
        self.failed_transmissions_in_row = 0
        self.channel.bytes_sent += self.frame_to_send.data_size
        # self.channel.total_frame_time += self.frame_to_send.t_to_send + t.get_ack_frame_time()
        # self.bytes_sent += self.frame_to_send.data_size
        # log(self, self.channel.succeeded_transmissions)
        return True


class Channel(object):
    def __init__(self, tx_queue: simpy.PreemptiveResource, env):
        self.tx_queue = tx_queue
        self.tx_list = []
        self.back_off_list = []
        self.tx_lock = simpy.Resource(env, capacity=1)
        self.failed_transmissions = 0
        self.succeeded_transmissions = 0
        self.bytes_sent = 0

    def join_back_off(self, station: Station):
        self.back_off_list.append(station)

    def leave_back_off(self, station: Station):
        self.back_off_list.remove(station)

    def join_tx_list(self, station: Station):
        self.tx_list.append(station)


def run_simulation(number_of_stations, seed, cw_min):
    environment = simpy.Environment()
    channel = Channel(simpy.PreemptiveResource(environment, capacity=1), environment)
    for i in range(1, number_of_stations + 1):
        Station(environment, "Station{}".format(i), channel, cw_min=cw_min)
    environment.run(until=SIMULATION_TIME)
    p_coll = "{:.4f}".format(
        channel.failed_transmissions
        / (channel.failed_transmissions + channel.succeeded_transmissions)
    )
    print(
        f"SEED = {seed} N={number_of_stations} CW_MIN = {cw_min} CW_MAX = {CW_MAX}  PCOLL: {p_coll} THR: {(channel.bytes_sent*8)/SIMULATION_TIME} "
        f"FAILED_TRANSMISSIONS: {channel.failed_transmissions}"
        f" SUCCEEDED_TRANSMISSION {channel.succeeded_transmissions}"
    )
    add_to_results(p_coll, channel, number_of_stations, seed, cw_min)


def add_to_results(p_coll, channel, n, seed, cw_min):
    results["TIMESTAMP"].append(time.time())
    results["CW_MIN"].append(cw_min)
    results["CW_MAX"].append(CW_MAX)
    results["N_OF_STATIONS"].append(n)
    results["SEED"].append(seed)
    results["P_COLL"].append(p_coll)
    results["THR"].append((channel.bytes_sent * 8) / (SIMULATION_TIME ))
    results["FAILED_TRANSMISSIONS"].append(channel.failed_transmissions)
    results["SUCCEEDED_TRANSMISSIONS"].append(channel.succeeded_transmissions)


if __name__ == "__main__":
    results = {
        "TIMESTAMP": [],
        "CW_MIN": [],
        "CW_MAX": [],
        "N_OF_STATIONS": [],
        "SEED": [],
        "P_COLL": [],
        "THR": [],
        "FAILED_TRANSMISSIONS": [],
        "SUCCEEDED_TRANSMISSIONS": [],
    }
    for cw_min in [pow(2, x) - 1 for x in range(2, 11)]:
        for seed in range(1, SIMS_PER_STATION_NUM + 1):
            random.seed(seed * 33)
            threads = [
                threading.Thread(target=run_simulation, args=(n, seed * 33, cw_min))
                for n in [5, 10, 20, 50]
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
    time_now = time.time()
    output_file_name = f"ChangeCW-{MAX_STATIONS}-{MIN_STATIONS}-{time_now}.csv"
    df = pd.DataFrame(results)
    df.to_csv(output_file_name, index=False)
    file_mean = calculate_mean_and_std(output_file_name, group_by=["N_OF_STATIONS", "CW_MIN"])
    plot_by_multiple_cw(file_mean)
    # calculate_p_coll_mse(output_file_name)
    # calculate_thr_mse(output_file_name)
