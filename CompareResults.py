import pandas as pd
import matplotlib.pyplot as plt
plt.close('all')
plt.figure()

def append_to_results(csv_name):
    results = pd.read_csv('results.csv', delimiter=',')
    results_dict = results.iloc[0, 1:11].to_dict()

    new_results = pd.read_csv(csv_name, delimiter=',').T
    new_results = {str(int(pair['N_OF_STATIONS'])): pair['P_COLL'] for pair in new_results.to_dict().values()}

    MSE = 0
    for key in results_dict.keys():
        new_results[f"MSEn{key}"] = pow(results_dict[key] - new_results[key], 2) / 2
        MSE += pow(results_dict[key] - new_results[key], 2)
    MSE = MSE / len(results_dict.keys())

    new_results['MSE'] = MSE
    new_results['N_OF_STATIONS'] = 'P_COLL'
    results = results.append(new_results, ignore_index=True)
    results.to_csv('results.csv', index=False)
    plt.figure()
    results.iloc[[0,-1], 1:11].T.plot.bar()
    plt.show()
    plt.figure()
    results.iloc[-1, 12:23].T.plot.bar()
    plt.show()
