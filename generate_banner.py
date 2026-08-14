from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
import math


# ============================================================
# CANVAS
# ============================================================

WIDTH = 1400
HEIGHT = 800


# ============================================================
# PANEL GEOMETRY
# ============================================================

LEFT_X = 35
LEFT_Y = 125
LEFT_W = 500
LEFT_H = 625

RIGHT_X = 555
RIGHT_Y = 125
RIGHT_W = 810
RIGHT_H = 625


# ============================================================
# PARTICLE FORMATION AREA
# ============================================================

# Images FORM inside this area.
# Explosion is allowed to travel outside it.

PARTICLE_X = LEFT_X + 35
PARTICLE_Y = LEFT_Y + 55

PARTICLE_W = LEFT_W - 70
PARTICLE_H = LEFT_H - 100


# ============================================================
# COLORS
# ============================================================

BG = "#0D1117"
PANEL = "#0D1117"
HEADER = "#161B22"

BORDER = "#22D3EE"
TEXT = "#F0F6FC"

CYAN = "#22D3EE"
PURPLE = "#A78BFA"

GREEN = "#10B981"
RED = "#F85149"
YELLOW = "#F59E0B"

DARK_BORDER = "#30363D"


# ============================================================
# ANIMATION SETTINGS
# ============================================================

FPS = 24

FORM_FRAMES = 42
HOLD_FRAMES = 36
EXPLODE_FRAMES = 30

PARTICLE_COUNT = 2200
PARTICLE_SIZE = 2

random.seed(42)


# ============================================================
# FONTS
# ============================================================

def get_font(size, bold=False):

    if bold:

        candidates = [
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/CascadiaMono-Bold.ttf",
            "C:/Windows/Fonts/DejaVuSansMono-Bold.ttf",
        ]

    else:

        candidates = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/CascadiaMono.ttf",
            "C:/Windows/Fonts/DejaVuSansMono.ttf",
        ]

    for path in candidates:

        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


FONT_TITLE = get_font(24, True)
FONT_SECTION = get_font(18, True)

FONT_MAIN = get_font(21, False)
FONT_MAIN_BOLD = get_font(21, True)

FONT_CURRENT = get_font(19, False)
FONT_CURRENT_BOLD = get_font(19, True)


# ============================================================
# EASING
# ============================================================

def ease_in_out(t):

    t = max(
        0.0,
        min(1.0, t)
    )

    return t * t * (3.0 - 2.0 * t)


# ============================================================
# LOAD IMAGE → PARTICLES
# ============================================================

def extract_particles(
    path,
    count=PARTICLE_COUNT
):

    img = Image.open(path).convert("RGBA")

    img.thumbnail(
        (
            PARTICLE_W,
            PARTICLE_H
        ),
        Image.Resampling.LANCZOS
    )

    canvas = Image.new(
        "RGBA",
        (
            PARTICLE_W,
            PARTICLE_H
        ),
        (
            13,
            17,
            23,
            255
        )
    )

    x_offset = (
        PARTICLE_W -
        img.width
    ) // 2

    y_offset = (
        PARTICLE_H -
        img.height
    ) // 2

    canvas.alpha_composite(
        img,
        (
            x_offset,
            y_offset
        )
    )

    gray = canvas.convert("L")

    candidates = []

    for y in range(PARTICLE_H):

        for x in range(PARTICLE_W):

            value = gray.getpixel(
                (
                    x,
                    y
                )
            )

            if value < 45:
                continue

            probability = (
                value - 45
            ) / 210.0

            probability = max(
                0.05,
                min(
                    1.0,
                    probability
                )
            )

            if random.random() < probability:

                candidates.append(
                    (
                        PARTICLE_X + x,
                        PARTICLE_Y + y
                    )
                )

    if not candidates:

        raise ValueError(
            f"No usable particles found in {path}"
        )

    if len(candidates) > count:

        candidates = random.sample(
            candidates,
            count
        )

    while len(candidates) < count:

        candidates.append(
            random.choice(candidates)
        )

    return candidates


# ============================================================
# LOAD ALL IMAGES
# ============================================================

def load_all_targets():

    folder = Path(
        "assets/dynamic"
    )

    files = sorted(
        folder.glob("image*.png")
    )

    if not files:

        raise FileNotFoundError(
            "No images found in assets/dynamic/"
        )

    print(
        "Images found:"
    )

    targets = []

    for file in files:

        print(
            f"  - {file.name}"
        )

        targets.append(
            extract_particles(file)
        )

    return targets


# ============================================================
# PARTICLE COLORS
# ============================================================

def create_particle_colors():

    colors = []

    for _ in range(
        PARTICLE_COUNT
    ):

        if random.random() < 0.18:

            colors.append(
                (
                    34,
                    211,
                    238
                )
            )

        else:

            colors.append(
                (
                    167,
                    139,
                    250
                )
            )

    return colors


# ============================================================
# STATIC BANNER
# ============================================================

