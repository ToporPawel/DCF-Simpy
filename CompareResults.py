import pandas as pd


def append_to_results(csv_name):
    results = pd.read_csv('results.csv', delimiter=',')
    results_dict = results.iloc[0, 1:11].to_dict()

    new_results = pd.read_csv(csv_name, delimiter=',').T
    new_results = {str(int(pair['N_OF_STATIONS'])): pair['P_COLL'] for pair in new_results.to_dict().values()}

    MSE = 0
    for key in results_dict.keys():
        MSE += pow(results_dict[key] - new_results[key], 2)
    MSE = MSE / len(results_dict.keys())

    new_results['MSE'] = MSE
    new_results['N_OF_STATIONS'] = 'P_COLL'
    results = results.append(new_results, ignore_index=True)
    results.to_csv('results.csv', index=False)

