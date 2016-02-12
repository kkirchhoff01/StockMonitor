import numpy as np
import csv
from matplotlib import pyplot as plt
from stock_monitor import Monitor

# Init monitor object
monitor = Monitor()
# Get portfolio
portfolio = monitor.get_portfolio()

# Attribute dictionaries
shares = {}
prices = {}
dates = {}
times = {}
data = {}

# Get all info from csv files
for stock in monitor.stocks:
    prices[stock] = []
    times[stock] = []
    with open("{0}/{0}.csv".format(stock), 'r') as fh:
        reader = csv.reader(fh, delimiter=',')
        i = 0
        for row in reader:
            if row[0] not in times[stock]:
                if i == 0:
                    # Assign None if date already in times for indexing
                    times[stock] = times[stock] + [None]
                    i += 1
                else:
                    # Add date if date if not in times
                    times[stock] = times[stock] + [row[0]]
            else:
                times[stock] = times[stock] + [None]
            prices[stock] = prices[stock] + [float(row[2])]

for key in portfolio.keys():
    shares[key] = float(portfolio[key][2])
    del portfolio[key]

fig, ax = plt.subplots(3, 2, sharex='col')

# Set x axis labels/settings
plt.setp(ax, xticks=[times[times.keys()[0]].index(i) for
                     i in times[times.keys()[0]] if i is not None],
         xticklabels=[i for i in times[times.keys()[0]] if i is not None])

i, j = 0, 0
# Add data to subplots
for key in prices.keys():
    if i < 1:
        ax[j][i].plot([shares[key]*d for d in prices[key]], label=key)
        ax[j][i].grid(True)
        ax[j][i].legend()
        i += 1
    else:
        ax[j][i].plot([shares[key]*d for d in prices[key]], label=key)
        ax[j][i].grid(True)
        ax[j][i].legend()
        j += 1
        i = 0

# Add total portfolio value to final subplot
ax[2][1].plot([sum([shares[d]*prices[d][i] for d in prices.keys()]) for
               i in range(len(prices['GOOG']))], label="Total")
ax[2][1].grid(True)
ax[2][1].legend()
plt.show()
