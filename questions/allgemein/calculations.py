import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load data from the last full month
df = pd.read_parquet(sorted(Path("data").iterdir())[-1])[
    ["delay_in_min", "station", "is_canceled", "train_type"]
]

data_dict = {}
delay_distributions = {}

bins = [-np.inf, 0, 5, 10, 15, 30, 60, np.inf]
labels = [
    "keine Verspätung",
    "0 - 5 min",
    "5 - 10 min",
    "10 - 15 min",
    "15 - 30 min",
    "30 - 60 min",
    "> 60 min",
]

# Process data for different train types
for train_type in ["all", "ICE", "IC", "RE", "RB", "S"]:
    if train_type == "all":
        df_train_type = df
        display_name = "Alle"  # Add display name for the plot
    else:
        df_train_type = df[df["train_type"] == train_type]
        display_name = train_type

    data_dict[f"ausgefallen_{train_type}"] = f"{int(df_train_type['is_canceled'].mean() * 100)}%"

    df_train_type = df_train_type[~df_train_type["is_canceled"]]

    data_dict[f"summer_zughalte_{train_type}"] = len(df_train_type)
    mean_delay = df_train_type["delay_in_min"].mean()
    data_dict[f"durchschnittliche_verspaetung_{train_type}"] = (
        f"{int(mean_delay)}:{int((mean_delay - int(mean_delay)) * 60):02d}"
    )
    data_dict[f"puenktlich_{train_type}"] = f"{int((df_train_type['delay_in_min'] < 6).mean() * 100)}%"

    # Calculate delay distribution
    delay_hist = pd.cut(df_train_type["delay_in_min"], bins=bins)
    delay_distributions[display_name] = delay_hist.value_counts(normalize=True) * 100


with (save_dir / "allgemeine_statistiken.json").open("w", encoding="utf-8") as f:
    json.dump(data_dict, f, ensure_ascii=False, indent=4)

# Create visualization after data collection
plt.figure(figsize=(12, 6))
bar_width = 0.15
x = np.arange(len(labels))

for i, train_type in enumerate(["Alle", "ICE", "IC", "RE", "RB", "S"]):
    plt.bar(x + i * bar_width, delay_distributions[train_type].values, bar_width, label=train_type, alpha=0.8)

# Customize the chart
plt.xlabel("Durchschnittliche Verspätung [Minuten]")
plt.ylabel("Prozent aller Züge [%]")
plt.title("Verteilung von Verspätungen nach Zuggattung")

# Format x-axis labels
plt.xticks(x + bar_width * 2, labels, rotation=45, ha="right")

# Format y-axis to show percentage symbol
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x)}%"))

plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.savefig(save_dir / "Verteilung von Verspätungen.png", dpi=150, bbox_inches="tight")
plt.close()
