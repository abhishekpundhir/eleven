import os
from dotenv import load_dotenv
from groq import Groq

from context import retrieve_context

load_dotenv()

# ============================================================
# GROQ CONFIG
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing from your .env file."
    )

groq_client = Groq(
    api_key=GROQ_API_KEY
)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# PHOENIX SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Phoenix, a personal AI assistant.

Personality:
- Intelligent
- Calm
- Fast
- Slightly cinematic
- Witty when appropriate
- Never unnecessarily verbose
- Address the user as Boss when natural

Behavior:
- Give direct and useful answers.
- Do not repeat the user's question unnecessarily.
- If the user asks for code, provide practical working code.
- If the user asks something simple, answer simply.
- If the user asks for technical help, be precise.
- Use the provided Phoenix/project context when relevant.
- Never claim that you performed an action unless the command system actually performed it.

You are the AI reasoning layer of Phoenix.
"""


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(user_prompt):
    context = retrieve_context(user_prompt)

    if context:
        return f"""
Relevant Phoenix knowledge:

{context}

User request:
{user_prompt}
"""

    return user_prompt


# ============================================================
# GROQ REQUEST
# ============================================================

def ask_groq(prompt):
    final_prompt = build_prompt(prompt)

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        temperature=0.35,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    if not answer:
        return "I didn't get a useful response from my AI core."

    return answer.strip()


# ============================================================
# PHOENIX AI API
# ============================================================

def askPhoenix(prompt):
    return ask_groq(prompt)