import os
import random
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from tqdm import tqdm

WIN_RATE = 50

S = 1_000
POPULATION = 100
EQUITY = 5_000_000

# mpl.rcParams['toolbar'] = 'None'
plt.style.use('seaborn')

def simulate(money:int, risk_reward_ratio:float, win_rate:int, max_loss:int):
    """
        Simulate the game
        money: int
        risk_reward_ratio: float
        win_rate: int
        max_loss: int
    """
    pass

win, loss, sum = 0, 0, 0
for i in tqdm(range(POPULATION)):
    data = []
    equity = EQUITY
    for inx in range(S):
        value = random.randint(0, 100)
        # TODO: Use dynamic value
        if value <= WIN_RATE:
            equity *= 1.1
        else:
            equity *= 0.95
        data.append(equity)
    if equity > EQUITY:
        win += 1
    else:
        loss += 1
    sum += equity
    plt.plot(np.arange(len(data)), data)
print(f"Profit at the end: {win/POPULATION*100}%")
print(f"Average profit at the end: {sum/POPULATION/EQUITY*100}% or {sum/POPULATION}")
plt.show()
