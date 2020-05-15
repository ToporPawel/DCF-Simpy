import random
import simpy
import Colors

CW_MIN = 15
ALL_STATIONS = None
TRANSMITTED_FRAMES = []
SIMULATION_TIME = 500
NUM_OF_STATIONS = 5
FAILED_TRANSMISSIONS = 0
SUCCEEDED_TRANSMISSIONS = 0
FRAME_MIN_TIME = 5
FRAME_MAX_TIME = 20
RES = Colors.get_normal()

# TODO use logger instead of print
# TODO Clean up and split into more transparent functions
# TODO Validate if working properly


class Frame:

    def __init__(self, frame_length, station_name):
        self.frame_length = frame_length
        self.number_of_retransmissions = 0
        self.t_start = environment.now
        self.t_end = None
        self.t_to_send = None
        self.station_name = station_name

    def __repr__(self):
        return "Frame: start=%d, end=%d, frame_time=%d, retransmissions=%d" \
               % (self.t_start, self.t_end, self.t_to_send, self.number_of_retransmissions)


def generate_new_frame(station_name):
    frame_length = random.randrange(FRAME_MIN_TIME, FRAME_MAX_TIME)
    return Frame(frame_length, station_name)


def generate_new_backoff():
    return random.randrange(1, CW_MIN)


class Station(object):

    def __init__(self, env, transmission_resource, transmission_store, name, output_color):
        self.name = name
        self.transmission_resource = transmission_resource
        self.transmission_store = transmission_store
        self.env = env
        self.frame_to_send = None
        self.process = env.process(self.wait_to_send())
        self.col = output_color

    def wait_to_send(self):
        while True:
            was_sent_completed = False
            self.frame_to_send = generate_new_frame(self.name)
            print(self.col + "New frame generated from station:{} , time: {}".format(self.name, self.env.now) + RES)
            while not was_sent_completed:
                back_off = generate_new_backoff()
                print(self.col + "Initial backoff: {} for station: {}".format(back_off, self.name) + RES)
                while back_off:
                    print(self.col + "In while backoff {}of station: {}".format(back_off, self.name) + RES)
                    start = self.env.now
                    try:
                        print(self.col + "Waiting backoff to send frame from station: {} time: {}"
                              .format(self.name, self.env.now) + RES)
                        yield self.env.timeout(back_off)
                        back_off = 0
                    except simpy.Interrupt:
                        print(self.col + "Waiting was interrupted, waiting to resume backoff from station: {}, time:{}"
                              .format(self.name, self.env.now) + RES)
                        back_off -= self.env.now - start
                        try:
                            with self.transmission_resource.request() as req:
                                yield req
                        except simpy.Interrupt:
                            print(self.col + "Frame holding lock was sent, resuming backoff from station: {}, time: {}"
                                  .format(self.name, self.env.now) + RES)
                try:
                    print(self.col + "Backoff waited, sending frame from station: {}, time: {}"
                          .format(self.name, self.env.now))
                    yield self.transmission_store.put(self)
                    with self.transmission_resource.request(self.frame_to_send.frame_length) as req:
                        for station in ALL_STATIONS:
                            if station not in self.transmission_store.items:
                                print(self.col + "Informing other station {} about frame transmission started from "
                                                 "station: {}, time: {}"
                                      .format(station.name, self.name, self.env.now) + RES)
                                station.process.interrupt()
                        print(self.col + "Holding transmission lock from station:{}, time:{}"
                              .format(self.name, self.env.now) + RES)
                        yield req
                        yield self.env.timeout(self.frame_to_send.frame_length)
                        print(self.col + "Check if there was any collision..., time: {}".format(self.env.now) + RES)
                        if len(self.transmission_store.items) != 1:
                            print(self.col + "There was collision, retrying, affected frames:{} time:{}"
                                  .format(len(self.transmission_store.items), self.env.now) + RES)
                            for i in range(len(self.transmission_store.items)):
                                station = yield self.transmission_store.get()
                                if station != self:
                                    station.process.interrupt()
                                    station.frame_to_send.number_of_retransmissions += 1
                            self.frame_to_send.number_of_retransmissions += 1
                            raise simpy.Interrupt(None)
                        print(self.col + "Successfully sent frame from station:{}, time: {}"
                              .format(self.name, self.env.now) + RES)
                        was_sent_completed = True
                        self.frame_to_send.t_end = self.env.now
                        self.frame_to_send.t_to_send = self.frame_to_send.t_end - self.frame_to_send.t_start
                        TRANSMITTED_FRAMES.append(self.frame_to_send)
                        global SUCCEEDED_TRANSMISSIONS
                        SUCCEEDED_TRANSMISSIONS += 1
                except simpy.Interrupt:
                    print(self.col + "Collision from station: {}, time: {}".format(self.name, self.env.now) + RES)
                    global FAILED_TRANSMISSIONS
                    FAILED_TRANSMISSIONS += 1


if __name__ == "__main__":
    # random.seed(444)
    environment = simpy.Environment()
    transmission_priority_resource = simpy.PriorityResource(environment, capacity=1)
    transmission_state_store = simpy.Store(environment)
    ALL_STATIONS = [Station(environment, transmission_priority_resource, transmission_state_store, "Station{}"
                            .format(i), Colors.get_color()) for i in range(NUM_OF_STATIONS)]
    print(ALL_STATIONS)
    environment.run(until=SIMULATION_TIME)
    for frame in TRANSMITTED_FRAMES:
        print(frame)
    print("FAILED_TRANSMISSIONS: {}, SUCCEEDED_TRANSMISSION{}".format(FAILED_TRANSMISSIONS, SUCCEEDED_TRANSMISSIONS))
