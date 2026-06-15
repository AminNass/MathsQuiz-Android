import random
from typing import Final
import mathCommon as mc
import math
from sympy import sympify

# The question class allows for a question to be in the correct format.
# Making use of object orientated programming I have made my own question making a question kinda its own DataType.
class Question:

    # Code that initialized when a new question is created.
    def __init__(self, question: str):
        """
        This class formats a question in a ready format. Stores the full question, the expression, and the answer.
        Also when checking the answer it will store the user answer as an attribute as well.\n
        * Question must have e.g "What is the sum of [4 + 6]?"\n
        Optional, but you can add the question wording at the start. This could be anything relevant to the question.
        Then the expression itself must be surrounded by square brackets. This is so this class knows where the expression is.
        If you put the '*' or '/' symbols it will automatically replace them with '×' or '÷'.
        :param question:
        """
        # All the generic keyboard symbols corresponding to the real maths symbols.
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

    def checkAnswer(self, answer: int, passedTimeLimit: bool):
        if passedTimeLimit:
            self.userAnswer = int(-1)
            return True
        if answer == "": return False
        self.userAnswer = int(answer)
        return True


class QuestionManager:

    def __init__(self, amount: int | None):
        if amount is not None and amount < 1: raise ValueError("Amount must be a positive integer")

        self.questions: list[Question] = []
        self.amount: Final[int | None] = amount
        self.currentDifficulty = 1
        self.timeLimitPassed = False
        self.activeTimer = None
        print(f"Created Question manager with amount {self.amount}")
        print(f"Questions List: {len(self.questions)}")

    def genQuestion(self, type: str, level: int):
        difficulty = self.currentDifficulty

        if len(self.questions) == self.amount: return None

        if difficulty < 1: raise ValueError("Difficulty must be a non-zero positive integer.")

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
        elif type == "mix":
            randomType = mc.randomType()
            return self.genQuestion(randomType, level)
        else: raise ValueError("Invalid question type")

        expression = expression[:-3]

        question = Question(f"{questionWord} [{expression}]?")
        self.questions.append(question)
        self.timeLimitPassed = False
        self.timer(level)
        return question

    def updateDifficulty(self, answer):
        if answer == self.questions[-1].answer:
            self.currentDifficulty += 1
            print(f"Updated difficulty: {self.currentDifficulty}")

    def saveToHistory(self):
        import json
        import os

        # I left this as a variable other than kinda hardcoding it since I might want to change this later.
        maxHistoryLimit = 100

        # Determine path for Android and Development Environment.
        if 'ANDROID_PRIVATE_VOLUME' in os.environ:
            basePath = os.environ['ANDROID_PRIVATE_VOLUME']
        else:
            # Falls back for dev env
            basePath = os.getcwd()

        directory = os.path.join(basePath, "mathQuizSaves")
        if not os.path.exists(directory):
            os.makedirs(directory)

        file = os.path.join(directory, "history.json")

        # Load directory if it already exists.
        existingHistory = []
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    existingHistory = json.load(f)
                    # Safety check to ensure the file contains a list
                    if not isinstance(existingHistory, list):
                        existingHistory = []
            except Exception:
                # If file is empty or corrupted, start fresh
                existingHistory = []

        # Convert current custom Question objects into dictionaries
        currentQuestionsData = []
        for question in self.questions:
            question_dict = {
                "question": question.question,
                "expression": question.expression,
                "answer": question.answer,
                "userAnswer": question.userAnswer
            }
            currentQuestionsData.append(question_dict)

        # Combine existing with current histories.
        updated_history = currentQuestionsData + existingHistory

        # Slice the list to keep only the maximum allowed newest items.
        updated_history = updated_history[:maxHistoryLimit]

        # Overwrite the file with the clean, updated history list.
        with open(file, 'w') as f:
            json.dump(updated_history, f, indent=4)


    def timer(self, level: int):
        from threading import Timer
        if level == 0: return
        if level == 1:
            self.activeTimer = Timer(21, QuestionManager.whenTimeLimitPassed, args=(self,))
            self.activeTimer.start()
        if level == 2:
            self.activeTimer = Timer(11, QuestionManager.whenTimeLimitPassed, args=(self,))
            self.activeTimer.start()

    def whenTimeLimitPassed(self):
        self.timeLimitPassed = True
        print("Time is up")