#!/usr/bin/python
import sqlite3
import urllib
import time
import os
from matplotlib import pyplot as plt


class MonitorSQL:
    def __init__(self):
        db_dir = os.path.join(os.getcwd(), 'db')  # Database located in db/
        db_path = os.path.join(db_dir, 'Stocks.db')  # Datebase name

        # Check for database path and create directory if not found
        if not os.path.exists(db_dir):
            print 'Creating database directory'
            os.makedirs(db_dir)

        # Dictionary to hold portfolio
        self.stocks = {"HON": 192, "GOOG": 27, "CMG": 44,
                       "TSLA": 105, "V": 270}

        # Connect to database
        self.conn = sqlite3.connect(database=db_path)
        self.curr = self.conn.cursor()

        # Create tables if they don't exist
        for stock in self.stocks.keys():
            self.curr.execute("""CREATE TABLE IF NOT EXISTS {0}(
                                    Time TEXT,
                                    Date TEXT,
                                    Price REAL
                                    );""".format(stock))

    # Function to insert attributes into table
    def insert_quote(self, stock_name, price):
        self.curr.execute("""INSERT INTO {0} VALUES
                                (?, ?, ?);""".format(stock_name),
                          (time.strftime('%X'),  # Time when quote was taken
                           time.strftime("%d/%m/%Y",  # Date quote was taken
                                         time.localtime(time.time())),
                           price))  # Quote

    # Format url to get quote from Yahoo! finance
    # Default options are to recieve the symbol and price
    def format_data(self, options=["s", "l1"]):
        base_url = "http://finance.yahoo.com/d/quotes.csv?s="
        url = "{0}".format(base_url)
        for key in self.stocks.keys():
            url = url + "{0}+".format(key)
        url = url[:-1] + "&f={0}".format(''.join(options))
        return url

    # Get local time
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
               (9 <= now[3] <= 15 or
               (now[3] == 8 and now[4] >= 30)))

    # Retrieve quote from Yahoo! finance and insert into table
    def get_data(self, url):
        response = urllib.urlopen(url)
        results = response.read()[:-1]

        for line in results.split('\n'):
            info = line.split(',')
            self.insert_quote(info[0].strip('"'), float(info[1]))

    # Get all data from table
    def get_table(self, table_name, attr=['*']):
        self.curr.execute("SELECT {0} FROM {1}".format(
                                ','.join(attr), table_name))

        rows = self.curr.fetchall()
        return rows

    # Main loop
    # Quotes are fetched every 10 minutes by default
    def monitor_stocks(self, freq=600):
        url = self.format_data()  # Get URL

        while 1:

            # Get time at beginning of loop
            begin = time.time()

            # If market is open get quote
            if self.is_open():
                self.get_data(url)
                # Commit transaction
                self.conn.commit()

            # Get closing price when after-market trading is finished
            elif self.get_time(3) == 17 and 30 <= self.get_time(4) <= 40:
                if self.get_time(6) < 5:
                    self.get_data(url)
                    # Commit transaction at end of day
                    self.conn.commit()

            # Find how long loop took to process
            process_time = time.time() - begin
            # Wait for designated freq time and consider processing time
            if process_time < freq:
                time.sleep(freq - process_time)

    # Stop process and commit if program is terminated
    # Roll back if commit fails
    def stop_monitor(self):
        try:
            self.conn.commit()
        except:
            self.conn.execute("rollback")
        self.curr.close()
        self.conn.close()

    # Plot total value of stock(s) from table
    def plot_table(self, tables):  # tables variable must be a list
        dates = []
        for table in tables:
            # Get dates for x axis labels
            data = self.get_table(table, ['Price', 'Date'])
            dates = [d[1] for d in data]
            plt.plot([d[0]*self.stocks[table] for d in data], label=table)

        date_indices = []
        i = 0
        for d in dates:
            # Find each date and the index of the first quote taken
            if d not in [di[0] for di in date_indices]:
                date_indices.append((d, i))
            i += 1

        # Plot settings
        plt.grid(True)
        plt.legend(loc=3)
        plt.title('Goldman Stock Chart')
        plt.ylabel('value of Shares')
        plt.xlabel('Time')

        # x axis labels
        plt.xticks([d[1] for d in date_indices],
                   [d[0][:-5] for d in date_indices],
                   rotation='vertical')

        plt.show()

if __name__ == "__main__":
    import sys

    # Init monitor
    monitor = MonitorSQL()

    # Monitor until script is stopped
    try:
        monitor.monitor_stocks()
    except Exception, err:
        monitor.stop_monitor()
        print err
        sys.exit()
