import sys
import termios
import time
import tty
from logging import debug, info, warning, error, critical

from pynput.keyboard import Key, Listener
import atexit


class KeyLog:
    """
    A class to wrap the pynput keyboard listener.

    This class is used to start a non-blocking listener on a separate thread.

    It also sets the terminal to 'cbreak' mode so that it doesn't echo key presses.
    Resets the terminal to its original mode when the listener is stopped. Or the program ends.
    """

    def __init__(self):
        info("Initializing KeyLog")
        self.key = None  # The last key pressed
        info("Initializing listener")

        # Saves file descriptors to be able to reset the terminal to its original mode
        self.original_descriptors = termios.tcgetattr(sys.stdin)
        # Stops the terminal from echoing input
        tty.setcbreak(sys.stdin)

        # Start non-blocking listener on another thread
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        # Ensures that the listener is cleaned up properly
        atexit.register(self.__del__)

    def get_key(self):
        return self.key

    def get_keys(self, resolution=0.001, period=0.1):
        """
        Returns a list of keys pressed since the last call to this function.
        """
        keys = []
        start_time = time.time()
        while time.time() - start_time < period:
            keys.append(self.key)
            time.sleep(resolution)
        return keys

    def on_press(self, key):
        self.key = key


    def on_release(self, key):
        self.key = None
        if key == Key.esc:
            # Stop listener
            print("ending")
            return False

    def __del__(self):
        info("Ending listener safely")
        self.listener.stop()

        # Resets the terminal to its original mode
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_descriptors)
