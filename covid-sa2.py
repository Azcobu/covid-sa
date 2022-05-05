import pandas as pd
import matplotlib.pyplot as plt
import requests
import os.path
from time import time
import seaborn as sns
from scipy.optimize import curve_fit

def logistic_model(x, a, b, c):
    return c / (1 + np.exp(-(x - b) / a))

def exponential_model(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

def plot(data):
    #data['7 Day Average'] = data.Cases.rolling(7, center=True).mean()
    #data.plot()
    #sns.lmplot(x='Date', y='Cases', data=data, order=4)
    sns.lineplot(data=data, dashes=False)
    plt.grid()
    plt.show()

def fetch_data():
    refresh = 3600 * 2
    if not os.path.exists('daily-stats.csv') or os.path.getmtime('daily-stats.csv') < time() - refresh:
        print('Downloading latest updates...', end='')
        try:
            r = requests.get('https://raw.githubusercontent.com/M3IT/COVID-19_Data/master/Data/COVID_AU_state.csv')
        except Exception as err:
            print(f'unable to retrieve file - {err}')
        else:
            if r.status_code == 200:
                print('done.')
                with open('daily-stats.csv', 'w') as outfile:
                    outfile.write(r.text)
            else:
                print('Failed to retrieve data.')

    with open('daily-stats.csv', 'r') as indata:
        return [x.strip() for x in indata.readlines()]

def process_data(indata):
    window_size = 7
    data = {}
    targ_state = 'South Australia'
    filtered = [x for x in indata if targ_state in x]
    filtered = filtered[700:]
    for f in filtered:
        splitline = f.split(',')
        data[splitline[0]] = (int(splitline[3]), int(splitline[5]))

    series = pd.DataFrame()
    #series['Date'] = list(range(len(data.keys()))) # data.keys()
    series['Date'] = data.keys()
    series['Date'] = pd.to_datetime(series['Date'])
    series.set_index('Date', inplace=True)
    series['Cases'] = [x[0] for x in data.values()]
    #series['Deaths'] = [x[1] for x in data.values()]

    x = list(range(len(data.keys())))
    y = [x[0] for x in data.values()]
    popt, _ = curve_fit(exponential_model, x, y)
    curve = [exponential_model(x_val, *popt) for x_val in x]
    series['Fitted Curve'] = curve

    return series

def main():
    d = fetch_data()
    if d:
        s = process_data(d)
        plot(s)

if __name__ == '__main__':
    main()
