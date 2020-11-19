import math

t_slot = 9  # [us]
t_sifs = 16  # [us]
t_difs = 2 * t_slot + t_sifs  # [us]
ack_timeout = 45  # [us]

# Mac overhead
mac_overhead = 40 * 8  # [b]

# ACK size
ack_size = 14 * 8  # [b]

# overhead
_overhead = 22  # [b]

# OFDM parameters
phy_data_rate = 54 * pow(10, -6)  # [Mb/us] Possible values 6, 9, 12, 18, 24, 36, 48, 54
phy_ctr_rate = 6 * pow(10, -6)  # [Mb/u]
n_data = 4 * phy_data_rate  # [b/symbol]
n_ctr = 4 * phy_ctr_rate  # [b/symbol]
ctr_rate = phy_ctr_rate * pow(10, 6)  # [b/us]
data_rate = phy_data_rate * pow(10, 6)  # [b/us]

ofdm_preamble = 16  # [us]
ofdm_signal = 24 / ctr_rate  # [us]


# Data frame time
def get_ppdu_frame_time(payload):
    msdu = payload * 8  # [b]
    # MacFrame
    mac_frame = mac_overhead + msdu  # [b]
    # PPDU Padding
    ppdu_padding = math.ceil((_overhead + mac_frame) / n_data) * n_data - (
        _overhead + mac_frame
    )
    # CPSDU Frame
    cpsdu = _overhead + mac_frame + ppdu_padding  # [b]
    # PPDU Frame
    ppdu = ofdm_preamble + ofdm_signal + cpsdu / data_rate  # [us]
    ppdu_tx_time = math.ceil(ppdu)
    return ppdu_tx_time  # [us]


# ACK frame time with SIFS
def get_ack_frame_time():
    ack = _overhead + ack_size  # [b]
    ack = ofdm_preamble + ofdm_signal + ack / ctr_rate  # [us]
    ack_tx_time = t_sifs + ack
    return math.ceil(ack_tx_time)  # [us]


# ACK Timeout
def get_ack_timeout():
    return ack_timeout


def get_thr(payload):
    return (payload * 8) / (
        get_ppdu_frame_time(payload) + get_ack_frame_time() + t_difs
    )


print(
    f"Tx time: {t_difs + get_ppdu_frame_time(1472) + get_ack_frame_time()} u, Tx speed: {get_thr(1472)} Mb/u"
)
print(get_ppdu_frame_time(1472) + get_ack_frame_time() + t_difs)
print(get_ppdu_frame_time(1472) + get_ack_timeout() + t_difs)
print(get_ack_frame_time() - t_sifs)
# print(get_ppdu_frame_time(1472), get_ack_timeout(), get_ack_frame_time())
