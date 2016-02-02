import csv
import urllib
import time
from matplotlib import pyplot as plt


class Monitor:
    def __init__(self):
        self.portfolio_log = "portfolio_log.csv"
        self.timer = time.time()
        self.open_hours = range(9, 15)
        self.stock_info = {}
        with open('portfolio.csv', 'rb') as fh:
            reader = csv.reader(fh, delimiter=',')
            for row in reader:
                if row[0] == "Ticker":
                    pass
                else:
                    self.stock_info[row[0]] = tuple(row[1:])

    def _log_data(self, log_file, data):
        with open(log_file, 'a') as fh:
            writer = csv.writer(fh, delimiter=',')
            writer.writerow(data)
            print log_file + ','.join(data)

    def _format_data(self, options=["s", "l1"]):
        base_url = "http://finance.yahoo.com/d/quotes.csv?s="
        url = "{}".format(base_url)
        for key in self.stock_info.keys():
            url = url + "{}+".format(key)
        url = url[:-1] + "&f={}".format(''.join(options))
        return url

    def get_time(self):
        return time.localtime(time.time())

    def get_data(self, url):
        current_time = self.get_time()
        response = urllib.urlopen(url)
        results = response.read()[:-1]
        timestamp = time.strftime("%H:%M:%S", current_time)
        datestamp = time.strftime("%d/%m/%Y", current_time)
        for line in results.split('\n'):
            info = line.split(',')
            symbol = info[0].strip('"')
            filename = "{}/{}.csv".format(symbol, symbol)
            data = [datestamp, timestamp] + info[1:]
            self._log_data(filename, data)
            self._log_data(portfolio_log,
                           [symbol] + [datestamp, timestamp] + info[1:],
                           data)

    def monitor_stocks(self):
        url = self._format_data()
        while 1:
            current_time = self.get_time()
            if(current_time[6] not in [5, 6] and
                    current_time[3] in self.open_hours):
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
