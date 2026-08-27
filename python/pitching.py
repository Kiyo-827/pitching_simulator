#!/usr/bin/env python3

import sys
import configparser
import ast
import math
from pathlib import Path

import numpy as np


# ============================================================
# 1. Parameter handling
# ============================================================

def parse_vector(text):
    """
    Parse a three-dimensional vector.

    Example:
        "[0.0, 35.0, 1.0]"

    Returns
    -------
    numpy.ndarray
        Three-component vector.
    """

    value = ast.literal_eval(text)

    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"Expected a list or tuple, got: {text}"
        )

    if len(value) != 3:
        raise ValueError(
            f"Expected exactly three components, got: {text}"
        )

    return np.array(value, dtype=float)


def load_parameters(filename):
    """
    Read parameters from parameter.ini.
    """

    config = configparser.ConfigParser()

    read_files = config.read(
        filename,
        encoding="utf-8",
    )

    if not read_files:
        raise FileNotFoundError(
            f"Could not read parameter file: {filename}"
        )

    if "parameters" not in config:
        raise KeyError(
            "[parameters] section was not found."
        )

    p = config["parameters"]

    params = {
        # Physical properties
        "gravity":
            p.getfloat("gravity"),

        "air_density":
            p.getfloat("air_density"),

        "ball_density":
            p.getfloat("ball_density"),

        "ball_sizes_mm":
            p.getfloat("ball_sizes_mm"),

        # Aerodynamic coefficients
        "drag_coefficient":
            p.getfloat("drag_coefficient"),

        "magnus_coefficient":
            p.getfloat("magnus_coefficient"),

        # Initial conditions
        "initial_position":
            parse_vector(
                p.get("initial_position")
            ),

        "initial_speed":
            parse_vector(
                p.get("initial_speed")
            ),

        "initial_direction":
            parse_vector(
                p.get("initial_direction")
            ),

        # Rotation
        "angular_velocity":
            parse_vector(
                p.get("angular_velocity")
            ),

        # Numerical settings
        "dt":
            p.getfloat("dt"),

        "max_time":
            p.getfloat("max_time"),

        "target_y":
            p.getfloat("target_y"),
    }

    validate_parameters(params)

    return params


def validate_parameters(params):
    """
    Validate parameter values.
    """

    if params["gravity"] < 0.0:
        raise ValueError(
            "gravity must be non-negative."
        )

    if params["air_density"] < 0.0:
        raise ValueError(
            "air_density must be non-negative."
        )

    if params["ball_density"] <= 0.0:
        raise ValueError(
            "ball_density must be positive."
        )

    if params["ball_sizes_mm"] <= 0.0:
        raise ValueError(
            "ball_sizes_mm must be positive."
        )

    if params["drag_coefficient"] < 0.0:
        raise ValueError(
            "drag_coefficient must be non-negative."
        )

    if params["magnus_coefficient"] < 0.0:
        raise ValueError(
            "magnus_coefficient must be non-negative."
        )

    if np.linalg.norm(
        params["initial_speed"]
    ) <= 0.0:
        raise ValueError(
            "initial_speed must not be [0, 0, 0]."
        )

    if np.linalg.norm(
        params["initial_direction"]
    ) <= 0.0:
        raise ValueError(
            "initial_direction must not be [0, 0, 0]."
        )

    if params["dt"] <= 0.0:
        raise ValueError(
            "dt must be positive."
        )

    if params["max_time"] <= 0.0:
        raise ValueError(
            "max_time must be positive."
        )

    if params["target_y"] <= params["initial_position"][1]:
        raise ValueError(
            "target_y must be larger than the initial y position."
        )


# ============================================================
# 2. Ball properties
# ============================================================

def calculate_ball_properties(params):
    """
    Calculate physical properties of the ball.

    The baseball is approximated as a sphere.
    """

    diameter = (
        params["ball_sizes_mm"]
        * 1.0e-3
    )

    radius = diameter / 2.0

    volume = (
        (4.0 / 3.0)
        * math.pi
        * radius**3
    )

    area = (
        math.pi
        * radius**2
    )

    mass = (
        params["ball_density"]
        * volume
    )

    return {
        "diameter": diameter,
        "radius": radius,
        "volume": volume,
        "area": area,
        "mass": mass,
    }


# ============================================================
# 3. Initial conditions
# ============================================================

