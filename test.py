from client import askPhoenix

print("Phoenix Online\n")

while True:

    question = input("You : who is cia and interpole ")

    if question.lower() == "exit":
        break

    answer = askPhoenix(question)

    print()

    print("Phoenix :", answer)

    print()





    