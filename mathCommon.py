import math
import random

from sympy import sympify
import os
import json

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def factors(num: int) -> list:

    factors = set()

    for i in range(1, int(math.sqrt(num))+1):
        if num % i == 0:
            factors.add(i)
            factors.add(num // i)

    sortedFactors = sorted(list(factors))
    return sortedFactors

def addAddition(expression, difficulty):
    minNum = round(clamp(difficulty - 5, 1, 12))
    maxNum = round(clamp(math.exp(2.1) * difficulty / 3, 2, 12))

def getHistory():
    if 'ANDROID_ARGUMENT' in os.environ:
        basePath = os.environ.get('ANDROID_PRIVATE_VOLUME', os.path.expanduser('~'))
    else:
        basePath = os.getcwd()

    filePath = os.path.join(basePath, "mathQuizSaves", "history.json")

    # If the file doesn't exist yet, return an empty list
    if not os.path.exists(filePath):
        return []

    try:
        with open(filePath, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def randomType():
    types = ["+","-","*","/"]
    return random.choice(types)