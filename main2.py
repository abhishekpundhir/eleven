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
from client import askPhoenix
import random
from gui import (
    create_window,
    listening,
    thinking,
    speaking,
    idle,
    set_conversation
)

import threading
import systemCommands as system



WEB_COMMANDS = {

    # ========================================================
    # PHOENIX LAB
    # ========================================================

    "phoenix lab": system.open_phoenix_lab,
    "phoenixlab": system.open_phoenix_lab,


    # ========================================================
    # NORMAL WEBSITES
    # ========================================================

    "google": system.open_google,

    "youtube": system.open_youtube,

    "github": system.open_github,

    "chatgpt": system.open_chatgpt,

    "instagram": system.open_instagram,

    "facebook": system.open_facebook,

    "linkedin": system.open_linkedin,

    "twitter": system.open_x,

    "reddit": system.open_reddit,

    "spotify": system.open_spotify,

    "netflix": system.open_netflix,

    "amazon": system.open_amazon,

    "gmail": system.open_gmail
}


session = requests.Session()
recognizer = sr.Recognizer()
pygame.mixer.init()
newsapi = "your_api_key"



STARTUP_LINES = [
    "Phoenix online. Let's disappoint some bugs.",
    "Systems green. Coffee optional.",
    "Back on duty. Try not to break reality.",
    "Phoenix online. What's today's chaos?",
    "Ready when you are Boss."
]

THINKING = [
    "Hmm...",
    "One second...",
    "Interesting...",
    "Let me think...",
    "Working on it...",
    "on it boss",
    "hold your beer boss i'll handle this"
]


WAKE_LINES = [
    "Good to see you Boss.",
    "Back already  Nice.",
    "Welcome back. Ready to build something?",
    "Coffee acquired?",
    "Good to have you back boss. I already have a plan for today It just works better if you've had coffee, because I can compensate for many things. expect a lack of caffeine",
    "Let's make today's bugs cry."
]



GOODBYE_LINES = [
    "get some sleep boss. I can handle being alone for a few hours. ",
    "Get some sleep Boss.",
    "Go recharge.",
    "I'll keep the electrons warm.",
    "See you soon.",
    "Don't make questionable decisions." 
]


VOICE = "en-US-AriaNeural"
  
# Other voices
# VOICE = "en-US-JennyNeural"
# VOICE = "en-US-EmmaNeural"
# VOICE = "en-GB-SoniaNeural"
# VOICE = "en-AU-NatashaNeural"
# VOICE = "en-IN-NeerjaNeural"



# ============================================
# Speak 
# ============================================


def speak(text):

    if not text:
        return

    text = str(text).strip()

    if not text:
        return


    voice_file = "voice.mp3"


    try:

        speaking()


        async def generate():

            communicate = edge_tts.Communicate(
                text=text,
                voice=VOICE
            )

            await communicate.save(
                voice_file
            )


        asyncio.run(
            generate()
        )


        if not os.path.exists(
            voice_file
        ):

            print(
                "TTS failed: audio file was not created."
            )

            idle()

            return


        pygame.mixer.music.load(
            voice_file
        )

        pygame.mixer.music.play()


        while pygame.mixer.music.get_busy():

            pygame.time.Clock().tick(10)


        pygame.mixer.music.unload()


    except edge_tts.exceptions.NoAudioReceived:

        print(
            "TTS error: No audio received."
        )


    except Exception as e:

        print(
            "TTS error:",
            e
        )


    finally:

        try:

            if pygame.mixer.music.get_busy():

                pygame.mixer.music.stop()

        except Exception:

            pass


        try:

            if pygame.mixer.get_init():

                pygame.mixer.music.unload()

        except Exception:

            pass


        try:

            if os.path.exists(
                voice_file
            ):

                os.remove(
                    voice_file
                )

        except Exception:

            pass


        idle()




# ============================================
# PROCESS COMMAND
# ============================================




