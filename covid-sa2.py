import pandas as pd
import matplotlib.pyplot as plt
import requests
import os.path
from time import time
import seaborn as sns

def plot(data):
    data['7 Day Average'] = data.Cases.rolling(7).mean()
    #data.plot()
    sns.lmplot(x='Date', y='Cases', data=data, order=4)
    #sns.lmplot(x='Date', y='Deaths', data=data, order=4)
    plt.show()

def fetch_data():
    if not os.path.exists('daily-stats.csv') or os.path.getmtime('daily-stats.csv') < time() - 3600:
        r = requests.get('https://raw.githubusercontent.com/M3IT/COVID-19_Data/master/Data/COVID_AU_state.csv')
        if r.status_code == 200:
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
    filtered = [x for x in indata if targ_state in x and '2022' in x]
    for f in filtered:
        splitline = f.split(',')
        data[splitline[0]] = (int(splitline[3]), int(splitline[5]))

    series = pd.DataFrame()
    series['Date'] = list(range(len(data.keys()))) #data.keys()
    series['Cases'] = [x[0] for x in data.values()]
    series['Deaths'] = [x[1] for x in data.values()]
    # series['Date'] = pd.to_datetime(series['Date'])
    return series

def main():
    d = fetch_data()
    s = process_data(d)
    plot(s)

if __name__ == '__main__':
    main()
