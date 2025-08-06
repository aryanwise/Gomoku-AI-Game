import time
import flask
import gomoku_game
import numpy as np
from flask import request

# Import your agents
import teams.dumb_agent
import teams.daddy_agent
import teams.human_agent

app = flask.Flask(__name__)

# Toggle between Human vs AI and AI vs AI
HUMAN_VS_AGENT = True  # Set to False for Agent vs Agent
AI_TIME_LIMIT = 9.5  # seconds

# Setup agents
if HUMAN_VS_AGENT:
    human_agent = teams.human_agent.GomokuAgent(
        gomoku_game.PLAYER_1_SYMBOL,
        gomoku_game.BLANK_SYMBOL,
        gomoku_game.PLAYER_2_SYMBOL,
    )
    ai_agent = teams.daddy_agent.GomokuAgent(
        board_size=gomoku_game.BOARD_SIZE,
        player=gomoku_game.PLAYER_2_SYMBOL,
        time_limit=AI_TIME_LIMIT,
    )
    p1, p2 = human_agent, ai_agent
else:
    p1 = teams.dumb_agent.GomokuAgent(
        gomoku_game.PLAYER_1_SYMBOL,
        gomoku_game.BLANK_SYMBOL,
        gomoku_game.PLAYER_2_SYMBOL,
    )
    p2 = teams.daddy_agent.GomokuAgent(
        board_size=gomoku_game.BOARD_SIZE,
        player=gomoku_game.PLAYER_2_SYMBOL,
        time_limit=AI_TIME_LIMIT,
    )

game = gomoku_game.GomokuGame(p1, p2)

team_info = {
    "player1": {"name": p1.name, "symbol": "X"},
    "player2": {"name": p2.name, "symbol": "O"},
}


@app.route("/")
def index():
    return flask.render_template("index.html", team_info=team_info)


@app.route("/get_board")
def get_board():
    return flask.jsonify(game.board.tolist())


@app.route("/play_turn")
def play_turn():
    # If human vs agent, check if it's human's turn
    human_turn = False
    winner = game.winner
    if HUMAN_VS_AGENT:
        # Human is p1, so even turns (0,2,4,...)
        human_turn = (game.turn_counter % 2 == 0) and (winner is None)
        # If it's human's turn, do not play agent move, just return board
        if human_turn:
            return flask.jsonify(
                {"board": game.board.tolist(), "winner": None, "human_turn": True}
            )
    # Otherwise, play turn as usual (AI vs AI, or AI turn in Human vs AI)
    board, winner = game.play_turn()
    winner_symbol = winner.agent_symbol if winner else None
    return flask.jsonify(
        {"board": board.tolist(), "winner": winner_symbol, "human_turn": False}
    )


@app.route("/human_move", methods=["POST"])
def human_move():
    if not HUMAN_VS_AGENT:
        return flask.jsonify({"error": "Not in human vs agent mode"}), 400
    data = request.get_json()
    row, col = data.get("row"), data.get("col")
    # Safety: check bounds
    if (
        row is None
        or col is None
        or not (0 <= row < gomoku_game.BOARD_SIZE and 0 <= col < gomoku_game.BOARD_SIZE)
    ):
        return flask.jsonify({"error": "Invalid move"}), 400
    # Set the move for the human agent, then play turn (which will apply this move)
    human_agent.next_move = (row, col)
    # After setting, immediately advance the turn (so the agent can play next)
    board, winner = game.play_turn()
    winner_symbol = winner.agent_symbol if winner else None
    return flask.jsonify({"board": board.tolist(), "winner": winner_symbol})


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
