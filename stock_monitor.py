#!/usr/bin/python

import csv
import urllib
import time
from matplotlib import pyplot as plt


class Monitor:
    def __init__(self):
        self.portfolio_log = "portfolio_log.csv"
        self.stocks = ["HON", "GOOG", "CMG", "TSLA", "V"]

    def get_portfolio(self):
        stock_info = {}
        with open('portfolio.csv', 'rb') as fh:
            reader = csv.reader(fh, delimiter=',')
            for row in reader:
                if row[0] == "Ticker":
                    pass
                else:
                    stock_info[row[0]] = tuple(row[1:])
        return stock_info

    def log_data(self, log_file, data):
        with open(log_file, 'a') as fh:
            writer = csv.writer(fh, delimiter=',')
            writer.writerow(data)

    def format_data(self, options=["s", "l1"]):
        base_url = "http://finance.yahoo.com/d/quotes.csv?s="
        url = "{}".format(base_url)
        for key in self.stocks:
            url = url + "{}+".format(key)
        url = url[:-1] + "&f={}".format(''.join(options))
        return url

    def get_time(self, tm):
        try:
            return time.localtime(time.time())[tm]
        except IndexError:
            return time.localtime(time.time())

    def is_open(self):
        now = time.localtime(time.time())
        return(now[6] < 5 and
               (now[3] in range(9, 15) or
               (now[3] == 8 and now[4] >= 30)))

    def get_data(self, url):
        response = urllib.urlopen(url)
        results = response.read()[:-1]

        current_time = map(self.get_time, range(0, 9))
        timestamp = time.strftime("%H:%M:%S", current_time)
        datestamp = time.strftime("%d/%m/%Y", current_time)

        for line in results.split('\n'):
            info = line.split(',')
            symbol = info[0].strip('"')
            filename = "{0}/{0}.csv".format(symbol)
            data = [datestamp, timestamp] + info[1:]
            self.log_data(filename, data)
            self.log_data(self.portfolio_log,
                          [symbol] + [datestamp, timestamp] + info[1:])

    def monitor_stocks(self):
        url = self.format_data()
        while 1:
            if self.is_open():
                self.get_data(url)
            elif self.get_time(3) == 15 and self.get_time(4) <= 10:
                if self.get_time(6) < 5:
                    self.get_data(url)
            time.sleep(600)

    def plot_data(self, data):
        plt.plot(data)
        plt.show()

if __name__ == "__main__":
    import sys
    sys.stdout = open('outfile.txt', 'a')
    monitor = Monitor()
    monitor.monitor_stocks()
