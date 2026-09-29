import speech_recognition as sr
import webbrowser
import asyncio
import edge_tts
import pygame
import os
import http.client
import time
import musicLibrary
import requests
import random
import threading
import io
import re

from dotenv import load_dotenv
from client import askPhoenix

import systemCommands as system

from phoenixLabProjects import (
    PHOENIX_LAB_URL,
    PROJECTS
)

from gui import (
    create_window,
    listening,
    thinking,
    speaking,
    idle,
    set_conversation
)


# =====================================================
# CONFIGURATION
# =====================================================

load_dotenv()

VOICE = "en-US-AriaNeural"

NEWSDATA_API_KEY = os.getenv(
    "NEWSDATA_API_KEY"
)

recognizer = sr.Recognizer()
session = requests.Session()

recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.65
recognizer.non_speaking_duration = 0.35
recognizer.phrase_threshold = 0.25


# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

KNOWLEDGE_DIR = os.path.join(
    BASE_DIR,
    "knowledge"
)

PROJECT_KNOWLEDGE_DIR = os.path.join(
    KNOWLEDGE_DIR,
    "projects"
)


# =====================================================
# ASSISTANT CONTROL
# =====================================================

assistant_stop_event = threading.Event()
assistant_thread = None


# =====================================================
# DIALOGUE
# =====================================================

STARTUP_LINES = [
    "Phoenix online. Good to go boss",
    "Boss phoenix at your service",
    "Systems online. Let's get to work",
    "I'm up boss, what's the task",
    "Phoenix is online",
    "Checking on you boss, is all good"
]

WAKE_LINES = [
    "I'm here Boss.",
    "Welcome back Ashlye",
    "At your service Boss.",
    "Hey there, any tea.",
    "Hey Boss, is that a 3AM overthink, or a new project idea.",
    "I missed you boss.",
    "Congratulations for your last progress boss. That was a smooth win.",
    "Hey welcome back boss. I'm just thinking about you."
]

THINKING_LINES = [
    "Give me a second.",
    "Working on it boss.",
    "Let me think bro.",
    "Let me handle that.",
    "Hold your coffee boss. I'll handle this.",
    "On it."
]

GOODBYE_LINES = [
    "Good night boss. I'm here whenever you need me.",
    "Get some sleep boss. I'll handle the rest of the work.",
    "Dude, gotta go. And you don't overthink. I'll be here by your side always.",
    "I'll be here when you need me.",
    "Shutting down boss."
]

ERROR_LINES = [
    "Boss. Something went wrong on my side.",
    "I hit an error. Give me another shot.",
    "Something broke in the system.",
    "That didn't go according to plan."
]


# =====================================================
# PHOENIX LAB
# =====================================================

LAB_INTRO = (
    "Welcome to Phoenix Lab, where ideas ignite and become reality. "
    "Let's build something worth remembering. "
    "Phoenix Lab is an ecosystem to deploy, monitor and upgrade "
    "your digital products, and I'm here to help you with that "
    "so you don't need to worry about manual headaches."
)


# =====================================================
# WEBSITE COMMANDS
# =====================================================

WEB_COMMANDS = {
    "phoenix lab": system.open_phoenix_lab,
    "phoenixlab": system.open_phoenix_lab,
    "google": system.open_google,
    "youtube": system.open_youtube,
    "github": system.open_github,
    "chatgpt": system.open_chatgpt,
    "instagram": system.open_instagram,
    "facebook": system.open_facebook,
    "linkedin": system.open_linkedin,
    "twitter": system.open_x,
    "x": system.open_x,
    "reddit": system.open_reddit,
    "spotify": system.open_spotify,
    "netflix": system.open_netflix,
    "amazon": system.open_amazon,
    "gmail": system.open_gmail
}


# =====================================================
# GUI HELPERS
# =====================================================

def ui_conversation(text):
    try:
        set_conversation(text)
    except Exception as e:
        print(
            "[Phoenix] UI conversation error:",
            e
        )


def ui_idle():
    try:
        idle()
    except Exception as e:
        print(
            "[Phoenix] UI idle error:",
            e
        )


# =====================================================
# TEXT NORMALIZATION
# =====================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower().strip()

    text = text.replace(
        "-",
        " "
    )

    text = text.replace(
        "_",
        " "
    )

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# PROJECT ALIASES
# =====================================================

