"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    moves_played = 0
    for row in board:
        for move in row:
            if move != EMPTY:
                moves_played += 1
    if moves_played % 2: return 'O'
    return 'X'


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    for i, row in enumerate(board):
        for j, column in enumerate(row):
            if column == EMPTY:
                possible_moves.add((i, j))
    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check Rows
    for row in board:
        if ((row[0] == row[1] == row[2]) and row[0] != EMPTY):
            # print('row win')
            return row[0]
    # Check Columns
    for column in range(3):
        if ((board[0][column] == board[1][column] == board[2][column]) and board[0][column] != EMPTY):
            # print('column win')
            return board[0][column]
    # Check Diagonals
    if (board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY):
        return board[0][0]
    if (board[2][0] == board[1][1] == board[0][2] and board [2][0] != EMPTY):
        return board[2][0]
    # No Winner
    return None


def terminal(board: list):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if someone is a Winner
    possible_winner = winner(board)
    if possible_winner is not None: return True

    # Check if all spots are taken
    for row in board:
        for column in row:
            if column == EMPTY: return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    terminal_state = winner(board)
    if terminal_state == 'O': return -1
    if terminal_state == 'X': return 1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Get Current Player to Determine min or max
    current_player = player(board)

    # Get the available moves
    available_moves = actions(board)

    # Get The correct move for the players wanted min or max
    max_wanted = False
    if current_player == 'X': max_wanted = True

    # Check initial Move
    best_value = 2 if max_wanted else -2
    best_move = None

    # Test all moves for the best one
    for move in available_moves:
        if max_wanted:
            move_result = min_value(result(board, move), best_value)
            # print('move result', moveResult)
            if (best_value < move_result or best_move is None):
                best_move = move
                best_value = move_result
        else:
            move_result = max_value(result(board, move), best_value)
            if (best_value > move_result or best_move is None):
                best_move = move
                best_value = move_result

    # Return the best move found
    return best_move

def min_value(state, current_max):
    v = 100
    if v <= current_max: return v
    if terminal(state):
        return utility(state)
    for move in actions(state):
        v = min(v, max_value(result(state, move), v))
    return v

def max_value(state, current_min):
    v = -100
    if v >= current_min: return v
    if terminal(state):
        return utility(state)
    for move in actions(state):
        v = max(v, min_value(result(state, move), v))
    return v
