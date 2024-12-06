from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load and combine data from the last 3 full months
df_list = []
for file in sorted(Path("data").iterdir())[-3:]:
    df_list.append(
        pd.read_parquet(file)[["delay_in_min", "time", "is_canceled", "train_type", "train_line_ride_id"]]
    )
df = pd.concat(df_list, ignore_index=True)

# only look at stops that are not canceled
df = df[~df["is_canceled"]]

# Create a 'time_minutes' column that uses time since 2024-01-01 in minutes
df["time_minutes"] = (df["time"] - pd.Timestamp("2024-01-01")).dt.total_seconds() / 60


def calculate_delay_progression(data, max_time_since_start, train_type):
    print(f"Calculation delay progression for {train_type}")
    # Group by train_line_ride_id and aggregate time and delay
    grouped = data.groupby("train_line_ride_id").agg({"time_minutes": list, "delay_in_min": list})

    # Calculate time since start and average delay
    all_times = []
    all_delays = []

    for _, row in tqdm(
        grouped.iterrows(), total=len(grouped), mininterval=1.0, smoothing=0.4, miniters=10000
    ):
        times = np.array(row["time_minutes"])
        delays = row["delay_in_min"]

        all_times.extend(times - np.min(times))  # add times deltas (minutes since first stop)
        all_delays.extend(delays)

    # Create a DataFrame with the results
    result_df = pd.DataFrame({"time_since_start": all_times, "delay_in_min": all_delays})

    # Filter by max_time_since_start
    result_df = result_df[result_df["time_since_start"] <= max_time_since_start]

    # Group by time_since_start and calculate mean delay and count
    avg_delay = result_df.groupby("time_since_start").agg({"delay_in_min": ["mean", "count"]}).reset_index()
    avg_delay.columns = ["time_since_start", "mean_delay", "count"]

    return avg_delay


def plot_delay_progression(avg_delay, prefix):
    # Plot delay progression with weighted regression
    plt.figure(figsize=(12, 6))

    # Scatter plot with point size proportional to count
    plt.scatter(
        avg_delay["time_since_start"],
        avg_delay["mean_delay"],
        alpha=0.99,
        s=avg_delay["count"] / avg_delay["count"].max() * 1000,
    )

    # Weighted regression
    weights = avg_delay["count"]
    x = avg_delay["time_since_start"]
    y = avg_delay["mean_delay"]

    # Perform weighted least squares regression
    wx = np.average(x, weights=weights)
    wy = np.average(y, weights=weights)
    wx2 = np.average(x**2, weights=weights)
    wxy = np.average(x * y, weights=weights)

    slope = (wxy - wx * wy) / (wx2 - wx**2)
    intercept = wy - slope * wx

    line = slope * x + intercept

    plt.plot(
        x, line, color="r", label=f"Startverspätung: {intercept:.0f} min, Steigung: {slope * 60:.1f} min/h"
    )

    plt.xlabel("Zeit seit Zugstart (Minuten)")
    plt.ylabel("Durchschnittliche Verspätung (Minuten)")
    plt.title(f"{prefix}Durchschnittlicher Verspätungsverlauf")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.ylim(0, 40)

    max_time = max(avg_delay["time_since_start"])
    xticks = np.arange(0, max_time + 60, 60)
    plt.xticks(xticks)

    plt.savefig(save_dir / f"{prefix}Verspätungsverlauf.png", dpi=150, bbox_inches="tight")


all_trains_delay = calculate_delay_progression(df, max_time_since_start=300, train_type="all trains")
plot_delay_progression(all_trains_delay, "")

for train_type, max_time_since_start in [("IC", 420), ("ICE", 480), ("RB", 180), ("RE", 180), ("S", 180)]:
    all_trains_delay = calculate_delay_progression(
        df[df["train_type"] == train_type], max_time_since_start=max_time_since_start, train_type=train_type
    )
    plot_delay_progression(all_trains_delay, prefix=f"[{train_type}] ")