def create_base():

    img = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT
        ),
        BG
    )

    draw = ImageDraw.Draw(img)


    # ========================================================
    # TERMINAL HEADER
    # ========================================================

    draw.rounded_rectangle(
        (
            30,
            30,
            WIDTH - 30,
            90
        ),
        radius=8,
        fill=HEADER
    )

    draw.ellipse(
        (
            48,
            51,
            66,
            69
        ),
        fill=RED
    )

    draw.ellipse(
        (
            76,
            51,
            94,
            69
        ),
        fill=YELLOW
    )

    draw.ellipse(
        (
            104,
            51,
            122,
            69
        ),
        fill=GREEN
    )

    draw.text(
        (
            145,
            39
        ),
        "profile.sh --live",
        font=FONT_TITLE,
        fill=CYAN
    )


    # ========================================================
    # LEFT PANEL
    # ========================================================

    draw.rounded_rectangle(
        (
            LEFT_X,
            LEFT_Y,
            LEFT_X + LEFT_W,
            LEFT_Y + LEFT_H
        ),
        radius=6,
        outline=BORDER,
        width=2
    )

    draw.rectangle(
        (
            55,
            116,
            200,
            142
        ),
        fill=BG
    )

    draw.text(
        (
            65,
            119
        ),
        "VISUAL.MAP",
        font=FONT_SECTION,
        fill=CYAN
    )


    # ========================================================
    # RIGHT PANEL
    # ========================================================

    draw.rounded_rectangle(
        (
            RIGHT_X,
            RIGHT_Y,
            RIGHT_X + RIGHT_W,
            RIGHT_Y + RIGHT_H
        ),
        radius=6,
        outline=BORDER,
        width=2
    )

    draw.rectangle(
        (
            575,
            116,
            730,
            142
        ),
        fill=BG
    )

    draw.text(
        (
            585,
            119
        ),
        "SYSTEM.INFO",
        font=FONT_SECTION,
        fill=CYAN
    )


    # ========================================================
    # USER BADGE
    # ========================================================

    draw.rounded_rectangle(
        (
            585,
            165,
            805,
            207
        ),
        radius=21,
        fill=GREEN
    )

    badge_text = "@NNAvadeep05"

    bbox = draw.textbbox(
        (
            0,
            0
        ),
        badge_text,
        font=FONT_MAIN_BOLD
    )

    badge_w = (
        bbox[2] -
        bbox[0]
    )

    draw.text(
        (
            695 - badge_w / 2,
            173
        ),
        badge_text,
        font=FONT_MAIN_BOLD,
        fill="#07130F"
    )


    # ========================================================
    # LIVE
    # ========================================================

    draw.ellipse(
        (
            830,
            174,
            846,
            190
        ),
        fill=RED
    )

    draw.text(
        (
            858,
            170
        ),
        "LIVE",
        font=FONT_MAIN_BOLD,
        fill=RED
    )


    # ========================================================
    # SYSTEM INFORMATION
    # ========================================================

    draw.text(
        (
            585,
            242
        ),
        "Subject ......................... Navadeep Nandedapu",
        font=FONT_MAIN,
        fill=TEXT
    )

    draw.text(
        (
            585,
            282
        ),
        "Domain .......................... AI / ML / Data",
        font=FONT_MAIN,
        fill=TEXT
    )

    draw.text(
        (
            585,
            322
        ),
        "Origin .......................... Hyderabad, India",
        font=FONT_MAIN,
        fill=TEXT
    )

    draw.text(
        (
            585,
            362
        ),
        "Education ....................... B.Tech at IIT Kharagpur",
        font=FONT_MAIN,
        fill=TEXT
    )

    draw.text(
        (
            585,
            402
        ),
        "Status .......................... Delusional",
        font=FONT_MAIN_BOLD,
        fill=PURPLE
    )


    # ========================================================
    # FOCUS
    # ========================================================

    draw.text(
        (
            585,
            455
        ),
        "Focus ........................... AI Systems",
        font=FONT_MAIN,
        fill=TEXT
    )

    draw.text(
        (
            585,
            495
        ),
        "Stack ........................... C / C++ / Python / SQL",
        font=FONT_MAIN,
        fill=TEXT
    )

    draw.text(
        (
            585,
            535
        ),
        "Currently ....................... Building + Researching",
        font=FONT_MAIN,
        fill=TEXT
    )


    # ========================================================
    # CURRENTLY
    # ========================================================

    draw.text(
        (
            585,
            590
        ),
        "CURRENTLY",
        font=FONT_CURRENT_BOLD,
        fill=CYAN
    )

    draw.line(
        (
            700,
            595,
            1295,
            595
        ),
        fill=BORDER,
        width=2
    )

    draw.text(
        (
            585,
            635
        ),
        "Research ........................ Quantum Machine Learning",
        font=FONT_CURRENT,
        fill=TEXT
    )

    draw.text(
        (
            585,
            670
        ),
        "Building ........................ AI / Data Projects",
        font=FONT_CURRENT,
        fill=TEXT
    )


    # ========================================================
    # BOTTOM DIVIDER
    # ========================================================

    draw.line(
        (
            35,
            775,
            1365,
            775
        ),
        fill=DARK_BORDER,
        width=3
    )

    return img


