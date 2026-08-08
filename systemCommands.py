import webbrowser

from phoenixLabProjects import (
    PROJECTS,
    PHOENIX_LAB_URL
)


# ============================================================
# PHOENIX LAB
# ============================================================

def open_phoenix_lab():

    webbrowser.open(PHOENIX_LAB_URL)

    return (
        "Opening Phoenix Lab. "
        "Your AI-managed ecosystem for projects, tools and workflows."
    )


# ============================================================
# PROJECT RESOLVER
# ============================================================

def open_project(command):

    command = command.lower().strip()

    matches = []

    for project_id, project in PROJECTS.items():

        for alias in project.get("aliases", []):

            alias = alias.lower().strip()

            if alias in command:

                matches.append(
                    (
                        len(alias),
                        project
                    )
                )

    if not matches:

        return None

    # Longest alias wins.
    matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    project = matches[0][1]

    # OPEN FIRST
    webbrowser.open(project["url"])

    # THEN RETURN INTRO
    return (
        f"Opening {project['name']}. "
        f"{project['intro']}"
    )


# ============================================================
# NORMAL WEBSITES
# ============================================================

def open_google():

    webbrowser.open(
        "https://google.com"
    )

    return "Opening Google."


def open_youtube():

    webbrowser.open(
        "https://youtube.com"
    )

    return "Opening YouTube."


def open_github():

    webbrowser.open(
        "https://github.com"
    )

    return "Opening GitHub."


def open_chatgpt():

    webbrowser.open(
        "https://chatgpt.com"
    )

    return "Opening ChatGPT."


def open_instagram():

    webbrowser.open(
        "https://instagram.com"
    )

    return "Opening Instagram."


def open_facebook():

    webbrowser.open(
        "https://facebook.com"
    )

    return "Opening Facebook."


def open_linkedin():

    webbrowser.open(
        "https://linkedin.com"
    )

    return "Opening LinkedIn."


def open_x():

    webbrowser.open(
        "https://x.com"
    )

    return "Opening X."


def open_reddit():

    webbrowser.open(
        "https://reddit.com"
    )

    return "Opening Reddit."


def open_spotify():

    webbrowser.open(
        "https://open.spotify.com"
    )

    return "Opening Spotify."


def open_netflix():

    webbrowser.open(
        "https://netflix.com"
    )

    return "Opening Netflix."


def open_amazon():

    webbrowser.open(
        "https://amazon.in"
    )

    return "Opening Amazon."


def open_gmail():

    webbrowser.open(
        "https://mail.google.com"
    )

    return "Opening Gmail."