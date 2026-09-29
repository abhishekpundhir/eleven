import os
import re


# ============================================================
# KNOWLEDGE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

KNOWLEDGE_DIR = os.path.join(
    BASE_DIR,
    "knowledge"
)


# ============================================================
# KNOWLEDGE FILES
# ============================================================

KNOWLEDGE_FILES = [
    "about_me.md",
    "phoenix.md",
    "phoenix_lab.md",
    "vibespace.md",
    "ketchup_ai.md",
    "igonestudio.md",
    "phoenix.md",
    "authoread.md",
    "stoxie.md"
]


# ============================================================
# KEYWORD MAP
# ============================================================

KEYWORD_MAP = {

    "about_me.md": [
        "about me",
        "who am i",
        "my skills",
        "my goals",
        "my career",
        "my profile"
    ],

    "phoenix.md": [
        "phoenix",
        "phoenix assistant",
        "phoenix ai",
        "how does phoenix work",
        "what is phoenix"
    ],

    "phoenix_lab.md": [
        "phoenix lab",
        "phoenixlab",
        "what is phoenix lab",
        "how does phoenix lab work"
    ],

    "vibespace.md": [
        "vibespace",
        "vibe space"
    ],

    "ketchup_ai.md": [
        "ketchup ai",
        "ketchup"
    ],

    "igonestudio.md": [
        "igone studio",
        "igonestudio"
    ],

    "authoread.md": [
        "authoread",
        "author read"
    ],

    "stoxie.md": [
        "stoxie",
        "stoxie project"
    ]
}


# ============================================================
# READ FILE
# ============================================================

def read_file(filename):

    path = os.path.join(
        KNOWLEDGE_DIR,
        filename
    )

    if not os.path.exists(path):
        return ""

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception as e:

        print(
            f"Knowledge read error [{filename}]:",
            e
        )

        return ""


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        text.lower()
    ).strip()


# ============================================================
# RETRIEVE CONTEXT
# ============================================================

def retrieve_context(query):

    query_normalized = normalize(query)

    matched_files = []

    for filename, keywords in KEYWORD_MAP.items():

        for keyword in keywords:

            if normalize(keyword) in query_normalized:

                matched_files.append(filename)
                break

    # --------------------------------------------------------
    # Generic project questions
    # --------------------------------------------------------

    project_queries = [
        "tell me about the project",
        "tell me about this project",
        "tell me about my project",
        "what is this project",
        "what is the project",
        "how does the project work",
        "how does this project work"
    ]

    if any(
        phrase in query_normalized
        for phrase in project_queries
    ):

        if "phoenix lab" in query_normalized:
            matched_files.append("phoenix_lab.md")

        elif "phoenix" in query_normalized:
            matched_files.append("phoenix.md")

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    matched_files = list(
        dict.fromkeys(matched_files)
    )

    if not matched_files:
        return ""

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    for filename in matched_files:

        content = read_file(filename)

        if content:

            context_parts.append(
                f"--- {filename} ---\n"
                f"{content}"
            )

    return "\n\n".join(
        context_parts
    )