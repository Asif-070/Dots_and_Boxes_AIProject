from Bot import Bot
from GameAction import GameAction
from GameState import GameState
from typing import List, Tuple
import numpy as np
import time

class MinimaxBot(Bot):
    def __init__(self, depth: int = 4) -> None:
        self.depth = depth
        self.is_player1 = True

    def get_action(self, state: GameState) -> GameAction:
        time.sleep(0.5)
        self.is_player1 = state.player1_turn
        _, best_actions = self.minimax(state, self.depth, -np.inf, np.inf, self.is_player1)
        return best_actions[0] if best_actions else None

    def minimax(self, state: GameState, depth: int, alpha: float, beta: float, is_maximizing: bool) -> Tuple[float, List[GameAction]]:
        if depth == 0 or self.is_terminal(state):
            return self.evaluate(state), []

        actions = self.generate_actions(state)
        best_actions = []

        if is_maximizing:
            max_eval = -np.inf
            for action in actions:
                new_state, points_scored = self.get_result(state, action)
                eval, _ = self.minimax(new_state, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_actions = [action]
                elif eval == max_eval:
                    best_actions.append(action)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_actions
        else:
            min_eval = np.inf
            for action in actions:
                new_state, points_scored = self.get_result(state, action)
                eval, _ = self.minimax(new_state, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_actions = [action]
                elif eval == min_eval:
                    best_actions.append(action)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_actions

    def generate_actions(self, state: GameState) -> List[GameAction]:
        row_positions = self.generate_positions(state.row_status)
        col_positions = self.generate_positions(state.col_status)
        actions: List[GameAction] = []

        for position in row_positions:
            actions.append(GameAction("row", position))
        for position in col_positions:
            actions.append(GameAction("col", position))

        return actions

    def generate_positions(self, matrix: np.ndarray) -> List[Tuple[int, int]]:
        positions: List[Tuple[int, int]] = [(x, y) for y in range(matrix.shape[0]) for x in range(matrix.shape[1]) if
                                            matrix[y, x] == 0]
        return positions

    def get_result(self, state: GameState, action: GameAction) -> Tuple[GameState, int]:
        type = action.action_type
        x, y = action.position

        new_state = GameState(
            state.board_status.copy(),
            state.row_status.copy(),
            state.col_status.copy(),
            state.player1_turn,
        )
        player_modifier = -1 if new_state.player1_turn else 1
        points_scored = 0
        val = 1

        [ny, nx] = new_state.board_status.shape

        if y < ny and x < nx:
            new_state.board_status[y, x] = (
                                                   abs(new_state.board_status[y, x]) + val
                                           ) * player_modifier
            if abs(new_state.board_status[y, x]) == 4:
                points_scored += 1

        if type == "row":
            new_state.row_status[y, x] = 1
            if y > 0:
                new_state.board_status[y - 1, x] = (
                                                           abs(new_state.board_status[y - 1, x]) + val
                                                   ) * player_modifier
                if abs(new_state.board_status[y - 1, x]) == 4:
                    points_scored += 1
        elif type == "col":
            new_state.col_status[y, x] = 1
            if x > 0:
                new_state.board_status[y, x - 1] = (
                                                           abs(new_state.board_status[y, x - 1]) + val
                                                   ) * player_modifier
                if abs(new_state.board_status[y, x - 1]) == 4:
                    points_scored += 1

        new_state = new_state._replace(
            player1_turn=not (new_state.player1_turn ^ (points_scored > 0))
        )
        return new_state, points_scored

    def evaluate(self, state: GameState) -> float:
        [ny, nx] = state.board_status.shape
        utility = 0
        high_points_moves = 0

        for y in range(ny):
            for x in range(nx):
                if self.is_player1:
                    if state.board_status[y, x] == -4:
                        utility += 1
                    elif state.board_status[y, x] == 4 or abs(state.board_status[y, x]) == 3:
                        utility -= 1
                else:
                    if state.board_status[y, x] == -4 or abs(state.board_status[y, x]) == 3:
                        utility -= 1
                    elif state.board_status[y, x] == 4:
                        utility += 1

        # Additional utility for high point-scoring moves
        for y in range(ny):
            for x in range(nx):
                if abs(state.board_status[y, x]) == 3:
                    if state.player1_turn:
                        if self.is_player1:
                            high_points_moves += 1
                        else:
                            high_points_moves -= 1
                    else:
                        if self.is_player1:
                            high_points_moves -= 1
                        else:
                            high_points_moves += 1

        return utility + high_points_moves * 2

    def is_terminal(self, state: GameState) -> bool:
        return (state.row_status == 1).all() and (state.col_status == 1).all()