PROJECT_ALIASES = {

    # -------------------------------------------------
    # VibeSpace
    # -------------------------------------------------

    "vibespace": "vibespace",
    "vibe space": "vibespace",
    "vibe": "vibespace",
    "project 1": "vibespace",

    # -------------------------------------------------
    # Ketchup AI
    # -------------------------------------------------

    "ketchupai": "ketchupai",
    "ketchup ai": "ketchupai",
    "ketchup": "ketchupai",
    "project 2": "ketchupai",

    # -------------------------------------------------
    # IgoneStudio
    # -------------------------------------------------

    "igonestudio": "igonestudio",
    "igone studio": "igonestudio",
    "igone": "igonestudio",
    "igon": "igonestudio",
    "project 3": "igonestudio",

    # -------------------------------------------------
    # Phoenix
    # -------------------------------------------------

    "phoenix": "phoenix",
    "phoenix ai": "phoenix",
    "phoenix assistant": "phoenix",
    "project 4": "phoenix",

    # -------------------------------------------------
    # AuthorRead
    # -------------------------------------------------

    "authoread": "authoread",
    "author read": "authoread",
    "auto read": "authoread",
    "book": "authoread",
    "books": "authoread",
    "read": "authoread",
    "project read": "authoread",
    "project 5": "authoread",

    # -------------------------------------------------
    # Stoxie
    # -------------------------------------------------

    "stoxie": "stoxie",
    "stoxy": "stoxie",
    "stoxie ui": "stoxie",
    "project 6": "stoxie"
}


# =====================================================
# BUILD PROJECT ALIAS MAP
# =====================================================

def build_project_aliases():

    aliases = dict(
        PROJECT_ALIASES
    )

    for project_id, project in PROJECTS.items():

        project_aliases = project.get(
            "aliases",
            []
        )

        for alias in project_aliases:

            normalized = normalize_text(
                alias
            )

            if normalized:
                aliases[
                    normalized
                ] = project_id

        name = normalize_text(
            project.get(
                "name",
                ""
            )
        )

        if name:
            aliases[
                name
            ] = project_id

    return aliases


PROJECT_ALIAS_MAP = build_project_aliases()


# =====================================================
# KNOWLEDGE SYSTEM
# =====================================================

def get_project_knowledge_path(
    project_id
):

    if not project_id:
        return None

    filename = (
        f"{project_id}.md"
    )

    return os.path.join(
        PROJECT_KNOWLEDGE_DIR,
        filename
    )


def clean_knowledge_line(line):

    if not line:
        return ""

    line = line.strip()

    # Remove markdown headings
    line = re.sub(
        r"^#+\s*",
        "",
        line
    )

    # Remove markdown bullets
    line = re.sub(
        r"^[-*+]\s*",
        "",
        line
    )

    # Remove markdown emphasis
    line = line.replace(
        "**",
        ""
    )

    line = line.replace(
        "__",
        ""
    )

    return line.strip()


def get_project_intro(
    project_id
):

    """
    Read the project's local knowledge file.

    Phoenix uses the local knowledge system first.
    No AI request is made for this.
    """

    path = get_project_knowledge_path(
        project_id
    )

    if not path:
        return None

    if not os.path.exists(path):

        print(
            "[Phoenix Knowledge] Missing:",
            path
        )

        # Fallback only if registry contains one.
        project = PROJECTS.get(
            project_id
        )

        if project:
            return project.get(
                "intro"
            )

        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        if not content.strip():
            return None

        lines = content.splitlines()

        paragraph = []

        for raw_line in lines:

            line = raw_line.strip()

            # Empty line = end of first paragraph
            if not line:

                if paragraph:
                    break

                continue

            # Ignore markdown headings
            if line.startswith("#"):
                continue

            # Ignore markdown separators
            if line.startswith("---"):
                continue

            cleaned = clean_knowledge_line(
                line
            )

            if cleaned:
                paragraph.append(
                    cleaned
                )

        if paragraph:

            intro = " ".join(
                paragraph
            )

            # Keep voice intro short.
            sentences = re.split(
                r"(?<=[.!?])\s+",
                intro
            )

            if sentences:
                return sentences[0].strip()

            return intro

    except Exception as e:

        print(
            "[Phoenix Knowledge] Read error:",
            e
        )

    # ---------------------------------------------
    # Registry fallback
    # ---------------------------------------------

    project = PROJECTS.get(
        project_id
    )

    if project:
        return project.get(
            "intro"
        )

    return None


# =====================================================
# FIND PROJECT
# =====================================================

