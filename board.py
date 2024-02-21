import copy
import random
import time

import numpy as np
from enum import Enum
from logging import debug, info, warning, error, critical
from pynput.keyboard import Key
import game
import copy

from abc import ABC, abstractmethod

EMPTY = "  "
BORDER = "\u2b1b"
APPLE = "\U0001f534"
SNAKE = "\U0001f7e9"

STARTING_SIZE = 3


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


def random_state(height, width, render=False):
    """
    Generate a random state.
    """
    state = Board(height, width, blank=True)
    state[1:-1, 1:-1] = Empty()  # Clear board, inefficient.

    # length = random.randint(1, len(state.available_spots()))
    length = (height - 1) * (width - 1)

    state.snake = Snake(state, state.rand_available(), 0)

    # If out of moves, pop from stack.
    # Depth first search.
    tail = state.snake.tail
    head = state.snake.head
    longest_snake = 0
    largest_state = None
    possible_moves = tail.data.open_ajacent
    iterations = 0
    while state.snake.length < length:
        iterations += 1
        if head.prev is None and len(possible_moves) == 0:
            # Impossible solution
            # Picking next best
            state = largest_state
            break
        else:
            possible_moves = tail.data.open_ajacent

            if state.snake.length > longest_snake:
                longest_snake = state.snake.length
                largest_state = copy.deepcopy(state)

            if len(possible_moves) == 0:
                state.snake.pop()
                # if render:
                #     game.render(state)

            else:
                move = random.choice(possible_moves)
                tail.data.open_ajacent.remove(move)
                state.snake.add(pos=move)
                if render:
                    game.render(state)
                    time.sleep(0.01)

            # if render:

            tail = state.snake.tail  # Must be last in loop.

    # TODO: If length == len(state.available_spots(), don't place an apple.

    return state, iterations


class Board:
    def __init__(self, height, width, blank=False):
        info("initializing Board")

        self.grid = np.full((height, width), Border(), dtype=object)
        self.grid[1:-1, 1:-1] = Empty()

        self.height = height
        self.width = width

        if not blank:
            self.snake = Snake(self)
            self.apple = Apple(self)

    def available_spots(self):
        """
        Returns:  a list of available spots.
        """

        return [
            (y, x)
            for y in range(1, self.height - 1)
            for x in range(1, self.width - 1)
            if isinstance(self.grid[y, x], Empty) or isinstance(self.grid[y, x], Head)
        ]

    def rand_available(self):
        """
        Returns: a random available spot.
        """
        return random.choice(self.available_spots())

    def __getitem__(self, item):
        return self.grid[item]

    def __setitem__(self, key, value):
        self.grid[key] = value

    def repr(self, type):
        output = []
        for row in self:
            for element in row:
                output.append(element.repr(type))
        return np.array(output).reshape(self.height, self.width)

    def __str__(self):
        output = ""
        for row in self:
            for column in row:
                output += column.repr("string")
            output += "\n"
        return output


class Snake:
    def __init__(self, board, pos=None, starting_size=STARTING_SIZE - 1):
        info("initializing Snake")
        self.board = board

        if pos is None:
            pos = [3, STARTING_SIZE + 2]

        self.head = Node(
            Head(
                board=self.board,
                pos=pos
            )
        )
        self.tail = self.head
        self.length = 1

        # Give the user a starter snake
        for i in range(starting_size): self.add()

    def __iter__(self):
        curr = self.head
        while curr is not None:
            yield curr
            curr = curr.prev

    def add(self, pos=None):
        if pos is None:
            pos = (self.tail.data.pos[0], self.tail.data.pos[1] - 1)
        self.tail.prev = Node(
            Body(board=self.board, pos=pos),
            next=self.tail
        )
        self.tail = self.tail.prev
        self.length += 1

    def pop(self):
        """
        Removes that tail of the snake.
        """
        self.tail = self.tail.next
        self.tail.prev.data.clear()
        self.tail.prev = None
        self.length -= 1

    def direction(self):
        return self.head.data.direction

    def move(self, keys=None, direction=None):
        curr = self.head
        curr_dir = curr.data.direction

        # Convert key press to direction
        # The first eight if-else statements are to help move the snake diagonally.
        # TODO: Implement switch when python supports it (3.10)
        if Key.up in keys and Key.right in keys and curr_dir == Direction.UP:
            direction = Direction.RIGHT
        elif Key.up in keys and Key.right in keys and curr_dir == Direction.RIGHT:
            direction = Direction.UP
        elif Key.right in keys and Key.down in keys and curr_dir == Direction.RIGHT:
            direction = Direction.DOWN
        elif Key.right in keys and Key.down in keys and curr_dir == Direction.DOWN:
            direction = Direction.RIGHT
        elif Key.down in keys and Key.left in keys and curr_dir == Direction.DOWN:
            direction = Direction.LEFT
        elif Key.down in keys and Key.left in keys and curr_dir == Direction.LEFT:
            direction = Direction.DOWN
        elif Key.left in keys and Key.up in keys and curr_dir == Direction.LEFT:
            direction = Direction.UP
        elif Key.left in keys and Key.up in keys and curr_dir == Direction.UP:
            direction = Direction.LEFT
        elif Key.up in keys:
            direction = Direction.UP
        elif Key.down in keys:
            direction = Direction.DOWN
        elif Key.left in keys:
            direction = Direction.LEFT
        elif Key.right in keys:
            direction = Direction.RIGHT

        debug(f"Moving snake in direction {direction}")

        # Checks for invalid key presses
        if curr_dir == Direction.UP and direction == Direction.DOWN \
                or curr_dir == Direction.DOWN and direction == Direction.UP \
                or curr_dir == Direction.LEFT and direction == Direction.RIGHT \
                or curr_dir == Direction.RIGHT and direction == Direction.LEFT \
                or direction is None:
            direction = curr_dir

        # Move the snake
        curr.data.move(direction)  # Move the head
        while curr.prev is not None:
            if curr != self.head:
                curr_dir = prev_dir
            prev_dir = curr.prev.data.direction
            curr.prev.data.move(curr_dir)
            curr = curr.prev

    def die(self, seconds=1.0):
        debug("___END____")
        for node in self:
            self.board[node.data.pos[0], node.data.pos[1]] = Empty()
            game.render(board=self.board)
            time.sleep(seconds / self.length)

    def __str__(self):
        output = ""
        for node in self:
            output += str(node) + "\n"
        return output


