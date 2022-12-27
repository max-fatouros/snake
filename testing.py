from collections import Counter

from key_log import KeyLog
from game import *
from board import *
import board
import numpy as np
import time
import tensorflow as tf

logging.basicConfig(filename="logs.txt",
                    level=logging.DEBUG,
                    filemode="w",
                    format="%(levelname) -9s %(module)s:%(lineno)s %(funcName) -10s %(message)s")

state, iterations = board.random_state(6, 6, render=True)

print(state)
print(iterations)
