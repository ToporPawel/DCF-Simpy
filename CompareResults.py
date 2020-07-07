import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import Times as t

plt.close('all')
plt.figure()
MSE_NAMES = {0: 'MSE-NS-3', 1: 'MSE-AM', 2: 'MSE-MS'}


def calculate_p_coll_mse(csv_name, notes=""):
    # csv_name = "15-1023-10-1593699780.1748621-mean.csv"
    # notes = ""
    results = pd.read_csv('results_p_coll.csv', delimiter=',')
    results_dict = results.iloc[0:3, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=',').T
    new_results = {str(int(pair['N_OF_STATIONS'])): pair['P_COLL'] for pair in new_results.to_dict().values()}
    new_results['Name'] = "DCF-SimPy"
    new_results['Notes'] = notes

    for i in range(3):
        mse = 0
        for key in results_dict.keys():
            mse += pow(results_dict[key][i] - new_results[key], 2)
        mse = mse / len(results_dict.keys())
        new_results[MSE_NAMES[i]] = "{:.2E}".format(mse)
    results = results.append(new_results, ignore_index=True)
    results.to_csv('results_p_coll.csv', index=False)
    plt.figure()
    ax = results.iloc[[0, 1, 2, -1], 0:10].T.plot(style='--o')
    ax.set_xlabel("Number Of Stations")
    ax.set_ylabel("P_COLL")
    ax.legend(results.iloc[[0, 1, 2, -1], 10].tolist())
    ax.text(0.61, 0.13, 'MSE for DCF-SimPy vs:\nNs-3: {}\nAnalitical model: {}\nMatlab simulation: {}'.format(*results.iloc[-1, 11:14].tolist()),
            bbox={'facecolor': 'none', 'pad': 10, 'edgecolor': 'grey'}, ha='left', va='center', transform=ax.transAxes)
    plt.show()


def calculate_thr_mse(csv_name, notes=""):
    # csv_name = "15-1023-10-1593715137.5164042-mean.csv"
    # notes = ""
    results = pd.read_csv('results_thr.csv', delimiter=',')
    results_dict = results.iloc[0:2, 0:10].to_dict()
    new_results = pd.read_csv(csv_name, delimiter=',').T
    new_results = {str(int(pair['N_OF_STATIONS'])): pair['THR'] for pair in new_results.to_dict().values()}
    new_results['Name'] = "DCF-SimPy"
    new_results['Notes'] = notes
    for i in range(2):
        mse = 0
        for key in results_dict.keys():
            mse += pow(results_dict[key][i] - new_results[key], 2)
        mse = mse / len(results_dict.keys())
        new_results[MSE_NAMES[i]] = "{:.2E}".format(mse)
    results = results.append(new_results, ignore_index=True)
    results.to_csv('results_thr.csv', index=False)
    plt.figure()
    ax = results.iloc[[0, 1, -1], 0:10].T.plot(style='o')
    ax.set_xlabel("Number Of Stations")
    ax.set_ylabel("Throughput [Mb/s]")
    ax.set_ylim(0, 32)
    ax.legend(results.iloc[[0, 1, -1], 10].tolist())
    ax.text(0.62, 0.11, 'MSE for DCF-SimPy vs:\nNs-3: {}\nAnalitical model: {}'.format(*results.iloc[-1, 11:13].tolist()),
            bbox={'facecolor': 'none', 'pad': 10, 'edgecolor': 'grey'}, ha='left', va='center', transform=ax.transAxes)
    plt.show()


def plot_thr(times_thr):
    matlab_thr = 34.6014
    ns_3_thr = 29.6172
    names = ['Matlab', 'NS-3', 'Times-DCF']
    values = [matlab_thr, ns_3_thr, times_thr]

    plt.figure()
    plt.bar(names, values)
    for index, value in enumerate(values):
        plt.text(index, value + 0.5, str(value))
    plt.ylabel("Throughput [Mb/s]")
    plt.title("Throughput comparison")
    plt.show()


if __name__ == "__main__":
    plot_thr(t.get_thr())