class Node:
    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next

    def __str__(self):
        return f"{self.data}"


# TODO: Clean all this up. It's a mess.
#  Should have board handle additions, e.g. board.add(Head(), (3, 5))
class Data(ABC):
    """test"""

    def __init__(self, board=None, pos=None, string=None, number=None):
        self.board = board

        if pos is not None:
            self._pos = list(pos)
            self.board[pos[0], pos[1]] = self
            self._prev_pos = [self._pos[0], self._pos[1] - 1]
            self.open_ajacent = self._open_ajacent()

        self.direction = Direction.RIGHT

        # Various representations of the data
        self._string = string
        self._number = number

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = list(pos)

    @property
    def prev_pos(self):
        return list(self._prev_pos)

    @prev_pos.setter
    def prev_pos(self, pos):
        self._prev_pos = list(pos)

    def move(self, direction):
        self.prev_pos = self.pos
        self.direction = direction

        self.board[self.pos[0], self.pos[1]] = Empty()

        if direction == Direction.UP:
            self.pos[0] -= 1
        elif direction == Direction.DOWN:
            self.pos[0] += 1
        elif direction == Direction.LEFT:
            self.pos[1] -= 1
        elif direction == Direction.RIGHT:
            self.pos[1] += 1

        self.board[self.pos[0], self.pos[1]] = self

    def clear(self):
        self.board[self.pos[0], self.pos[1]] = Empty()

    def _open_ajacent(self):
        """
        :return: A list of non-empty spaces around the data in the board. (up, down, left, right).
        """
        posible_positions = [
            (self.pos[0] - 1, self.pos[1]),
            (self.pos[0] + 1, self.pos[1]),
            (self.pos[0], self.pos[1] - 1),
            (self.pos[0], self.pos[1] + 1)
        ]
        moves = [
            pos for pos in posible_positions
            if isinstance(self.board[pos[0], pos[1]], Empty)
        ]
        return moves

    def repr(self, type):
        """
        :param type: "int", "string"
        :return: Various representation of the object
        """
        if type == "int":
            return self._number
        elif type == "string":
            return self._string

    # def __str__(self):
    #     return self.symbol


class Empty(Data):
    def __init__(self):
        super().__init__(
            string=EMPTY,
            number=0
        )


class Border(Data):
    def __init__(self):
        super().__init__(
            string=BORDER,
            number=1
        )


class Head(Data):
    def __init__(self, board=None, pos=None):
        super().__init__(
            board=board,
            pos=pos,
            string=SNAKE,
            number=2
        )


class Body(Data):
    def __init__(self, board=None, pos=None):
        super().__init__(
            board=board,
            pos=pos,
            string=SNAKE,
            number=3
        )


class Apple(Data):
    def __init__(self, board=None, pos=None):
        # self.pos = random.choice(self.board.available_spots())
        # self.board[self.pos[0], self.pos[1]] = self
        if pos is None and board is not None:
            pos = board.rand_available()

        super().__init__(
            board=board,
            pos=pos,
            string=APPLE,
            number=4
        )
