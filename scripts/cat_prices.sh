#!/bin/bash

# This script cats the prices from the CSV files to a new txt file

# List of stocks
STOCKS="GOOG
V
CMG
HON
TSLA"

fname="prices.txt"  # Output prices file

for file in $STOCKS
do
    if [ -e $file/$fname ]  # Remove existing prices file if it exists
    then
        echo "Removing $file/$fname"
        rm $file/$fname
    fi

    if [ -e $file/$file.csv ]   # If the CSV file exists extract prices
    then
        echo "Cat $file/$file.csv to $file/$fname"
        cat $file/$file.csv | cut -d "," -f 3 > $file/$fname    # Cut output with delimiter and get 3rd field
    fi
done
