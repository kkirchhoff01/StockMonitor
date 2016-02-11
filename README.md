# StockMonitor
Program to fetch and store stock quotes from Yahoo! finance. It can store the quotes in CSV files or an SQLite database.

## stock_monitor.py

This script is used to fetch the quotes and store them in CSV files. This script is mostly for my FIN 301 class, which requires data in the form of Excell spreadsheets.

To use:

    ./stock_monitor.py

## monitor_sql.py

This script uses an SQLite database. I prefer this method and will update the script more frequently.

To run either script with a quote frequency of 10 minutes:

    ./monitor_sql.py

## Plotting

- From CSV:
 - plot_prices.py generates subplots for each stock's total value, along with the total value of the portfolio
 - plot_prices_single.py plots the total value of each stock in one window

- From SQL database:
 - monitor_sql.py has a plotting function to plot the total value of each stock in one window:

   ```python
   from monitor_sql import MonitorSQL
   monitor = MonitorSQL()
   monitor.plot_table(monitor.stocks.keys())
   ```
