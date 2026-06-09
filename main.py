import random


def createAdditionQuestion():

    randNum1: int = random.randint(1,50)
    randNum2: int = random.randint(1, 50)

    print("--------\n",
          "What is?\n",
          f"{randNum1} + {randNum2}?\n",
          "--------\n")
    userInput = input("Type your answer:\n")

    if userInput == randNum1 + randNum2:
        print("You got it!")
    else:
        print(f"Incorrect answer!,\nThe correct answer is {randNum1 + randNum2}")


createAdditionQuestion()