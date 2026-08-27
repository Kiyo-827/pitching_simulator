#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np


# ============================================================
# Animation settings
# ============================================================

FPS = 60
FRAME_STRIDE = 1


# ============================================================
# Plot settings
# ============================================================

COLOR_TRAJECTORY = "#4084BD"
COLOR_BALL = "#D1495B"

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


def main():

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    csv_file = (
        project_root / "output" / "csv" / "pitching.csv"
    )

    movie_dir = (
        project_root / "output" / "movie"
    )

    movie_file = (
        movie_dir / "pitching.mp4"
    )

    movie_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Load trajectory
    # --------------------------------------------------------

    data = load_data(csv_file)

    t = data["t"]
    x = data["x"]
    y = data["y"]
    z = data["z"]

    # --------------------------------------------------------
    # Axis limits
    # --------------------------------------------------------

    x_limits = calculate_limits(x)
    y_limits = calculate_limits(y)
    z_limits = calculate_limits(z)

    x_range = x_limits[1] - x_limits[0]
    y_range = y_limits[1] - y_limits[0]
    z_range = z_limits[1] - z_limits[0]

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    fig = plt.figure(figsize=(12, 9))

    ax_xy = fig.add_subplot(2, 2, 1)
    ax_xz = fig.add_subplot(2, 2, 2)
    ax_yz = fig.add_subplot(2, 2, 3)
    ax_3d = fig.add_subplot(2, 2, 4, projection="3d")

    # --------------------------------------------------------
    # x-y plane
    # --------------------------------------------------------

    ax_xy.set_xlim(x_limits)
    ax_xy.set_ylim(y_limits)
    ax_xy.set_xlabel("x [m]")
    ax_xy.set_ylabel("y [m]")
    ax_xy.set_title("x-y plane")
    ax_xy.grid(True)

    # Equal scaling
    ax_xy.set_aspect("equal", adjustable="box")

    # --------------------------------------------------------
    # x-z plane
    # --------------------------------------------------------

    ax_xz.set_xlim(x_limits)
    ax_xz.set_ylim(z_limits)
    ax_xz.set_xlabel("x [m]")
    ax_xz.set_ylabel("z [m]")
    ax_xz.set_title("x-z plane")
    ax_xz.grid(True)

    # Equal scaling
    ax_xz.set_aspect("equal", adjustable="box")

    # --------------------------------------------------------
    # y-z plane
    # --------------------------------------------------------

    ax_yz.set_xlim(y_limits)
    ax_yz.set_ylim(z_limits)
    ax_yz.set_xlabel("y [m]")
    ax_yz.set_ylabel("z [m]")
    ax_yz.set_title("y-z plane")
    ax_yz.grid(True)

    # Equal scaling
    ax_yz.set_aspect("equal", adjustable="box")

    # --------------------------------------------------------
    # 3D trajectory
    # --------------------------------------------------------

    ax_3d.set_xlim(x_limits)
    ax_3d.set_ylim(y_limits)
    ax_3d.set_zlim(z_limits)

    ax_3d.set_xlabel("x [m]")
    ax_3d.set_ylabel("y [m]")
    ax_3d.set_zlabel("z [m]")
    ax_3d.set_title("3D trajectory")

    # --------------------------------------------------------
    # Important:
    # make x, y, z have the same data scale in 3D
    # --------------------------------------------------------
    ax_3d.set_box_aspect(
        (x_range, y_range, z_range)
    )

    # 見やすい視点
    ax_3d.view_init(elev=20, azim=-60)

    # --------------------------------------------------------
    # Plot objects
    # --------------------------------------------------------

    line_xy, = ax_xy.plot(
        [], [],
        color=COLOR_TRAJECTORY,
        linewidth=2.0,
    )
    point_xy, = ax_xy.plot(
        [], [],
        marker="o",
        linestyle="None",
        color=COLOR_BALL,
        markersize=7,
    )

    line_xz, = ax_xz.plot(
        [], [],
        color=COLOR_TRAJECTORY,
        linewidth=2.0,
    )
    point_xz, = ax_xz.plot(
        [], [],
        marker="o",
        linestyle="None",
        color=COLOR_BALL,
        markersize=7,
    )

    line_yz, = ax_yz.plot(
        [], [],
        color=COLOR_TRAJECTORY,
        linewidth=2.0,
    )
    point_yz, = ax_yz.plot(
        [], [],
        marker="o",
        linestyle="None",
        color=COLOR_BALL,
        markersize=7,
    )

    line_3d, = ax_3d.plot(
        [], [], [],
        color=COLOR_TRAJECTORY,
        linewidth=2.0,
    )
    point_3d, = ax_3d.plot(
        [], [], [],
        marker="o",
        linestyle="None",
        color=COLOR_BALL,
        markersize=6,
    )

    # --------------------------------------------------------
    # Time display
    # --------------------------------------------------------

    time_text = fig.text(
        0.5,
        0.97,
        "",
        horizontalalignment="center",
        verticalalignment="top",
        fontsize=14,
    )

    fig.suptitle(
        "Baseball pitching simulation",
        fontsize=16,
        y=0.995,
    )

    fig.tight_layout(
        rect=[0.0, 0.0, 1.0, 0.94]
    )

    # --------------------------------------------------------
    # Initialization
    # --------------------------------------------------------

    def init():

        line_xy.set_data([], [])
        point_xy.set_data([], [])

        line_xz.set_data([], [])
        point_xz.set_data([], [])

        line_yz.set_data([], [])
        point_yz.set_data([], [])

        line_3d.set_data_3d([], [], [])
        point_3d.set_data_3d([], [], [])

        time_text.set_text("")

        return (
            line_xy, point_xy,
            line_xz, point_xz,
            line_yz, point_yz,
            line_3d, point_3d,
            time_text,
        )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(frame_index):

        i = frame_index

        xs = x[:i + 1]
        ys = y[:i + 1]
        zs = z[:i + 1]

        # x-y
        line_xy.set_data(xs, ys)
        point_xy.set_data([x[i]], [y[i]])

        # x-z
        line_xz.set_data(xs, zs)
        point_xz.set_data([x[i]], [z[i]])

        # y-z
        line_yz.set_data(ys, zs)
        point_yz.set_data([y[i]], [z[i]])

        # 3D
        line_3d.set_data_3d(xs, ys, zs)
        point_3d.set_data_3d(
            [x[i]], [y[i]], [z[i]]
        )

        time_text.set_text(
            f"t = {t[i]:.3f} s"
        )

        return (
            line_xy, point_xy,
            line_xz, point_xz,
            line_yz, point_yz,
            line_3d, point_3d,
            time_text,
        )

    # --------------------------------------------------------
    # Frames
    # --------------------------------------------------------

    frame_indices = list(
        range(0, len(t), FRAME_STRIDE)
    )

    if frame_indices[-1] != len(t) - 1:
        frame_indices.append(len(t) - 1)

    # --------------------------------------------------------
    # Animation
    # --------------------------------------------------------

    animation = FuncAnimation(
        fig,
        update,
        frames=frame_indices,
        init_func=init,
        interval=1000.0 / FPS,
        blit=False,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    writer = FFMpegWriter(
        fps=FPS,
        metadata={
            "title": "Baseball pitching simulation"
        },
    )

    animation.save(
        movie_file,
        writer=writer,
        dpi=150,
    )

    plt.close(fig)

    print(f"Movie was saved to {movie_file}")


if __name__ == "__main__":
    main()