#!/usr/bin/python

import sqlite3
import urllib
import time
import os


class MonitorSQL:
    def __init__(self):
        db_dir = os.getcwd() + '/db'
        db_path = db_dir + '/stocks.db'
        if not os.path.exists(db_dir):
            print 'Creating database directory'
            os.makedirs(os.getcwd() + '/db')

        self.stocks = ["HON", "GOOG", "CMG", "TSLA", "V"]
        self.conn = sqlite3.connect(database=db_path)
        self.curr = self.conn.cursor()

        for stock in self.stocks:
            self.curr.execute("""CREATE TABLE IF NOT EXISTS {0}(
                                    Time TEXT,
                                    Date TEXT,
                                    Price REAL
                                    );""".format(stock))

    def insert_quote(self, stock_name, price):
        self.curr.execute("""INSERT INTO {0} VALUES
                                (?, ?, ?);""".format(stock_name),
                          (time.strftime('%X'),
                           time.strftime('%x'),
                           price))

    def format_data(self, options=["s", "l1"]):
        base_url = "http://finance.yahoo.com/d/quotes.csv?s="
        url = "{0}".format(base_url)
        for key in self.stocks:
            url = url + "{0}+".format(key)
        url = url[:-1] + "&f={0}".format(''.join(options))
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

        for line in results.split('\n'):
            info = line.split(',')
            self.insert_quote(info[0].strip('"'), float(info[1]))

    def get_table(self, table_name):
        self.curr.execute("SELECT * FROM {0}".format(table_name))
        rows = self.curr.fetchall()
        return rows

    def monitor_stocks(self):
        url = self.format_data()
        while 1:
            if self.is_open():
                self.get_data(url)
            elif self.get_time(3) == 15 and self.get_time(4) <= 10:
                if self.get_time(6) < 5:
                    self.get_data(url)
                    self.conn.commit()
            time.sleep(600)

    def stop_monitor(self):
        self.conn.commit()
        self.curr.close()
        self.conn.close()

if __name__ == "__main__":
    import sys

    monitor = MonitorSQL()
    try:
        monitor.monitor_stocks()
    except Exception, e:
        monitor.stop_monitor()
        print e
        sys.exit()
