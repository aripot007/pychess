import abc


class Variant:

    NAME = None
    DESC = None

    @abc.abstractmethod
    def start(self):
        """
        Starts the game. Should be blocking
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """Stops the game."""

    @abc.abstractmethod
    def setup(self):
        """Setup the game (fill the board, creates the players, etc). Called once before `start()`"""
