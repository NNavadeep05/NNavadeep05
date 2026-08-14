from pathlib import Path
import base64


# ============================================================
# CANVAS
# ============================================================

WIDTH = 1400
HEIGHT = 650


# ============================================================
# GITHUB DARK THEME + ACCENTS
# ============================================================

BG = "#0D1117"
PANEL = "#0D1117"
HEADER = "#161B22"

BORDER = "#22D3EE"
TEXT = "#F0F6FC"
MUTED = "#8B949E"

CYAN = "#22D3EE"
PURPLE = "#A78BFA"

GREEN = "#10B981"
RED = "#F85149"
YELLOW = "#F59E0B"


# ============================================================
# HELPER
# ============================================================

def text(
    x,
    y,
    content,
    color=TEXT,
    size=15,
    weight="normal",
    anchor="start",
):
    return f'''
        <text
            x="{x}"
            y="{y}"
            fill="{color}"
            font-family="monospace"
            font-size="{size}"
            font-weight="{weight}"
            text-anchor="{anchor}"
        >{content}</text>
    '''


# ============================================================
# GENERATE BANNER
# ============================================================

def create_banner():

    # --------------------------------------------------------
    # LOAD PORTRAIT
    # --------------------------------------------------------

    portrait_path = Path("assets/portrait.png")

    if not portrait_path.exists():
        raise FileNotFoundError(
            "assets/portrait.png was not found. "
            "Run prepare_portrait.py first."
        )

    portrait_data = base64.b64encode(
        portrait_path.read_bytes()
    ).decode("utf-8")

    portrait_uri = f"data:image/png;base64,{portrait_data}"


    # --------------------------------------------------------
    # SVG
    # --------------------------------------------------------

    svg = f'''<svg
        xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}"
        height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}"
    >

        <!-- ================================================= -->
        <!-- BACKGROUND                                        -->
        <!-- ================================================= -->

        <rect
            width="{WIDTH}"
            height="{HEIGHT}"
            fill="{BG}"
        />


        <!-- ================================================= -->
        <!-- TERMINAL HEADER                                   -->
        <!-- ================================================= -->

        <rect
            x="30"
            y="25"
            width="{WIDTH - 60}"
            height="55"
            rx="8"
            fill="{HEADER}"
        />

        <!-- Terminal buttons -->

        <circle
            cx="55"
            cy="52"
            r="8"
            fill="{RED}"
        />

        <circle
            cx="80"
            cy="52"
            r="8"
            fill="{YELLOW}"
        />

        <circle
            cx="105"
            cy="52"
            r="8"
            fill="{GREEN}"
        />

        <!-- Terminal title -->

        {text(
            135,
            59,
            "profile.sh --live",
            CYAN,
            18,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- LEFT PANEL                                       -->
        <!-- ================================================= -->

        <rect
            x="35"
            y="110"
            width="500"
            height="500"
            rx="6"
            fill="{PANEL}"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- VISUAL.MAP label -->

        <rect
            x="55"
            y="101"
            width="145"
            height="24"
            fill="{BG}"
        />

        {text(
            65,
            118,
            "VISUAL.MAP",
            CYAN,
            15,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- PORTRAIT                                         -->
        <!-- ================================================= -->

        <image
            href="{portrait_uri}"
            x="70"
            y="145"
            width="430"
            height="430"
            preserveAspectRatio="xMidYMid meet"
        />


        <!-- ================================================= -->
        <!-- RIGHT PANEL                                      -->
        <!-- ================================================= -->

        <rect
            x="555"
            y="110"
            width="810"
            height="500"
            rx="6"
            fill="{PANEL}"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- SYSTEM.INFO label -->

        <rect
            x="575"
            y="101"
            width="155"
            height="24"
            fill="{BG}"
        />

        {text(
            585,
            118,
            "SYSTEM.INFO",
            CYAN,
            15,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- USER BADGE                                       -->
        <!-- ================================================= -->

        <rect
            x="585"
            y="145"
            width="190"
            height="32"
            rx="16"
            fill="{GREEN}"
        />

        {text(
            680,
            166,
            "@NNAvadeep05",
            "#07130F",
            14,
            "bold",
            "middle"
        )}


        <!-- ================================================= -->
        <!-- LIVE INDICATOR                                   -->
        <!-- ================================================= -->

        <circle
            cx="810"
            cy="161"
            r="6"
            fill="{RED}"
        />

        {text(
            825,
            166,
            "LIVE",
            RED,
            13,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- SYSTEM INFORMATION                               -->
        <!-- ================================================= -->

        {text(
            585,
            215,
            "Subject ......................... Navadeep Nandedapu",
            TEXT,
            15
        )}

        {text(
            585,
            250,
            "Domain .......................... AI / ML / Data",
            TEXT,
            15
        )}

        {text(
            585,
            285,
            "Origin .......................... Hyderabad, India",
            TEXT,
            15
        )}

        {text(
            585,
            320,
            "Education ....................... Pursuing Bachelor's at IIT Kharagpur",
            TEXT,
            15
        )}

        {text(
            585,
            355,
            "Status .......................... Delusional",
            PURPLE,
            15,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- FOCUS                                             -->
        <!-- ================================================= -->

        {text(
            585,
            405,
            "Focus ........................... AI Systems",
            TEXT,
            15
        )}

        {text(
            585,
            440,
            "Stack ........................... C / C++ / Python / SQL",
            TEXT,
            15
        )}

        {text(
            585,
            475,
            "Currently ....................... Building + Researching",
            TEXT,
            15
        )}


        <!-- ================================================= -->
        <!-- CURRENTLY SECTION                                -->
        <!-- ================================================= -->

        {text(
            585,
            515,
            "CURRENTLY",
            CYAN,
            14,
            "bold"
        )}

        <line
            x1="680"
            y1="510"
            x2="1290"
            y2="510"
            stroke="{BORDER}"
            stroke-width="2"
        />

        {text(
            585,
            550,
            "Research ........................ Quantum Machine Learning",
            TEXT,
            14
        )}

        {text(
            585,
            580,
            "Building ........................ AI / Data Projects",
            TEXT,
            14
        )}


        <!-- ================================================= -->
        <!-- BOTTOM DIVIDER                                   -->
        <!-- ================================================= -->

        <line
            x1="35"
            y1="625"
            x2="1365"
            y2="625"
            stroke="#30363D"
            stroke-width="3"
        />

    </svg>
    '''


    # --------------------------------------------------------
    # WRITE SVG
    # --------------------------------------------------------

    Path("dark.svg").write_text(
        svg,
        encoding="utf-8"
    )

    print("Created dark.svg")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    create_banner()