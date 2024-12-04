import json
from pathlib import Path

import pandas as pd

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

# Load and combine data from the last 3 full months
df_list = []
for file in sorted(Path("data").iterdir())[-3:]:
    df_list.append(pd.read_parquet(file)[["station", "train_type"]])
df = pd.concat(df_list, ignore_index=True)


# Function to categorize train types
def categorize_train_type(train_type):
    return train_type if train_type in ["IC", "ICE", "RB", "RE", "S"] else "Sonstige"


# Add a new column for categorized train types
df["train_type_category"] = df["train_type"].map(categorize_train_type)

# Group by station and train type, then count
station_train_counts = df.groupby(["station", "train_type_category"]).size().unstack(fill_value=0)

# Add total column
station_train_counts["Total"] = station_train_counts.sum(axis=1)

station_train_counts.sort_values(by="ICE", ascending=False, inplace=True)

data_for_json = station_train_counts.reset_index().to_dict("records")

# Save data as JSON
with open(save_dir / "Verteilung_von_Zuggattungen_pro_Bahnhof.json", "w", encoding="utf-8") as f:
    json.dump(data_for_json, f, ensure_ascii=False, indent=4)
