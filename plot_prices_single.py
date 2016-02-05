import csv
from matplotlib import pyplot as plt
from stock_monitor import Monitor

monitor = Monitor()
portfolio = monitor.get_portfolio()
shares = {}
prices = {}
times = {}#[]
for stock in monitor.stocks:
    prices[stock] = []
    times[stock] = []
    with open("{0}/{0}.csv".format(stock), 'r') as fh:
        reader = csv.reader(fh, delimiter=',')
        i = 0
        for row in reader:
            if row[0] not in times[stock]:
                if i == 0:
                    times[stock] = times[stock] + [None]
                    i += 1
                else:
                    times[stock] = times[stock] + [row[0]]
            else:
                times[stock] = times[stock] + [None]
            prices[stock] = prices[stock] + [float(row[2])]

for key in portfolio.keys():
    shares[key] = float(portfolio[key][2])
    del portfolio[key]

for key in prices.keys():
    plt.plot([shares[key]*d for d in prices[key]], label=key)
plt.grid(True)
plt.legend()
plt.title('Goldman Stock Chart')
plt.ylabel('value of Shares')
plt.xlabel('Time')
plt.xticks([times[times.keys()[0]].index(i) for i in times[times.keys()[0]] if i is not None],
            [i for i in times[times.keys()[0]] if i is not None])#["2/3", "2/4"])
plt.ylim([16000,22000])
plt.show()
