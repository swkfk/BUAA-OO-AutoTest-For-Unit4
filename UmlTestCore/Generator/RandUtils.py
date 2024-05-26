import random as __random

def gen_int(low=10, high=40):
    return __random.randint(low, high)

def probability(ratio=0.5):
    return __random.random() < ratio

def pick_list(users):
    return __random.choice(users)
