#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_results(path: str = "results.csv"):
    sync = []
    async_ = []
    with Path(path).open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["drop_prob"] = float(row["drop_prob"])
            row["clients_expected"] = int(row["clients_expected"])
            row["received"] = int(row["received"])
            row["dropped"] = int(row["dropped"])
            row["duration"] = float(row["duration"])
            row["global_n"] = int(row["global_n"])
            row["global_mean"] = float(row["global_mean"]) if row["global_mean"] != "nan" else float("nan")
            row["global_var"] = float(row["global_var"]) if row["global_var"] != "nan" else float("nan")

            if row["mode"] == "sync":
                sync.append(row)
            else:
                async_.append(row)

    # sort by drop_prob just to be safe
    sync.sort(key=lambda r: r["drop_prob"])
    async_.sort(key=lambda r: r["drop_prob"])
    return sync, async_


def plot_duration(sync, async_):
    x_sync = [r["drop_prob"] for r in sync]
    y_sync = [r["duration"] for r in sync]

    x_async = [r["drop_prob"] for r in async_]
    y_async = [r["duration"] for r in async_]

    plt.figure()
    plt.plot(x_sync, y_sync, marker="o", label="sync")
    plt.plot(x_async, y_async, marker="o", label="async")
    plt.xlabel("Drop probability")
    plt.ylabel("Round duration (s)")
    plt.title("Runtime vs Drop Probability")
    plt.legend()
    plt.grid(True)
    plt.savefig("plot_duration_vs_drop.png", dpi=200)


def plot_success(sync, async_):
    def frac(r):
        return r["received"] / r["clients_expected"] if r["clients_expected"] else 0.0

    x_sync = [r["drop_prob"] for r in sync]
    y_sync = [frac(r) for r in sync]

    x_async = [r["drop_prob"] for r in async_]
    y_async = [frac(r) for r in async_]

    plt.figure()
    plt.plot(x_sync, y_sync, marker="o", label="sync")
    plt.plot(x_async, y_async, marker="o", label="async")
    plt.xlabel("Drop probability")
    plt.ylabel("Fraction of clients received")
    plt.ylim(-0.05, 1.05)
    plt.title("Client Success Rate vs Drop Probability")
    plt.legend()
    plt.grid(True)
    plt.savefig("plot_success_vs_drop.png", dpi=200)


def plot_mean_error(sync, async_):
    # “True” global mean for your synthetic data is ~0
    x_sync = [r["drop_prob"] for r in sync]
    y_sync = [abs(r["global_mean"]) for r in sync]

    x_async = [r["drop_prob"] for r in async_]
    y_async = [abs(r["global_mean"]) for r in async_]

    plt.figure()
    plt.plot(x_sync, y_sync, marker="o", label="sync")
    plt.plot(x_async, y_async, marker="o", label="async")
    plt.xlabel("Drop probability")
    plt.ylabel("|global_mean - 0|")
    plt.title("Mean Error vs Drop Probability")
    plt.legend()
    plt.grid(True)
    plt.savefig("plot_mean_error_vs_drop.png", dpi=200)


def main():
    sync, async_ = load_results("results.csv")
    plot_duration(sync, async_)
    plot_success(sync, async_)
    plot_mean_error(sync, async_)
    print("Saved: plot_duration_vs_drop.png, plot_success_vs_drop.png, plot_mean_error_vs_drop.png")


if __name__ == "__main__":
    main()
