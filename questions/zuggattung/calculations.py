from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from train_type_name_mapping import train_type_name_mapping

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load and combine data from the last 3 full months
df_list = []
for file in sorted(Path("data").iterdir())[-3:]:
    df_list.append(pd.read_parquet(file)[["station", "delay_in_min", "is_canceled", "train_type"]])
df = pd.concat(df_list, ignore_index=True)

df["train_type_name"] = df["train_type"].map(train_type_name_mapping)

stats = (
    df[~df["is_canceled"]]
    .groupby("train_type_name")
    .agg(
        {
            "delay_in_min": "mean",
            "train_type": lambda x: ", ".join(sorted(set(x))),
        }
    )
    .reset_index()
)

cancellation_sample_size_df = (
    df.groupby("train_type_name")
    .agg({"is_canceled": "mean", "station": "size"})
    .rename(
        columns={
            "is_canceled": "cancellation_rate",
            "station": "sample_size",
        }
    )
)
stats = stats.merge(cancellation_sample_size_df, on="train_type_name")

stats_sorted = stats.sort_values("sample_size", ascending=False)
stats_sorted.to_json(save_dir / "alle_zuggattungen_statistik.json", orient="records", force_ascii=False)


top_15 = stats_sorted.head(15)
labels = [
    f"{name} ({train_type})" for name, train_type in zip(top_15["train_type_name"], top_15["train_type"])
]

fig, ax1 = plt.subplots(figsize=(16, 10))

# Set the width of each bar and the positions of the bars
width = 0.35
x = range(len(labels))

# Plot average delay bars
bars1 = ax1.bar(
    [i - width / 2 for i in x],
    top_15["delay_in_min"],
    width,
    label="Durchschnittliche Verspätung",
    color="b",
    alpha=0.7,
)

# Create a second y-axis
ax2 = ax1.twinx()

# Plot cancellation rate bars
bars2 = ax2.bar(
    [i + width / 2 for i in x], top_15["cancellation_rate"], width, label="Ausfallquote", color="r", alpha=0.7
)

ax1.set_xlabel("Name der Zuggattung")
ax1.set_ylabel("Durchschnittliche Verspätung (Minuten)")
ax2.set_ylabel("Ausfallquote")
plt.title("Durchschnittliche Verspätung und Ausfallquote der 15 größten Zuggattungen")

ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha="right")


# Add value labels on the bars
def add_value_labels(bars, ax, x_offset=0):
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0 + x_offset,
            height,
            f"{height:.2f}",
            ha="center",
            va="bottom",
        )


add_value_labels(bars1, ax1)
add_value_labels(bars2, ax2, x_offset=0.07)

# Add legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.savefig(save_dir / "top_15_verspaetung_und_ausfallquote.png", dpi=100, bbox_inches="tight")
