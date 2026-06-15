import math
import random

from sympy import sympify
import os
import json

# Created my own clamp function using python's max and min.
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

# This function gets all the factors.
def factors(num: int) -> list:

    factors = set()

    for i in range(1, int(math.sqrt(num))+1):
        if num % i == 0:
            factors.add(i)
            factors.add(num // i)

    sortedFactors = sorted(list(factors))
    return sortedFactors

# This gets the history of questions.
def getHistory():
    # Checks if the app is running on a android environment.
    if 'ANDROID_PRIVATE_VOLUME' in os.environ:
        # If in the android environment then set the base path to 'ANDROID_PRIVATE_VOLUME'.
        # This path is a reserved place for this app to read and write files.
        # No other apps has access to this reserved space.
        basePath = os.environ['ANDROID_PRIVATE_VOLUME']
    else:
        # Falls back for dev env
        basePath = os.getcwd()

    # Sets the file path to the right location.
    filePath = os.path.join(basePath, "mathQuizSaves", "history.json")

    # If the file doesn't exist yet, return an empty list
    if not os.path.exists(filePath):
        return []

    # This will attempt to read the file and return the data inside the json file.
    try:
        with open(filePath, 'r') as f:
            data = json.load(f)
            # This will only return if it's an instance of a list (Since the questions are stored in a list).
            return data if isinstance(data, list) else []
    except Exception:
        # If error accouters then it returns nothing.
        return []

# A function that returns a random operation.
def randomType():
    types = ["+","-","*","/"]
    return random.choice(types)