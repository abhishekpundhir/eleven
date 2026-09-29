from client import askPhoenix


print("=" * 60)
print("PHOENIX CONTEXT + GEMINI TEST")
print("=" * 60)


while True:

    prompt = input("\nYou: ").strip()

    if prompt.lower() in {"exit", "quit"}:
        break

    try:
        response = askPhoenix(prompt)
        print(f"\nPhoenix: {response}")

    except Exception as e:
        print(f"\nERROR: {e}")