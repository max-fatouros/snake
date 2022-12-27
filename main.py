import time
from game import Game
import logging

logging.basicConfig(filename="logs.txt",
                    level=logging.DEBUG,
                    filemode="w",
                    format="%(levelname) -9s %(module)s:%(lineno)s %(funcName) -10s %(message)s")

snake = Game(30, 50)

snake.play()
