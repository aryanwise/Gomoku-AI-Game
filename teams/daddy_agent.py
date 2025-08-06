import math
import random
import copy
import time


class GomokuAgent:
    def __init__(self, board_size=15, player=1, max_depth=5, time_limit=9.5):
        self.name = __name__
        self.board_size = board_size
        self.player = player  # 1 for black, 2 for white
        self.agent_symbol = player
        self.opponent = 2 if player == 1 else 1
        self.max_depth = max_depth  # Maximum search depth
        self.time_limit = time_limit  # Time limit in seconds (should be <10s)
        self.start_time = None

    def get_move(self, board):
        """Entry point for agent. Returns best move as (x, y) tuple within time limit."""
        self.start_time = time.time()
        best_move = None
        best_score = -math.inf

        # Iterative deepening
        for depth in range(1, self.max_depth + 1):
            score, move = self.alpha_beta(board, depth, -math.inf, math.inf, True)
            if time.time() - self.start_time > self.time_limit:
                break
            if move is not None:
                best_move = move
                best_score = score
        # Fallback: play center if no move found (shouldn't happen)
        if best_move is None:
            best_move = (self.board_size // 2, self.board_size // 2)
        return best_move

    def alpha_beta(self, board, depth, alpha, beta, maximizingPlayer):
        """Alpha-beta pruning search with time check."""
        if time.time() - self.start_time > self.time_limit:
            return self.evaluate(board), None
        if self.is_terminal(board) or depth == 0:
            return self.evaluate(board), None

        legal_moves = self.generate_moves(board)
        if not legal_moves:
            return self.evaluate(board), None

        best_move = None
        if maximizingPlayer:
            max_eval = -math.inf
            for move in legal_moves:
                new_board = self.make_move(board, move, self.player)
                eval, _ = self.alpha_beta(new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                if time.time() - self.start_time > self.time_limit:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in legal_moves:
                new_board = self.make_move(board, move, self.opponent)
                eval, _ = self.alpha_beta(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                if time.time() - self.start_time > self.time_limit:
                    break
            return min_eval, best_move

    def is_terminal(self, board):
        return self.check_win(board, self.player) or self.check_win(
            board, self.opponent
        )

    def generate_moves(self, board):
        """Generate moves near stones (threat space search)."""
        moves = set()
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] != 0:
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < self.board_size
                            and 0 <= ny < self.board_size
                            and board[nx][ny] == 0
                        ):
                            moves.add((nx, ny))
        # If board is empty, play center
        if not moves:
            moves.add((self.board_size // 2, self.board_size // 2))
        return list(moves)

    def make_move(self, board, move, player):
        """Returns a new board with the move applied."""
        new_board = copy.deepcopy(board)
        x, y = move
        new_board[x][y] = player
        return new_board

    def evaluate(self, board):
        """Heuristic board evaluation using threats and patterns."""
        patterns = [
            (100000, self.player, [1, 1, 1, 1, 1]),  # Five in a row
            (10000, self.player, [0, 1, 1, 1, 1, 0]),  # Open four
            (5000, self.player, [1, 1, 1, 1, 0]),  # Four with one empty
            (1000, self.player, [0, 1, 1, 1, 0]),  # Open three
            (500, self.player, [1, 1, 1, 0, 0]),  # Three with two empty
            (100, self.player, [0, 1, 1, 0, 0]),  # Open two
        ]
        score = 0
        for val, who, pattern in patterns:
            score += val * self.count_pattern(board, who, pattern)
        # Opponent patterns: penalize
        for val, who, pattern in patterns:
            score -= (val // 2) * self.count_pattern(board, self.opponent, pattern)
        return score + random.uniform(-0.05, 0.05)  # Small randomness for move variety

    def count_pattern(self, board, player, pattern):
        """Count occurrences of a pattern for given player."""
        count = 0
        plen = len(pattern)
        # Horizontal, vertical, diagonal (/), diagonal (\)
        for x in range(self.board_size):
            for y in range(self.board_size):
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    px, py = x, y
                    match = True
                    for i in range(plen):
                        if 0 <= px < self.board_size and 0 <= py < self.board_size:
                            val = board[px][py]
                            # pattern: 1 = player, 0 = empty
                            if pattern[i] == 1 and val != player:
                                match = False
                                break
                            elif pattern[i] == 0 and val != 0:
                                match = False
                                break
                        else:
                            match = False
                            break
                        px += dx
                        py += dy
                    if match:
                        count += 1
        return count

    def check_win(self, board, player):
        """Check if player has five in a row."""
        for x in range(self.board_size):
            for y in range(self.board_size):
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    cnt = 0
                    px, py = x, y
                    for i in range(5):
                        if 0 <= px < self.board_size and 0 <= py < self.board_size:
                            if board[px][py] == player:
                                cnt += 1
                            else:
                                break
                        else:
                            break
                        px += dx
                        py += dy
                    if cnt == 5:
                        return True
        return False

    def play(self, board):
        return self.get_move(board)


# Example usage (for your game env):
# agent = GomokuAgent(board_size=15, player=1, max_depth=5, time_limit=9.5)
# move = agent.get_move(current_board)  # current_board: 2D list, 0-empty, 1-black, 2-white
