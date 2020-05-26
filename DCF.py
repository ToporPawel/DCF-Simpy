import random
import simpy
import Colors
import logging

FRAME_LENGTH = 10
CW_MIN = 1023
ALL_STATIONS = None
TRANSMITTED_FRAMES = []
SIMULATION_TIME = 1000
NUM_OF_STATIONS = 5
FAILED_TRANSMISSIONS = 0
SUCCEEDED_TRANSMISSIONS = 0
FRAME_MIN_TIME = 5
FRAME_MAX_TIME = 20
RES = Colors.get_normal()
TRANSMITTING_STATIONS = []
logging.basicConfig(format='%(message)s', level=logging.INFO)

# TODO Clean up and split into more transparent functions


class Frame:

    def __init__(self, frame_length, station_name, output_color):
        self.frame_length = frame_length
        self.number_of_retransmissions = 0
        self.t_start = environment.now
        self.t_end = None
        self.t_to_send = None
        self.station_name = station_name
        self.col = output_color

    def __repr__(self):
        return self.col + "Frame: start=%d, end=%d, frame_time=%d, retransmissions=%d" \
               % (self.t_start, self.t_end, self.t_to_send, self.number_of_retransmissions)


def generate_new_frame(station_name, output_color):
    # frame_length = random.randrange(FRAME_MIN_TIME, FRAME_MAX_TIME)
    frame_length = FRAME_LENGTH
    return Frame(frame_length, station_name, output_color)


def generate_new_backoff():
    return random.randint(0, CW_MIN)


def log(station, mes):
    logging.info(station.col + f"Time: {station.env.now} Station: {station.name} Message: {mes}" + RES)


class Station(object):

    def __init__(self, env, transmission_resource, transmission_store, name, output_color):
        self.name = name
        self.transmission_resource = transmission_resource
        # self.transmission_store = transmission_store
        self.env = env
        self.frame_to_send = None
        self.process = env.process(self.wait_to_send())
        self.col = output_color
        self.succeeded_transmissions = 0
        self.failed_transmissions = 0

    def wait_to_send(self):
        while True:
            was_sent_completed = False
            self.frame_to_send = generate_new_frame(self.name, self.col)
            log(self, "New frame generated")
            while not was_sent_completed:
                back_off = generate_new_backoff()
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
                        try:
                            with self.transmission_resource.request() as req:
                                yield req
                        except simpy.Interrupt:
                            log(self, "Frame holding lock was sent, resuming backoff")
                try:
                    log(self, "Backoff completed, sending frame")
                    TRANSMITTING_STATIONS.append(self)
                    with self.transmission_resource.request(self.frame_to_send.frame_length) as req:
                        for station in ALL_STATIONS:
                            if station not in TRANSMITTING_STATIONS:
                                # print(self.col + "Informing station {} about frame transmission started from "
                                #                  "station: {}, time: {}"
                                #       .format(station.name, self.name, self.env.now) + RES)
                                log(self, f"Informing station {station.name} about frame transmission started")
                                station.process.interrupt()
                        log(self, "Holding transmission lock")
                        yield req
                        yield self.env.timeout(self.frame_to_send.frame_length)
                        # print(self.col + "Check if there was any collision..., time: {}".format(self.env.now) + RES)
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
                        log(self, "Successfully sent frame")
                        was_sent_completed = True
                        self.frame_to_send.t_end = self.env.now
                        self.frame_to_send.t_to_send = self.frame_to_send.t_end - self.frame_to_send.t_start
                        TRANSMITTED_FRAMES.append(self.frame_to_send)
                        global SUCCEEDED_TRANSMISSIONS
                        SUCCEEDED_TRANSMISSIONS += 1
                        self.succeeded_transmissions += 1
                except simpy.Interrupt:
                    log(self, "Collision")
                    global FAILED_TRANSMISSIONS
                    FAILED_TRANSMISSIONS += 1
                    self.failed_transmissions +=1

    def get_station_statistics(self):
        sum_failed_succeeded = 1 if self.succeeded_transmissions + self.failed_transmissions == 0 else self.succeeded_transmissions + self.failed_transmissions
        return self.col + f"Station name: {self.name}, Succeeded transmissions: {self.succeeded_transmissions}, Failed transmissions: " \
               f"{self.failed_transmissions}," \
               f" PCOLL: {self.failed_transmissions/sum_failed_succeeded}" + RES


if __name__ == "__main__":
    # random.seed(444)
    environment = simpy.Environment()
    transmission_priority_resource = simpy.PriorityResource(environment, capacity=1)
    transmission_state_store = simpy.Store(environment)
    ALL_STATIONS = [Station(environment, transmission_priority_resource, transmission_state_store, "Station{}"
                            .format(i), Colors.get_color()) for i in range(NUM_OF_STATIONS)]
    print(ALL_STATIONS)
    environment.run(until=SIMULATION_TIME)
    # for frame in TRANSMITTED_FRAMES:
    #     print(frame)
    print("GLOBAL FAILED_TRANSMISSIONS: {}, SUCCEEDED_TRANSMISSION{}, PCOLL: {}"
          .format(FAILED_TRANSMISSIONS, SUCCEEDED_TRANSMISSIONS, FAILED_TRANSMISSIONS/(FAILED_TRANSMISSIONS + SUCCEEDED_TRANSMISSIONS)))
    for station in ALL_STATIONS:
        print(station.get_station_statistics())
