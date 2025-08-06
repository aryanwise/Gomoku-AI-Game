import time


class GomokuAgent:
    def __init__(self, agent_symbol, blank_symbol, opponent_symbol):
        self.agent_symbol = agent_symbol
        self.blank_symbol = blank_symbol
        self.opponent_symbol = opponent_symbol
        self.name = "Human Player"
        self.next_move = None

    def play(self, board):
        # Wait (with sleep) for the Flask route to set self.next_move
        while self.next_move is None:
            time.sleep(0.1)  # Sleep instead of busy wait
        move = self.next_move
        self.next_move = None
        return move