def processCommand(command):

    command = command.lower().strip()

    print("Command:", command)


    # ========================================================
    # 1. PHOENIX LAB
    # ========================================================

    if (
        command == "phoenix lab"
        or command == "phoenixlab"
        or command == "open lab"
        or command == "open phoenix lab"
        or command == "open phoenixlab"
        or command == "launch lab"
        or command == "launch phoenix lab"
    ):

        reply = system.open_phoenix_lab()

        set_conversation(
            f"Phoenix: {reply}"
        )

        speak(reply)

        return True


    # ========================================================
    # 2. PROJECTS
    # ========================================================

    project_reply = system.open_project(command)

    if project_reply:

        set_conversation(
            f"Phoenix: {project_reply}"
        )

        speak(project_reply)

        return True


    # ========================================================
    # 3. NORMAL WEBSITES
    # ========================================================

    for keyword, action in sorted(
        WEB_COMMANDS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):

        if (
            command == keyword
            or command.startswith(
                "open " + keyword
            )
            or command.startswith(
                "launch " + keyword
            )
            or command.startswith(
                "go to " + keyword
            )
            or (
                keyword in command
                and (
                    "open" in command
                    or "launch" in command
                    or "go to" in command
                )
            )
        ):

            reply = action()

            set_conversation(
                f"Phoenix: {reply}"
            )

            speak(reply)

            return True


    # ========================================================
    # 4. MUSIC
    # ========================================================

    if command.startswith("play"):

        song = command.replace(
            "play",
            "",
            1
        ).strip()

        print(
            f"Requested Song: {song}"
        )

        link = musicLibrary.music.get(
            song
        )

        if link:

            reply = (
                f"Playing {song}."
            )

            set_conversation(
                f"Phoenix: {reply}"
            )

            speak(reply)

            webbrowser.open(link)

        else:

            reply = (
                f"Sorry Boss, I couldn't "
                f"find {song} in your music library."
            )

            set_conversation(
                f"Phoenix: {reply}"
            )

            speak(reply)

        return True


    # ========================================================
    # 5. NEWS
    # ========================================================

    if "news" in command:

        intro = (
            "Scanning today's headlines."
        )

        set_conversation(
            f"Phoenix: {intro}"
        )

        speak(intro)

        url = (
            "https://newsapi.org/v2/"
            f"top-headlines?country=us"
            f"&apiKey={newsapi}"
        )

        try:

            response = session.get(
                url,
                timeout=8
            )

            if response.status_code != 200:

                reply = (
                    "Sorry Boss. "
                    "I couldn't connect to the news server."
                )

                set_conversation(
                    f"Phoenix: {reply}"
                )

                speak(reply)

                return True


            data = response.json()

            articles = data.get(
                "articles",
                []
            )


            if not articles:

                reply = (
                    "Sorry Boss. "
                    "There are no headlines available right now."
                )

                set_conversation(
                    f"Phoenix: {reply}"
                )

                speak(reply)

                return True


            transitions = [
                "Leading today's headlines.",
                "In another development.",
                "Meanwhile.",
                "Turning to technology.",
                "On the business front."
            ]


            for i, article in enumerate(
                articles[:5]
            ):

                title = article.get(
                    "title",
                    ""
                )

                description = article.get(
                    "description",
                    ""
                )


                if " - " in title:

                    title = title.rsplit(
                        " - ",
                        1
                    )[0]


                headline = (
                    f"{transitions[i]} "
                    f"{title}"
                )

                print(headline)

                set_conversation(
                    f"Phoenix: {title}"
                )

                speak(headline)


                if description:

                    speak(
                        description
                    )


            reply = (
                "That concludes your "
                "intelligence briefing, Boss."
            )

            set_conversation(
                f"Phoenix: {reply}"
            )

            speak(reply)

        except Exception as e:

            print(
                "News error:",
                e
            )

            reply = (
                "I couldn't retrieve "
                "the news right now."
            )

            set_conversation(
                f"Phoenix: {reply}"
            )

            speak(reply)

        return True


    # ========================================================
    # 6. NOTHING MATCHED
    # ========================================================

    return False

