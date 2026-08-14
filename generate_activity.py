import os
import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

USERNAME = "NNavadeep05"

OUTPUT = "activity.svg"

WIDTH = 1400
HEIGHT = 430

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

def get_activity_data():

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
                totalCommitContributions
                totalPullRequestContributions
                totalIssueContributions
                totalPullRequestReviewContributions
            }

            repositories(first: 20) {
                nodes {
                    nameWithOwner
                    isFork
                    isPrivate
                }
            }
        }
    }
    """

    now = datetime.utcnow()
    start = now - timedelta(days=365)

    variables = {
        "login": USERNAME,
        "from": start.strftime(
            "%Y-%m-%dT00:00:00Z"
        ),
        "to": now.strftime(
            "%Y-%m-%dT23:59:59Z"
        ),
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
            "User-Agent": "github-profile-activity",
        },
        method="POST",
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

    return data["data"]["user"]


# ============================================================
# SVG TEXT
# ============================================================

def text(
    x,
    y,
    value,
    size,
    color,
    weight="normal",
    anchor="start",
):

    return f"""
        <text
            x="{x}"
            y="{y}"
            fill="{color}"
            font-family="monospace"
            font-size="{size}px"
            font-weight="{weight}"
            text-anchor="{anchor}"
        >{value}</text>
    """


# ============================================================
# GENERATE ACTIVITY SVG
# ============================================================

def generate_activity(user):

    contributions = user[
        "contributionsCollection"
    ]

    commits = contributions[
        "totalCommitContributions"
    ]

    pull_requests = contributions[
        "totalPullRequestContributions"
    ]

    issues = contributions[
        "totalIssueContributions"
    ]

    reviews = contributions[
        "totalPullRequestReviewContributions"
    ]


    # --------------------------------------------------------
    # Repository list
    # --------------------------------------------------------

    repositories = []

    for repo in user["repositories"]["nodes"]:

        if repo is None:
            continue

        if repo["isFork"]:
            continue

        if repo["isPrivate"]:
            continue

        repositories.append(
            repo["nameWithOwner"]
        )

    repositories = repositories[:7]

    if not repositories:

        repositories = [
            "No public repositories found"
        ]


    # ========================================================
    # SVG START
    # ========================================================

    svg = f"""
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}"
        height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}"
    >

        <rect
            x="0"
            y="0"
            width="{WIDTH}"
            height="{HEIGHT}"
            rx="10"
            fill="{BG}"
        />

        {text(
            55,
            48,
            "Activity overview",
            24,
            TEXT,
            "bold"
        )}

        <line
            x1="45"
            y1="70"
            x2="{WIDTH - 45}"
            y2="70"
            stroke="{BORDER}"
            stroke-width="2"
        />

        <line
            x1="700"
            y1="95"
            x2="700"
            y2="370"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- LEFT SIDE -->

        {text(
            70,
            110,
            "Contributed to",
            18,
            CYAN,
            "bold"
        )}
    """


    # ========================================================
    # REPOSITORIES
    # ========================================================

    y = 150

    for repo in repositories:

        display_name = repo

        if len(display_name) > 48:

            display_name = (
                display_name[:45]
                + "..."
            )

        svg += text(
            90,
            y,
            "• " + display_name,
            16,
            TEXT
        )

        y += 32


    if len(repositories) >= 7:

        svg += text(
            90,
            y + 5,
            "and more repositories",
            15,
            MUTED
        )


    # ========================================================
    # RIGHT SIDE
    # ========================================================

    svg += text(
        755,
        110,
        "Contribution breakdown",
        18,
        PURPLE,
        "bold"
    )


    # --------------------------------------------------------
    # Radar-style visual
    # --------------------------------------------------------

    center_x = 1035
    center_y = 225

    radius_x = 135
    radius_y = 105

    svg += f"""
        <line
            x1="{center_x - radius_x}"
            y1="{center_y}"
            x2="{center_x + radius_x}"
            y2="{center_y}"
            stroke="{GREEN}"
            stroke-width="2"
        />

        <line
            x1="{center_x}"
            y1="{center_y - radius_y}"
            x2="{center_x}"
            y2="{center_y + radius_y}"
            stroke="{GREEN}"
            stroke-width="2"
        />

        <circle
            cx="{center_x}"
            cy="{center_y}"
            r="6"
            fill="{GREEN}"
        />
    """


    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    svg += text(
        center_x,
        center_y - radius_y - 15,
        "Code review",
        14,
        MUTED,
        anchor="middle"
    )

    svg += text(
        center_x + radius_x + 15,
        center_y + 5,
        "Issues",
        14,
        MUTED
    )

    svg += text(
        center_x,
        center_y + radius_y + 28,
        "Pull requests",
        14,
        MUTED,
        anchor="middle"
    )

    svg += text(
        center_x - radius_x - 15,
        center_y + 5,
        "Commits",
        14,
        MUTED,
        anchor="end"
    )


    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    svg += text(
        755,
        325,
        f"Commits ............... {commits}",
        15,
        GREEN
    )

    svg += text(
        990,
        325,
        f"Code reviews .......... {reviews}",
        15,
        CYAN
    )

    svg += text(
        755,
        352,
        f"Issues ................ {issues}",
        15,
        PURPLE
    )

    svg += text(
        990,
        352,
        f"Pull requests ......... {pull_requests}",
        15,
        TEXT
    )


    # ========================================================
    # OUTER BORDER
    # ========================================================

    svg += f"""
        <rect
            x="25"
            y="20"
            width="{WIDTH - 50}"
            height="{HEIGHT - 40}"
            rx="10"
            fill="none"
            stroke="{BORDER}"
            stroke-width="2"
        />

    </svg>
    """


    # ========================================================
    # WRITE
    # ========================================================

    Path(OUTPUT).write_text(
        svg,
        encoding="utf-8"
    )

    print(
        f"Created {OUTPUT}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Fetching GitHub activity data..."
    )

    user = get_activity_data()

    generate_activity(
        user
    )


if __name__ == "__main__":

    main()