def find_project(target):

    if not target:
        return None

    target = normalize_text(
        target
    )

    # ---------------------------------------------
    # Exact alias
    # ---------------------------------------------

    if target in PROJECT_ALIAS_MAP:

        project_id = PROJECT_ALIAS_MAP[
            target
        ]

        return (
            PROJECTS.get(
                project_id
            ),
            project_id
        )

    # ---------------------------------------------
    # Exact project ID
    # ---------------------------------------------

    if target in PROJECTS:

        return (
            PROJECTS.get(
                target
            ),
            target
        )

    # ---------------------------------------------
    # Exact project name
    # ---------------------------------------------

    for project_id, project in PROJECTS.items():

        name = normalize_text(
            project.get(
                "name",
                ""
            )
        )

        if target == name:

            return (
                project,
                project_id
            )

    # ---------------------------------------------
    # Partial aliases
    # ---------------------------------------------

    for alias, project_id in PROJECT_ALIAS_MAP.items():

        if target == alias:

            return (
                PROJECTS.get(
                    project_id
                ),
                project_id
            )

    # ---------------------------------------------
    # Partial project names
    # ---------------------------------------------

    for project_id, project in PROJECTS.items():

        name = normalize_text(
            project.get(
                "name",
                ""
            )
        )

        if (
            target in name
            or
            name in target
        ):

            return (
                project,
                project_id
            )

    return None


# =====================================================
# OPEN TARGET EXTRACTION
# =====================================================

def get_open_target(command):

    target = normalize_text(
        command
    )

    prefixes = [
        "open the ",
        "launch the ",
        "go to the ",
        "open ",
        "launch ",
        "go to "
    ]

    for prefix in prefixes:

        if target.startswith(
            prefix
        ):

            return target[
                len(prefix):
            ].strip()

    return target


# =====================================================
# PREPARE LAB ACTION
# =====================================================

def prepare_lab_action():

    return {
        "reply": LAB_INTRO,

        "action": lambda:
            webbrowser.open(
                PHOENIX_LAB_URL
            )
    }


# =====================================================
# PREPARE PROJECT ACTION
# =====================================================

def prepare_project_action(
    project,
    project_id
):

    if not project:
        return None

    name = project.get(
        "name",
        "that project"
    )

    url = project.get(
        "url"
    )

    if not url:

        return {
            "reply": (
                f"I found {name}, "
                "but it doesn't have an opening link."
            ),
            "action": None
        }

    # ---------------------------------------------
    # Get intro from knowledge/
    # ---------------------------------------------

    intro = get_project_intro(
        project_id
    )

    if not intro:

        intro = (
            f"{name} is ready to open."
        )

    return {
        "reply": intro,

        "action": lambda:
            webbrowser.open(
                url
            )
    }


# =====================================================
# PROJECT COMMAND HANDLER
# =====================================================

def handle_project_command(command):

    if not command:
        return None

    normalized = normalize_text(
        command
    )

    # =================================================
    # PHOENIX LAB
    # =================================================

    lab_commands = [
        "open lab",
        "launch lab",
        "go to lab",
        "open phoenix lab",
        "launch phoenix lab",
        "go to phoenix lab",
        "open phoenixlab",
        "launch phoenixlab",
        "phoenix lab",
        "phoenixlab"
    ]

    if normalized in lab_commands:

        return prepare_lab_action()

    # =================================================
    # OPEN / LAUNCH / GO TO
    # =================================================

    open_prefixes = [
        "open ",
        "launch ",
        "go to "
    ]

    is_open_command = any(
        normalized.startswith(
            prefix
        )
        for prefix in open_prefixes
    )

    if not is_open_command:
        return None

    target = get_open_target(
        normalized
    )

    if not target:

        return {
            "reply": (
                "Tell me which project "
                "you want me to open, Boss."
            ),
            "action": None
        }

    # =================================================
    # PROJECT LOOKUP
    # =================================================

    result = find_project(
        target
    )

    if result:

        project, project_id = result

        return prepare_project_action(
            project,
            project_id
        )

    # =================================================
    # UNKNOWN TARGET
    # =================================================

    return {
        "reply": (
            f"I don't recognize {target}, Boss."
        ),
        "action": None
    }


# =====================================================
# WEBSITE COMMAND HANDLER
# =====================================================

