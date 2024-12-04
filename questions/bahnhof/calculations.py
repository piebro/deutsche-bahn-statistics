import json
from pathlib import Path

import pandas as pd

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load and combine data from the last 3 full months
df_list = []
for file in sorted(Path("data").iterdir())[-3:]:
    df_list.append(pd.read_parquet(file)[["delay_in_min", "station", "is_canceled", "train_type"]])
df = pd.concat(df_list, ignore_index=True)

# Calculate statistics for all trains (marking them as "alle Züge")
all_stats = (
    df.groupby("station")
    .agg(
        {
            "delay_in_min": lambda x: x[~df.loc[x.index, "is_canceled"]].mean(),
            "is_canceled": "mean",
            "station": "size",
        }
    )
    .rename(
        columns={
            "delay_in_min": "average_delay",
            "is_canceled": "cancellation_rate",
            "station": "sample_size",
        }
    )
    .reset_index()
)
all_stats["train_type"] = "alle Züge"

# Calculate statistics by train type
type_stats = (
    df.groupby(["station", "train_type"])
    .agg(
        {
            "delay_in_min": lambda x: x[~df.loc[x.index, "is_canceled"]].mean(),
            "is_canceled": "mean",
            "station": "size",
        }
    )
    .rename(
        columns={
            "delay_in_min": "average_delay",
            "is_canceled": "cancellation_rate",
            "station": "sample_size",
        }
    )
    .reset_index()
)

# Combine all_stats and type_stats
combined_stats = pd.concat([all_stats, type_stats], ignore_index=True)

# Round the numeric columns
combined_stats["average_delay"] = combined_stats["average_delay"].round(2).fillna(0)
combined_stats["cancellation_rate"] = combined_stats["cancellation_rate"].round(2)

# Create a dictionary where each station has a list of its train type statistics
station_dict = {}
for station in combined_stats["station"].unique():
    station_stats = (
        combined_stats[combined_stats["station"] == station]
        .sort_values(["sample_size"], ascending=False)[
            ["train_type", "average_delay", "cancellation_rate", "sample_size"]
        ]
        .to_dict("records")
    )
    station_dict[station] = station_stats

# Save the combined statistics
title = "Bahnhof_Statistiken"
with (save_dir / f"{title}.json").open("w", encoding="utf-8") as f:
    json.dump(station_dict, f, ensure_ascii=False, indent=2)
