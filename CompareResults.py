import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import Times as t
import scipy.stats as st

plt.close("all")
MSE_NAMES = {0: "MSE-NS-3", 1: "MSE-AM", 2: "MSE-MS"}
CIL = 1.96

def calculate_p_coll_mse(csv_name, notes=""):
    results = pd.read_csv("results_p_coll.csv", delimiter=",")
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
    results.to_csv("results_p_coll.csv", index=False)
    ax = results.iloc[[0, 1, 2, -1], 0:10].T.plot(style="--o")
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
    plt.savefig("P_COLL_PER_STATION.pdf")
    plt.show()


def calculate_thr_mse(csv_name, notes=""):
    results = pd.read_csv("results_thr.csv", delimiter=",")
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
    results.to_csv("results_thr.csv", index=False)
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
    plt.savefig("THR_PER_STATION.pdf")
    plt.show()

def calculate_thr_mse2(csv_name, notes=""):
    results = pd.read_csv("results_thr.csv", delimiter=",")
    results_dict = results.iloc[0:2, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=",").T
    std = new_results.T["THR_STD"].to_list()
    new_results = {
        str(int(pair["N_OF_STATIONS"])): pair["THR"]
        for pair in new_results.to_dict().values()
    }
    ci = []
    for n in range(len(std)):
        ci.append(CIL * std[n] / new_results.get(f"{(n + 1)}"))
    new_results["Name"] = "DCF-SimPy"
    new_results["Notes"] = notes
    for i in range(2):
        mse = 0
        for key in results_dict.keys():
            mse += pow(results_dict[key][i] - new_results[key], 2)
        mse = mse / len(results_dict.keys())
        new_results[MSE_NAMES[i]] = "{:.2E}".format(mse)
    results = results.append(new_results, ignore_index=True)
    results.to_csv("results_thr.csv", index=False)
    plt.figure()
    plt.plot(results.iloc[0, 0:10].T, "--o")
    plt.plot(results.iloc[1, 0:10].T, "--o")
    dcf_res = results.iloc[-1, 0:10].to_dict()
    plt.errorbar(dcf_res.keys(),dcf_res.values(), yerr=ci, fmt="--")
    plt.xlabel("Number of stations")
    plt.ylabel("Throughput [Mb/s]")
    plt.ylim(0, 35)
    # x_ticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # plt.xticks(range(len(x_ticks)))
    # plt.xticklabels(x_ticks)
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
    plt.savefig("THR_PER_STATION_WITH_ERR.pdf")
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
    plt.savefig("THR_Comparison.pdf")
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
    ax.set_yscale('log')
    ax.set_xscale('log')
    plt.savefig("Backoffs.pdf")
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


if __name__ == "__main__":
    file = "15-1023-10-1594202254.353538.csv"
    file_mean = f"{file[:-4]}-mean.csv"
    # calculate_mean_and_std(file)
    # calculate_p_coll_mse(file_mean)
    # calculate_thr_mse(file_mean)
    # plot_thr(t.get_thr())
    show_backoffs("backoffs.csv")

    # calculate_mean()
