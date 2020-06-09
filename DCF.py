import random
import simpy
import Colors
import logging
import time
import pandas as pd
import matplotlib.pyplot as plt

FRAME_LENGTH = 10
CW_MIN = 15
CW_MAX = 1023
SIMULATION_TIME = 1000000

STATION_RANGE = 10
SIMS_PER_STATION_NUM = 5

FAILED_TRANSMISSIONS = 0
SUCCEEDED_TRANSMISSIONS = 0
# FRAME_MIN_TIME = 5
# FRAME_MAX_TIME = 20
ALL_STATIONS = None
TRANSMITTED_FRAMES = []
TRANSMITTING_STATIONS = []


logging.basicConfig(format='%(message)s', level=logging.ERROR)


class Frame:

    def __init__(self, frame_length, station_name, output_color, env):
        self.frame_length = frame_length
        self.number_of_retransmissions = 0
        self.t_start = env.now
        self.t_end = None
        self.t_to_send = None
        self.station_name = station_name
        self.col = output_color

    def __repr__(self):
        return self.col + "Frame: start=%d, end=%d, frame_time=%d, retransmissions=%d" \
               % (self.t_start, self.t_end, self.t_to_send, self.number_of_retransmissions)


def log(station, mes):
    logging.info(station.col + f"Time: {station.env.now} Station: {station.name} Message: {mes}" + Colors.get_normal())


class Station(object):
    
    def __init__(self, env, transmission_resource, name, output_color, cw_min=CW_MIN, cw_max=CW_MAX, frame_length=FRAME_LENGTH):
        self.name = name
        self.transmission_resource = transmission_resource
        self.env = env
        self.frame_to_send = None
        self.process = env.process(self.wait_to_send())
        self.col = output_color
        self.succeeded_transmissions = 0
        self.failed_transmissions = 0
        self.cw_min = cw_min
        self.cw_max = cw_max
        self.frame_length = frame_length

    def __repr__(self):
        return self.col + f"{self.name}" + Colors.get_normal()

    def wait_to_send(self):
        while True:
            was_sent_completed = False
            self.frame_to_send = self.generate_new_frame(self.name, self.col, self.env)
            log(self, "New frame generated")
            while not was_sent_completed:
                back_off = self.generate_new_backoff(self.frame_to_send.number_of_retransmissions)
                log(self, f"Initial backoff: {back_off}")
                while back_off:
                    log(self, f"In while backoff {back_off}")
                    start = self.env.now
                    try:
                        log(self, "Waiting backoff to send frame")
                        yield self.env.timeout(back_off)
                        back_off = 0
                    except simpy.Interrupt:
                        log(self, "Waiting was interrupted, waiting to resume backoff")
                        back_off -= self.env.now - start
                        back_off -= 1
                        try:
                            with self.transmission_resource.request() as req:
                                yield req
                        except simpy.Interrupt:
                            log(self, "Frame holding lock was sent, resuming backoff")
                try:
                    log(self, "Backoff waited, sending frame")
                    TRANSMITTING_STATIONS.append(self)
                    with self.transmission_resource.request(self.frame_to_send.frame_length) as req:
                        yield req
                        self.interrupt_other_stations_backoff()
                        log(self, "Holding transmission lock")
                        yield self.env.timeout(self.frame_to_send.frame_length)
                        self.check_if_was_collision()
                        was_sent_completed = self.sent_completed()

                except simpy.Interrupt:
                    self.sent_failed()

    def sent_failed(self):
        log(self, "Collision")
        global FAILED_TRANSMISSIONS
        FAILED_TRANSMISSIONS += 1
        self.failed_transmissions += 1

    def sent_completed(self):
        log(self, "Successfully sent frame")
        self.frame_to_send.t_end = self.env.now
        self.frame_to_send.t_to_send = self.frame_to_send.t_end - self.frame_to_send.t_start
        TRANSMITTED_FRAMES.append(self.frame_to_send)
        global SUCCEEDED_TRANSMISSIONS
        SUCCEEDED_TRANSMISSIONS += 1
        self.succeeded_transmissions += 1
        return True

    def check_if_was_collision(self):
        log(self, "Check if there was any collision...")
        if len(TRANSMITTING_STATIONS) != 1:
            log(self, f"There was collision, retrying, affected frames:{len(TRANSMITTING_STATIONS)}")
            for station in TRANSMITTING_STATIONS:
                if station != self:
                    station.process.interrupt()
                    station.frame_to_send.number_of_retransmissions += 1
            self.frame_to_send.number_of_retransmissions += 1
            TRANSMITTING_STATIONS.clear()
            raise simpy.Interrupt(None)
        TRANSMITTING_STATIONS.clear()

    def interrupt_other_stations_backoff(self):
        for station in ALL_STATIONS:
            if station not in TRANSMITTING_STATIONS:
                log(self, f"Informing station {station.name} about frame transmission started")
                station.process.interrupt()

    def generate_new_frame(self, station_name, output_color, env):
        # frame_length = random.randrange(FRAME_MIN_TIME, FRAME_MAX_TIME)
        frame_length = self.frame_length
        return Frame(frame_length, station_name, output_color, env)

    def generate_new_backoff(self, n):
        upper_limit = pow(2, n) * (self.cw_min + 1) - 1
        upper_limit = upper_limit if upper_limit <= self.cw_max else self.cw_max
        return random.randint(0, upper_limit)

    def get_station_statistics(self):
        sum_failed_succeeded = 1 if self.succeeded_transmissions + self.failed_transmissions == 0 \
            else self.succeeded_transmissions + self.failed_transmissions
        return self.col + f"Station name: {self.name}, Succeeded transmissions: {self.succeeded_transmissions}," \
                          f" Failed transmissions: {self.failed_transmissions} " \
                          f"PCOLL: {self.failed_transmissions/sum_failed_succeeded}" + Colors.get_normal()


