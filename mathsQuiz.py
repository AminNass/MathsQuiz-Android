import random
from typing import Final
import mathCommon as mc
import math
from sympy import sympify

infinity = float("inf")

class Question:

    def __init__(self, question: str):
        symbols = {"+":"+","-":"-","*":"×","/":"÷"}

        # Removing square brackets from the question.
        qQuestion = question.replace("[","").replace("]","")
        for symbol in symbols: qQuestion = qQuestion.replace(symbol, symbols[symbol])

        # Getting the expression from inside the square brackets.
        expression = question[(question.find("[") + 1):(question.find("]"))]
        answer = sympify(expression)
        for symbol in symbols: expression = expression.replace(symbol, symbols[symbol])

        self.question: Final[str] = qQuestion
        self.expression: Final[str] = expression
        self.answer: Final[int] = int(answer)

    def __str__(self): return str({"Question": self.question, "Expression": self.expression, "Answer": self.answer})

    def __int__(self): return self.answer

class QuestionManager:



    def __init__(self, amount: int | None):
        if amount is not None and amount < 1: raise ValueError("Amount must be a positive integer")

        self.questions: list[Question] = []
        self.amount: Final[int | None] = amount

    def generateQuestion(self, type: str, difficulty: int):

        minNumNumber = round(math.pow(1.05, difficulty) + 1)
        maxNumNumber = round(math.pow(1.15, difficulty) + 1)
        numNumbers = min(6, minNumNumber)
        print(f"{minNumNumber} - {maxNumNumber}")



        expression = ""
        for num in range(numNumbers):
            minNum = round(max(1, difficulty - 5))
            maxNum = round(max(2, math.exp(2.1) * difficulty / 3))
            number = random.randint(minNum, maxNum)
            print(f"{minNum} - {maxNum}")

            expression += f"{number} {type} "
        expression = expression[:-2]

        question = Question(f"What is the sum of [{expression}]?")
        self.questions.append(question)
        return question





q = Question("What is the sum of [5 + 4]")
p = Question("What is the sum of [8 + 1]")
print(q)
print(p)
print(int(q) + int(p))

manager = QuestionManager(1)
manager.generateQuestion("+", 18)

print(manager.questions[0])