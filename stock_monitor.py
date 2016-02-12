#!/usr/bin/python

import csv
import os
import urllib
import time
from matplotlib import pyplot as plt


class Monitor:
    def __init__(self):
        # Set variables
        self.portfolio_log = "portfolio_log.csv"  # FIN301 portfolio CSV
        self.stocks = ["HON", "GOOG", "CMG", "TSLA", "V"]

        # Create directory for each symbol in portfolio
        for folder in self.stocks:
            if not os.path.exists(folder):
                os.makedirs(folder)

    # Retrieve portfolio
    def get_portfolio(self):
        stock_info = {}
        with open('portfolio.csv', 'rb') as fh:
            reader = csv.reader(fh, delimiter=',')
            for row in reader:
                # Don't add header row
                if row[0] == "Ticker":
                    pass
                # Add portfolio data
                else:
                    stock_info[row[0]] = tuple(row[1:])
        return stock_info

    # Add data to CSV file
    def log_data(self, log_file, data):
        with open(log_file, 'a') as fh:
            writer = csv.writer(fh, delimiter=',')
            writer.writerow(data)

    # Format url to get quote from Yahoo! finance
    # Default options are to recieve the symbol and price
    def format_data(self, options=["s", "l1"]):
        base_url = "http://finance.yahoo.com/d/quotes.csv?s="
        url = "{0}".format(base_url)
        for key in self.stocks:
            url = url + "{0}+".format(key)
        url = url[:-1] + "&f={0}".format(''.join(options))
        return url

    # GEt local time
    def get_time(self, tm):  # tm: index of time attribute
        try:
            return time.localtime(time.time())[tm]
        except IndexError:
            # Return complete time object if tm index is out of range
            return time.localtime(time.time())

    # Return True/False if market is open/closed
    def is_open(self):
        now = time.localtime(time.time())
        return(now[6] < 5 and
               (now[3] in range(9, 15) or
               (now[3] == 8 and now[4] >= 30)))

    # Retrieve quote from Yahoo! finance and insert into table
    def get_data(self, url):
        response = urllib.urlopen(url)
        results = response.read()[:-1]

        # Get complete time object
        current_time = map(self.get_time, range(0, 9))
        # Create timestampe and datestamp from time object
        timestamp = time.strftime("%H:%M:%S", current_time)
        datestamp = time.strftime("%d/%m/%Y", current_time)

        # Parse data
        for line in results.split('\n'):
            info = line.split(',')
            symbol = info[0].strip('"')

            # Set file name
            filename = "{0}/{0}.csv".format(symbol)

            # Format data list
            data = [datestamp, timestamp] + info[1:]

            # Log data and portfolio
            self.log_data(filename, data)
            self.log_data(self.portfolio_log,
                          [symbol] + [datestamp, timestamp] + info[1:])

    # Main loop
    # Quotes are fetched every 10 minutes by default
    def monitor_stocks(self):
        url = self.format_data()  # Get URL

        while 1:

            # If market is open get quote
            if self.is_open():
                self.get_data(url)

            # Get closing price less than 10 minutes ater close
            # Need to fix inaccuracy from after market trading
            elif self.get_time(3) == 15 and self.get_time(4) <= 10:
                if self.get_time(6) < 5:
                    self.get_data(url)

            # Wait to fetch new quote
            time.sleep(600)

if __name__ == "__main__":
    import sys

    sys.stdout = open('outfile.txt', 'a')
    monitor = Monitor()
    monitor.monitor_stocks()
