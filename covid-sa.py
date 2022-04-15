from scipy.optimize import curve_fit, fsolve
import numpy as np
import matplotlib.pyplot as plt
import requests
import os.path
from time import time

def fit_curve(days, cases, curvetype='exponential'):
    if curvetype == 'exponential':
        return curve_fit(exponential_model, days, cases)
    elif curvetype == 'logistic':
        initial_guess = 4, 100, 25000
        return curve_fit(logistic_model, days, cases, p0=initial_guess, maxfev=9999)

def extrapolate(currmodel, days, popt, advance_days):
    pcent_needs_ic = 0.05
    models = {'logistic':logistic_model, 'exponential':exponential_model,
              'simple_exp':simple_exp}
    fit_y, needs_ic = [], []

    for d in days:
        fit_y.append(models[currmodel](d, *popt))

    extrapolate_x = list(range(days[-1], days[-1]+advance_days+1))
    extrapolate_y = []
    for x in extrapolate_x:
        newy = int(models[currmodel](x, *popt))
        extrapolate_y.append(newy)
    return fit_y, extrapolate_x, extrapolate_y, needs_ic

def simple_exp(x, a, b, c):
    return a**x + b*x + c

def logistic_model(x, a, b, c):
    return c / (1 + np.exp(-(x - b) / a))

def exponential_model(x, a, b, c):
    return a*np.exp(b*(x-c))

def plot(indata):
    advance_days = 7

    cases = list(indata.values())
    dates = list(indata.keys())
    days = list(range(len(cases)))

    #currmodel = 'logistic'
    currmodel = 'exponential'
    #currmodel = 'simple_exp'

    #logi_popt, logi_pcov = fit_curve(days, cases, 'logistic')
    expo_popt, expo_pcov = fit_curve(days, cases, 'exponential')

    #logi_fit_y, logi_extrap_x, logi_extrap_y, needs_ic = extrapolate('logistic', days, logi_popt, advance_days)
    expo_fit_y, expo_extrap_x, expo_extrap_y, needs_ic = extrapolate('exponential', days, expo_popt, advance_days)

    fig, ax = plt.subplots()

    # actual data
    ax.plot(dates, cases, '-bx', label='Cases')

    #logistic curve
    #ax.plot(days, logi_fit_y, '--g', label='Logistic fitted curve')
    ax.plot(logi_extrap_x, logi_extrap_y, '--xg', label='Exponential extrapolated')
    # label extrapolated points
    '''
    for num, x in enumerate(logi_extrap_x[1:]): #skip first extrap as it overlaps last datum
        y = logi_extrap_y[num+1]
        ax.text(x + 0.2, y, str(y), va='center')
    '''

    fig.autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Cases')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.grid(which='both')
    plt.show()

def fetch_data():
    filetime = os.path.getmtime('daily-stats.csv')
    if filetime < time() - 3600:
        r = requests.get('https://raw.githubusercontent.com/M3IT/COVID-19_Data/master/Data/COVID_AU_state.csv')
        if r.status_code == 200:
            with open('daily-stats.csv', 'w') as outfile:
                outfile.write(r.text)
        else:
            print('Failed to retrieve data.')

    with open('daily-stats.csv', 'r') as indata:
        return [x.strip() for x in indata.readlines()]

def process_data(indata):
    data = {}
    targ_state = 'South Australia'
    filtered = [x for x in indata if targ_state in x and '2022' in x]
    for f in filtered:
        splitline = f.split(',')
        data[splitline[0]] = int(splitline[3])
    return data

def main():
    d = fetch_data()
    d = process_data(d)
    plot(d)

if __name__ == '__main__':
    main()
