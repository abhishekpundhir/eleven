import webbrowser


# ============================================================
# PHOENIX LAB
# ============================================================

def open_phoenix_lab():

    webbrowser.open(
        "https://phoenixlab.netlify.app/"
    )

    return "Phoenix Lab is open."


# ============================================================
# WEBSITES
# ============================================================

def open_google():

    webbrowser.open(
        "https://www.google.com"
    )

    return "Google is open."


def open_youtube():

    webbrowser.open(
        "https://www.youtube.com"
    )

    return "YouTube is open."


def open_github():

    webbrowser.open(
        "https://github.com"
    )

    return "GitHub is open."


def open_chatgpt():

    webbrowser.open(
        "https://chatgpt.com"
    )

    return "ChatGPT is open."


def open_instagram():

    webbrowser.open(
        "https://www.instagram.com"
    )

    return "Instagram is open."


def open_facebook():

    webbrowser.open(
        "https://www.facebook.com"
    )

    return "Facebook is open."


def open_linkedin():

    webbrowser.open(
        "https://www.linkedin.com"
    )

    return "LinkedIn is open."


def open_x():

    webbrowser.open(
        "https://x.com"
    )

    return "X is open."


def open_reddit():

    webbrowser.open(
        "https://www.reddit.com"
    )

    return "Reddit is open."


def open_spotify():

    webbrowser.open(
        "https://open.spotify.com"
    )

    return "Spotify is open."


def open_netflix():

    webbrowser.open(
        "https://www.netflix.com"
    )

    return "Netflix is open."


def open_amazon():

    webbrowser.open(
        "https://www.amazon.in"
    )

    return "Amazon is open."


def open_gmail():

    webbrowser.open(
        "https://mail.google.com"
    )

    return "Gmail is open."


# ============================================================
# PROJECTS
# ============================================================

def open_project(command):

    command = command.lower().strip()

    # --------------------------------------------------------
    # IMPORTANT
    # This function expects your existing
    # phoenixLabProjects.py project resolver.
    # --------------------------------------------------------

    try:

        import phoenixLabProjects

        resolver = getattr(
            phoenixLabProjects,
            "open_project",
            None
        )

        if resolver:

            return resolver(command)

    except Exception as e:

        print(
            "Project resolver error:",
            e
        )

    return None