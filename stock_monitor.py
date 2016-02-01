import csv
import urllib


portfolio_log = "portfolio_log.csv"
info_key = {}
stock_info = {}
with open('portfolio.csv', 'rb') as fh:
    reader = csv.reader(fh, delimiter=',')
    for row in reader:
        if row[0] == "Ticker":
            info_key[row[0]] = tuple(row[1:])
        else:
            stock_info[row[0]] = tuple(row[1:])

def log_data(data):
    with open(portfolio_log, 'a') as fh:
        writer = csv.writer(fh, delimiter=',')
        for key in data.keys():
            writer.writerow([key] + list(data[key]))

log_data(stock_info)
