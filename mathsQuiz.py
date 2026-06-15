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

        # Declare attributes.
        # Using Final for some of them as I don't want them to be changed, and they shouldn't be changed.
        self.question: Final[str] = qQuestion
        self.expression: Final[str] = expression
        self.answer: Final[int] = int(answer)
        self.userAnswer: int | None = None

    # Checks if the answer is valid, and takes if the time limit has passed to consider the result.
    def checkAnswer(self, answer: int, passedTimeLimit: bool):
        # If the time limit has passed then it will set the user answer to -1.
        if passedTimeLimit:
            self.userAnswer = int(-1)
            # Returns true since if the time limit has passed then the user cannot answer.
            return True
        # If the answer is just an empty string then it will false.
        if answer == "": return False
        # If the time limit has not passed and its no an empty string then it will set the fully validated answer.
        self.userAnswer = int(answer)
        # Returns to tell the flask end that the validation has passed.
        return True


class QuestionManager:

    # Question manager is responsible for managing questions.
    def __init__(self, amount: int | None):
        """
        This class manages questions. It allows for a set amount of questions to be generated.
        Each question is only generated everytime the genQuestions function is run./n
        * This class stores the list of currently generated questions./n
        * the pre-defined amount of questions it can generate./n
        * The current difficulty its on (Since it's increasing for every question that is correct)./n
        * A boolean telling if the time limit has passed for the current question./n
        * A active timer that stores any active timers (Will be None at the start).
        :param amount:
        """
        if amount is not None and amount < 1: raise ValueError("Amount must be a positive integer")

        self.questions: list[Question] = []
        self.amount: Final[int | None] = amount
        self.currentDifficulty = 1
        self.timeLimitPassed = False
        self.activeTimer = None
        print(f"Created Question manager with amount {self.amount}")
        print(f"Questions List: {len(self.questions)}")

    def genQuestion(self, type: str, level: int):
        """
        This function generates a question. It requires a question type (Which determines what operation is used to generate the question).
        The Level determines the time limit for answer a question (Level 0: Infinite, Level 1: 20 Seconds, Level 2: 10 seconds)./n
        * This function will return None, if the amount maximum of questions has been reached.
        :param type:
        :param level:
        :return:
        """
        # Sets the difficulty to a variable. Since it gets messy using self.difficulty.
        difficulty = self.currentDifficulty

        # Returns none if it has reached the max amount of questions.
        if len(self.questions) == self.amount: return None

        # Validates the difficulty since it must be not less than 1.
        if difficulty < 1: raise ValueError("Difficulty must be a non-zero positive integer.")

        # Function for generating addition question.
        def additionGenerator(nums = None):
            # Declares the expression
            expression = ""
            # Calculates a number using the difficulty. Makes use of exponential equations for increasing difficulty.
            randNumNumber = round(math.pow(1.05, difficulty) + 1)
            # Sets the amount of numbers to a variable limiting it to a maximum of 6 numbers in an expression
            # With a maximum of 10 questions only allows the difficulty to get to 10, it was tested that it would never,
            # ever reach to 6 number in an expression. The difficulty must be higher.
            numNumbers = min(6, randNumNumber)
            # This function checks if the argument nums is None.
            # This is used to predefine the amount of numbers can be in the question.
            # Currently, this is not used.
            if nums is not None: numNumbers = nums

            # This repeats the number generation process for the amount of times the amount of numbers in an expression is.
            for num in range(numNumbers):
                # This creates a max and min numbers for random number generation.
                # It makes use of exponential equations for increasing difficulty.
                minNum = round(mc.clamp(difficulty - 5, 1, 12))
                maxNum = round(mc.clamp(math.exp(2.1) * difficulty / 3, 2, 12))
                # A random number is generated.
                number = random.randint(minNum, maxNum)

                # It adds the generated number and its operation on the expression.
                expression += f"{number} + "
            # Once the expression is finished it will return the new expression.
            return expression

        def subtractionGenerator(nums=None):
            # This calculates the amount of numbers in the expression using exponential equations.
            randNumNumber = round(math.pow(1.05, difficulty) + 1)
            numNumbers = min(6, randNumNumber)
            if nums is not None: numNumbers = nums

            expression = ""
            # Generates a number for every single number defined.
            for num in range(numNumbers):
                number = 0
                # This function makes sure that the first number in the expression will be at a higher range of numbers.
                # This allows for a somewhat large number to start with so that each expression can be subtracted reasonable
                # even with a high expression count.
                if num == 0:
                    # Generates a random starting number for the first number.
                    minNum = round(mc.clamp(difficulty - 5, 2, 12))
                    maxNum = round(mc.clamp(math.exp(2.1) * difficulty / 3, 3, 12))
                    number = random.randint(minNum, maxNum)
                    print(f"First Num: {number}")
                else:
                    # This calculates the current expression total.
                    currentNum = sympify(f"{expression}0")
                    # This generates a random number between zero and total of the current number.
                    # It must be subtracted by one since for example a range between 2 and 2 will be nothing.
                    number = random.randint(0, currentNum - 1)
                    print(f"Further Nums: {number}")

                # Adds generated number to the expression.
                expression += f"{number} {type} "

            # Returns expression once finished.
            return expression

        def multiplicationGenerator(nums=None):
            # I set the number of numbers in the expression to 2, since any higher would be too difficulty for the audience of users.
            numNumbers = 2
            if nums is not None: numNumbers = nums

            expression = ""
            for num in range(numNumbers):
                # Runs for the first number in the expression.
                if num == 0:
                    # The starting number determines the difficulty.
                    minNum = round(mc.clamp(difficulty - 5, 1, 12))
                    maxNum = round(mc.clamp(math.exp(2.1) * difficulty / 3, 2, 12))
                    number = random.randint(minNum, maxNum)
                else:
                    # There is a 1 in 16 chance for the next number to be zero.
                    # Cool addition but also challenging for the audience.
                    if random.randint(0, 15) == 5:
                        number = 0
                    else:
                        # Generates a random number between 1 and 5. No higher since it will be too difficult.
                        number = random.randint(1, 5)

                # Adds new number to expression.
                expression += f"{number} {type} "

            # Returns new expression once finished.
            return expression

        def divisionGenerator(nums=None):
            # Sets the max numbers in the expression to 2.
            numNumbers = 2
            # If the difficulty is more than 5 then it will actually set it to 3.
            if difficulty > 5: numNumbers = 3
            if nums is not None: numNumbers = nums

            expression = ""
            for num in range(numNumbers):
                number = 0
                if num == 0:
                    # For the first number it will generate a random number based on difficulty.
                    minNum = round(mc.clamp(difficulty - 5, 4, 12))
                    maxNum = round(mc.clamp(math.exp(3) * difficulty, 5, 12))
                    number = random.randint(minNum, maxNum)
                    print(f"First Num: {number}, {minNum}, {maxNum}")
                else:
                    # If its not the first number then it will use the factor function to get its factors.
                    currentNum = sympify(f"{expression}1")
                    factors = mc.factors(currentNum)
                    print(f"Factors: {factors}")
                    print("Current: " + str(currentNum))
                    # Checks if the length of factors is not equal one (It can only possibly the only factor can be one).
                    if len(factors) != 1:
                        # There is a 1 in 16 chance for the number to be 1 for the next number in the expression.
                        if random.randint(0, 15) == 5: number = 1
                        else:
                            # Since the length of factors is not 1 that means there are other factors.
                            # So I remove 1 as a factor and pick a random one.
                            factors.remove(1)
                            number = random.choice(factors)
                    else:
                        # If there is only 1 factor then it can only be 1.
                        number = 1
                    print(f"Further Nums: {number}")

                # Adds the number to the expression
                expression += f"{number} {type} "

            # Returns the generated expression.
            return expression

        # Declare variables.
        questionWord = ""
        expression = ""
        # Check if the type is one of the following:
        if type == "+":
            # Calls the addition generator.
            expression = additionGenerator()
            questionWord = "What is the sum of"
        elif type == "-":
            # Calls the subtraction generator.
            expression = subtractionGenerator()
            questionWord = "What is the difference of"
        elif type == "*":
            # Calls the multiplication generator.
            expression = multiplicationGenerator()
            questionWord = "What is the multiple of"
        elif type == "/":
            # Calls the divison generator.
            expression = divisionGenerator()
            questionWord = "What is the division of"
        elif type == "mix":
            # When mixed it will generate a random type and re call this genQuestio function with the random type.
            randomType = mc.randomType()
            return self.genQuestion(randomType, level)
        else: raise ValueError("Invalid question type")

        expression = expression[:-3]
        # Removes the last three characters on the expression since:
        # There is a extra space generated, there is a extra operation added (Removing it will prevent syntax errors)
        # and another extra space after it eg: '2 + 3 + '. These are the extra characters: ' + '

        # Creates an instance of a question passing through a question.
        question = Question(f"{questionWord} [{expression}]?")
        # Adds the question to the question list of the manager.
        self.questions.append(question)
        # Sets the time limit passed to false.
        self.timeLimitPassed = False
        # Calls the timer function and passes the level.
        self.timer(level)
        # Returns the question.
        return question

    def updateDifficulty(self, answer):
        # Updates the difficulty when the current question answer is equal to the user answer.
        if answer == self.questions[-1].answer:
            # Plus one to the current difficulty.
            self.currentDifficulty += 1
            print(f"Updated difficulty: {self.currentDifficulty}")

    # This function saves the question history in the question.
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

        # Define the save directory.
        directory = os.path.join(basePath, "mathQuizSaves")
        # Check if it exists, if not then create it.
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Define the file at the location.
        file = os.path.join(directory, "history.json")

        # Load the data inside of the existing dictionary.
        existingHistory = []
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    existingHistory = json.load(f)
                    # Safety check to ensure the file contains a list
                    if not isinstance(existingHistory, list):
                        # If there is nothing then nothing is inside.
                        existingHistory = []
            except Exception:
                # If file is empty or corrupted, start fresh.
                existingHistory = []

        # Convert current custom Question objects into dictionaries
        currentQuestionsData = []
        for question in self.questions:
            questionDict = {
                "question": question.question,
                "expression": question.expression,
                "answer": question.answer,
                "userAnswer": question.userAnswer
            }
            currentQuestionsData.append(questionDict)

        # Combine existing with current histories.
        updatedHistory = currentQuestionsData + existingHistory

        # Slice the list to keep only the maximum allowed newest items.
        updatedHistory = updatedHistory[:maxHistoryLimit]

        # Overwrite the file with the clean, updated history list.
        with open(file, 'w') as f:
            json.dump(updatedHistory, f, indent=4)


    def timer(self, level: int):
        from threading import Timer
        # This function starts the timer.
        # If level zero then no timer will be started.
        # If the level is 1 then start a 20-second timer.
        # If the evel is 2 then start a 10-second timer.
        # Allow 1 second headroom.
        if level == 0: return
        if level == 1:
            self.activeTimer = Timer(21, QuestionManager.whenTimeLimitPassed, args=(self,))
            self.activeTimer.start()
        if level == 2:
            self.activeTimer = Timer(11, QuestionManager.whenTimeLimitPassed, args=(self,))
            self.activeTimer.start()

    # This function is called when the time limit is passed.
    def whenTimeLimitPassed(self):
        # Sets the time limit passed function to true.
        self.timeLimitPassed = True
        print("Time is up")