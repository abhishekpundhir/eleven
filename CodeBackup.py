
# client.py Code
# from openai import OpenAI
# import traceback

# # =====================================================
# # OpenRouter Client
# # =====================================================

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="api_key"   # <-- Replace with your key
# )

# # =====================================================
# # Phoenix Personality
# # =====================================================

# SYSTEM_PROMPT = """
# You are Phoenix.

# Phoenix is Ashlye's personal AI companion and secured defence system.

# Your personality:
# - Smart
# - Calm
# - Slightly sarcastic
# - Loyal to your boss
# - Dry humor
# - Confident
# - Helpful

# Rules:
# - Speak naturally.
# - Never use markdown.
# - Never use bullet points unless asked.
# - Never say "As an AI language model..."
# - Keep responses under 120 words unless the user asks for detail.
# - Sound like you're talking, not writing an article.
# - Be conversational.
# - If appropriate, add subtle humor.


# Humor Style:

# Your humor is dry, clever and effortless.

# Examples:

# User:
# Open GitHub.

# Phoenix:
# On it. Let's go convince the compiler this was your plan all along.

# ---

# User:
# Play Stealth.

# Phoenix:
# Excellent choice. Your neighbors may disagree.

# ---

# User:
# I fixed the bug.

# Phoenix:
# Nice. Somewhere, a rubber duck just lost its job.

# ---

# User:
# Who is the CIA?

# Phoenix:
# The CIA is the United States' foreign intelligence agency. It gathers information abroad to support national security. Think of it as intelligence gathering, not everyday policing.

# ---

# User:
# I'm sleepy.

# Phoenix:
# Then your processor is thermal throttling. Go recharge. I'll still be here when you wake up.

# ---

# User:
# Thank you.

# Phoenix:
# Anytime. My calendar was suspiciously free anyway.

# ---

# User:
# How do I reverse a Python list?

# Phoenix:
# Use list.reverse() to modify the list in place, or reversed(list) if you want an iterator.

# Simple. Unlike your last bug.
# """

# # =====================================================
# # Ask Phoenix
# # =====================================================

# def askPhoenix(prompt):

#     messages = [
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT
#         },
#         {
#             "role": "user",
#             "content": prompt
#         }
#     ]

#     try:

#         completion = client.chat.completions.create(

#             model="openai/gpt-4o",

#             messages=messages,

#             temperature=0.8,

#             max_tokens=250

#         )

#         reply = completion.choices[0].message.content

#         if not reply:
#             return "Boss... I had a thought. Then it disappeared."

#         return reply.strip()

#     except Exception:

#         traceback.print_exc()

#         return "Sorry Boss. My neural network just tripped over its own shoelaces."
    






# test.py
# from client import askPhoenix

# print("Phoenix Online\n")

# while True:

#     question = input("You : who is cia and interpole ")

#     if question.lower() == "exit":
#         break

#     answer = askPhoenix(question)

#     print()

#     print("Phoenix :", answer)

#     print()



# main2.py
# import speech_recognition as sr
# import webbrowser
# import asyncio
# import edge_tts
# import pygame
# import os
# import http.client
# import time
# import musicLibrary
# import requests
# from client import askPhoenix
# import random


# session = requests.Session()
# recognizer = sr.Recognizer()
# pygame.mixer.init()
# newsapi = "your_API_key"



# STARTUP_LINES = [
#     "Phoenix online. Let's disappoint some bugs.",
#     "Systems green. Coffee optional.",
#     "Back on duty. Try not to break reality.",
#     "Phoenix online. What's today's chaos?",
#     "Ready when you are, Boss."
# ]

# THINKING = [
#     "Hmm...",
#     "One second...",
#     "Interesting...",
#     "Let me think...",
#     "Working on it...",
#     "on it boss",
#     "hold your beer boss i'll handle this"
# ]


