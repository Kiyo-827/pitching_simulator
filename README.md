#!/bin/bash

# Stop immediately if an error occurs.
set -e

# Move to the directory containing this script.
cd "$(dirname "$0")"


# ============================================================
# Python virtual environment
# ============================================================

VENV_DIR="./venv"

# Create virtual environment if it does not exist.
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "${VENV_DIR}"
fi

# Activate virtual environment.
if [ "${VIRTUAL_ENV:-}" != "$(pwd)/venv" ]; then
    echo "Activating Python virtual environment..."
    source "${VENV_DIR}/bin/activate"
fi


# ============================================================
# Install required Python packages
# ============================================================

echo "Checking Python packages..."

python3 -c "import numpy, matplotlib" 2>/dev/null || \
    python3 -m pip install numpy matplotlib


# ============================================================
# Check ffmpeg
# ============================================================

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "Error: ffmpeg is required to create the movie."
    echo
    echo "On Ubuntu / Debian, install it with:"
    echo "  sudo apt install ffmpeg"
    exit 1
fi


# ============================================================
# File settings
# ============================================================

PARAM_FILE="./param/parameter.ini"

PITCHING_SCRIPT="./python/pitching.py"
IMAGE_SCRIPT="./python/image.py"
MOVIE_SCRIPT="./python/movie.py"

CSV_DIR="./output/csv"
IMAGE_DIR="./output/image"
MOVIE_DIR="./output/movie"

CSV_FILE="${CSV_DIR}/pitching.csv"

IMAGE_XY="${IMAGE_DIR}/trajectory_xy.png"
IMAGE_XZ="${IMAGE_DIR}/trajectory_xz.png"
IMAGE_YZ="${IMAGE_DIR}/trajectory_yz.png"

MOVIE_FILE="${MOVIE_DIR}/pitching.mp4"


# ============================================================
# Check input files
# ============================================================

if [ ! -f "${PARAM_FILE}" ]; then
    echo "Error: parameter file was not found:"
    echo "  ${PARAM_FILE}"
    exit 1
fi

if [ ! -f "${PITCHING_SCRIPT}" ]; then
    echo "Error: pitching.py was not found:"
    echo "  ${PITCHING_SCRIPT}"
    exit 1
fi

if [ ! -f "${IMAGE_SCRIPT}" ]; then
    echo "Error: image.py was not found:"
    echo "  ${IMAGE_SCRIPT}"
    exit 1
fi

if [ ! -f "${MOVIE_SCRIPT}" ]; then
    echo "Error: movie.py was not found:"
    echo "  ${MOVIE_SCRIPT}"
    exit 1
fi


# ============================================================
# Prepare output directories
# ============================================================

mkdir -p "${CSV_DIR}"
mkdir -p "${IMAGE_DIR}"
mkdir -p "${MOVIE_DIR}"


# Remove previous results.
rm -f "${CSV_FILE}"
rm -f "${IMAGE_XY}"
rm -f "${IMAGE_XZ}"
rm -f "${IMAGE_YZ}"
rm -f "${MOVIE_FILE}"


# ============================================================
# STEP 1 / 4
# Run pitching simulation
# ============================================================

echo
echo "============================================================"
echo "STEP 1 / 4 : Pitching simulation"
echo "============================================================"
echo

python3 "${PITCHING_SCRIPT}" "${PARAM_FILE}"


# ============================================================
# STEP 2 / 4
# Check CSV output
# ============================================================

echo
echo "============================================================"
echo "STEP 2 / 4 : Check CSV output"
echo "============================================================"
echo

if [ ! -f "${CSV_FILE}" ]; then
    echo "Error: CSV file was not created:"
    echo "  ${CSV_FILE}"
    exit 1
fi

echo "CSV file:"
echo "  ${CSV_FILE}"

# Display the number of data rows.
NUM_LINES=$(wc -l < "${CSV_FILE}")

# Subtract one line for the CSV header.
NUM_DATA=$((NUM_LINES - 1))

echo "Number of time steps:"
echo "  ${NUM_DATA}"


# ============================================================
# STEP 3 / 4
# Create trajectory images
# ============================================================

echo
echo "============================================================"
echo "STEP 3 / 4 : Create trajectory images"
echo "============================================================"
echo

python3 "${IMAGE_SCRIPT}"


# Check image files.
for IMAGE_FILE in \
    "${IMAGE_XY}" \
    "${IMAGE_XZ}" \
    "${IMAGE_YZ}"
do
    if [ ! -f "${IMAGE_FILE}" ]; then
        echo "Error: image file was not created:"
        echo "  ${IMAGE_FILE}"
        exit 1
    fi
done

echo
echo "Image files:"
echo "  ${IMAGE_XY}"
echo "  ${IMAGE_XZ}"
echo "  ${IMAGE_YZ}"


# ============================================================
# STEP 4 / 4
# Create movie
# ============================================================

echo
echo "============================================================"
echo "STEP 4 / 4 : Create movie"
echo "============================================================"
echo

python3 "${MOVIE_SCRIPT}"


# Check movie file.
if [ ! -f "${MOVIE_FILE}" ]; then
    echo "Error: movie file was not created:"
    echo "  ${MOVIE_FILE}"
    exit 1
fi

echo
echo "Movie file:"
echo "  ${MOVIE_FILE}"


# ============================================================
# Finish
# ============================================================

echo
echo "============================================================"
echo "All processes completed successfully."
echo "============================================================"
echo

echo "Outputs:"
echo
echo "CSV:"
echo "  ${CSV_FILE}"
echo
echo "Images:"
echo "  ${IMAGE_XY}"
echo "  ${IMAGE_XZ}"
echo "  ${IMAGE_YZ}"
echo
echo "Movie:"
echo "  ${MOVIE_FILE}"
echo
