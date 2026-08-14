from pathlib import Path

import cv2
import numpy as np


INPUT = Path("assets/me.png")
OUTPUT = Path("assets/portrait.png")


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 430
HEIGHT = 430
GRID = 4


# IMPORTANT:
# These are RGB colors.
# We convert the final image to BGR before saving with OpenCV.

BG = np.array([13, 17, 23], dtype=np.uint8)          # #0D1117
PURPLE = np.array([167, 139, 250], dtype=np.uint8)   # #A78BFA
CYAN = np.array([34, 211, 238], dtype=np.uint8)      # #22D3EE


# ============================================================
# LOAD IMAGE
# ============================================================

image = cv2.imread(str(INPUT))

if image is None:
    raise FileNotFoundError(f"Could not find {INPUT}")


# ============================================================
# CROP TO SQUARE
# ============================================================

h, w = image.shape[:2]

size = min(w, h)

x1 = max((w - size) // 2, 0)
y1 = max((h - size) // 2, 0)

image = image[
    y1:y1 + size,
    x1:x1 + size
]


# ============================================================
# RESIZE
# ============================================================

image = cv2.resize(
    image,
    (WIDTH, HEIGHT),
    interpolation=cv2.INTER_AREA
)


# ============================================================
# HSV BACKGROUND MASK
# ============================================================

hsv = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2HSV
)

hue = hsv[:, :, 0]
sat = hsv[:, :, 1]
val = hsv[:, :, 2]


# Detect the cyan/blue background.
cyan_background = (
    (hue >= 75) &
    (hue <= 110) &
    (sat >= 60) &
    (val >= 70)
)


# ============================================================
# GRAYSCALE
# ============================================================

gray = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2GRAY
)


# ============================================================
# CONTRAST
# ============================================================

gray = cv2.normalize(
    gray,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)


# ============================================================
# DARK-SUBJECT MASK
# ============================================================

# Dark areas become strong.
# Bright background becomes weak.

darkness = 255 - gray

# Remove the detected background completely.
darkness[cyan_background] = 0


# ============================================================
# DOWNSAMPLE
# ============================================================

small_w = WIDTH // GRID
small_h = HEIGHT // GRID

small = cv2.resize(
    darkness,
    (small_w, small_h),
    interpolation=cv2.INTER_AREA
)


# ============================================================
# OUTPUT CANVAS
# ============================================================

# This canvas is RGB for now.
output = np.full(
    (HEIGHT, WIDTH, 3),
    BG,
    dtype=np.uint8
)


# ============================================================
# DRAW DOTS
# ============================================================

for y in range(small_h):

    for x in range(small_w):

        value = int(small[y, x])

        # Ignore weak areas.
        if value < 55:
            continue


        # Strong highlights -> cyan
        if value > 190:

            radius = 2
            color = CYAN


        # Medium areas -> purple
        elif value > 125:

            radius = 2
            color = PURPLE


        # Darker details -> purple, smaller dots
        else:

            radius = 1
            color = PURPLE


        cx = x * GRID + GRID // 2
        cy = y * GRID + GRID // 2


        cv2.circle(
            output,
            (cx, cy),
            radius,
            color.tolist(),
            -1
        )


# ============================================================
# CONVERT RGB -> BGR FOR OPENCV
# ============================================================

output = cv2.cvtColor(
    output,
    cv2.COLOR_RGB2BGR
)


# ============================================================
# SAVE
# ============================================================

cv2.imwrite(
    str(OUTPUT),
    output
)

print(f"Created {OUTPUT}")