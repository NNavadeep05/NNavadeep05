import os
import json
import urllib.request
from datetime import datetime, timedelta


# ============================================================
# SETTINGS
# ============================================================

USERNAME = "NNavadeep05"

OUTPUT = "stats.svg"

WIDTH = 1200
HEIGHT = 180

BG = "#0D1117"
TEXT = "#F0F6FC"
MUTED = "#8B949E"

CYAN = "#22D3EE"
PURPLE = "#A78BFA"
GREEN = "#10B981"


# ============================================================
# GITHUB GRAPHQL
# ============================================================

def get_contribution_data():

    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable not found."
        )

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $login) {
            contributionsCollection(
                from: $from
                to: $to
            ) {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            date
                            contributionCount
                        }
                    }
                }
            }
        }
    }
    """

    now = datetime.utcnow()

    start = now - timedelta(days=365)

    variables = {
        "login": USERNAME,
        "from": start.strftime("%Y-%m-%dT00:00:00Z"),
        "to": now.strftime("%Y-%m-%dT23:59:59Z"),
    }

    payload = json.dumps({
        "query": query,
        "variables": variables
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-profile-stats"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:

        data = json.loads(
            response.read().decode("utf-8")
        )

    if "errors" in data:

        raise RuntimeError(
            json.dumps(
                data["errors"],
                indent=2
            )
        )

    return data["data"]["user"]["contributionsCollection"][
        "contributionCalendar"
    ]


# ============================================================
# CALCULATE STREAKS
# ============================================================

def calculate_streaks(calendar):

    days = []

    for week in calendar["weeks"]:

        for day in week["contributionDays"]:

            days.append({
                "date": datetime.strptime(
                    day["date"],
                    "%Y-%m-%d"
                ).date(),
                "count": day["contributionCount"]
            })


    days.sort(
        key=lambda x: x["date"]
    )


    # --------------------------------------------------------
    # Current streak
    # --------------------------------------------------------

    today = days[-1]["date"]

    current_streak = 0

    index = len(days) - 1

    # If today has no contribution, allow yesterday
    # to be the beginning of the current streak.

    if days[index]["count"] == 0:

        index -= 1

        if index >= 0:
            today = days[index]["date"]


    while index >= 0:

        if days[index]["count"] <= 0:
            break

        if current_streak == 0:

            current_streak = 1

        else:

            previous = days[index + 1]["date"]

            current = days[index]["date"]

            if (previous - current).days != 1:
                break

            current_streak += 1

        index -= 1


    # --------------------------------------------------------
    # Longest streak
    # --------------------------------------------------------

    longest_streak = 0
    running_streak = 0

    previous_date = None

    for day in days:

        if day["count"] > 0:

            if (
                previous_date is not None
                and (day["date"] - previous_date).days == 1
            ):
                running_streak += 1

            else:
                running_streak = 1

            longest_streak = max(
                longest_streak,
                running_streak
            )

            previous_date = day["date"]

        else:

            running_streak = 0
            previous_date = None


    return (
        current_streak,
        longest_streak
    )


# ============================================================
# SVG TEXT
# ============================================================

def svg_text(
    x,
    y,
    value,
    size,
    color,
    weight="normal",
    anchor="middle"
):

    return f'''
    <text
        x="{x}"
        y="{y}"
        fill="{color}"
        font-family="monospace"
        font-size="{size}px"
        font-weight="{weight}"
        text-anchor="{anchor}"
    >{value}</text>
    '''


# ============================================================
# GENERATE SVG
# ============================================================

def generate_svg(
    total,
    current,
    longest
):

    third = WIDTH / 3

    svg = f'''<svg
        xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}"
        height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}"
    >

        <!-- Background -->

        <rect
            width="{WIDTH}"
            height="{HEIGHT}"
            rx="8"
            fill="{BG}"
        />


        <!-- Top accent -->

        <line
            x1="40"
            y1="12"
            x2="{WIDTH - 40}"
            y2="12"
            stroke="{CYAN}"
            stroke-width="2"
        />


        <!-- ================================================= -->
        <!-- TOTAL CONTRIBUTIONS                              -->
        <!-- ================================================= -->

        {svg_text(
            third * 0.5,
            78,
            total,
            38,
            TEXT,
            "bold"
        )}

        {svg_text(
            third * 0.5,
            112,
            "TOTAL CONTRIBUTIONS",
            15,
            CYAN,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- CURRENT STREAK                                   -->
        <!-- ================================================= -->

        {svg_text(
            third * 1.5,
            78,
            current,
            38,
            TEXT,
            "bold"
        )}

        {svg_text(
            third * 1.5,
            112,
            "CURRENT STREAK",
            15,
            GREEN,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- LONGEST STREAK                                   -->
        <!-- ================================================= -->

        {svg_text(
            third * 2.5,
            78,
            longest,
            38,
            TEXT,
            "bold"
        )}

        {svg_text(
            third * 2.5,
            112,
            "LONGEST STREAK",
            15,
            PURPLE,
            "bold"
        )}


        <!-- Dividers -->

        <line
            x1="{third}"
            y1="42"
            x2="{third}"
            y2="135"
            stroke="#30363D"
            stroke-width="2"
        />

        <line
            x1="{third * 2}"
            y1="42"
            x2="{third * 2}"
            y2="135"
            stroke="#30363D"
            stroke-width="2"
        />


        <!-- Bottom accent -->

        <line
            x1="40"
            y1="150"
            x2="{WIDTH - 40}"
            y2="150"
            stroke="#30363D"
            stroke-width="2"
        />


        <!-- Footer -->

        {svg_text(
            WIDTH / 2,
            172,
            "@NNAvadeep05 • CONTRIBUTION.STATS",
            11,
            MUTED,
            "normal"
        )}

    </svg>
    '''

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(svg)


# ============================================================
# MAIN
# ============================================================

def main():

    print("Fetching GitHub contribution data...")

    calendar = get_contribution_data()

    total = calendar["totalContributions"]

    current, longest = calculate_streaks(
        calendar
    )

    print()
    print(
        f"Total contributions : {total}"
    )

    print(
        f"Current streak      : {current}"
    )

    print(
        f"Longest streak      : {longest}"
    )

    generate_svg(
        total,
        current,
        longest
    )

    print()
    print(
        f"Created {OUTPUT}"
    )


if __name__ == "__main__":
    main()