def handle_website_command(command):

    command_lower = normalize_text(
        command
    )

    for keyword, action in sorted(
        WEB_COMMANDS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        normalized_keyword = normalize_text(
            keyword
        )

        valid_patterns = [
            normalized_keyword,
            f"open {normalized_keyword}",
            f"launch {normalized_keyword}",
            f"go to {normalized_keyword}",
            f"open the {normalized_keyword}",
            f"launch the {normalized_keyword}"
        ]

        if command_lower in valid_patterns:

            return {
                "reply": (
                    f"Opening {keyword}."
                ),
                "action": action
            }

    return None


# =====================================================
# MUSIC
# =====================================================

def handle_music(command):

    lower = normalize_text(
        command
    )

    if not lower.startswith(
        "play "
    ):
        return None

    song = command[5:].strip()

    if not song:

        return {
            "reply": (
                "Tell me what you want me to play."
            ),
            "action": None
        }

    link = musicLibrary.music.get(
        song.lower()
    )

    if link:

        return {
            "reply": f"Playing {song}.",

            "action": lambda:
                webbrowser.open(
                    link
                )
        }

    return {
        "reply": (
            f"Sorry Boss, I couldn't find "
            f"{song} in your music library."
        ),
        "action": None
    }


# =====================================================
# NEWS
# =====================================================

def get_news():

    if not NEWSDATA_API_KEY:

        return (
            "News API key is missing."
        )

    try:

        response = session.get(
            "https://newsdata.io/api/1/latest",
            params={
                "apikey": NEWSDATA_API_KEY,
                "language": "en",
                "country": "in",
                "size": 3
            },
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        articles = data.get(
            "results",
            []
        )

        headlines = []

        for article in articles[:3]:

            title = article.get(
                "title"
            )

            if title:

                headlines.append(
                    title
                )

        if not headlines:

            return (
                "I couldn't find any recent headlines."
            )

        parts = [
            "Here are the latest headlines."
        ]

        for index, headline in enumerate(
            headlines,
            start=1
        ):

            parts.append(
                f"{index}. {headline}"
            )

        return " ".join(
            parts
        )

    except Exception as e:

        print(
            "[Phoenix] News error:",
            e
        )

        return (
            "I couldn't fetch the latest news."
        )


# =====================================================
# COMMAND ENGINE
# =====================================================

def processCommand(command):

    if not command:
        return None

    command = command.strip()

    print(
        "[Phoenix] Command:",
        command
    )

    # =================================================
    # PROJECT / LAB COMMANDS
    # =================================================

    project_result = handle_project_command(
        command
    )

    if project_result:
        return project_result

    # =================================================
    # WEBSITE COMMANDS
    # =================================================

    website_result = handle_website_command(
        command
    )

    if website_result:
        return website_result

    # =================================================
    # MUSIC
    # =================================================

    music_result = handle_music(
        command
    )

    if music_result:
        return music_result

    # =================================================
    # NEWS
    # =================================================

    normalized = normalize_text(
        command
    )

    if normalized in [
        "news",
        "latest news",
        "today news",
        "latest headlines",
        "headlines"
    ]:

        return {
            "reply": get_news(),
            "action": None
        }

    return None


# =====================================================
# TTS ENGINE
# =====================================================
# =====================================================
# TTS ENGINE
# =====================================================

TTS_CHUNK_SIZE = 900


def generate_tts_audio(text):

    async def generate():

        communicator = edge_tts.Communicate(
            text=text,
            voice=VOICE
        )

        audio_data = bytearray()

        async for chunk in communicator.stream():

            if chunk["type"] == "audio":
                audio_data.extend(
                    chunk["data"]
                )

        return bytes(audio_data)

    return asyncio.run(
        generate()
    )


def clean_tts_text(text):

    """
    Convert AI / Markdown responses
    into natural speech.

    IMPORTANT:
    This only changes what Phoenix speaks.
    The original AI response remains untouched
    in the UI.
    """

    if not text:
        return ""

    text = str(text).strip()

    # Remove fenced code blocks completely.
    text = re.sub(
        r"```.*?```",
        "",
        text,
        flags=re.DOTALL
    )

    # Remove markdown bold.
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text,
        flags=re.DOTALL
    )

    # Remove markdown italic.
    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text,
        flags=re.DOTALL
    )

    # Remove markdown underline/bold.
    text = re.sub(
        r"__(.*?)__",
        r"\1",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"_(.*?)_",
        r"\1",
        text,
        flags=re.DOTALL
    )

    # Remove markdown headings.
    text = re.sub(
        r"^\s*#+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove markdown bullets.
    text = re.sub(
        r"^\s*[-*+]\s+",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove numbered list formatting.
    text = re.sub(
        r"^\s*\d+\.\s+",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove inline code markers.
    text = text.replace(
        "`",
        ""
    )

    # Remove URLs.
    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    # Replace excessive whitespace/newlines.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_tts_text(
    text,
    max_chars=TTS_CHUNK_SIZE
):

    """
    Split long responses into larger,
    natural speech chunks.

    900 characters is intentional.

    The previous 260-character limit caused
    too many separate Edge-TTS requests.
    """

    text = clean_tts_text(
        text
    )

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    chunks = []
    current = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # -------------------------------------------------
        # Sentence fits into current chunk
        # -------------------------------------------------

        if (
            len(current)
            + len(sentence)
            + 1
            <= max_chars
        ):

            if current:
                current += " "

            current += sentence

            continue

        # -------------------------------------------------
        # Save current chunk
        # -------------------------------------------------

        if current:

            chunks.append(
                current.strip()
            )

        # -------------------------------------------------
        # Sentence itself is too large
        # -------------------------------------------------

        if len(sentence) > max_chars:

            parts = re.split(
                r"(?<=[,;:])\s+",
                sentence
            )

            sub_current = ""

            for part in parts:

                part = part.strip()

                if not part:
                    continue

                if (
                    len(sub_current)
                    + len(part)
                    + 1
                    <= max_chars
                ):

                    if sub_current:
                        sub_current += " "

                    sub_current += part

                else:

                    if sub_current:

                        chunks.append(
                            sub_current.strip()
                        )

                    # -------------------------------------------------
                    # Hard split only when absolutely necessary
                    # -------------------------------------------------

                    while len(part) > max_chars:

                        cut = part.rfind(
                            " ",
                            0,
                            max_chars
                        )

                        if cut <= 0:
                            cut = max_chars

                        chunks.append(
                            part[:cut].strip()
                        )

                        part = part[
                            cut:
                        ].strip()

                    sub_current = part

            if sub_current:
                current = sub_current
            else:
                current = ""

        else:

            current = sentence

    if current:
        chunks.append(
            current.strip()
        )

    return [
        chunk
        for chunk in chunks
        if chunk
    ]


def play_tts_audio(audio_data):

    if not audio_data:
        return False

    try:

        # Stop previous playback if necessary.
        if pygame.mixer.music.get_busy():

            pygame.mixer.music.stop()

        # Release previous audio stream.
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

        audio_stream = io.BytesIO(
            audio_data
        )

        audio_stream.seek(
            0
        )

        pygame.mixer.music.load(
            audio_stream,
            "mp3"
        )

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            if assistant_stop_event.is_set():
                pygame.mixer.music.stop()
                break

            pygame.time.Clock().tick(
                30
            )

        return True

    except Exception as e:

        print(
            "[Phoenix] Audio playback error:",
            repr(e)
        )

        return False


def speak(text):

    if not text:
        return

    text = str(
        text
    ).strip()

    if not text:
        return

    chunks = split_tts_text(
        text
    )

    if not chunks:
        return

    try:
        speaking()
    except Exception:
        pass

    try:

        total = len(chunks)

        print(
            f"[Phoenix] Speaking {total} TTS chunk(s)"
        )

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            if assistant_stop_event.is_set():
                break

            print(
                f"[Phoenix] TTS chunk "
                f"{index}/{total} "
                f"({len(chunk)} chars)"
            )

            # -------------------------------------------------
            # Generate one reasonably large chunk.
            # This drastically reduces Edge-TTS requests.
            # -------------------------------------------------

            try:

                audio_data = generate_tts_audio(
                    chunk
                )

            except Exception as e:

                print(
                    "[Phoenix] TTS generation error:",
                    repr(e)
                )

                continue

            if not audio_data:

                print(
                    "[Phoenix] Empty TTS audio."
                )

                continue

            # -------------------------------------------------
            # Play entire chunk before generating next one.
            # -------------------------------------------------

            success = play_tts_audio(
                audio_data
            )

            if not success:

                print(
                    f"[Phoenix] Failed to play "
                    f"TTS chunk {index}/{total}"
                )

    finally:

        try:
            idle()
        except Exception:
            pass


def speak_random(lines):

    if not lines:
        return

    line = random.choice(
        lines
    )

    speak(
        line
    )

def clean_tts_text(text):

    """
    Convert AI / Markdown responses
    into natural speech.
    """

    if not text:
        return ""

    text = str(
        text
    ).strip()

    # Remove markdown bold
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    # Remove markdown italic
    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text
    )

    # Remove markdown underline/bold
    text = re.sub(
        r"__(.*?)__",
        r"\1",
        text
    )

    text = re.sub(
        r"_(.*?)_",
        r"\1",
        text
    )

    # Remove markdown headings
    text = re.sub(
        r"^\s*#+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove markdown bullets
    text = re.sub(
        r"^\s*[-*+]\s+",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove numbered list formatting
    text = re.sub(
        r"^\s*\d+\.\s+",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove code blocks
    text = re.sub(
        r"```.*?```",
        "",
        text,
        flags=re.DOTALL
    )

    # Remove inline code markers
    text = text.replace(
        "`",
        ""
    )

    # Remove URLs
    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    # Convert line breaks into spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_tts_text(
    text,
    max_chars=260
):

    """
    Split long responses into safe speech chunks.

    Preference:

    1. Sentences
    2. Commas
    3. Word boundaries
    """

    text = clean_tts_text(
        text
    )

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    chunks = []
    current = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Normal sentence fits
        if (
            len(current)
            + len(sentence)
            + 1
            <= max_chars
        ):

            if current:
                current += " "

            current += sentence

            continue

        # Save current chunk
        if current:

            chunks.append(
                current.strip()
            )

        # Sentence itself is too large
        if len(sentence) > max_chars:

            parts = re.split(
                r"(?<=[,;:])\s+",
                sentence
            )

            sub_current = ""

            for part in parts:

                part = part.strip()

                if not part:
                    continue

                if (
                    len(sub_current)
                    + len(part)
                    + 1
                    <= max_chars
                ):

                    if sub_current:
                        sub_current += " "

                    sub_current += part

                else:

                    if sub_current:

                        chunks.append(
                            sub_current.strip()
                        )

                    # Still too long:
                    # hard split at word boundary
                    while len(part) > max_chars:

                        cut = part.rfind(
                            " ",
                            0,
                            max_chars
                        )

                        if cut <= 0:
                            cut = max_chars

                        chunks.append(
                            part[:cut].strip()
                        )

                        part = part[
                            cut:
                        ].strip()

                    sub_current = part

            if sub_current:
                current = sub_current
            else:
                current = ""

        else:

            current = sentence

    if current:

        chunks.append(
            current.strip()
        )

    return [
        chunk
        for chunk in chunks
        if chunk
    ]


def play_tts_audio(
    audio_data
):

    if not audio_data:
        return False

    try:

        # Stop previous playback
        if pygame.mixer.music.get_busy():

            pygame.mixer.music.stop()

        # Release previous stream
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

        audio_stream = io.BytesIO(
            audio_data
        )

        audio_stream.seek(
            0
        )

        pygame.mixer.music.load(
            audio_stream,
            "mp3"
        )

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            pygame.time.Clock().tick(
                30
            )

        return True

    except Exception as e:

        print(
            "[Phoenix] Audio playback error:",
            e
        )

        return False


def speak(text):

    if not text:
        return

    text = str(
        text
    ).strip()

    if not text:
        return

    chunks = split_tts_text(
        text
    )

    if not chunks:
        return

    try:
        speaking()
    except Exception:
        pass

    try:

        for index, chunk in enumerate(
            chunks
        ):

            if assistant_stop_event.is_set():
                break

            print(
                f"[Phoenix] TTS chunk "
                f"{index + 1}/{len(chunks)}"
            )

            try:

                audio_data = generate_tts_audio(
                    chunk
                )

            except Exception as e:

                print(
                    "[Phoenix] TTS generation error:",
                    e
                )

                continue

            if not audio_data:
                continue

            # Play this chunk completely
            play_tts_audio(
                audio_data
            )

    finally:

        try:
            idle()
        except Exception:
            pass


def speak_random(lines):

    if not lines:
        return

    line = random.choice(
        lines
    )

    speak(
        line
    )


# =====================================================
# AUDIO INITIALIZATION
# =====================================================

def initialize_audio():

    try:

        if pygame.mixer.get_init():
            return

        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512
        )

        print(
            "Audio system initialized."
        )

    except Exception as e:

        print(
            "[Phoenix] Audio initialization error:",
            e
        )


# =====================================================
# DIRECT COMMAND RESPONSE
# =====================================================

def deliver_command_result(
    result
):

    if not result:
        return

    reply = result.get(
        "reply"
    )

    action = result.get(
        "action"
    )

    # =================================================
    # SPEAK FIRST
    # =================================================

    if reply:

        print(
            f"[Phoenix] Response: {reply}"
        )

        ui_conversation(
            f"Phoenix: {reply}"
        )

        speak(
            reply
        )

    # =================================================
    # ACTION SECOND
    # =================================================

    if action:

        try:

            action()

        except Exception as e:

            print(
                "[Phoenix] Action error:",
                e
            )


# =====================================================
# AI FALLBACK
# =====================================================

def handle_ai(command):

    thinking_line = random.choice(
        THINKING_LINES
    )

    ui_conversation(
        f"Phoenix: {thinking_line}"
    )

    # Don't let GUI state crash AI.
    try:
        thinking()
    except Exception:
        pass

    speak(
        thinking_line
    )

    try:

        reply = askPhoenix(
            command
        )

        if not reply:

            reply = random.choice(
                ERROR_LINES
            )

    except Exception as e:

        print(
            "[Phoenix] AI error:",
            e
        )

        reply = random.choice(
            ERROR_LINES
        )

    ui_conversation(
        f"Phoenix: {reply}"
    )

    print(
        f"[Phoenix] Response: {reply}"
    )

    speak(
        reply
    )


# =====================================================
# WAKE WORD
# =====================================================

WAKE_WORDS = [
    "phoenix",
    "hey phoenix",
    "okay phoenix",
    "ok phoenix"
]

PARTIAL_WAKE_WORDS = [
    "phoen",
    "phoe",
    "pho"
]


def contains_wake_word(text):

    if not text:
        return False

    lower = text.lower().strip()

    for wake_word in WAKE_WORDS:

        if lower == wake_word:
            return True

        if lower.startswith(
            wake_word + " "
        ):

            return True

    for partial in PARTIAL_WAKE_WORDS:

        if lower == partial:
            return True

        if lower.startswith(
            partial + " "
        ):

            return True

    return False


def remove_wake_word(text):

    if not text:
        return ""

    cleaned = text.strip()

    lower = cleaned.lower()

    all_wake_words = (
        WAKE_WORDS
        +
        PARTIAL_WAKE_WORDS
    )

    for wake_word in sorted(
        all_wake_words,
        key=len,
        reverse=True
    ):

        if lower == wake_word:

            return ""

        if lower.startswith(
            wake_word + " "
        ):

            return cleaned[
                len(wake_word):
            ].strip()

    return cleaned


# =====================================================
# SLEEP DETECTION
# =====================================================

def is_sleep_command(text):

    if not text:
        return False

    command = normalize_text(
        text
    )

    phrases = [
        "sleep",
        "go to sleep",
        "sleep phoenix",
        "stand down",
        "stand down phoenix",
        "go idle",
        "enter standby",
        "standby",
        "be quiet",
        "quiet phoenix",
        "that's all",
        "thats all",
        "we're done",
        "we are done",
        "good night phoenix",
        "goodnight phoenix"
    ]

    return any(
        phrase == command
        or phrase in command
        for phrase in phrases
    )


# =====================================================
# SHUTDOWN DETECTION
# =====================================================

def is_shutdown_command(text):

    if not text:
        return False

    command = normalize_text(
        text
    )

    phrases = [
        "shutdown",
        "shut down",
        "shutdown phoenix",
        "shut down phoenix",
        "exit phoenix",
        "quit phoenix",
        "close phoenix",
        "terminate phoenix",
        "echo null",
        "leave env",
        "fuck off"
    ]

    return any(
        phrase == command
        or phrase in command
        for phrase in phrases
    )


# =====================================================
# LISTEN
# =====================================================

def listen(
    timeout=5,
    phrase_time_limit=8
):

    try:

        listening()

        with sr.Microphone() as source:

            print(
                "[Phoenix] Listening..."
            )

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = recognizer.recognize_google(
            audio
        )

        ui_idle()

        if not text:
            return None

        text = text.strip()

        print(
            "[Phoenix Heard]:",
            text
        )

        return text

    except sr.WaitTimeoutError:

        print(
            "[Phoenix] Listening timeout."
        )

        ui_idle()

        return None

    except sr.UnknownValueError:

        print(
            "[Phoenix] Speech not understood."
        )

        ui_idle()

        return None

    except sr.RequestError as e:

        print(
            "[Phoenix] Speech recognition error:",
            e
        )

        ui_idle()

        time.sleep(
            0.5
        )

        return None

    except http.client.RemoteDisconnected:

        print(
            "[Phoenix] Speech service disconnected."
        )

        ui_idle()

        time.sleep(
            0.5
        )

        return None

    except ConnectionResetError:

        print(
            "[Phoenix] Speech connection reset."
        )

        ui_idle()

        time.sleep(
            0.5
        )

        return None

    except OSError as e:

        print(
            "[Phoenix] Microphone/audio error:",
            e
        )

        ui_idle()

        time.sleep(
            0.5
        )

        return None

    except Exception as e:

        print(
            "[Phoenix] Listen error:",
            e
        )

        ui_idle()

        time.sleep(
            0.3
        )

        return None


# =====================================================
# MAIN ASSISTANT LOOP
# =====================================================

def assistant():

    print(
        "\n================================"
    )

    print(
        "       PHOENIX ASSISTANT"
    )

    print(
        "================================\n"
    )

    # ---------------------------------------------
    # Audio
    # ---------------------------------------------

    initialize_audio()

    # ---------------------------------------------
    # Startup
    # ---------------------------------------------

    speak_random(
        STARTUP_LINES
    )

    # ---------------------------------------------
    # Phoenix starts inactive
    # ---------------------------------------------

    active = False

    pending_command = None

    ui_idle()

    ui_conversation(
        "Awaiting wake word..."
    )

    # =================================================
    # CONTINUOUS LOOP
    # =================================================

    while not assistant_stop_event.is_set():

        try:

            # =================================================
            # INACTIVE MODE
            # =================================================

            if not active:

                ui_idle()

                ui_conversation(
                    "Awaiting wake word..."
                )

                text = listen(
                    timeout=5,
                    phrase_time_limit=5
                )

                if not text:
                    continue

                if not contains_wake_word(
                    text
                ):
                    continue

                print(
                    "[Phoenix] Wake word detected."
                )

                active = True

                pending_command = (
                    remove_wake_word(
                        text
                    )
                )

                speak_random(
                    WAKE_LINES
                )

            # =================================================
            # GET COMMAND
            # =================================================

            if pending_command:

                command = pending_command

                pending_command = None

            else:

                ui_conversation(
                    "Listening..."
                )

                text = listen(
                    timeout=5,
                    phrase_time_limit=8
                )

                if not text:
                    continue

                command = text.strip()

            if not command:
                continue

            print(
                "[Phoenix] Processing:",
                command
            )

            ui_conversation(
                f"You: {command}"
            )

            # =================================================
            # SHUTDOWN
            # =================================================

            if is_shutdown_command(
                command
            ):

                goodbye = random.choice(
                    GOODBYE_LINES
                )

                print(
                    f"[Phoenix] Response: {goodbye}"
                )

                ui_conversation(
                    f"Phoenix: {goodbye}"
                )

                # Speak BEFORE stopping.
                speak(
                    goodbye
                )

                assistant_stop_event.set()

                break

            # =================================================
            # SLEEP / STANDBY
            # =================================================

            if is_sleep_command(
                command
            ):

                goodbye = random.choice(
                    GOODBYE_LINES
                )

                print(
                    f"[Phoenix] Response: {goodbye}"
                )

                ui_conversation(
                    f"Phoenix: {goodbye}"
                )

                speak(
                    goodbye
                )

                active = False

                pending_command = None

                ui_idle()

                ui_conversation(
                    "Awaiting wake word..."
                )

                continue

            # =================================================
            # DIRECT COMMAND ENGINE
            # =================================================

            start_time = time.time()

            result = processCommand(
                command
            )

            elapsed = (
                time.time()
                -
                start_time
            )

            print(
                "[Phoenix] Command engine:",
                f"{elapsed:.3f}s"
            )

            # =================================================
            # DIRECT COMMAND FOUND
            # =================================================

            if result:

                deliver_command_result(
                    result
                )

                # Phoenix stays active.
                active = True

                continue

            # =================================================
            # AI FALLBACK
            # =================================================

            handle_ai(
                command
            )

            # Phoenix stays active.
            active = True

        except KeyboardInterrupt:

            print(
                "\nPhoenix interrupted."
            )

            assistant_stop_event.set()

            break

        except Exception as e:

            print(
                "\n================================"
            )

            print(
                "PHOENIX ENGINE ERROR:"
            )

            print(
                repr(e)
            )

            print(
                "================================\n"
            )

            ui_idle()

            time.sleep(
                0.3
            )

    # =================================================
    # AUDIO CLEANUP
    # =================================================

    try:

        if pygame.mixer.get_init():

            if pygame.mixer.music.get_busy():

                pygame.mixer.music.stop()

            pygame.mixer.quit()

    except Exception as e:

        print(
            "[Phoenix] Audio cleanup error:",
            e
        )

    print(
        "Phoenix assistant thread stopped."
    )


# =====================================================
# START ASSISTANT
# =====================================================

def start_assistant():

    global assistant_thread

    if (
        assistant_thread
        and
        assistant_thread.is_alive()
    ):

        print(
            "Phoenix assistant is already running."
        )

        return

    assistant_stop_event.clear()

    assistant_thread = threading.Thread(
        target=assistant,
        name="PhoenixAssistant",
        daemon=True
    )

    assistant_thread.start()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    try:

        start_assistant()

        create_window()

    except KeyboardInterrupt:

        print(
            "Phoenix shutting down..."
        )

        assistant_stop_event.set()

    except Exception as e:

        print(
            "[Phoenix] Startup error:",
            e
        )

        assistant_stop_event.set()