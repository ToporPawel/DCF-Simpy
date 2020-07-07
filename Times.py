import math
import matplotlib.pyplot as plt

t_slot = 9  # [u]
t_sifs = 16  # [u]
t_difs = 2 * t_slot + t_sifs  # [u]

# phy_data_rate = {"6": 6,"9": 9,"12": 12,"18": 18, "24": 24, "36": 36,"48": 48,"54": 54}  # [Mb/s]
phy_data_rate = 54 * pow(10, -6)  # [Mb/u]
phy_ctr_rate = 6 * pow(10, -6)  # [Mb/u]
n_data = 4 * phy_data_rate  # [b/symbol]
n_ctr = 4 * phy_ctr_rate  # [b/symbol]
ctr_rate = phy_ctr_rate * pow(10, 6)  # [b/u]
data_rate = phy_data_rate * pow(10, 6)  # [b/u]

mac_header = 36 * 8  # [b]
mac_tail = 4 * 8  # [b]

service = 16  # [b]
tail = 6  # [b]

# OFDM
ofdm_preamble = 16  # [u]
ofdm_signal = 24 / ctr_rate  # [u]


def get_ppdu_frame_time(msdu):  # [u]

    # backoff = t_cw * t_slot
    msdu = msdu * 8  # [b]

    # MacFrame
    mac_frame = mac_header + msdu + mac_tail  # [b]

    # PPDU Frame

    ppdu_padding = (16 + mac_frame + 6)/n_data
    ppdu_padding = math.ceil(ppdu_padding)
    ppdu_padding = ppdu_padding * n_data
    ppdu_padding = ppdu_padding - (16 + mac_frame + 6)  # [b]
    cpsdu = service + mac_frame + tail + ppdu_padding  # [b]

    ppdu = ofdm_preamble + ofdm_signal + cpsdu/data_rate  # [u]

    ppdu_tx_time = t_difs + ppdu

    return math.ceil(ppdu_tx_time)


def get_ack_frame_time():
    # ACK Frame
    ack_size = service + 14 * 8 + tail  # [b]
    ack = ofdm_preamble + ofdm_signal + ack_size / ctr_rate  # [u]
    ack_tx_time = t_sifs + ack
    return math.ceil(ack_tx_time)


def get_ack_timeout():
    return 45


def get_thr():
    return (1472*8)/(get_ppdu_frame_time(1472) + get_ack_frame_time())


# print(f"Tx time: {get_ppdu_frame_time(1472) + get_ack_frame_time()} u, Tx speed: {(1472*8*pow(10,6))/(get_ppdu_frame_time(1472) + get_ack_frame_time())/pow(10, 6)} Mb/u")