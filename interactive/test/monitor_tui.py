#!/usr/bin/python
import curses
import csv
import sys
import traceback
import requests
import time


class MonitorTUI:
    def __init__(self):
        try:
            self.options = [("Ticker", 's'),
                            ("Last", 'l1'),
                            ("Change", 'c1'),
                            ("Change (%)", 'p2'),
                            ("Low", 'g'),
                            ("High", 'h'),
                            ("Volume", 'v')
                            ]
            # Init Screen
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            curses.noecho()
            self.stdscr.nodelay(1)
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

    # Format url to get quote from Yahoo! finance
    # Default options are to recieve the symbol and price
    def format_data(self):
        base_url = "http://finance.yahoo.com/d/quotes.csv"
        url = "{0}?s=".format(base_url)

        # Add stock symbols to URL
        for key in self.stocks.keys():
            url = url + "{0}+".format(key)

        # Add options to URL (and remove extra '+'
        url = "{0}&f={1}".format(url[:-1],
                                 ''.join([o[1] for o in self.options]))

        return url

    # Return True/False if market is open/closed
    def is_open(self):
        now = time.localtime(time.time())
        return(now[6] < 5 and
               (9 <= now[3] < 15 or
               (now[3] == 8 and now[4] >= 30)))

    # Add string containing labels
    def add_title(self):
        self.stdscr.addstr("Time: " +
                           time.strftime('%X', time.localtime(
                                                 time.time())) + " CST ")
        if not self.is_open():
            self.stdscr.addstr(" (Market closed)")

        self.stdscr.addstr("\n"*2)
        for option in self.options:
            self.stdscr.addstr(option[0] +
                               " "*(self.maxx//len(self.options) -
                                    len(option[0])))

        self.stdscr.addstr("\n")

        self.stdscr.addstr("_"*(self.maxx) + "\n")
        self.stdscr.refresh()

    def update_screen(self, data, direction):
        data_size = len(data)
        # Add symbol

        self.stdscr.addstr(data[0] + " "*(self.maxx//data_size - len(data[0])),
                           curses.color_pair(3))

        for d in data[1:4]:
            self.stdscr.addstr(d, curses.color_pair(direction))
            self.stdscr.addstr(" "*(self.maxx//data_size - len(d)))

        for d in data[4:]:
            self.stdscr.addstr(d + " "*(self.maxx//data_size - len(d)),
                               curses.color_pair(3))

        self.stdscr.addstr("\n")

        self.stdscr.refresh()

    # Retrieve quote from Yahoo! finance and display
    def get_data(self, url):
        response = requests.get(url)
        results = response.text
        self.stdscr.clear()
        self.add_title()

        for line in csv.reader(results.splitlines(), delimiter=','):
            # Find direction of quote price
            # 3: No change, 2: increase, 1: decrease
            direction = 3  # Assume no change
            if line[2][0] == '+':
                direction = 2
            elif line[2][0] == '-':
                direction = 1

            # Add data to screen
            self.update_screen(line, direction)

    # Get stock ticker from input
    def get_ticker(self):
        self.stdscr.clear()
        self.stdscr.addstr("Input ticker: ")
        self.stdscr.refresh()
        self.stdscr.nodelay(0)

        curses.echo()
        ticker = self.stdscr.getstr()
        # Check for proper symbol
        curses.noecho()
        self.stdscr.nodelay(1)
        return ticker.upper()

    # Main function
    def run(self):
        # Get url
        url = self.format_data()

        # Infinite loop
        while 1:
            # Interactive portfolio managing
            ch = self.stdscr.getch()
            # Quit on 'q' pressed
            if ch == ord('q'):
                self.end_session()
                sys.exit(0)

            # Add stock ticker
            elif ch == ord('+'):
                ticker = self.get_ticker()
                if ticker is not None:
                    # Default price set to $0
                    self.stocks[ticker] = 0.0
                    # Reformat URL with new ticker
                    url = self.format_data()

            # Remove ticker
            elif ch == ord('-'):
                ticker = self.get_ticker()
                if ticker in self.stocks.keys():
                    del self.stocks[ticker]
                    url = self.format_data()

            self.get_data(url)
            # Sleep for .5 seconds before getting new data
            time.sleep(.5)

    # Properly end session
    def end_session(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

if __name__ == "__main__":
    # Init monitor
    monitor = MonitorTUI()

    # Monitor until script is stopped
    try:
        monitor.run()
    except KeyboardInterrupt:
        monitor.end_session()
        sys.exit(0)
    except SystemExit:
        monitor.end_session()
        sys.exit(0)
    except:
        monitor.end_session()
        traceback.print_exc()
        sys.exit(1)
