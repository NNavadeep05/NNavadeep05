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

            repositories(
                first: 20
                ownerAffiliations: OWNER, COLLABORATOR, ORGANIZATION_MEMBER
                privacy: PUBLIC
            ) {
                nodes {
                    nameWithOwner
                    isFork
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
            "User-Agent": "github-profile-activity"
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
    anchor="start"
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
# GENERATE ACTIVITY SVG
# ============================================================

def generate_activity(user):

    contributions = user["contributionsCollection"]

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


    repositories = []

    for repo in user["repositories"]["nodes"]:

        if repo is None:
            continue

        if repo["isFork"]:
            continue

        repositories.append(
            repo["nameWithOwner"]
        )


    repositories = repositories[:8]

    if not repositories:
        repositories = [
            "No public repository activity found"
        ]


    # ========================================================
    # SVG
    # ========================================================

    svg = f'''
    <svg
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
            rx="10"
            fill="{BG}"
        />


        <!-- ================================================= -->
        <!-- TITLE                                             -->
        <!-- ================================================= -->

        {text(
            55,
            48,
            "Activity overview",
            24,
            TEXT,
            "bold"
        )}


        <!-- ================================================= -->
        <!-- MAIN DIVIDER                                     -->
        <!-- ================================================= -->

        <line
            x1="45"
            y1="70"
            x2="{WIDTH - 45}"
            y2="70"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- ================================================= -->
        <!-- LEFT / RIGHT DIVIDER                             -->
        <!-- ================================================= -->

        <line
            x1="700"
            y1="95"
            x2="700"
            y2="360"
            stroke="{BORDER}"
            stroke-width="2"
        />


        <!-- ================================================= -->
        <!-- LEFT: CONTRIBUTED TO                             -->
        <!-- ================================================= -->

        {text(
            70,
            110,
            "Contributed to",
            18,
            CYAN,
            "bold"
        )}

    '''


    # --------------------------------------------------------
    # Repository list
    # --------------------------------------------------------

    y = 150

    for repo in repositories:

        display_name = repo

        if len(display_name) > 46:

            display_name = (
                display_name[:43] +
                "..."
            )

        svg += text(
            90,
            y,
            "• " + display_name,
            17,
            TEXT
        )

        y += 32


    if len(repositories) >= 8:

        svg += text(
            90,
            y + 5,
            "and more repositories",
            15,
            MUTED
        )


    # ========================================================
    # RIGHT: CONTRIBUTION BREAKDOWN
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
    # Radar-like graphic
    # --------------------------------------------------------

    center_x = 1035
    center_y = 235

    radius_x = 130
    radius_y = 105

    # axes

    svg += f'''
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
            r="5"
            fill="{GREEN}"
        />
    '''


    # --------------------------------------------------------
    # Contribution values
    # --------------------------------------------------------

    total_actions = (
        commits +
        pull_requests +
        issues +
        reviews
    )

    if total_actions == 0:
        total_actions = 1


    # Percentages relative to total
    commit_pct = round(
        commits / total_actions * 100
    )

    review_pct = round(
        reviews / total_actions * 100
    )

    issue_pct = round(
        issues / total_actions * 100
    )

    pr_pct = round(
        pull_requests / total_actions * 100
    )


    svg += text(
        center_x - radius_x - 20,
        center_y + 5,
        f"{commit_pct}%\\n",
        14,
        MUTED,
        "bold",
        "end"
    )

    svg += text(
        center_x + radius_x + 20,
        center_y + 5,
        "Issues",
        14,
        MUTED
    )

    svg += text(
        center_x,
        center_y - radius_y - 12,
        "Code review",
        14,
        MUTED,
        "normal",
        "middle"
    )

    svg += text(
        center_x,
        center_y + radius_y + 25,
        "Pull requests",
        14,
        MUTED,
        "normal",
        "middle"
    )


    # --------------------------------------------------------
    # Exact counts
    # --------------------------------------------------------

    svg += text(
        755,
        330,
        f"Commits ............... {commits}",
        15,
        GREEN
    )

    svg += text(
        990,
        330,
        f"Code reviews .......... {reviews}",
        15,
        CYAN
    )

    svg += text(
        755,
        355,
        f"Issues ................ {issues}",
        15,
        PURPLE
    )

    svg += text(
        990,
        355,
        f"Pull requests ......... {pull_requests}",
        15,
        TEXT
    )


    # ========================================================
    # OUTER BORDER
    # ========================================================

    svg += f'''
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
    '''

    svg += """
    </svg>
    """


    # ========================================================
    # WRITE FILE
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