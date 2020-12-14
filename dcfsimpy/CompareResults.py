import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st

from .Times import *

plt.close("all")
MSE_NAMES = {0: "MSE-NS-3.30.1", 1: "MSE-NS-3.31", 2: "MSE-AM", 3: "MSE-MS"}
results_thr = "reference-data/results_thr-24.csv"
results_pcoll = "reference-data/results_p_coll-24.csv"


def calculate_p_coll_mse(path, notes=""):
    results = pd.read_csv(results_pcoll, delimiter=",")
    results_dict = results.iloc[0:5, 0:10].to_dict()
    new_results = pd.read_csv(f"{path}results.csv", delimiter=",").T
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
    plt.savefig(f"{path}pdf/P_COLL_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse(path, notes=""):
    results = pd.read_csv(results_thr, delimiter=",")
    results_dict = results.iloc[0:4, 0:10].to_dict()
    new_results = pd.read_csv(f"{path}results-mean.csv", delimiter=",").T
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
    plt.savefig(f"{path}pdf/THR_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse_stderr(path, notes=""):
    results = pd.read_csv(results_thr, delimiter=",")
    dcf_results = pd.read_csv(f"{path}results.csv", delimiter=",")
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
        f"{os.getcwd()}/reference-data/ns-3.30.1.csv", delimiter=",", header=None
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
        f"{os.getcwd()}/reference-data/ns-3.31.csv", delimiter=",", header=None
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
    plt.legend(results.iloc[[2, -1, 0, 1], 10].tolist())
    plt.savefig(f"{path}pdf/THR_PER_STATION_ERR.pdf")
    plt.show()


def plot_thr(times_thr, path):
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
    plt.savefig(f"{path}pdf/THR_Comparison.pdf")
    plt.show()


def calculate_mean_and_std(file, file_mean):
    data = pd.read_csv(file, delimiter=",")
    df = pd.DataFrame(data.groupby(["N_OF_STATIONS"]).mean())
    df["THR_STD"] = data.groupby(["N_OF_STATIONS"])["THR"].std()
    df.to_csv(file_mean)


def show_backoffs(path):
    plt.figure()
    data = pd.read_csv(f"{path}backoffs.csv", delimiter=",")
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
    plt.savefig(f"{path}pdf/Backoffs.pdf")
    plt.show()
    pd_merged = pd.DataFrame.from_dict(merged)
    plt.figure()
    ax = pd_merged.T.plot.bar(legend=False)
    ax.set_yscale("log")
    ax.set_xlabel("Backoff range")
    ax.set_ylabel("Frequency")
    plt.savefig(f"{path}pdf/BackoffsMerged.pdf")
    plt.show()


def show_payload(csv_name, file_mean, notes=""):
    dcf_results = pd.read_csv(csv_name, delimiter=",")
    dcf_results_mean = pd.read_csv(file_mean, delimiter=",")
    ns3_df = pd.read_csv("csv_results/change_payload_ns3.csv")
    ns3_results = pd.DataFrame(ns3_df.groupby(["PAYLOAD"]).mean())
    alpha = 0.05
    std = dcf_results.groupby("PAYLOAD").std().loc[:, "THR"]
    n = dcf_results.groupby("PAYLOAD").count().loc[:, "THR"]
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    plt.errorbar(
        dcf_results_mean.PAYLOAD, dcf_results_mean.THR, yerr=yerr, fmt="--", capsize=4,
    )
    dcf_results_mean["THR_NS3"] = ns3_results["THR"].tolist()
    std = ns3_df.groupby("PAYLOAD").std().loc[:, "THR"]
    n = ns3_df.groupby("PAYLOAD").count().loc[:, "THR"]
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    plt.errorbar(
        dcf_results_mean.PAYLOAD,
        dcf_results_mean.THR_NS3,
        yerr=yerr,
        fmt="--",
        capsize=4,
    )
    plt.xlabel("Payload size [B]")
    plt.ylabel("Throughput [Mb/s]")
    plt.legend(["DCF-SimPy", "ns-3.31"])
    plt.savefig("pdf/CHANGING_PAYLOAD.pdf")
    plt.show()


def show_mcs(csv_name, csv_mean, notes=""):
    results = pd.read_csv(csv_name, delimiter=",")
    dcf_results_mean = pd.read_csv(csv_mean, delimiter=",")
    ns3_df = pd.read_csv("csv_results/change_mcs_ns3.csv")
    ns3_results = pd.DataFrame(ns3_df.groupby(["MCS"]).mean())
    alpha = 0.05
    std = results.groupby("MCS").std().loc[:, "THR"]
    n = results.groupby("MCS").count().loc[:, "THR"]
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    print(dcf_results_mean.head())

    dcf_results_mean["THR_NS3"] = ns3_results["THR"].tolist()

    std = ns3_df.groupby("MCS").std().loc[:, "THR"]
    n = ns3_df.groupby("MCS").count().loc[:, "THR"]
    yerr2 = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    dcf_results_mean.plot(
        x="MCS",
        y=["THR", "THR_NS3"],
        kind="bar",
        yerr=[yerr, yerr2],
        align="center",
        alpha=1,
        ecolor="black",
        capsize=5,
        rot=0,
    )
    plt.xlabel("MCS")
    plt.ylabel("Throughput [Mb/s]")
    plt.legend(["DCF-SimPy", "ns-3.31"])
    plt.savefig("pdf/MCS_CHANGE.pdf")
    plt.show()


def plot_by_multiple_cw(csv_name):
    new_results = pd.read_csv(csv_name, delimiter=",").loc[
        :, ["N_OF_STATIONS", "THR", "CW_MIN"]
    ]
    cw = new_results.loc[new_results["N_OF_STATIONS"] == 5]["CW_MIN"].to_list()
    print(cw)
    plt.figure()
    plt.plot(cw, new_results.loc[new_results["N_OF_STATIONS"] == 5]["THR"] / 54, "-bo")
    plt.plot(cw, new_results.loc[new_results["N_OF_STATIONS"] == 10]["THR"] / 54, "-sb")
    plt.plot(
        cw,
        new_results.loc[new_results["N_OF_STATIONS"] == 20]["THR"] / 54,
        "-bo",
        fillstyle="none",
    )
    plt.plot(
        cw,
        new_results.loc[new_results["N_OF_STATIONS"] == 50]["THR"] / 54,
        "-bs",
        fillstyle="none",
    )
    plt.xscale("log")
    plt.xticks(cw, [str(n + 1) for n in cw])
    plt.legend(["n=5", "n=10", "n=20", "n=50"])
    plt.xlabel("Cw_min size")
    plt.ylabel("Normalized throughput")
    plt.title("Saturation throughput vs cw_min")
    plt.savefig("pdf/CW_Comparison.pdf")
    plt.show()


def show_results_changing_stations(path):
    file = f"{path}results.csv"
    file_mean = f"{path}results-mean.csv"
    calculate_mean_and_std(file, file_mean)
    os.mkdir(f"{path}pdf")
    calculate_p_coll_mse(path)
    calculate_thr_mse_stderr(path)
    calculate_thr_mse(path)
    plot_thr(Times().get_thr(), path)
    show_backoffs(path)


def show_results_changing_payload(path):
    file = f"{path}results.csv"
    file_mean = f"{path}results-mean.csv"
    calculate_mean_and_std(file, file_mean)
    os.mkdir(f"{path}pdf")
    show_payload(file, file_mean)


def show_results_changing_mcs(path):
    file = f"{path}results.csv"
    file_mean = f"{path}results-mean.csv"
    calculate_mean_and_std(file, file_mean)
    os.mkdir(f"{path}pdf")
    show_mcs(file, file_mean)


def show_results_changing_cw(path):
    file = f"{path}results.csv"
    file_mean = f"{path}results-mean.csv"
    calculate_mean_and_std(file, file_mean)
    os.mkdir(f"{path}pdf")
    plot_by_multiple_cw(file_mean)
