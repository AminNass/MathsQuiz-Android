import random
from typing import Final

import mathCommon as mc
import math
from sympy import sympify

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
        self.userAnswer: int | None = None

    def __str__(self): return str({"Question": self.question, "Expression": self.expression, "Answer": self.answer})

    def __int__(self): return self.answer

    def checkAnswer(self, answer: int):
        if answer == "":
            return False
        self.userAnswer = int(answer)
        print(f"User answer: {answer}")
        return True


class QuestionManager:

    def __init__(self, amount: int | None):
        if amount is not None and amount < 1: raise ValueError("Amount must be a positive integer")

        self.questions: list[Question] = []
        self.amount: Final[int | None] = amount
        self.currentDifficulty = 1
        print(f"Created Question manager with amount {self.amount}")
        print(f"Questions List: {len(self.questions)}")

    def genQuestion(self, type: str, level: int):
        difficulty = self.currentDifficulty

        if len(self.questions) == self.amount: return None

        if difficulty > 10 or difficulty < 1: raise ValueError("Difficulty must be a non-zero positive integer and no higher than 10.")

        def additionGenerator(nums = None):
            expression = ""
            randNumNumber = round(math.pow(1.05, difficulty) + 1)
            numNumbers = min(6, randNumNumber)
            if nums is not None: numNumbers = nums

            for num in range(numNumbers):
                minNum = round(mc.clamp(difficulty - 5, 1, 12))
                maxNum = round(mc.clamp(math.exp(2.1) * difficulty / 3, 2, 12))
                number = random.randint(minNum, maxNum)

                expression += f"{number} + "
            return expression

        def subtractionGenerator(nums=None):
            randNumNumber = round(math.pow(1.05, difficulty) + 1)
            numNumbers = min(6, randNumNumber)
            if nums is not None: numNumbers = nums

            expression = ""
            for num in range(numNumbers):
                number = 0
                if num == 0:
                    minNum = round(mc.clamp(difficulty - 5, 2, 12))
                    maxNum = round(mc.clamp(math.exp(2.1) * difficulty / 3, 3, 12))
                    number = random.randint(minNum, maxNum)
                    print(f"First Num: {number}")
                else:
                    currentNum = sympify(f"{expression}0")
                    number = random.randint(0, currentNum - 1)
                    print(f"Further Nums: {number}")

                expression += f"{number} {type} "
            return expression

        def multiplicationGenerator(nums=None):
            numNumbers = 2
            if nums is not None: numNumbers = nums

            expression = ""
            for num in range(numNumbers):
                if num == 0:
                    minNum = round(mc.clamp(difficulty - 5, 1, 12))
                    maxNum = round(mc.clamp(math.exp(2.1) * difficulty / 3, 2, 12))
                    number = random.randint(minNum, maxNum)
                else:
                    if random.randint(0, 15) == 5:
                        number = 0
                    else:
                        currentNum = sympify(f"{expression}1")
                        number = random.randint(1, 5)

                expression += f"{number} {type} "
            return expression

        def divisionGenerator(nums=None):
            numNumbers = 2
            if difficulty > 5: numNumbers = 3
            if nums is not None: numNumbers = nums

            expression = ""
            for num in range(numNumbers):
                number = 0
                if num == 0:
                    minNum = round(mc.clamp(difficulty - 5, 4, 12))
                    maxNum = round(mc.clamp(math.exp(3) * difficulty, 5, 12))
                    number = random.randint(minNum, maxNum)
                    print(f"First Num: {number}, {minNum}, {maxNum}")
                else:
                    currentNum = sympify(f"{expression}1")
                    factors = mc.factors(currentNum)
                    print(f"Factors: {factors}")
                    print("Current: " + str(currentNum))
                    if len(factors) != 1:
                        if random.randint(0, 15) == 5: number = 1
                        else:
                            factors.remove(1)
                            number = random.choice(factors)
                    else:
                        number = 1
                    print(f"Further Nums: {number}")

                expression += f"{number} {type} "
            return expression


        questionWord = ""
        expression = ""
        if type == "+":
            expression = additionGenerator()
            questionWord = "What is the sum of"
        elif type == "-":
            expression = subtractionGenerator()
            questionWord = "What is the difference of"
        elif type == "*":
            expression = multiplicationGenerator()
            questionWord = "What is the multiple of"
        elif type == "/":
            expression = divisionGenerator()
            questionWord = "What is the division of"
        else: raise ValueError("Invalid question type")

        expression = expression[:-2]

        question = Question(f"{questionWord} [{expression}]?")
        self.questions.append(question)

        self.timer(level)
        return question

    def timer(self, level: int):
        from threading import Timer
        if level == 0: return
        if level == 2: Timer(20, print, args=('Time is up',)).start()
        if level == 3: Timer(10, print, args=('Time is up',)).start()