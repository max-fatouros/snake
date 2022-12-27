import atexit
import logging
import time

import numpy as np
from pynput.keyboard import Key
from key_log import KeyLog
from board import Board, Apple, Direction


def render(board=None, file: str = None):
    """
    Render one frame of the game.
    """
    if file is not None:
        boards = np.load(file)
        for board in boards['arr_0']:
            render(board=board)
            time.sleep(0.1)

    elif board is not None:
        for i in range(len(board[0])):
            print("\033[1A", end="")
            print("\033[K", end="")

        for i, row in enumerate(board):
            for j, column in enumerate(row):
                print(column.repr("string"), end='')
            print()


class Game:
    def __init__(self, height, width):
        logging.info("initializing Game")
        self.board = Board(height, width)

    def step(self, key=None, keys=[]):
        """
        Perform one step of the game.
        :param key: Single key.
        :param keys: list of keys.
        :return: (observation, reward, terminated, truncated, info)
        """

        if keys is None:
            keys = list()
        observation = self.board
        reward = 0
        terminated = False
        truncated = False
        info = None

        # TODO: Use either Key or Direction, not both.
        if key is not None:
            if key == Direction.UP:
                keys.append(Key.up)
            elif key == Direction.DOWN:
                keys.append(Key.down)
            elif key == Direction.LEFT:
                keys.append(Key.left)
            elif key == Direction.RIGHT:
                keys.append(Key.right)

        self.board.snake.move(keys=keys)
        # reward -= 1
        logging.debug(self.board.snake.head.data.pos)
        logging.debug(self.board.available_spots())
        logging.debug([(s.data, s.data.pos) for s in self.board.snake])
        if tuple(self.board.snake.head.data.pos) not in self.board.available_spots():
            # Snake hits border or itself.
            truncated = True
            reward -= 100
        elif self.board.snake.head.data.pos == self.board.apple.pos:
            # Snake eats apple.
            self.board.snake.add(self.board.snake.tail.data.prev_pos)
            self.board.apple = Apple(self.board)
            reward += 20

        logging.info(f"reward: {reward}")

        observation = self.board

        return observation, reward, terminated, truncated, info

    def play(self, logo=True):
        """
        Start an interactive game.

        :param logo: Whether to show the logo at the beginning of the game.
        """
        truncated = False
        terminated = False

        print("\n" * 100)  # Clear the screen
        print("\033[?25l")  # Hide cursor
        atexit.register(self.__del__)  # Ensure that the cursor is un-hidden when the program ends

        if logo:
            # Display logo before starting the game
            self._logo()

        key_logger = KeyLog()
        keys = []

        while Key.esc not in keys and not (truncated or terminated):
            keys = key_logger.get_keys(period=0.1)
            logging.debug(f"len(key): {len(keys)}")

            _, _, terminated, truncated, _ = self.step(keys=keys)
            render(self.board)

        if truncated:
            self._game_over()

    def _game_over(self):
        self.board.snake.die()
        self._print_art(GAME_OVER)

    def _logo(self):
        self._print_art(LOGO)
        input()
        print("\n" * 100)  # Clear the screen

    def _print_art(self, ascii_art):
        print("\n" * 100)  # Clear the screen
        art_width = max([len(line) for line in ascii_art.splitlines()])
        art_height = len(ascii_art.splitlines())

        for line in ascii_art.splitlines():
            # The units of self.board.width are 2*char width
            print(" " * int(self.board.width - (art_width / 2)), end="")
            print(line)
        print("\n" * int((self.board.height - art_height) / 2))

    def __del__(self):
        try:
            logging.info("Deleting Game")
        except AttributeError:
            # HACK: the logging module was throwing an error. Seems to work still though.
            pass

        print("\033[?25h", end='')  # Show cursor


# Snake logo printed before game starts
LOGO = """
              _______
             / _   _ \\
            / (.) (.) \\
           ( _________ )
            \`-V-|-V-'/
             \   |   /
              \  ^  /
               \    \\
                \    `-_
                 `-_    -_
                    -_    -_
                    _-    _-        \033[5m\033[1mSNAKE!\033[m
                  _-    _-          Press enter to start
                _-    _-
              _-    _-
              -_    -_
                -_    -_
                  -_    -_
                    -_    -_
                    _-    _-
          \033[31m,-=:_-_-_-_ _ _-_-_-_:=-.
         /=I=I=I=I=I=I=I=I=I=I=I=I=\\
        |=I=I=I=I=I=I=I=I=I=I=I=I=I=|
        |I=I=I=I=I=I=I=I=I=I=I=I=I=I|
        \=I=I=I=I=I=I=I=I=I=I=I=I=I=/
         \=I=I=I=I=I=I=I=I=I=I=I=I=/
          \=I=I=I=I=I=I=I=I=I=I=I=/
           \=I=I=I=I=I=I=I=I=I=I=/
            \=I=I=I=I=I=I=I=I=I=/
             `================='\033[m
\033[2mArt by Max Strandberg\033[m"""

GAME_OVER = """
 ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗ 
██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝"""