def clear_values():
    global FAILED_TRANSMISSIONS, SUCCEEDED_TRANSMISSIONS, ALL_STATIONS, TRANSMITTED_FRAMES, TRANSMITTING_STATIONS
    FAILED_TRANSMISSIONS = 0
    SUCCEEDED_TRANSMISSIONS = 0
    # FRAME_MIN_TIME = 5
    # FRAME_MAX_TIME = 20
    ALL_STATIONS = None
    TRANSMITTED_FRAMES = []
    TRANSMITTING_STATIONS = []


def run_simulation(number_of_stations, seed):
    global ALL_STATIONS
    clear_values()
    random.seed(seed)
    environment = simpy.Environment()
    transmission_priority_resource = simpy.PriorityResource(environment, capacity=1)
    ALL_STATIONS = [Station(environment, transmission_priority_resource, "Station{}"
                            .format(i), Colors.get_color()) for i in range(1, number_of_stations + 1)]
    # print(ALL_STATIONS)
    environment.run(until=SIMULATION_TIME)
    # for frame in TRANSMITTED_FRAMES:
    #     print(frame)
    p_coll = "{:.4f}".format(FAILED_TRANSMISSIONS / (FAILED_TRANSMISSIONS + SUCCEEDED_TRANSMISSIONS))
    print(f"SEED = {seed} N={number_of_stations} CW_MIN = {CW_MIN} CW_MAX = {CW_MAX}  PCOLL: {p_coll} "
          f"FAILED_TRANSMISSIONS: {FAILED_TRANSMISSIONS},"
          f" SUCCEEDED_TRANSMISSION {SUCCEEDED_TRANSMISSIONS}")
    add_to_results(p_coll)
    # for station in ALL_STATIONS:
    #     print(station.get_station_statistics())


def add_to_results(p_coll):
    results["TIMESTAMP"].append(time.time())
    results["CW_MIN"].append(CW_MIN)
    results["CW_MAX"].append(CW_MAX)
    results["N_OF_STATIONS"].append(n)
    results["SEED"].append(seed)
    results["P_COLL"].append(p_coll)
    results["FAILED_TRANSMISSIONS"].append(FAILED_TRANSMISSIONS)
    results["SUCCEEDED_TRANSMISSIONS"].append(SUCCEEDED_TRANSMISSIONS)


if __name__ == "__main__":
    results = {"TIMESTAMP": [],  "CW_MIN": [], "CW_MAX": [], "N_OF_STATIONS": [], "SEED": [], "P_COLL": [],
               "FAILED_TRANSMISSIONS": [], "SUCCEEDED_TRANSMISSIONS": []}
    for seed in range(1, SIMS_PER_STATION_NUM + 1):
        for n in range(1, STATION_RANGE + 1):
            run_simulation(n, seed*33)
    output_file_name = f"{CW_MIN}-{CW_MAX}-{STATION_RANGE}.csv"
    pd.DataFrame(results).to_csv(output_file_name, index=False)
    data = pd.read_csv(output_file_name, delimiter=',')
    plt.figure()
    print(pd.DataFrame(data.groupby(['N_OF_STATIONS'])['P_COLL'].mean()))
    df = pd.DataFrame(data.groupby(['N_OF_STATIONS'])['P_COLL'].mean()).plot(kind='bar')
    df.to_csv(f"{CW_MIN}-{CW_MAX}-{STATION_RANGE}-mean.csv")
    plt.show()


