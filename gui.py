import os
import webview

# ======================================================
# Paths
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_FILE = os.path.join(
    BASE_DIR,
    "ui",
    "index.html"
)

ICON_FILE = os.path.join(
    BASE_DIR,
    "assets",
    "phoenix.ico"
)

window = None


# ======================================================
# Create Window
# ======================================================

def create_window():
    global window

    window = webview.create_window(
    title="Phoenix AI",
    url=HTML_FILE,
    width=1280,
    height=800,
    resizable=True,
    frameless=False,
    confirm_close=False
)
    webview.start(debug=False)


# ======================================================
# Internal Helpers
# ======================================================

def run_js(js):
    if window:
        try:
            window.evaluate_js(js)
        except Exception as e:
            print("GUI Error:", e)


# ======================================================
# Orb States
# ======================================================

def idle():
    run_js("PhoenixUI.setState('idle')")


def listening():
    run_js("PhoenixUI.setState('listening')")


def thinking():
    run_js("PhoenixUI.setState('thinking')")


def speaking():
    run_js("PhoenixUI.setState('speaking')")


# ======================================================
# Conversation
# ======================================================

def set_conversation(text):
    run_js(f"PhoenixUI.setConversation({text!r})")