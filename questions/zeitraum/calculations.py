from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

save_dir = Path(__file__).parent / "data"
save_dir.mkdir(exist_ok=True)


def create_time_period_plots(df, save_dir, freq, format_func, xlabel):
    """Create plots for a specific time period.

    Args:
        df: DataFrame with the data
        save_dir: Path object for saving the plots
        freq: Frequency string for period creation (e.g., 'M', 'D', 'h') or None for weekday
        format_func: Function to format period labels
        xlabel: Label for x-axis
    """
    save_dir.mkdir(exist_ok=True)

    # Create time period column
    if freq is None:  # weekday case
        df["period"] = pd.to_datetime(df["time"]).dt.weekday
    elif freq == "h":
        df["period"] = pd.to_datetime(df["time"]).dt.hour
    else:
        df["period"] = pd.to_datetime(df["time"]).dt.to_period(freq)

    # Create figures
    figs_axes = {
        "cancellations": plt.subplots(figsize=(10, 6)),
        "delays": plt.subplots(figsize=(10, 6)),
        "punctuality": plt.subplots(figsize=(10, 6)),
        "stops": plt.subplots(figsize=(10, 6)),
    }

    # Process data for different train types
    for train_type in ["all", "ICE", "IC", "RE", "RB", "S"]:
        df_train_type = df if train_type == "all" else df[df["train_type"] == train_type]
        display_name = "Alle" if train_type == "all" else train_type

        # Calculate statistics by period
        period_stats = df_train_type.groupby("period").agg(
            {
                "is_canceled": ["mean", "count"],
                "delay_in_min": [
                    ("avg_delay", lambda x: x[~df_train_type.loc[x.index, "is_canceled"]].mean()),
                    ("punctuality", lambda x: (x[~df_train_type.loc[x.index, "is_canceled"]] < 6).mean()),
                ],
            }
        )

        period_stats.columns = ["canceled_rate", "total_stops", "avg_delay", "punctuality"]
        periods_str = period_stats.index.map(format_func)

        # Plot the statistics
        plot_configs = [
            ("cancellations", "canceled_rate", 100, "Ausgefallene Züge", "Prozent (%)"),
            ("delays", "avg_delay", 1, "Durchschnittliche Verspätung", "Minuten"),
            ("punctuality", "punctuality", 100, "Pünktlichkeit (<6 min)", "Prozent (%)"),
            ("stops", "total_stops", 1, "Anzahl geplanter Halte", "Anzahl"),
        ]

        for plot_type, stat, multiplier, title, ylabel in plot_configs:
            fig, ax = figs_axes[plot_type]
            ax.plot(periods_str, period_stats[stat] * multiplier, marker="o", label=display_name)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
            ax.grid(True)

            # Special handling for hourly plots
            if freq == "h":
                ax.set_xticks(range(24))
                ax.set_xticklabels([f"{hour:02d}:00" for hour in range(24)], rotation=45)
            elif freq == "D":
                all_days = pd.to_datetime(periods_str)
                tick_mask = all_days.day.isin([1, 15])
                tick_positions = [i for i, mask in enumerate(tick_mask) if mask]
                tick_labels = periods_str[tick_mask]
                ax.set_xticks(tick_positions)
                ax.set_xticklabels(tick_labels, rotation=45)
            else:
                plt.setp(ax.get_xticklabels(), rotation=45)

            if plot_type == "stops":
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ",")))

    # Save the plots
    for plot_type, (fig, _) in figs_axes.items():
        filename = f"{plot_type}.png"
        fig.tight_layout()
        fig.savefig(save_dir / filename, bbox_inches="tight", dpi=300)
        plt.close(fig)


# Load data from all full months
df_list = []
for file in sorted(Path("data").iterdir()):
    df_list.append(pd.read_parquet(file)[["delay_in_min", "time", "is_canceled", "train_type"]])
df = pd.concat(df_list, ignore_index=True)

create_time_period_plots(df, save_dir / "monat", "M", lambda x: str(x), "Monat")

df = pd.concat(df_list[-3:], ignore_index=True)

create_time_period_plots(df, save_dir / "tag", "D", lambda x: x.strftime("%Y-%m-%d"), "Tag")

create_time_period_plots(df, save_dir / "uhrzeit", "h", lambda x: f"{x:02d}:00", "Stunde")

weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
create_time_period_plots(df, save_dir / "wochentag", None, lambda x: weekdays[x], "Wochentag")