# ============================================
# Listen Helper
# ============================================



def listen():

    listening()

    try:

        with sr.Microphone() as source:

            print("Listening...")

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

        text = recognizer.recognize_google(audio)

        idle()

        if text:
            print("Heard:", text)
            return text.strip()

        return None

    except sr.WaitTimeoutError:

        print("No speech detected.")
        idle()
        return None

    except sr.UnknownValueError:

        print("Couldn't understand.")
        idle()
        return None

    except sr.RequestError as e:

        print("Google Speech Error:", e)
        idle()
        return None

    except http.client.RemoteDisconnected:

        print("Google closed the connection.")
        idle()
        time.sleep(1)
        return None

    except ConnectionResetError:

        print("Connection reset.")
        idle()
        time.sleep(1)
        return None

    except Exception as e:

        print("Listen error:", e)
        idle()
        return None


# ============================================
# Main
# ============================================
# ============================================
# Assistant Loop
# ============================================



def assistant():

    speak(
        random.choice(
            STARTUP_LINES
        )
    )

    active = False

    idle()

    set_conversation(
        "Awaiting wake word... Say 'Phoenix'"
    )


    while True:

        try:

            text = listen()


            if text is None:

                idle()

                time.sleep(0.2)

                continue


            print(
                "Heard:",
                text
            )


            # =================================================
            # WAKE MODE
            # =================================================

            if not active:

                if "phoenix" in text.lower():

                    active = True

                    wake = random.choice(
                        WAKE_LINES
                    )

                    set_conversation(
                        f"Phoenix: {wake}"
                    )

                    speak(wake)

                else:

                    set_conversation(
                        "Awaiting wake word..."
                    )

                idle()

                time.sleep(0.2)

                continue


            # =================================================
            # USER MESSAGE
            # =================================================

            set_conversation(
                f"You: {text}"
            )


            # =================================================
            # SLEEP COMMANDS
            # =================================================

            lower_text = text.lower()


            if (
                "sleep" in lower_text
                or "hold your horses" in lower_text
                or "stand down" in lower_text
                or "shutdown" in lower_text
                or "echo null" in lower_text
                or "leave env" in lower_text
                or "see you later" in lower_text
                or "fuck off" in lower_text
            ):

                goodbye = random.choice(
                    GOODBYE_LINES
                )

                set_conversation(
                    f"Phoenix: {goodbye}"
                )

                speak(goodbye)

                active = False

                idle()

                time.sleep(0.2)

                continue


            # =================================================
            # COMMAND ENGINE FIRST
            # =================================================

            handled = processCommand(
                text
            )


            # =================================================
            # COMMAND WAS SUCCESSFUL
            # =================================================

            if handled:

                idle()

                time.sleep(0.2)

                continue


            # =================================================
            # AI FALLBACK
            # =================================================

            thinking()

            try:

                reply = askPhoenix(
                    text
                )

            except Exception as e:

                print(
                    "AI error:",
                    e
                )

                reply = random.choice(
                    [
                        "Boss, my cloud brain is offline.",
                        "Looks like the internet ghosted me.",
                        "Connection lost. Give me a second.",
                        "Sorry Boss, I can't reach my AI servers."
                    ]
                )


            set_conversation(
                f"Phoenix: {reply}"
            )

            print(
                f"\nPhoenix: {reply}\n"
            )


            with open(
                "logs.txt",
                "a",
                encoding="utf-8"
            ) as log:

                log.write(
                    f"User: {text}\n"
                )

                log.write(
                    f"Phoenix: {reply}\n"
                )

                log.write(
                    "-" * 60 + "\n"
                )


            speak(reply)

            idle()

            time.sleep(0.2)


        except KeyboardInterrupt:

            speak(
                "Standing down, Boss."
            )

            break


        except Exception as e:

            print(
                "Assistant error:",
                e
            )

            idle()

            time.sleep(0.5)




# ============================================
# Main
# ============================================

if __name__ == "__main__":

    threading.Thread(
        target=assistant,
        daemon=True
    ).start()

    create_window()