# ============================================================
# EXPLOSION POSITIONS
# ============================================================

def create_explosion_positions():

    positions = []

    center_x = (
        PARTICLE_X +
        PARTICLE_W / 2
    )

    center_y = (
        PARTICLE_Y +
        PARTICLE_H / 2
    )

    # --------------------------------------------------------
    # Explosion deliberately extends beyond VISUAL.MAP.
    # It is NOT clamped to the panel.
    # --------------------------------------------------------

    for _ in range(
        PARTICLE_COUNT
    ):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        radius = random.uniform(
            120,
            560
        )

        dx = (
            math.cos(angle) *
            radius
        )

        dy = (
            math.sin(angle) *
            radius
        )

        positions.append(
            (
                center_x + dx,
                center_y + dy
            )
        )

    return positions


# ============================================================
# DRAW PARTICLES
# ============================================================

def draw_particles(
    image,
    positions,
    colors,
    restrict_to_panel=False
):

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # During FORM/HOLD:
    # particles stay inside VISUAL.MAP.
    #
    # During EXPLOSION:
    # restrict_to_panel=False, so particles can leak.
    # --------------------------------------------------------

    if restrict_to_panel:

        min_x = LEFT_X + 2
        max_x = LEFT_X + LEFT_W - 4

        min_y = LEFT_Y + 25
        max_y = LEFT_Y + LEFT_H - 4

    else:

        min_x = 0
        max_x = WIDTH - PARTICLE_SIZE - 1

        min_y = 0
        max_y = HEIGHT - PARTICLE_SIZE - 1


    for i, (x, y) in enumerate(
        positions
    ):

        x = int(x)
        y = int(y)

        x = max(
            min_x,
            min(
                max_x,
                x
            )
        )

        y = max(
            min_y,
            min(
                max_y,
                y
            )
        )

        color = colors[i]

        draw.rectangle(
            (
                x,
                y,
                x + PARTICLE_SIZE,
                y + PARTICLE_SIZE
            ),
            fill=color
        )


# ============================================================
# INTERPOLATE
# ============================================================

def interpolate(
    start,
    end,
    progress
):

    eased = ease_in_out(
        progress
    )

    return (
        start[0] +
        (
            end[0] -
            start[0]
        ) * eased,

        start[1] +
        (
            end[1] -
            start[1]
        ) * eased
    )


# ============================================================
# CREATE ANIMATION
# ============================================================

def create_animation():

    targets = load_all_targets()

    colors = create_particle_colors()

    base = create_base()

    frames = []

    image_count = len(
        targets
    )

    print()

    print(
        f"Creating animation with {image_count} images..."
    )

    print(
        f"Particles: {PARTICLE_COUNT}"
    )

    print(
        f"FPS: {FPS}"
    )


    # ========================================================
    # IMAGE CYCLES
    # ========================================================

    for image_index in range(
        image_count
    ):

        current = targets[
            image_index
        ]

        explosion = (
            create_explosion_positions()
        )


        # ====================================================
        # REFORM
        # ====================================================

        for frame_number in range(
            FORM_FRAMES
        ):

            progress = (
                frame_number /
                (FORM_FRAMES - 1)
            )

            frame = base.copy()

            positions = []

            for i in range(
                PARTICLE_COUNT
            ):

                positions.append(
                    interpolate(
                        explosion[i],
                        current[i],
                        progress
                    )
                )

            draw_particles(
                frame,
                positions,
                colors,
                restrict_to_panel=True
            )

            frames.append(
                frame
            )


        # ====================================================
        # HOLD
        # ====================================================

        for _ in range(
            HOLD_FRAMES
        ):

            frame = base.copy()

            draw_particles(
                frame,
                current,
                colors,
                restrict_to_panel=True
            )

            frames.append(
                frame
            )


        # ====================================================
        # EXPLODE
        # ====================================================

        for frame_number in range(
            EXPLODE_FRAMES
        ):

            progress = (
                frame_number /
                (EXPLODE_FRAMES - 1)
            )

            frame = base.copy()

            positions = []

            for i in range(
                PARTICLE_COUNT
            ):

                positions.append(
                    interpolate(
                        current[i],
                        explosion[i],
                        progress
                    )
                )

            draw_particles(
                frame,
                positions,
                colors,
                restrict_to_panel=False
            )

            frames.append(
                frame
            )


        print(
            f"Completed image {image_index + 1}/{image_count}"
        )


    # ========================================================
    # SAVE GIF
    # ========================================================

    output = Path(
        "dark.gif"
    )

    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=int(
            1000 / FPS
        ),
        loop=0,
        optimize=True,
        disposal=2
    )

    print()

    print(
        f"Created {output}"
    )

    print(
        f"Frames: {len(frames)}"
    )

    print(
        f"Duration: {len(frames) / FPS:.1f} seconds"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_animation()