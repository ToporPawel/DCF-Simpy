import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import Times as t
import scipy.stats as st

plt.close("all")
MSE_NAMES = {0: "MSE-NS-3", 1: "MSE-AM", 2: "MSE-MS"}


def calculate_p_coll_mse(csv_name, notes=""):
    results = pd.read_csv("csv_results/results_p_coll.csv", delimiter=",")
    results_dict = results.iloc[0:3, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=",").T
    new_results = {
        str(int(pair["N_OF_STATIONS"])): pair["P_COLL"]
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
    results.to_csv("csv_results/results_p_coll.csv", index=False)
    styles = ["*--", ".--", "1--", "|--"]
    ax = results.iloc[[0, 1, 2, -1], 0:10].T.plot(style=styles, lw=0.5)
    ax.set_xlabel("Number of stations")
    ax.set_ylabel("Collision probability")
    x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels(x_ticks)
    ax.legend(results.iloc[[0, 1, 2, -1], 10].tolist())
    ax.text(
        0.58,
        0.13,
        "MSE for DCF-SimPy vs:\nns-3: {}\nAnalitical model: {}\nMatlab simulation: {}".format(
            *results.iloc[-1, 11:14].tolist()
        ),
        bbox={"facecolor": "none", "pad": 10, "edgecolor": "grey"},
        ha="left",
        va="center",
        transform=ax.transAxes,
    )
    plt.savefig("pdf/P_COLL_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse(csv_name, notes=""):
    results = pd.read_csv("csv_results/results_thr.csv", delimiter=",")
    results_dict = results.iloc[0:2, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=",").T
    new_results = {
        str(int(pair["N_OF_STATIONS"])): pair["THR"]
        for pair in new_results.to_dict().values()
    }
    new_results["Name"] = "DCF-SimPy"
    new_results["Notes"] = notes
    for i in range(2):
        mse = 0
        for key in results_dict.keys():
            mse += pow(results_dict[key][i] - new_results[key], 2)
        mse = mse / len(results_dict.keys())
        new_results[MSE_NAMES[i]] = "{:.2E}".format(mse)
    results = results.append(new_results, ignore_index=True)
    results.to_csv("csv_results/results_thr.csv", index=False)
    # plt.figure()
    ax = results.iloc[[0, 1, -1], 0:10].T.plot(style="--o")
    ax.set_xlabel("Number of stations")
    ax.set_ylabel("Throughput [Mb/s]")
    ax.set_ylim(0, 35)
    x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels(x_ticks)
    ax.legend(results.iloc[[0, 1, -1], 10].tolist())
    ax.text(
        0.60,
        0.11,
        "MSE for DCF-SimPy vs:\nns-3: {}\nAnalitical model: {}".format(
            *results.iloc[-1, 11:13].tolist()
        ),
        bbox={"facecolor": "none", "pad": 10, "edgecolor": "grey"},
        ha="left",
        va="center",
        transform=ax.transAxes,
    )
    plt.savefig("pdf/THR_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse2(csv_name, notes=""):
    results = pd.read_csv("csv_results/results_thr.csv", delimiter=",")
    thr_frame = pd.read_csv(csv_name, delimiter=",")
    thr_frame.drop("TIMESTAMP", axis=1, inplace=True)
    thr_frame.drop("CW_MIN", axis=1, inplace=True)
    thr_frame.drop("CW_MAX", axis=1, inplace=True)
    thr_frame.drop("SEED", axis=1, inplace=True)
    thr_frame.drop("P_COLL", axis=1, inplace=True)
    thr_frame.drop("FAILED_TRANSMISSIONS", axis=1, inplace=True)
    thr_frame.drop("SUCCEEDED_TRANSMISSIONS", axis=1, inplace=True)
    alpha = 0.05
    std = thr_frame.groupby("N_OF_STATIONS").std().loc[:, "THR"]
    n = thr_frame.groupby("N_OF_STATIONS").count().loc[:, "THR"]
    yerr = std / np.sqrt(n) * st.t.ppf(1 - alpha / 2, n - 1)
    plot_sum = thr_frame.groupby(["N_OF_STATIONS"]).mean()
    plt.plot(results.iloc[0, 0:10].T, "--o")
    plt.plot(results.iloc[1, 0:10].T, "--o")
    plt.errorbar(
        [i for i in range(0, 10)],
        plot_sum.loc[:, "THR"],
        yerr=yerr,
        fmt="--",
        capsize=4,
    )
    plt.xlabel("Number of stations")
    plt.ylabel("Throughput [Mb/s]")
    # plt.ylim(0, 35)
    # # x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # # plt.xticks(range(len(x_ticks)))
    # # plt.xticklabels(x_ticks)
    plt.legend(results.iloc[[0, 1, -1], 10].tolist())
    plt.text(
        5.7,
        3.4,
        "MSE for DCF-SimPy vs:\nns-3: {}\nAnalitical model: {}".format(
            *results.iloc[-1, 11:13].tolist()
        ),
        bbox={"facecolor": "none", "pad": 10, "edgecolor": "grey"},
        ha="left",
        va="center",
        wrap=True,
    )
    plt.savefig("pdf/THR_PER_STATION_ERR.pdf")
    plt.show()


def plot_thr(times_thr):
    times_thr = float("{:.4f}".format(times_thr))
    matlab_thr = 34.6014
    ns_3_thr = 36.1225
    names = ["Analytical model", "Times-DCF", "ns-3"]
    values = [matlab_thr, times_thr, ns_3_thr]
    plt.figure()
    plt.bar(names, values)
    plt.ylabel("Throughput [Mb/s]")
    plt.title("Throughput comparison")
    plt.savefig("pdf/THR_Comparison.pdf")
    plt.show()


def calculate_mean_and_std(csv_name):
    data = pd.read_csv(csv_name, delimiter=",")
    df = pd.DataFrame(data.groupby(["N_OF_STATIONS"]).mean())
    df["THR_STD"] = data.groupby(["N_OF_STATIONS"])["THR"].std()
    df.to_csv(f"{csv_name[:-4]}-mean.csv")


def show_backoffs(csv_name):
    plt.figure()
    data = pd.read_csv(csv_name, delimiter=",")
    ax = data.iloc[9, :].plot(style=".")
    ax.set_xlabel("Backoff")
    ax.set_ylabel("Number of draws")
    ax.set_yscale("log")
    ax.set_xscale("linear")
    plt.savefig("pdf/Backoffs.pdf")
    plt.show()
    ranges = [16, 32, 64, 128, 256, 512, 1024]
    merged = {}
    start = 0
    for cw in ranges:
        merged[str(cw - 1)] = [sum(data.iloc[9, start:cw])]
        start = cw
    pd_merged = pd.DataFrame.from_dict(merged)
    plt.figure()
    ax = pd_merged.T.plot.bar()
    ax.set_yscale("log")
    ax.set_xlabel("Backoff")
    ax.set_ylabel("Number of draws")
    ax.legend(["CW Draws"])
    plt.savefig("pdf/BackoffsMerged.pdf")
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
    calculate_p_coll_mse(file_mean)
    calculate_thr_mse2(file)
    calculate_thr_mse(file_mean)
    plot_thr(t.get_thr(1472))
    show_backoffs("csv_results/final.csv")


if __name__ == "__main__":
    show_results("csv/final.csv")
