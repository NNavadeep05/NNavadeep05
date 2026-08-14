import os
import json
import urllib.request
from datetime import datetime, timedelta


# ============================================================
# SETTINGS
# ============================================================

USERNAME = "NNavadeep05"

OUTPUT = "stats.svg"

WIDTH = 1400
HEIGHT = 360

BG = "#0D1117"
TEXT = "#F0F6FC"
MUTED = "#8B949E"

CYAN = "#22D3EE"
PURPLE = "#A78BFA"
GREEN = "#10B981"
BORDER = "#30363D"


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
# STREAK CALCULATIONS
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

    days.sort(key=lambda x: x["date"])


    # --------------------------------------------------------
    # Current streak
    # --------------------------------------------------------

    current_streak = 0
    index = len(days) - 1

    if days[index]["count"] == 0:
        index -= 1

    while index >= 0:

        if days[index]["count"] <= 0:
            break

        current_streak += 1

        if index == 0:
            break

        current_day = days[index]["date"]
        previous_day = days[index - 1]["date"]

        if (current_day - previous_day).days != 1:
            break

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

    return current_streak, longest_streak


# ============================================================
# SVG TEXT HELPER
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

    first_center = third * 0.5
    second_center = third * 1.5
    third_center = third * 2.5

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
            x="0"
            y="0"
            width="{WIDTH}"
            height="{HEIGHT}"
            rx="12"
            fill="{BG}"
        />


        <!-- ================================================= -->
        <!-- TOP ACCENT                                        -->
        <!-- ================================================= -->

        <line
            x1="55"
            y1="24"
            x2="{WIDTH - 55}"
            y2="24"
            stroke="{CYAN}"
            stroke-width="3"
        />


        <!-- ================================================= -->
        <!-- TOTAL CONTRIBUTIONS                              -->
        <!-- ================================================= -->

        {svg_text(
            first_center,
            125,
            total,
            78,
            TEXT,
            "bold"
        )}

        {svg_text(
            first_center,
            178,
            "TOTAL CONTRIBUTIONS",
            22,
            CYAN,
            "bold"
        )}

        {svg_text(
            first_center,
            216,
            "LAST 12 MONTHS",
            14,
            MUTED
        )}


        <!-- ================================================= -->
        <!-- CURRENT STREAK                                   -->
        <!-- ================================================= -->

        {svg_text(
            second_center,
            125,
            current,
            78,
            TEXT,
            "bold"
        )}

        {svg_text(
            second_center,
            178,
            "CURRENT STREAK",
            22,
            GREEN,
            "bold"
        )}

        {svg_text(
            second_center,
            216,
            "ACTIVE",
            14,
            MUTED
        )}


        <!-- ================================================= -->
        <!-- LONGEST STREAK                                   -->
        <!-- ================================================= -->

        {svg_text(
            third_center,
            125,
            longest,
            78,
            TEXT,
            "bold"
        )}

        {svg_text(
            third_center,
            178,
            "LONGEST STREAK",
            22,
            PURPLE,
            "bold"
        )}

        {svg_text(
            third_center,
            216,
            "ALL TIME",
            14,
            MUTED
        )}


        <!-- ================================================= -->
        <!-- VERTICAL DIVIDERS                                -->
        <!-- ================================================= -->

        <line
            x1="{third}"
            y1="62"
            x2="{third}"
            y2="245"
            stroke="{BORDER}"
            stroke-width="2"
        />

        <line
            x1="{third * 2}"
            y1="62"
            x2="{third * 2}"
            y2="245"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- ================================================= -->
        <!-- BOTTOM DIVIDER                                   -->
        <!-- ================================================= -->

        <line
            x1="55"
            y1="270"
            x2="{WIDTH - 55}"
            y2="270"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- ================================================= -->
        <!-- FOOTER                                           -->
        <!-- ================================================= -->

        {svg_text(
            WIDTH / 2,
            315,
            "@NNAvadeep05 • CONTRIBUTION.STATS",
            15,
            MUTED
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
    print(f"Total contributions : {total}")
    print(f"Current streak      : {current}")
    print(f"Longest streak      : {longest}")

    generate_svg(
        total,
        current,
        longest
    )

    print()
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()