#!/bin/bash
     
# Create a data directory
mkdir -p data

# Set the start date
start_date="2024-07-01"

# Get the current date
current_date=$(date +"%Y-%m-01")

# Loop through months and download files
while [[ "$start_date" < "$current_date" ]]; do
    year_month=$(date -d "$start_date" +"%Y-%m")
    url="https://github.com/piebro/deutsche-bahn-data/raw/refs/heads/main/monthly_data_releases/data-$year_month.parquet"
    output_file="data/data-$year_month.parquet"
    
    echo "Downloading $url"
    curl -L "$url" -o "$output_file"
    
    # Move to next month
    start_date=$(date -d "$start_date +1 month" +"%Y-%m-01")
done

echo "Download complete"