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
# TTS CACHE
# =====================================================

TTS_CACHE = {}

TTS_CACHE_LOCK = threading.Lock()


# =====================================================
# DIALOGUE
# =====================================================

STARTUP_LINES = [
    "Phoenix online. Systems are green.",
    "Phoenix online. Ready when you are, Boss.",
    "Systems online. Let's get to work.",
    "Phoenix is awake. What's the mission?",
    "Back online, Boss."
]


WAKE_LINES = [
    "I'm here, Boss.",
    "Online and listening.",
    "At your service, Boss.",
    "I'm listening.",
    "Ready. What's the move?",
    "Go ahead, Boss."
]


THINKING_LINES = [
    "Give me a second.",
    "Working on it.",
    "One moment, Boss.",
    "Let me handle that.",
    "Processing.",
    "On it."
]


GOODBYE_LINES = [
    "Standing down, Boss.",
    "Going quiet. Call me when you need me.",
    "Entering standby.",
    "I'll be here when you need me.",
    "Phoenix standing down."
]


ERROR_LINES = [
    "Boss, something went wrong on my side.",
    "I hit an error. Give me another shot.",
    "Something broke in the system.",
    "That didn't go according to plan."
]


# =====================================================
# PHOENIX LAB
# =====================================================

LAB_INTRO = (
    "Phoenix Lab is your developer ecosystem "
    "for building, managing, and exploring your projects."
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

        set_conversation(
            text
        )

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

    text = str(
        text
    ).lower().strip()

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

        # Fallback only if the registry contains one.
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
            "[Phoenix Knowledge] "
            "Read error:",
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
# LOGGING
# =====================================================

def log_conversation(
    user_text,
    phoenix_text
):

    try:

        log_path = os.path.join(
            BASE_DIR,
            "logs.txt"
        )

        with open(
            log_path,
            "a",
            encoding="utf-8"
        ) as log:

            log.write(
                f"User: {user_text}\n"
            )

            log.write(
                f"Phoenix: {phoenix_text}\n"
            )

            log.write(
                "-" * 60
                + "\n"
            )

    except Exception as e:

        print(
            "[Phoenix] Logging error:",
            e
        )


# =====================================================
# TTS ENGINE
# =====================================================

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

        return bytes(
            audio_data
        )

    return asyncio.run(
        generate()
    )


def cache_tts(text):

    if not text:

        return

    text = str(
        text
    ).strip()

    if not text:

        return

    with TTS_CACHE_LOCK:

        if text in TTS_CACHE:

            return

    try:

        audio_data = generate_tts_audio(
            text
        )

        if audio_data:

            with TTS_CACHE_LOCK:

                TTS_CACHE[text] = audio_data

            print(
                "[Phoenix] Cached voice:",
                text
            )

    except Exception as e:

        print(
            "[Phoenix] TTS cache error:",
            e
        )


def preload_tts():

    lines = []

    lines.extend(
        STARTUP_LINES
    )

    lines.extend(
        WAKE_LINES
    )

    lines.extend(
        THINKING_LINES
    )

    lines.extend(
        GOODBYE_LINES
    )

    lines.extend(
        ERROR_LINES
    )

    lines.append(
        LAB_INTRO
    )

    # ---------------------------------------------
    # Project intros from knowledge files
    # ---------------------------------------------

    for project_id in PROJECTS:

        intro = get_project_intro(
            project_id
        )

        if intro:

            lines.append(
                intro
            )

    # ---------------------------------------------
    # Remove duplicates
    # ---------------------------------------------

    lines = list(
        dict.fromkeys(
            lines
        )
    )

    # ---------------------------------------------
    # Cache
    # ---------------------------------------------

    for line in lines:

        if assistant_stop_event.is_set():

            break

        cache_tts(
            line
        )


def start_tts_preloader():

    thread = threading.Thread(
        target=preload_tts,
        name="PhoenixTTSPreloader",
        daemon=True
    )

    thread.start()


def speak(text):

    if not text:

        return

    text = str(
        text
    ).strip()

    if not text:

        return

    try:

        speaking()

    except Exception:

        pass

    audio_data = None

    # ---------------------------------------------
    # Check cache
    # ---------------------------------------------

    with TTS_CACHE_LOCK:

        audio_data = TTS_CACHE.get(
            text
        )

    # ---------------------------------------------
    # Generate if not cached
    # ---------------------------------------------

    if audio_data is None:

        try:

            audio_data = generate_tts_audio(
                text
            )

        except Exception as e:

            print(
                "[Phoenix] TTS generation error:",
                e
            )

            try:
                idle()
            except Exception:
                pass

            return

    if not audio_data:

        try:
            idle()
        except Exception:
            pass

        return

    # ---------------------------------------------
    # Playback
    # ---------------------------------------------

    try:

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

    except Exception as e:

        print(
            "[Phoenix] Audio playback error:",
            e
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

    log_conversation(
        command,
        reply
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
    # Preload common TTS in background
    # ---------------------------------------------

    start_tts_preloader()

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