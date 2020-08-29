import random
import simpy
import logging
import time
import pandas as pd
import threading
import Times as t
from CompareResults import show_results
from dataclasses import dataclass, field
from typing import List

colors = [
    "\033[30m",
    "\033[32m",
    "\033[31m",
    "\033[33m",
    "\033[34m",
    "\033[35m",
    "\033[36m",
    "\033[37m",
]  # colors to distinguish stations in output
logging.basicConfig(format="%(message)s", level=logging.ERROR)


DATA_SIZE = 1472  # size od paylod in b
CW_MIN = 15  # min cw window size
CW_MAX = 1023  # max cw window size
R_limit = 7  # max count of failed retransmissions before cw reset

SIMULATION_TIME = 100000000  # time of simulation in un
SIMULATION_TIME = 10000
STATION_RANGE = 10  # max count of station in simulation
SIMS_PER_STATION_NUM = 10  # runs per station count

big_num = 10000000  # some big number for transmitting query preemption
backoffs = {
    key: [0 for i in range(1, STATION_RANGE + 1)] for key in range(CW_MAX + 1)
}  # dict for storing drawn Back Offs


def log(station, mes: str) -> None:
    logging.info(
        f"{station.col}Time: {station.env.now} Station: {station.name} Message: {mes}"
    )


class Station:
    """Class representing """

    def __init__(
        self,
        env: simpy.Environment,
        name: str,
        channel: dataclass,
        cw_min: int = CW_MIN,
        cw_max: int = CW_MAX,
    ):
        self.name = name  # name of the station
        self.env = env  # current environment
        self.col = random.choice(colors)  # color of output
        self.frame_to_send = None  #
        self.succeeded_transmissions = 0
        self.failed_transmissions = 0
        self.failed_transmissions_in_row = 0
        self.cw_min = cw_min
        self.cw_max = cw_max
        self.channel = channel
        env.process(self.start())
        self.process = None
        self.event = env.event()

    def start(self):
        while True:
            self.frame_to_send = self.generate_new_frame()
            was_sent = False
            while not was_sent:
                self.process = self.env.process(self.wait_back_off())
                yield self.process
                was_sent = yield self.env.process(self.send_frame())

    def wait_back_off(self):
        back_off_time = self.generate_new_back_off_time(
            self.failed_transmissions_in_row
        )  # generate the new Back Off time
        while back_off_time > -1:
            try:
                with self.channel.tx_lock.request() as req:  # wait for the lock/idle channel
                    yield req
                back_off_time += t.t_difs  # add DIFS time
                log(self, f"Starting to wait backoff: ({back_off_time})u...")
                start = self.env.now  # store the current simulation time
                self.channel.back_off_list.append(
                    self
                )  # join the list off stations which are waiting Back Offs
                yield self.env.timeout(
                    back_off_time
                )  # join the environment action queue
                log(self, f"Backoff waited, sending frame...")
                back_off_time = -1  # leave the loop
                self.channel.back_off_list.remove(
                    self
                )  # leave the waiting list as Back Off was waited successfully
            except simpy.Interrupt:  # handle the interruptions from transmitting stations
                log(self, "Waiting was interrupted, waiting to resume backoff...")
                back_off_time -= (
                    self.env.now - start
                )  # set the Back Off to the remaining one
                back_off_time -= 9  # simulate the delay of sensing the channel state

    def send_frame(self):
        self.channel.tx_list.append(self)
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
                    yield self.env.timeout(t.get_ack_frame_time())
                    self.channel.tx_list.clear()
                    self.channel.tx_queue.release(res)
                    return was_sent
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

    def generate_new_back_off_time(self, failed_transmissions_in_row):
        upper_limit = (
            pow(2, failed_transmissions_in_row) * (self.cw_min + 1) - 1
        )  # define the upper limit basing on  unsuccessful transmissions in the row
        upper_limit = (
            upper_limit if upper_limit <= self.cw_max else self.cw_max
        )  # set upper limit to CW Max if is bigger then this parameter
        back_off = random.randint(0, upper_limit)  # draw the back off value
        backoffs[back_off][
            self.channel.n_of_stations - 1
        ] += 1  # store drawn value for future analyzes
        return back_off * t.t_slot

    def generate_new_frame(self):
        # data_size = random.randrange(0, 2304)
        data_size = DATA_SIZE
        frame_length = t.get_ppdu_frame_time(data_size)
        return Frame(frame_length, self.name, self.col, data_size, self.env.now)

    def sent_failed(self):
        log(self, "There was a collision")
        self.frame_to_send.number_of_retransmissions += 1
        self.channel.failed_transmissions += 1
        self.failed_transmissions += 1
        self.failed_transmissions_in_row += 1
        log(self, self.channel.failed_transmissions)
        if self.frame_to_send.number_of_retransmissions > R_limit:
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
        return True


