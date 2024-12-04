from pathlib import Path

import pandas as pd

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load and combine data from the last 3 full months
df_list = []
for file in sorted(Path("data").iterdir())[-3:]:
    df_list.append(pd.read_parquet(file)[["delay_in_min", "station", "is_canceled", "train_type"]])
df = pd.concat(df_list, ignore_index=True)

# Process data for different train types
for train_type in ["all", "ICE", "IC", "RE", "RB", "S"]:
    # Set up the title and filter data if necessary
    title = "Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten"
    if train_type == "all":
        df_train_type = df
    else:
        df_train_type = df[df["train_type"] == train_type]
        title = f"[{train_type}] {title}"

    # Calculate average delays and stop counts for each station
    station_df = (
        df_train_type[~df_train_type["is_canceled"]]
        .groupby("station")["delay_in_min"]
        .agg(["mean", "count"])
        .reset_index()
        .sort_values("mean", ascending=False)
        .reset_index(drop=True)
    )
    station_df.columns = ["station", "average_delay", "stop_count"]

    # Calculate cancellation rates and sample sizes for each station
    cancellation_sample_size_df = (
        df_train_type.groupby("station")
        .agg({"is_canceled": "mean", "station": "size"})
        .rename(
            columns={
                "is_canceled": "cancellation_rate",
                "station": "sample_size",
            }
        )
    )

    # Combine all statistics for each station
    station_df = station_df.merge(cancellation_sample_size_df, on="station")

    station_df.sort_values("average_delay")

    # Convert the results to JSON and save to a file
    json_data = station_df.to_json(orient="records")
    with (save_dir / f"{title}.json").open("w") as f:
        f.write(json_data)
