import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import Times as t
import scipy.stats as st

plt.close("all")
MSE_NAMES = {0: "MSE-NS-3.30.1",1: "MSE-NS-3.31", 2: "MSE-AM", 3: "MSE-MS"}
results_thr = "csv_results/results_thr-24.csv"
results_pcoll = "csv_results/results_p_coll-24.csv"

def calculate_p_coll_mse(csv_name, notes=""):
    results = pd.read_csv(results_pcoll, delimiter=",")
    results_dict = results.iloc[0:5, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=",").T
    new_results = {
        str(int(pair["N_OF_STATIONS"])): pair["P_COLL"]
        for pair in new_results.to_dict().values()
    }
    new_results["Name"] = "DCF-SimPy"
    new_results["Notes"] = notes
    for i in range(4):
        mse = 0
        for key in results_dict.keys():
            mse += pow(results_dict[key][i] - new_results[key], 2)
        mse = mse / len(results_dict.keys())
        new_results[MSE_NAMES[i]] = "{:.2E}".format(mse)
    results = results.append(new_results, ignore_index=True)
    results.to_csv(results_pcoll, index=False)
    styles = ["*--", ".--", "1--", "|--", ".--"]
    ax = results.iloc[[0, 1, 2, 3, -1], 0:10].T.plot(style=styles, lw=0.7, ms=8)
    ax.set_xlabel("Number of stations")
    ax.set_ylabel("Collision probability")
    x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels(x_ticks)
    ax.legend(results.iloc[[0, 1, 2, 3, -1], 10].tolist())
    print(
        "\ncalculate_p_coll_mse\nMSE for DCF-SimPy vs:\nns-3.30.1: {}\nns-3.31: {}\nAnalitical model: {}\nMatlab simulation: {}".format(
            *results.iloc[-1, 11:15].tolist()
        )
    )
    plt.savefig("pdf/P_COLL_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse(csv_name, notes=""):
    results = pd.read_csv(results_thr, delimiter=",")
    results_dict = results.iloc[0:4, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=",").T
    new_results = {
        str(int(pair["N_OF_STATIONS"])): pair["THR"]
        for pair in new_results.to_dict().values()
    }
    new_results["Name"] = "DCF-SimPy"
    new_results["Notes"] = notes

    for i in range(3):
        mse = 0
        for key in results_dict.keys():
            mse += pow(results_dict[key][i] - new_results[key], 2)
        mse = mse / len(results_dict.keys())
        new_results[MSE_NAMES[i]] = "{:.2E}".format(mse)
    results = results.append(new_results, ignore_index=True)
    results.to_csv(results_thr, index=False)
    plt.figure()
    ax = results.iloc[[0, 1, 2, -1], 0:10].T.plot(style="--o")
    ax.set_xlabel("Number of stations")
    ax.set_ylabel("Throughput [Mb/s]")
    ax.set_ylim(0, 35)
    x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels(x_ticks)
    ax.legend(results.iloc[[0, 1, 2, -1], 10].tolist())
    print(
        "\ncalculate_thr_mse\nMSE for DCF-SimPy vs:\nns-3.30.1: {}\nns-3.31: {}\nAnalitical model: {}".format(
            *results.iloc[-1, 11:14].tolist()
        )
    )
    plt.savefig("pdf/THR_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse_stderr(csv_name, notes=""):
    results = pd.read_csv(results_thr, delimiter=",")
    dcf_results = pd.read_csv(csv_name, delimiter=",")
    dcf_results.drop("TIMESTAMP", axis=1, inplace=True)
    dcf_results.drop("CW_MIN", axis=1, inplace=True)
    dcf_results.drop("CW_MAX", axis=1, inplace=True)
    dcf_results.drop("SEED", axis=1, inplace=True)
    dcf_results.drop("P_COLL", axis=1, inplace=True)
    dcf_results.drop("FAILED_TRANSMISSIONS", axis=1, inplace=True)
    dcf_results.drop("SUCCEEDED_TRANSMISSIONS", axis=1, inplace=True)
    alpha = 0.05
    std = dcf_results.groupby("N_OF_STATIONS").std().loc[:, "THR"]
    n = dcf_results.groupby("N_OF_STATIONS").count().loc[:, "THR"]
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    dcf_results_mean = dcf_results.groupby(["N_OF_STATIONS"]).mean()
    plt.errorbar(
        [i for i in range(0, 10)],
        dcf_results_mean.loc[:, "THR"],
        yerr=yerr,
        fmt="--",
        capsize=4,
    )
    ns_3_30_1_results = pd.read_csv(
        "csv_results/ns-3.30.1.csv", delimiter=",", header=None
    ).T
    std = ns_3_30_1_results.std(axis=0, skipna=True)
    n = ns_3_30_1_results.count(axis=0)
    ns_3_30_1_results_mean = ns_3_30_1_results.mean(axis=0)
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    plt.errorbar(
        [i for i in range(0, 10)],
        ns_3_30_1_results_mean,
        yerr=yerr,
        fmt="--",
        capsize=4,
    )
    ns_3_31_results = pd.read_csv(
        "csv_results/ns-3.31.csv", delimiter=",", header=None
    ).T
    std = ns_3_31_results.std(axis=0, skipna=True)
    n = ns_3_31_results.count(axis=0)
    ns_3_31_results_mean = ns_3_31_results.mean(axis=0)
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    plt.errorbar(
        [i for i in range(0, 10)], ns_3_31_results_mean, yerr=yerr, fmt="--", capsize=4,
    )
    plt.plot(results.iloc[2, 0:10].T, "--o")

    plt.xlabel("Number of stations")
    plt.ylabel("Throughput [Mb/s]")
    # plt.ylim(0, 35)
    # # # x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # # # plt.xticks(range(len(x_ticks)))
    # # # plt.xticklabels(x_ticks)
    plt.legend(results.iloc[[2, -1, 0, 1], 10].tolist())
    plt.savefig("pdf/THR_PER_STATION_ERR.pdf")
    plt.show()


def plot_thr(times_thr):
    times_thr = float("{:.4f}".format(times_thr))
    # matlab_thr = 34.6014
    matlab_thr = 37.0800
    ns_3_30_1_thr = 36.1225
    ns_3_31_thr = 36.1296
    # wifi_airtime_calculator = 35.0
    wifi_airtime_calculator = 37.0
    names = ["Analytical model", "DCF-SimPy", "Wi-Fi AirTime", "ns-3.30.1", "ns-3.31"]
    values = [
        matlab_thr,
        times_thr,
        wifi_airtime_calculator,
        ns_3_30_1_thr,
        ns_3_31_thr,
    ]
    plt.figure()
    plt.bar(names, values)
    plt.ylabel("Throughput [Mb/s]")
    plt.xticks(rotation=10)
    plt.savefig("pdf/THR_Comparison.pdf")
    plt.show()


def calculate_mean_and_std(csv_name):
    data = pd.read_csv(csv_name, delimiter=",")
    df = pd.DataFrame(data.groupby(["N_OF_STATIONS", "PAYLOAD"]).mean())
    df["THR_STD"] = data.groupby(["N_OF_STATIONS", "PAYLOAD"])["THR"].std()
    df.to_csv(f"{csv_name[:-4]}-mean.csv")


def show_backoffs(csv_name):
    plt.figure()
    data = pd.read_csv(csv_name, delimiter=",")
    ranges = [16, 32, 64, 128, 256, 512, 1024]
    merged = {}
    start = 0
    for cw in ranges:
        merged[f"[{start},{cw - 1}]"] = [sum(data.iloc[9, start:cw])]
        start = cw
    ax = data.iloc[9, :].plot(style=".", rot=90)
    ax.set_xlabel("Backoff value")
    ax.set_ylabel("Frequency")
    ax.set_yscale("log")
    ax.set_xscale("linear")
    plt.savefig("pdf/Backoffs.pdf")
    plt.show()
    pd_merged = pd.DataFrame.from_dict(merged)
    plt.figure()
    ax = pd_merged.T.plot.bar(legend=False)
    ax.set_yscale("log")
    ax.set_xlabel("Backoff range")
    ax.set_ylabel("Frequency")
    plt.savefig("pdf/BackoffsMerged.pdf")
    plt.show()


def show_payload(csv_name, notes=""):
    results = pd.read_csv(csv_name, delimiter=",")
    ns3_results = pd.DataFrame(pd.read_csv("csv_results/change_payload_ns3.csv").groupby(["PAYLOAD"]).mean())

    results["THR_NS3"] = ns3_results["THR"].tolist()
    print(results)
    ax = results.plot(x="PAYLOAD", y=["THR", "THR_NS3"], kind="bar")
    # plt.bar(x=results["PAYLOAD"], y=[results["THR", ns3_results["THR"]]])
    ax.set_xlabel("Payload size [B]")
    ax.set_ylabel("Throughput [Mb/s]")

    plt.savefig("pdf/CHANGING_PAYLOAD.pdf")
    plt.show()


# def calculate_mean():
#     with open("results.txt", "r") as f:
#         res = {'1': [0,0], '2': [0,0],'3': [0,0],'4': [0,0],'5': [0,0],'6': [0,0],'7': [0,0],'8': [0,0],'9': [0,0],'10': [0,0]}
#         line = f.readline()
#         while line:
#             n = line.split(": ")[1].replace("\n", "")
#             res[n][0] += float(f.readline().split(": ")[1].split(" ")[0].replace("\n", ""))
#             res[n][1] += float(f.readline().split(": ")[1].replace("\n", ""))
#             line = f.readline()
#         for key in res.keys():
#             res[key][0] = "{:.4f}".format(res[key][0] / 10)
#             res[key][1] = "{:.4f}".format(res[key][1] / 10)
#         frame = pd.DataFrame.from_dict(res)
#         frame.to_csv("results.csv")
#         print(frame)


def show_results(file):
    file_mean = f"{file[:-4]}-mean.csv"
    calculate_mean_and_std(file)
    # calculate_p_coll_mse(file_mean)
    # calculate_thr_mse_stderr(file)
    # calculate_thr_mse(file_mean)
    # plot_thr(t.get_thr(1472))
    # show_backoffs("csv_results/final.csv")
    show_payload(file_mean)


if __name__ == "__main__":
    # show_results("csv/final.csv")
    show_results("csv/different-payload-15-1023-10-2020-11-28-12-36-1606563419.csv")