def initial_state(params):
    """
    Construct the initial position and velocity.

    initial_speed:
        Only the magnitude of this vector is used.

    initial_direction:
        Determines the direction of the velocity vector.
    """

    position = np.array(
        params["initial_position"],
        dtype=float,
    )

    speed = np.linalg.norm(
        params["initial_speed"]
    )

    direction = np.array(
        params["initial_direction"],
        dtype=float,
    )

    direction_unit = (
        direction
        / np.linalg.norm(direction)
    )

    velocity = (
        speed
        * direction_unit
    )

    return position, velocity


# ============================================================
# 4. Forces
# ============================================================

def force_gravity(
    t,
    position,
    velocity,
    ball,
    params,
):
    """
    Gravity

        F_g = (0, 0, -m g)
    """

    mass = ball["mass"]
    g = params["gravity"]

    return np.array([
        0.0,
        0.0,
        -mass * g,
    ])


def force_drag(
    t,
    position,
    velocity,
    ball,
    params,
):
    """
    Aerodynamic drag.

        F_D = -1/2 * rho * C_D * A * |v| * v

    Parameters
    ----------
    velocity : numpy.ndarray
        Ball velocity [m/s]

    ball["area"] : float
        Cross-sectional area of the ball [m^2]

    params["air_density"] : float
        Air density [kg/m^3]

    params["drag_coefficient"] : float
        Drag coefficient [-]

    Returns
    -------
    numpy.ndarray
        Drag force [N]
    """

    rho = params["air_density"]
    cd = params["drag_coefficient"]
    area = ball["area"]

    speed = np.linalg.norm(velocity)

    # If the ball is stationary, drag is zero.
    if speed == 0.0:
        return np.zeros(3)

    force = (
        -0.5
        * rho
        * cd
        * area
        * speed
        * velocity
    )

    return force

def force_magnus(
    t,
    position,
    velocity,
    ball,
    params,
):
    """
    Magnus force.

        F_M =
        1/2 * rho * C_L * A * |v|^2
        * (omega_hat x v_hat)

    Parameters
    ----------
    velocity : numpy.ndarray
        Ball velocity [m/s]

    params["angular_velocity"] : numpy.ndarray
        Angular velocity vector [rad/s]

        [omega_x, omega_y, omega_z]

    ball["area"] : float
        Cross-sectional area [m^2]

    params["air_density"] : float
        Air density [kg/m^3]

    params["magnus_coefficient"] : float
        Magnus coefficient [-]

    Returns
    -------
    numpy.ndarray
        Magnus force [N]
    """

    rho = params["air_density"]
    cl = params["magnus_coefficient"]
    area = ball["area"]

    omega = params["angular_velocity"]

    speed = np.linalg.norm(velocity)
    omega_magnitude = np.linalg.norm(omega)

    # Magnus force is zero if there is no translation
    # or no rotation.
    if speed == 0.0 or omega_magnitude == 0.0:
        return np.zeros(3)

    # Unit vectors
    v_hat = velocity / speed
    omega_hat = omega / omega_magnitude

    # Direction and sin(theta) factor are both contained
    # in this cross product.
    magnus_direction = np.cross(
        omega_hat,
        v_hat,
    )

    force = (
        0.5
        * rho
        * cl
        * area
        * speed**2
        * magnus_direction
    )

    return force


def force_original(
    t,
    position,
    velocity,
    ball,
    params,
):
    """
    Original aerodynamic-force model.

    For example:
        seam-induced aerodynamic force.

    ----------------------------------------------------------
    Student implementation area
    ----------------------------------------------------------

    At present, this function returns zero.
    """

    # TODO:
    # Implement the seam-force model here.

    return np.zeros(3)


# ============================================================
# 5. Total force and acceleration
# ============================================================

def total_force(
    t,
    position,
    velocity,
    ball,
    params,
):
    """
    Sum all forces acting on the ball.
    """

    gravity = force_gravity(
        t,
        position,
        velocity,
        ball,
        params,
    )

    drag = force_drag(
        t,
        position,
        velocity,
        ball,
        params,
    )

    magnus = force_magnus(
        t,
        position,
        velocity,
        ball,
        params,
    )

    original = force_original(
        t,
        position,
        velocity,
        ball,
        params,
    )

    return (
        gravity
        + drag
        + magnus
        + original
    )


