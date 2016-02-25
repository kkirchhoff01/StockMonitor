#!/usr/bin/python
import sqlite3
import requests
import time
import os
from matplotlib import pyplot as plt


class MonitorSQL:
    def __init__(self, stock_db='Stocks.db', portfolio_db='Portfolio.db',
                 portfolio_table='portfolio'):

        db_dir = os.path.join(os.getcwd(), 'db')  # Database located in db/
        db_path = os.path.join(db_dir, stock_db)  # Datebase name
        portfolio_path = os.path.join(db_dir, portfolio_db)

        # Check for database path and create directory if not found
        if not os.path.exists(db_dir):
            print('Creating database directory')
            os.makedirs(db_dir)

        # Get portfolio from Portfolio database
        pconn = sqlite3.connect(database=portfolio_path)
        pcurr = pconn.cursor()
        pcurr.execute("SELECT * FROM {0};".format(portfolio_table))
        self.stocks = dict(pcurr.fetchall())
        pcurr.close()
        pconn.close()

        # Connect to database
        self.conn = sqlite3.connect(database=db_path)
        self.curr = self.conn.cursor()

        # Create tables if they don't exist
        for stock in self.stocks.keys():
            self.curr.execute("""CREATE TABLE IF NOT EXISTS {0}(
                                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Time TEXT,
                                    Date TEXT,
                                    Price REAL
                                    );""".format(stock))

    # Function to insert attributes into table
    def insert_quote(self, stock_name, price):
        # Check to make sure proper data is being passed
        assert(stock_name in self.stocks.keys())
        assert(isinstance(price, float))

        self.curr.execute("""INSERT INTO {0} (Time, Date, Price) VALUES
                                (?, ?, ?);""".format(stock_name),
                          (time.strftime('%X'),  # Time when quote was taken
                           time.strftime("%d/%m/%Y",  # Date quote was taken
                                         time.localtime(time.time())),
                           price))  # Quote

    # Format url to get quote from Yahoo! finance
    # Default options are to recieve the symbol and price
    def format_data(self, options=["s", "l1"]):
        url = "http://finance.yahoo.com/d/quotes.csv?s="

        # Add stock symbols to URL
        for key in self.stocks.keys():
            url = url + "{0}+".format(key)

        # Add options to URL (and remove extra '+'
        url = "{0}&f={1}".format(url[:-1], ''.join(options))

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
               (9 <= now[3] < 15 or
               (now[3] == 8 and now[4] >= 30)))

    # Retrieve quote from Yahoo! finance and insert into table
    def get_data(self, url):
        response = requests.get(url)
        results = response.text[:-1]

        for line in results.split('\n'):
            info = line.split(',')

            # Parse the symbol and price (remove quotes from symbol)
            try:
                self.insert_quote(info[0].strip('"'), float(info[1]))

            # Yahoo sometimes returns bad data
            # Running get_data again solves the problem
            except IndexError:
                self.get_data(url)

    # Get data from table with specified attributes (all by default)
    def get_table(self, table_name, attr=['*']):
        # Make sure proper data is being passed
        # assert(table_name in self.stocks.keys())

        self.curr.execute("SELECT {0} FROM {1};".format(
                                ','.join(attr), table_name))

        rows = self.curr.fetchall()
        return rows

    # Function to get the time or date from the last quote fetched
    # The attribute comes from the last row in the stocks db
    def get_last_quote(self, attr):
        last_time = ''  # Last quote time or date
        i = 0
        for stock in self.stocks.keys():
            # Get last row from stock table
            self.curr.execute("""SELECT {1} FROM {0}
                                WHERE Id=(SELECT MAX(Id) FROM {0});""".format(
                                    stock, attr))
            last_entry = self.curr.fetchone()
            if len(last_entry) == 0:
                return '0:0:0'

            if i == 0:
                # Set last_time
                last_time = last_entry[0]
            else:
                # Assert that table entries are consistant
                assert(last_time == last_entry[0])

        return last_time

    # Function to wait until the time limit (freq)
    # Used for restarting script
    def wait_from_last(self, freq=600):
        now = time.localtime(time.time())

        # If the monitor is restarted on the same day
        if self.get_last_quote('Date') == time.strftime("%d/%m/%Y", now):
            last_quote = self.get_last_quote('Time')  # Get time of last quote

            # Get last quote time in intiger form
            hour, minute, second = map(lambda x: int(x), last_quote.split(':'))

            # Convert time since last quote to seconds
            time_since = (60*60*(now[3] - hour) +
                          60*(now[4] - minute) +
                          (now[5] - second))

            # If the last quote fetched was < 10 minutes ago, wait
            if 0 <= time_since < 10:
                time.sleep(freq - time_since)

    # Main loop
    # Quotes are fetched every 10 minutes by default
    def monitor_stocks(self, freq=600):
        self.wait_from_last(freq)

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
            elif self.get_time(3) == 17 and 30 < self.get_time(4) <= 40:
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
        # Check for proper data type
        assert(isinstance(tables, list))

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
        plt.tight_layout()

        # x axis labels
        plt.xticks([d[1] for d in date_indices],
                   [d[0][:-5] for d in date_indices],
                   rotation='vertical')

        plt.show()

if __name__ == "__main__":
    import sys
    import traceback

    # Init monitor
    monitor = MonitorSQL()

    # Monitor until script is stopped
    try:
        monitor.monitor_stocks()
    except KeyboardInterrupt:
        monitor.stop_monitor()
        sys.exit(0)
    except:
        monitor.stop_monitor()
        traceback.print_exc()
        sys.exit(1)
