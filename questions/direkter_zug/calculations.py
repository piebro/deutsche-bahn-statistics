import json
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def populate_direct_train_dict(df, direct_train_dict):
    df["arrival_time_delta_in_min"] = (
        df["arrival_change_time"] - df["arrival_planned_time"]
    ).dt.total_seconds() / 60
    df["departure_time_delta_in_min"] = (
        df["departure_change_time"] - df["departure_planned_time"]
    ).dt.total_seconds() / 60

    grouped = df.groupby("train_line_ride_id")
    for _, group in tqdm(grouped, total=grouped.ngroups, mininterval=2.0, smoothing=0.4, miniters=2000):
        if len(group) == 1:
            continue

        group = group.sort_values("train_line_station_num")
        num_of_stations = len(group)

        for i in range(num_of_stations - 1):
            row = group.iloc[i]
            from_station = row["station"]
            departure_time_delta = row["departure_time_delta_in_min"]

            if from_station not in direct_train_dict:
                direct_train_dict[from_station] = {}
            
            for j in range(i + 1, num_of_stations):
                next_row = group.iloc[j]
                to_station = next_row["station"]
                if to_station not in direct_train_dict[from_station]:
                    direct_train_dict[from_station][to_station] = []
                
                is_canceled = row["is_canceled"] or next_row["is_canceled"]
                ride_time_with_delay = int(
                    (next_row["arrival_change_time"] - row["departure_change_time"]).total_seconds() / 60
                )
                
                arrival_time_delta = next_row["arrival_time_delta_in_min"]
                direct_train_dict[from_station][to_station].append(
                    [
                        row["train_name"],
                        ride_time_with_delay,
                        departure_time_delta,
                        arrival_time_delta,
                        is_canceled,
                    ]
                )


def calculate_stats_and_save(direct_train_dict, save_dir):
    for station in list(direct_train_dict.keys()):
        for station2 in list(direct_train_dict[station].keys()):
            if not direct_train_dict[station][station2]:  # if list is empty
                del direct_train_dict[station][station2]
            else:
                direct_train_df = pd.DataFrame(
                    direct_train_dict[station][station2],
                    columns=[
                        "train_name",
                        "ride_time_with_delay",
                        "departure_time_delta",
                        "arrival_time_delta",
                        "is_canceled",
                    ],
                )
                direct_train_df = (
                    direct_train_df.groupby("train_name")
                    .agg(
                        {
                            "ride_time_with_delay": lambda x: x[~direct_train_df["is_canceled"]].mean(),
                            "departure_time_delta": lambda x: x[~direct_train_df["is_canceled"]].mean(),
                            "arrival_time_delta": lambda x: x[~direct_train_df["is_canceled"]].mean(),
                            "is_canceled": "mean",
                        }
                    )
                    .assign(sample_count=lambda x: direct_train_df.groupby("train_name").size())
                    .sort_values("sample_count", ascending=False)
                    .reset_index()
                    .set_axis(
                        [
                            "Zug",
                            "Fahrzeit inkl. Verspätungen [min]",
                            "Verspätung Abfahrt [min]",
                            "Verspätung Ankunft [min]",
                            "Ausfallquote",
                            "Stichprobengröße",
                        ],
                        axis=1,
                    )
                )
                file_name = f"{station}_to_{station2}.json".replace("/", "_").replace(" ", "_")
                with (save_dir / "alle_direkten_zuege" / file_name).open("w") as f:
                    f.write(direct_train_df.to_json(orient="records"))
                direct_train_dict[station][station2] = file_name



save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)

columns = [
    "station",
    "train_name",
    "train_line_ride_id",
    "train_line_station_num",
    "is_canceled",
    "arrival_planned_time",
    "arrival_change_time",
    "departure_planned_time",
    "departure_change_time",
]

last_full_months = sorted(Path("data").iterdir())[-3:]

direct_train_dict = {}
print("Processing Month 1/3")
populate_direct_train_dict(pd.read_parquet(last_full_months[0], columns=columns), direct_train_dict)
print("Processing Month 2/3")
populate_direct_train_dict(pd.read_parquet(last_full_months[1], columns=columns), direct_train_dict)
print("Processing Month 3/3")
populate_direct_train_dict(pd.read_parquet(last_full_months[2], columns=columns), direct_train_dict)
print("Calculating Stats")
calculate_stats_and_save(direct_train_dict, save_dir)

with (save_dir / "direkte_zuege_uebersicht.json").open("w", encoding="utf-8") as f:
    json.dump(direct_train_dict, f, ensure_ascii=False, indent=2)