def acceleration(
    t,
    position,
    velocity,
    ball,
    params,
):
    """
    Calculate acceleration from Newton's second law.

        F = m a

    therefore

        a = F / m
    """

    force = total_force(
        t,
        position,
        velocity,
        ball,
        params,
    )

    return (
        force
        / ball["mass"]
    )


# ============================================================
# 6. Differential equations
# ============================================================

def derivatives(
    t,
    state,
    ball,
    params,
):
    """
    Calculate the derivative of the state vector.

    State:

        [x, y, z, vx, vy, vz]

    Derivative:

        [vx, vy, vz, ax, ay, az]
    """

    position = state[0:3]
    velocity = state[3:6]

    accel = acceleration(
        t,
        position,
        velocity,
        ball,
        params,
    )

    return np.array([
        velocity[0],
        velocity[1],
        velocity[2],
        accel[0],
        accel[1],
        accel[2],
    ])


# ============================================================
# 7. Fourth-order Runge-Kutta method
# ============================================================

def rk4_step(
    t,
    state,
    ball,
    params,
):
    """
    Advance the state by one time step using the
    classical fourth-order Runge-Kutta method.
    """

    dt = params["dt"]

    k1 = derivatives(
        t,
        state,
        ball,
        params,
    )

    k2 = derivatives(
        t + 0.5 * dt,
        state + 0.5 * dt * k1,
        ball,
        params,
    )

    k3 = derivatives(
        t + 0.5 * dt,
        state + 0.5 * dt * k2,
        ball,
        params,
    )

    k4 = derivatives(
        t + dt,
        state + dt * k3,
        ball,
        params,
    )

    new_state = (
        state
        + (dt / 6.0)
        * (
            k1
            + 2.0 * k2
            + 2.0 * k3
            + k4
        )
    )

    return new_state


# ============================================================
# 8. Simulation
# ============================================================

def simulate(params):
    """
    Run the pitching simulation.

    Output columns:

        t
        x
        y
        z
        v_x
        v_y
        v_z
        a_x
        a_y
        a_z
    """

    ball = calculate_ball_properties(
        params
    )

    position, velocity = initial_state(
        params
    )

    state = np.concatenate([
        position,
        velocity,
    ])

    t = 0.0

    data = []

    while t <= params["max_time"]:

        position = state[0:3]
        velocity = state[3:6]

        accel = acceleration(
            t,
            position,
            velocity,
            ball,
            params,
        )

        data.append([
            t,
            position[0],
            position[1],
            position[2],
            velocity[0],
            velocity[1],
            velocity[2],
            accel[0],
            accel[1],
            accel[2],
        ])

        # Reached the home-plate plane.
        if position[1] >= params["target_y"]:
            break

        # Hit the ground.
        if (
            t > 0.0
            and position[2] <= 0.0
        ):
            break

        state = rk4_step(
            t,
            state,
            ball,
            params,
        )

        t += params["dt"]

    else:
        raise RuntimeError(
            "Simulation exceeded max_time."
        )

    return np.array(data)


# ============================================================
# 9. CSV output
# ============================================================

def write_csv(
    data,
    filename,
):
    """
    Write simulation results to CSV.

    Columns:

        t,x,y,z,v_x,v_y,v_z,a_x,a_y,a_z
    """

    filename.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    header = (
        "t,x,y,z,"
        "v_x,v_y,v_z,"
        "a_x,a_y,a_z"
    )

    np.savetxt(
        filename,
        data,
        delimiter=",",
        header=header,
        comments="",
        fmt="%.8e",
    )


# ============================================================
# 10. Main
# ============================================================

def main():

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    if len(sys.argv) >= 2:
        parameter_file = Path(
            sys.argv[1]
        )
    else:
        parameter_file = (
            project_root
            / "param"
            / "parameter.ini"
        )

    output_file = (
        project_root
        / "output"
        / "csv"
        / "pitching.csv"
    )

    try:

        params = load_parameters(
            parameter_file
        )

        data = simulate(
            params
        )

        write_csv(
            data,
            output_file,
        )

    except (
        FileNotFoundError,
        KeyError,
        ValueError,
        RuntimeError,
    ) as exc:

        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)

    print("Simulation completed.")
    print(
        f"CSV file was saved to {output_file}"
    )


if __name__ == "__main__":
    main()