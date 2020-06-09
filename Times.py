Tslot = 9
Tdifs = 34
Tsifs = 16
Tpre = 16
Tphy = 4
Tofdm = 4
Lmac_overhead = 28 # +- in bytes
Lack = 14

PHYdatarate = {"6": 6,"9": 9,"12": 12,"18": 18, "24": 24, "36": 36,"48": 48,"54": 54}
PHYctrrate = 6
Ndata = 4 * PHYdatarate["54"]
Nctr = 4 * 6
Data_size = 1500

def t_time(cw_time):
    return Tdifs + cw_time + 2 * Tpre + 2 * Tphy + Tofdm*((22+8*Lmac_overhead + 8 * Data_size)/ Ndata) + Tsifs + Tofdm*((22 + 8 * Lack ) / Nctr)

def data_rate():
    return (8 * Data_size) / t_time(23)

print(f"Tx time: {t_time(23)}, Tx speed: {data_rate()} Mb/s")