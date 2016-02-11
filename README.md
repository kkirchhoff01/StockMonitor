# StockMonitor
Program to fetch and store stock quotes from Yahoo! finance. It can store the quotes in CSV files or an SQLite database.

## monitor_sql.py

This script uses an SQLite database. I prefer this method and will update it more frequently.

Each table is a unique stock symbol, which has the format:

    | Time  | Date  | Quote  |
    | ----- |:-----:|-------:|
    | H:M:S | D/M/Y | $XX.XX |

To run with a quote frequency of 10 minutes:

    ./monitor_sql.py

## stock_monitor.py

This script is used to fetch the quotes and store them in CSV files. It is mostly for my FIN 301 class, which requires data in the form of Excel spreadsheets.

Stock symbols have their own folder, which contains their CSV file. The CSV files uses a comma (,) as the delimiter and use the format:

    Time,Date,Price

To run with a quote frequency of 10 minutes:

    ./stock_monitor.py

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

## Contributing

Anyone can contribute. Just submit a pull request.
