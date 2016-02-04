import numpy as np
from matplotlib import pyplot as plt
from stock_monitor import Monitor

monitor = Monitor()
portfolio = monitor.get_portfolio()
shares = {}
prices = {}
dates = []
data = {}
for key in portfolio.keys():
    prices[key] = float(portfolio[key][1])
    shares[key] = int(portfolio[key][2])
    data[key] = np.fromfile(file="{0}/prices.txt".format(key),
                            dtype=float, sep='\n')
    del portfolio[key]

fig, ax = plt.subplots(3, 2, sharex='col')
plt.setp(ax, xticks=[0, len(data['GOOG'])], xticklabels=["1/29", "2/4"])
i,j = 0,0
keys = data.keys()
for key in data.keys():
    if i < 1:
        ax[j][i].plot([shares[key]*d for d in data[key]], label=key)
        ax[j][i].grid(True)
        ax[j][i].legend()
        i += 1
    else:
        ax[j][i].plot([shares[key]*d for d in data[key]], label=key)
        ax[j][i].grid(True)
        ax[j][i].legend()
        j += 1
        i = 0

ax[2][1].plot([sum([shares[d]*data[d][i] for d in data.keys()]) for
               i in range(len(data['GOOG']))], label="Total")
ax[2][1].grid(True)
ax[2][1].legend()
plt.show()
