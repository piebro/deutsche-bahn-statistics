from pathlib import Path

import pandas as pd

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load and combine data from the last 3 full months
df_list = []
for file in sorted(Path("data").iterdir())[-3:]:
    df = pd.read_parquet(file, columns=["delay_in_min", "train_name", "train_type", "is_canceled"])
    df_list.append(df)
df = pd.concat(df_list, ignore_index=True)

# Define long-distance train types
long_distance_train_types = ["ICE", "IC", "FLX", "EC"]

# Calculate average delays, cancellation percentages, and sample counts by train
train_stats = (
    df[df["train_type"].isin(long_distance_train_types)]
    .groupby("train_name")
    .agg({"delay_in_min": ["mean", "count"], "is_canceled": "mean"})
    .sort_values(("delay_in_min", "count"), ascending=False)
)

# Flatten column names and rename for clarity
train_stats.columns = ["avg_delay", "sample_count", "cancellation_rate"]

# Reset index to include train name in the DataFrame
train_stats = train_stats.reset_index()

# Convert cancellation rate to percentage and remove the original rate
train_stats["cancellation_percentage"] = train_stats["cancellation_rate"] * 100
train_stats = train_stats.drop(columns=["cancellation_rate"])

# Round avg_delay and cancellation_percentage to two decimal places
train_stats["avg_delay"] = train_stats["avg_delay"].round(2)
train_stats["cancellation_percentage"] = train_stats["cancellation_percentage"].round(2)

# Convert the results to JSON and save to a file
json_data = train_stats.to_json(orient="records")
with (save_dir / "long_distance_train_stats.json").open("w") as f:
    f.write(json_data)
