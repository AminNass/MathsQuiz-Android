import math
from sympy import sympify

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