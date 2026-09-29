import os
import webview


# ============================================================
# GLOBAL WINDOW
# ============================================================

window = None


# ============================================================
# CREATE WINDOW
# ============================================================

def create_window():

    global window

    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "ui", "index.html")

    window = webview.create_window(
        "Phoenix",
        index_path,
        width=1100,
        height=700,
        resizable=True
    )

    webview.start(
        debug=False
    )


# ============================================================
# SAFE JS CALL
# ============================================================

def run_js(script):

    global window

    if window is None:
        return

    try:

        window.evaluate_js(
            script
        )

    except Exception as e:

        print(
            "GUI error:",
            e
        )


# ============================================================
# STATES
# ============================================================

def idle():

    run_js(
        "window.PhoenixUI && "
        "window.PhoenixUI.setState('idle');"
    )


def listening():

    run_js(
        "window.PhoenixUI && "
        "window.PhoenixUI.setState('listening');"
    )


def thinking():

    run_js(
        "window.PhoenixUI && "
        "window.PhoenixUI.setState('thinking');"
    )


def speaking():

    run_js(
        "window.PhoenixUI && "
        "window.PhoenixUI.setState('speaking');"
    )


# ============================================================
# CONVERSATION
# ============================================================

def set_conversation(text):

    safe_text = (
        str(text)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "")
    )

    run_js(
        "window.PhoenixUI && "
        f"window.PhoenixUI.setConversation('{safe_text}');"
    )