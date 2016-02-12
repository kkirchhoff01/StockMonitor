#!/bin/bash

# This script will take the stocks from each day and write them to their own file

# List of symbols
STOCKS="GOOG
V
CMG
HON
TSLA"

for month in {02..05}
do
    for day in {01..30}
    do
        for file in $STOCKS
        do
            if [ ! -e "$file/day_logs/" ]   # Create day_log directory if it doesn't exist
            then
                mkdir $file/day_logs
            fi
            if grep -q "$day/$month" "$file/$file.csv"  # Check for existing date
            then
                # Send data to it's own file for that day
                grep "$day/$month" $file/$file.csv > $file/day_logs/$day-$month.csv
            fi
        done
    done
done