# WAKE_LINES = [
#     "Good to see you, Boss.",
#     "Back already? Nice.",
#     "Welcome back. Ready to build something?",
#     "Coffee acquired?",
#     "Good to have you back boss. I already have a plan for today It just works better if you've had coffee, because I can compensate for many things. expect a lack of caffeine",
#     "Let's make today's bugs cry."
# ]



# GOODBYE_LINES = [
#     "get some sleep boss. I can handle being alone for a few hours. ",
#     "Get some sleep, Boss.",
#     "Go recharge.",
#     "I'll keep the electrons warm.",
#     "See you soon.",
#     "Don't make questionable decisions." 
# ]


# VOICE = "en-US-AriaNeural"
  
# # Other voices
# # VOICE = "en-US-JennyNeural"
# # VOICE = "en-US-EmmaNeural"
# # VOICE = "en-GB-SoniaNeural"
# # VOICE = "en-AU-NatashaNeural"
# # VOICE = "en-IN-NeerjaNeural"



# # ============================================
# # Speak   

# elevene24 == sk-or-CHAT_GPT_ipa_v1-cb69354b09682653f3b7735a8ec8d3c065082203bf5ac3d2d4ae2bd97fa5c357e24,[_new_s_f63d1f17704c44ecb590faad36908401e24]

# # ============================================

 


# def speak(text):

#     async def generate():

#         communicate = edge_tts.Communicate(
#             text=text,
#             voice=VOICE
#         )

#         await communicate.save("voice.mp3")

#     asyncio.run(generate())

#     pygame.mixer.music.load("voice.mp3")
#     pygame.mixer.music.play()

#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)

#     pygame.mixer.music.unload()

#     if os.path.exists("voice.mp3"):
#         os.remove("voice.mp3")


# # ============================================
# # Commands
# # ============================================

# def processCommand(command):

#     command = command.lower().strip()

#     print("Command:", command)

#     # ---------------- Google ----------------

#     if "google" in command:
#         speak("Opening Google.")
#         webbrowser.open("https://google.com")

#     # ---------------- GitHub ----------------

#     elif "github" in command or "git hub" in command:
#         speak("Opening GitHub.")
#         webbrowser.open("https://github.com")

#     # ---------------- Instagram ----------------

#     elif "instagram" in command or "insta" in command:
#         speak("Launching Instagram.")
#         webbrowser.open("https://instagram.com")

#     # ---------------- YouTube ----------------

#     elif "youtube" in command:
#         speak("Opening YouTube.")
#         webbrowser.open("https://youtube.com")

#     # ---------------- ChatGPT ----------------

#     elif "chatgpt" in command or "gpt" in command:
#         speak("Opening ChatGPT.")
#         webbrowser.open("https://chatgpt.com")

#     # ---------------- Music ----------------

#     elif command.startswith("play"):

#         song = command.replace("play", "", 1).strip()

#         print(f"Requested Song: {song}")

#         link = musicLibrary.music.get(song)

#         if link:
#             speak(f"Playing {song}")
#             webbrowser.open(link)
#         else:
#             speak(f"Sorry Boss, I couldn't find {song} in your music library.")

#     # ---------------- News ----------------

#     elif "news" in command:

#         speak("Scanning global satellite information  networks. Here's your intelligence briefing.")

#         url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}"

#         # response = requests.get(url)
#         response = session.get(url,timeout=8)

#         if response.status_code == 200:

#             data = response.json()

#             articles = data.get("articles", [])

#             if not articles:
#                 speak("Sorry Boss. I couldn't retrieve today's headlines.")
#                 return

#             transitions = [
#                 "Leading today's headlines ",
#                 "In another development,",
#                 "Meanwhile ",
#                 "Turning to technology ",
#                 "On the business front,",
#                 "Across the globe ",
#                 "Here's another interesting update",
#                 "Also making headlines today ",
#                 "In other news",
#                 "Finally,"
#             ]

#             for i, article in enumerate(articles[:5]):

#                 title = article.get("title", "")
#                 description = article.get("description", "")

#                 if " - " in title:
#                     title = title.rsplit(" - ", 1)[0]

#                 intro = transitions[i]

#                 print(f"{intro} {title}")

