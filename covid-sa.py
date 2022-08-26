import pandas as pd
import matplotlib.pyplot as plt
import requests
import os.path
import seaborn as sns
from datetime import datetime, date
from scipy.optimize import curve_fit

def logistic_model(x, a, b, c):
    return c / (1 + np.exp(-(x - b) / a))

def exponential_model(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

def plot(data):
    data['14 Day Average'] = data.Cases.rolling(14, center=True).mean()
    data.plot()
    # sns.lmplot(x='Date', y='Cases', data=data, order=4)
    # sns.lineplot(data=data, dashes=False)
    plt.grid()
    #plt.show()
    
    figure = plt.gcf()
    figure.set_size_inches(16.8, 10.5)
    plt.savefig('covid-sa-current.png', bbox_inches='tight')

def get_covidlive_data(startdate):
    url = 'https://covidlive.com.au/report/daily-cases/sa'
    df = pd.read_html(url)[1][:-1]
    df = df[df['NEW'] != '-']
    dates = [datetime.strptime(date, "%d %b %y").strftime('%Y-%m-%d') for date in df['DATE']][::-1]
    cases = [int(x) for x in df['NEW']][::-1]
    pos = 0
    while dates[pos] < startdate:
        pos += 1
    return dates[pos:], cases[pos:]
   
def process_data():
    dates, cases = get_covidlive_data('2021-12-24')
    series = pd.DataFrame()
    series['Date'] = dates
    series['Date'] = pd.to_datetime(series['Date'])
    series.set_index('Date', inplace=True)
    series['Cases'] = cases
    return series

def main():
    s = process_data()
    plot(s)

if __name__ == '__main__':
    main()
