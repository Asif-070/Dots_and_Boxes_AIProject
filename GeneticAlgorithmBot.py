from Bot import Bot
from GameAction import GameAction
from GameState import GameState
import random
import numpy as np
import time

class GeneticAlgorithmBot(Bot):
    def __init__(self, population_size=50, generations=100, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.is_player1 = True

    def get_action(self, state: GameState) -> GameAction:
        time.sleep(0.25)  # Optional delay for human-like response
        self.is_player1 = state.player1_turn
        population = self.initialize_population(state)

        for generation in range(self.generations):
            fitness_scores = self.evaluate_population(population, state)
            selected_individuals = self.selection(population, fitness_scores)
            new_population = []

            for i in range(0, len(selected_individuals), 2):
                if i + 1 < len(selected_individuals):
                    offspring1, offspring2 = self.crossover(selected_individuals[i], selected_individuals[i + 1])
                    new_population.extend([self.mutation(offspring1, state), self.mutation(offspring2, state)])
                else:
                    new_population.append(self.mutation(selected_individuals[i], state))

            population = new_population
            #print(f"Generation {generation}: Best fitness: {max(fitness_scores)}, Avg fitness: {np.mean(fitness_scores)}")

        best_individual = self.select_best_individual(population, state)

        if not self.is_valid_action(best_individual, state):
            print("Failed to generate a valid action. Selecting a random valid action.")
            valid_actions = self.generate_valid_actions(state)
            best_individual = random.choice(valid_actions)

        print(best_individual)
        return best_individual



    def mutation1(self, individual, state: GameState):
        if random.random() < self.mutation_rate:  # Probability check for mutation
            pos_len = len(individual.position)
            if pos_len > 1:
                start, end = sorted(random.sample(range(pos_len), 2))  # Ensure start < end
                inverted_position = individual.position[:start] + individual.position[start:end + 1][
                                                                  ::-1] + individual.position[end + 1:]
                individual = GameAction(individual.action_type,
                                        inverted_position)
        return individual

    def initialize_population(self, state: GameState):
        valid_actions = self.generate_valid_actions(state)
        population = [random.choice(valid_actions) for _ in range(self.population_size)]
        return population

    def evaluate_population(self, population, state: GameState):
        fitness_scores = []
        for individual in population:
            new_state, _ = self.get_result(state, individual)
            fitness = self.evaluate(new_state)
            fitness_scores.append(fitness)
        return fitness_scores

    def selection(self, population, fitness_scores):
        total_fitness = sum(fitness_scores)
        if total_fitness == 0:
            return random.choices(population, k=self.population_size)
        else:
            probabilities = [score / total_fitness for score in fitness_scores]
            selected = random.choices(population, weights=probabilities, k=self.population_size)
            return selected

    def crossover(self, parent1, parent2):
        if parent1.action_type == parent2.action_type:
            point = random.randint(1, max(1, len(parent1.position) - 1))
            offspring1 = GameAction(parent1.action_type, parent1.position[:point] + parent2.position[point:])
            offspring2 = GameAction(parent2.action_type, parent2.position[:point] + parent1.position[point:])
        else:
            offspring1 = parent1
            offspring2 = parent2
        return offspring1, offspring2

    def select_best_individual(self, population, state: GameState) -> GameAction:
        best_fitness = -np.inf
        best_individual = None
        for individual in population:
            new_state, _ = self.get_result(state, individual)
            fitness = self.evaluate(new_state)
            if fitness > best_fitness:
                best_fitness = fitness
                best_individual = individual
        return best_individual

    def mutation(self, individual, state: GameState):
        if random.random() < self.mutation_rate:
            valid_actions = self.generate_valid_actions(state)
            if valid_actions:
                individual = random.choice(valid_actions)
        return individual
    def generate_valid_actions(self, state: GameState):
        row_positions = self.generate_positions(state.row_status)
        col_positions = self.generate_positions(state.col_status)
        actions = [GameAction("row", pos) for pos in row_positions] + [GameAction("col", pos) for pos in col_positions]
        valid_actions = [action for action in actions if self.is_valid_action(action, state)]
        return valid_actions

    def generate_positions(self, matrix: np.ndarray):
        positions = [(x, y) for y in range(matrix.shape[0]) for x in range(matrix.shape[1]) if matrix[y, x] == 0]
        return positions

    def is_valid_action(self, action: GameAction, state: GameState):
        x, y = action.position
        if action.action_type == "row" and state.row_status[y, x] == 0:
            return True
        if action.action_type == "col" and state.col_status[y, x] == 0:
            return True
        return False

    def get_result(self, state: GameState, action: GameAction):
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

        if 0 <= y < ny and 0 <= x < nx:
            new_state.board_status[y, x] = (abs(new_state.board_status[y, x]) + val) * player_modifier
            if abs(new_state.board_status[y, x]) == 4:
                points_scored += 1

        if type == "row":
            if 0 <= y < new_state.row_status.shape[0] and 0 <= x < new_state.row_status.shape[1]:
                new_state.row_status[y, x] = 1
                if y > 0:
                    if 0 <= y - 1 < new_state.board_status.shape[0] and 0 <= x < new_state.board_status.shape[1]:
                        new_state.board_status[y - 1, x] = (abs(
                            new_state.board_status[y - 1, x]) + val) * player_modifier
                        if abs(new_state.board_status[y - 1, x]) == 4:
                            points_scored += 1
        elif type == "col":
            if 0 <= y < new_state.col_status.shape[0] and 0 <= x < new_state.col_status.shape[1]:
                new_state.col_status[y, x] = 1
                if x > 0:
                    if 0 <= y < new_state.board_status.shape[0] and 0 <= x - 1 < new_state.board_status.shape[1]:
                        new_state.board_status[y, x - 1] = (abs(
                            new_state.board_status[y, x - 1]) + val) * player_modifier
                        if abs(new_state.board_status[y, x - 1]) == 4:
                            points_scored += 1

        new_state = new_state._replace(
            player1_turn=not (new_state.player1_turn ^ (points_scored > 0))
        )
        return new_state, points_scored

    def evaluate(self, state: GameState):
        [ny, nx] = state.board_status.shape
        utility = 0
        high_points_moves = 0

        for y in range(ny):
            for x in range(nx):
                cell_value = state.board_status[y, x]
                if self.is_player1:
                    if cell_value == -4:
                        utility += 1
                    elif cell_value == 4 or abs(cell_value) == 3:
                        utility -= 1
                else:
                    if cell_value == -4 or abs(cell_value) == 3:
                        utility -= 1
                    elif cell_value == 4:
                        utility += 1

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

        return max(1, utility + high_points_moves * 2)

