#!/usr/bin/python
import MySQLdb
import curses
import csv
import requests
import time
from matplotlib import pyplot as plt


class MonitorTUI:
    def __init__(self):
        try:
            # Init Screen
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.noecho()
            self.stdscr.nodelay(1)
            self.last = {}
            self.maxy, self.maxx = self.stdscr.getmaxyx()
            # Init color pairs
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
            self.add_title()
            # Init stocks
            self.stocks = {}
            self.import_portfolio()

        except:
            self.end_session()
            traceback.print_exc()
            sys.exit(1)

    # Get portfolio
    def import_portfolio(self, file_path='portfolio.csv'):
        with open(file_path) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                self.stocks[row[0]] = int(row[1])
                self.last[row[0]] = 0.0

    # Add string containing labels
    def add_title(self):
        self.stdscr.addstr("Symbol" + " "*(self.maxx//4 - 6) +
                           "Price" + " "*(self.maxx//4 - 5) +
                           "Change" + " "*(self.maxx//4 - 6) +
                           "Time", curses.color_pair(3)
                           )
        if not self.is_open():
            self.stdscr.addstr(" (Market closed)")
        self.stdscr.addstr("\n")

        self.stdscr.addstr("_"*(self.maxx) + "\n")
        self.stdscr.refresh()

    def add_price(self, price, change, colorpair):
        self.stdscr.addstr(price, curses.color_pair(colorpair))
        # Evenly space strings
        self.stdscr.addstr(" "*(self.maxx//4 - len(price)))
        self.stdscr.addstr(change, curses.color_pair(colorpair))

    def update_screen(self, symbol, price, change, direction):
        # Add symbol
        self.stdscr.addstr(symbol + " "*(self.maxx//4 - len(symbol)),
                           curses.color_pair(3))

        # Add price change with red/green/white for up/down/no change
        if direction == 'up':
            self.add_price(price, change, 2)
        elif direction == 'down':
            self.add_price(price, change, 1)
        else:
            self.add_price(price, change, 3)

        # Add time
        self.stdscr.addstr(" "*(self.maxx//4-len(change)) +
                           time.strftime('%X', time.localtime(
                                                 time.time())) + "\n",
                           curses.color_pair(3))

        self.stdscr.refresh()

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

    # Retrieve quote from Yahoo! finance and display
    def get_data(self, url):
        response = requests.get(url)
        results = response.text
        self.stdscr.clear()
        self.add_title()

        for line in csv.reader(results.splitlines(), delimiter=','):
            # Parse the symbol and price (remove quotes from symbol)
            try:
                direction = 'up'  # Assume no change is up
                # Calculate change
                change = (self.last[line[0]] - float(line[1]))
                # Get direction from up/down change
                if change > 0:
                    direction = 'up'
                elif change < 0:
                    direction = 'down'

                # Add data to screen
                self.update_screen(line[0], line[1], str(change), direction)
                # Update last quote price
                self.last[line[0]] = float(line[1])

            # Yahoo sometimes returns bad data
            except:
                pass

    # Main function
    def run(self):
        # Get url
        url = self.format_data()

        # Infinite loop
        while 1:
            self.get_data(url)
            # Sleep for 5 seconds before getting new data
            time.sleep(5)

    # Properly end session
    def end_session(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

if __name__ == "__main__":
    import sys
    import traceback

    # Init monitor
    monitor = MonitorTUI()

    # Monitor until script is stopped
    try:
        monitor.run()
    except KeyboardInterrupt:
        monitor.end_session()
        sys.exit(0)
    except:
        monitor.end_session()
        traceback.print_exc()
        sys.exit(1)