@dataclass()
class Channel:
    tx_queue: simpy.PreemptiveResource
    tx_lock: simpy.Resource
    n_of_stations: int
    tx_list: List[Station] = field(default_factory=list)
    back_off_list: List[Station] = field(default_factory=list)
    failed_transmissions: int = 0
    succeeded_transmissions: int = 0
    bytes_sent: int = 0


@dataclass()
class Frame:
    frame_time: int
    station_name: str
    col: str
    data_size: int
    t_start: int
    number_of_retransmissions: int = 0
    t_end: int = None
    t_to_send: int = None

    def __repr__(self):
        return (
            self.col
            + "Frame: start=%d, end=%d, frame_time=%d, retransmissions=%d"
            % (self.t_start, self.t_end, self.t_to_send, self.number_of_retransmissions)
        )


def run_simulation(number_of_stations, seed):
    random.seed(seed * 33)
    environment = simpy.Environment()
    channel = Channel(
        simpy.PreemptiveResource(environment, capacity=1),
        simpy.Resource(environment, capacity=1),
        number_of_stations,
    )
    for i in range(1, number_of_stations + 1):
        Station(environment, "Station {}".format(i), channel)
    environment.run(until=SIMULATION_TIME)
    p_coll = "{:.4f}".format(
        channel.failed_transmissions
        / (channel.failed_transmissions + channel.succeeded_transmissions)
    )
    print(
        f"SEED = {seed} N={number_of_stations} CW_MIN = {CW_MIN} CW_MAX = {CW_MAX}  PCOLL: {p_coll} THR: {(channel.bytes_sent*8)/SIMULATION_TIME} "
        f"FAILED_TRANSMISSIONS: {channel.failed_transmissions}"
        f" SUCCEEDED_TRANSMISSION {channel.succeeded_transmissions}"
    )
    add_to_results(p_coll, channel, number_of_stations)


def add_to_results(p_coll, channel, n):
    results.setdefault("TIMESTAMP", []).append(time.time())
    results.setdefault("CW_MIN", []).append(CW_MIN)
    results.setdefault("CW_MAX", []).append(CW_MAX)
    results.setdefault("N_OF_STATIONS", []).append(n)
    results.setdefault("SEED", []).append(seed)
    results.setdefault("P_COLL", []).append(p_coll)
    results.setdefault("THR", []).append((channel.bytes_sent * 8) / SIMULATION_TIME)
    results.setdefault("FAILED_TRANSMISSIONS", []).append(channel.failed_transmissions)
    results.setdefault("SUCCEEDED_TRANSMISSIONS", []).append(
        channel.succeeded_transmissions
    )


if __name__ == "__main__":
    results = dict()
    for seed in range(1, SIMS_PER_STATION_NUM + 1):
        threads = [
            threading.Thread(target=run_simulation, args=(n, seed * 33,))
            for n in range(1, STATION_RANGE + 1)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    time_now = time.time()
    output_file_name = f"csv/{CW_MIN}-{CW_MAX}-{STATION_RANGE}-{time_now}.csv"
    pd.DataFrame(results).to_csv(output_file_name, index=False)
    pd.DataFrame(dict(sorted(backoffs.items()))).to_csv(
        f"csv_results/{CW_MIN}-{CW_MAX}-{STATION_RANGE}-{time_now}-backoffs.csv",
        index=False,
    )
    show_results(output_file_name)