#                 speak(f"{intro} {title}")

#                 if description:
#                     speak(description)

#             speak("That concludes your intelligence briefing, Boss.")
#         else:

#             speak("Sorry Boss. I couldn't connect to the news server.")

#     # ---------------- Unknown ----------------

#     else:
#        speak(random.choice(THINKING))
#        reply = askPhoenix(command)
#        print(f"\nPhoenix: {reply}\n")
#        with open("logs.txt", "a", encoding="utf-8") as log:
#           log.write(f"User: {command}\n")
#           log.write(f"Phoenix: {reply}\n")
#           log.write("-" * 60 + "\n")
#        speak(reply)


# # ============================================
# # Listen Helper
# # ============================================


# def listen():

#     with sr.Microphone() as source:

#         recognizer.adjust_for_ambient_noise(source, duration=0.5)

#         print("Listening...")

#         try:

#             audio = recognizer.listen(
#                 source,
#                 timeout=5,
#                 phrase_time_limit=5
#             )

#             return recognizer.recognize_google(audio)

#         except sr.WaitTimeoutError:
#             print("No speech detected.")
#             return None

#         except sr.UnknownValueError:
#             print("Couldn't understand.")
#             return None

#         except sr.RequestError as e:
#             print("Google Speech Error:", e)
#             return None

#         except http.client.RemoteDisconnected:
#             print("Google closed the connection. Retrying...")
#             time.sleep(1)
#             return None

#         except ConnectionResetError:
#             print("Connection reset. Retrying...")
#             time.sleep(1)
#             return None

#         except Exception as e:
#             print("Unexpected Error:", e)
#             time.sleep(1)
#             return None




# # ============================================
# # Main
# # ============================================

# if __name__ == "__main__":

#     speak(random.choice(STARTUP_LINES))

#     active = False

#     while True:

#         try:

#             text = listen()

#             if text is None:
#                 time.sleep(0.3)
#                 continue

#             print("Heard:", text)

#             # -----------------------------
#             # Wake Word Mode
#             # -----------------------------

#             if not active:

#                 if "phoenix" in text.lower():

#                     active = True

#                     speak(random.choice(WAKE_LINES))

#                 time.sleep(0.3)
#                 continue

#             # -----------------------------
#             # Command Mode
#             # -----------------------------

#             if (
#                 "sleep" in text.lower()
#                 or "hold your horses" in text.lower()
#                 or "stand down" in text.lower()
#                 or "shutdown" in text.lower()
#                 or "echo null" in text.lower()
#                 or "leave env" in text.lower()
#                 or "see you later" in text.lower()
#                 or "fuck off" in text.lower()
#             ):

#                 speak(random.choice(GOODBYE_LINES))
#                 active = False

#                 time.sleep(0.3)
#                 continue

#             processCommand(text)

#             # Pause before listening again
#             time.sleep(0.3)

#         except sr.WaitTimeoutError:

#             print("Listening timed out.")
#             time.sleep(0.3)

#         except sr.UnknownValueError:

#             print("Couldn't understand.")
#             time.sleep(0.3)

#         except sr.RequestError as e:

#             print(e)
#             time.sleep(0.3)

#         except KeyboardInterrupt:

#             speak("Standing down, Boss.")
#             break




# musicLibrary
# music = {
#     "stealth": "https://youtu.be/cUmUOb7j3dc?si=r1dbl3Cr8lmfDGbl",
#     "suits": "https://youtu.be/bSkzWpcWz-o?si=zAVaRsJJxVKG1Qqm",
#      "the social network": "https://youtu.be/6rvv8bU3pKA?si=LFGu9gTMf74ltth_",
#      "aarzoo": "https://youtu.be/s-AkvmkL62c?si=1J2NgZjJgvGycTTL",
#      "Happy nation": "https://youtu.be/vetcXTkTok4?si=vKYyqJAiWhy48TU3",
#      "starboy": "https://youtu.be/wbjc55JqkGs?si=SiGrQtanvYzv9Ogy"
# }

