import pandas as pd
import matplotlib.pyplot as plt
import requests
import os.path
import seaborn as sns
from datetime import datetime, date
from scipy.optimize import curve_fit
from itertools import islice

def logistic_model(x, a, b, c):
    return c / (1 + np.exp(-(x - b) / a))

def exponential_model(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

def plot(data):
    lastdate = data.iloc[-1]
    lastdate = str(lastdate.name).split(' ')[0]
    txt = f'South Australian Weekly Covid Cases (last updated {lastdate})'
    data.plot(title=txt)
    plt.grid()
    #plt.show()
    
    figure = plt.gcf()
    figure.set_size_inches(16.8, 10.5)
    plt.savefig('covid-sa-weekly.png', bbox_inches='tight')

def chunk_cases(cases):
    it = iter(cases)
    while True:
        chunk = tuple(islice(it, 7))
        if not chunk:
            break
        yield chunk

def convert_to_weekly(cases, dates):
    # converts daily into weekly until 09-09-22, thrn switches to weekly
    startdate = '2021-12-25'
    enddate = '2022-09-09'
    weekdates, weekcases = [], []

    startpos = dates.index(startdate)
    dates, cases = dates[startpos:], cases[startpos:]

    enddaily = dates.index(enddate) + 1
    weekcases2, weekdates2 = cases[enddaily:], dates[enddaily:]
    cases, dates = cases[:enddaily], dates[:enddaily]

    weekdates = dates[6::7]
    weekcases = [sum(x) for x in chunk_cases(cases)]

    return weekcases + weekcases2, weekdates + weekdates2

def get_covidlive_data():
    url = 'https://covidlive.com.au/report/daily-cases/sa'
    df = pd.read_html(url)[1][:-1]
    dates = [datetime.strptime(date, "%d %b %y").strftime('%Y-%m-%d') for date in df['DATE']][::-1]
    cases = [int(x) for x in df['NEW']][::-1]
    return cases, dates
   
def process_data():
    cases, dates = get_covidlive_data()
    cases, dates = convert_to_weekly(cases, dates)
    series = pd.DataFrame()
    series['Date'] = dates
    series['Date'] = pd.to_datetime(series['Date'])
    series.set_index('Date', inplace=True)
    series['Weekly Cases'] = cases
    return series

def main():
    s = process_data()
    plot(s)

if __name__ == '__main__':
    main()
