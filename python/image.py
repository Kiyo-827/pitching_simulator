#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# Plot settings
# ============================================================

COLOR_TRAJECTORY = "#4084BD"
COLOR_RELEASE = "#4C956C"
COLOR_END = "#D1495B"

MARGIN_FACTOR = 0.08
MIN_SPAN = 0.5


def load_data(csv_file):
    """
    Read pitching.csv.
    """

    if not csv_file.exists():
        raise FileNotFoundError(
            f"CSV file was not found: {csv_file}"
        )

    data = np.genfromtxt(
        csv_file,
        delimiter=",",
        names=True,
    )

    return {
        "t": np.atleast_1d(data["t"]),
        "x": np.atleast_1d(data["x"]),
        "y": np.atleast_1d(data["y"]),
        "z": np.atleast_1d(data["z"]),
    }


def calculate_limits(values):
    """
    Calculate plotting limits with margins.
    """

    vmin = float(np.min(values))
    vmax = float(np.max(values))

    span = vmax - vmin

    if span < MIN_SPAN:
        center = 0.5 * (vmin + vmax)
        half = 0.5 * MIN_SPAN
        return center - half, center + half

    margin = span * MARGIN_FACTOR
    return vmin - margin, vmax + margin


def plot_projection(
    horizontal,
    vertical,
    horizontal_label,
    vertical_label,
    title,
    output_file,
):
    """
    Save one 2D projection with equal axis scaling.
    """

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(
        horizontal,
        vertical,
        color=COLOR_TRAJECTORY,
        linewidth=2.0,
        label="trajectory",
    )

    ax.scatter(
        horizontal[0],
        vertical[0],
        color=COLOR_RELEASE,
        s=70,
        zorder=3,
        label="release",
    )

    ax.scatter(
        horizontal[-1],
        vertical[-1],
        color=COLOR_END,
        s=70,
        zorder=3,
        label="final point",
    )

    ax.set_xlim(calculate_limits(horizontal))
    ax.set_ylim(calculate_limits(vertical))

    ax.set_xlabel(horizontal_label)
    ax.set_ylabel(vertical_label)
    ax.set_title(title)
    ax.grid(True)
    ax.legend()

    # --------------------------------------------------------
    # Important:
    # make 1 m in horizontal direction equal to 1 m in vertical
    # direction
    # --------------------------------------------------------
    ax.set_aspect("equal", adjustable="box")

    fig.tight_layout()

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Image was saved to {output_file}")


def main():

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    csv_file = (
        project_root / "output" / "csv" / "pitching.csv"
    )

    image_dir = (
        project_root / "output" / "image"
    )

    image_dir.mkdir(parents=True, exist_ok=True)

    data = load_data(csv_file)

    x = data["x"]
    y = data["y"]
    z = data["z"]

    # x-y plane
    plot_projection(
        x,
        y,
        "x [m]",
        "y [m]",
        "Pitch trajectory: x-y plane",
        image_dir / "trajectory_xy.png",
    )

    # x-z plane
    plot_projection(
        x,
        z,
        "x [m]",
        "z [m]",
        "Pitch trajectory: x-z plane",
        image_dir / "trajectory_xz.png",
    )

    # y-z plane
    plot_projection(
        y,
        z,
        "y [m]",
        "z [m]",
        "Pitch trajectory: y-z plane",
        image_dir / "trajectory_yz.png",
    )


if __name__ == "__main__":
    main()