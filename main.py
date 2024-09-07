from tkinter import *  #GUI
import numpy as np  #Array & Matrix
from Bot import Bot
from typing import Optional
from GameState import GameState
from MinimaxBot import MinimaxBot
from GeneticAlgorithmBot import GeneticAlgorithmBot
import pygame  #Sound

pygame.mixer.init()

# Load sounds
click_sound = pygame.mixer.Sound('sound/click.mp3')
win_sound = pygame.mixer.Sound('sound/win.mp3')
lose_sound = pygame.mixer.Sound('sound/lose.mp3')
score_sound = pygame.mixer.Sound('sound/score.mp3')

#Tkinter Config
size_of_board = 700
number_of_dots = 6
symbol_size = (size_of_board / 3 - size_of_board / 8) / 2
symbol_thickness = 50
dot_color = "#7BC043"
player1_color = "#0492CF"
player1_color_light = "#67B0CF"
player2_color = "#EE4035"
player2_color_light = "#EE7E77"
Green_color = "#7BC043"
dot_width = 0.25 * size_of_board / number_of_dots
edge_width = 0.1 * size_of_board / number_of_dots
distance_between_dots = size_of_board / number_of_dots
move1 = 0
move2 = 0
streak1 = 0
streak2 = 0
highest_streak1 = 0
highest_streak2 = 0

LEFT_CLICK = "<Button-1>"

class Dots_and_Boxes:
    def __init__(self, bot1: Optional[Bot] = None, bot2: Optional[Bot] = None):
        self.window = Tk()
        #self.window.attributes("-fullscreen", True)
        self.window.title("Dots_and_Boxes")
        self.canvas = Canvas(
            self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()
        self.player1_starts = True
        self.refresh_board()

        self.bot1 = bot1
        self.bot2 = bot2
        self.create_main_menu()

    def play_again(self):
        self.refresh_board()
        self.board_status = np.zeros(
            shape=(number_of_dots - 1, number_of_dots - 1))
        self.row_status = np.zeros(shape=(number_of_dots, number_of_dots - 1))
        self.col_status = np.zeros(shape=(number_of_dots - 1, number_of_dots))
        self.pointsScored = False

        # Reset the move counters
        global move1, move2, streak1, streak2, highest_streak1, highest_streak2
        move1 = 0
        move2 = 0
        streak1 = 0
        streak2 = 0
        highest_streak1 = 0
        highest_streak2 = 0

        # Input from user in form of clicks
        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = []

        self.already_marked_boxes = []
        self.display_turn_text()

        self.turn()

    def create_main_menu(self):
        self.clear_window()
        self.canvas.create_text(
            size_of_board / 2,
            size_of_board / 4,
            font="cmr 60 bold",
            fill=Green_color,
            text="Dots and Boxes",
        )

        single_player_button = Button(
            self.window, text="Play", font="cmr 30 bold", command=self.display_grid_size_menu)
        self.canvas.create_window(
            size_of_board / 2, size_of_board / 2, window=single_player_button)

        exit_button = Button(
            self.window, text="Exit", font="cmr 30 bold", command=self.window.destroy)
        self.canvas.create_window(
            size_of_board / 2, size_of_board / 1.5, window=exit_button)

    def display_grid_size_menu(self):
        click_sound.play()
        self.clear_window()
        self.canvas.create_text(
            size_of_board / 2,
            size_of_board / 6,
            font="cmr 40 bold",
            fill=Green_color,
            text="Select Grid Size",
        )

        size4_button = Button(
            self.window, text="Easy", font="cmr 30 bold", command=lambda: self.start_single_player(5, "e"))
        self.canvas.create_window(
            size_of_board / 2, size_of_board / 2.5, window=size4_button)

        size8_button = Button(
            self.window, text="Moderate", font="cmr 30 bold", command=lambda: self.start_single_player(5, "g"))
        self.canvas.create_window(
            size_of_board / 2, size_of_board / 1.8, window=size8_button)

        back_button = Button(
            self.window, text="Back", font="cmr 30 bold", command=self.back)
        self.canvas.create_window(
            size_of_board / 2, size_of_board / 1.2, window=back_button)

    def back(self):
        click_sound.play()
        self.bot2 = MinimaxBot()
        self.create_main_menu()
    def start_single_player(self, dots, bot):
        click_sound.play()
        global number_of_dots, distance_between_dots, dot_width, edge_width
        number_of_dots = dots
        distance_between_dots = size_of_board / number_of_dots
        dot_width = 0.25 * size_of_board / number_of_dots
        edge_width = 0.1 * size_of_board / number_of_dots

        if bot == 'e':
            self.bot2 = MinimaxBot()
        elif bot == 'g':
            self.bot2 = GeneticAlgorithmBot()

        self.clear_window()
        self.play_again()
    def mainloop(self):
        self.window.mainloop()

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        self.canvas = Canvas(
            self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()

    def is_grid_occupied(self, logical_position, type):
        x = logical_position[0]
        y = logical_position[1]
        occupied = True

        if type == "row" and self.row_status[y][x] == 0:
            occupied = False
        if type == "col" and self.col_status[y][x] == 0:
            occupied = False

        return occupied

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position - distance_between_dots / 4) // (
            distance_between_dots / 2
        )

        type = False
        logical_position = []
        if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0:
            x = int((position[0] - 1) // 2)
            y = int(position[1] // 2)
            logical_position = [x, y]
            type = "row"
            # self.row_status[c][r]=1
        elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0:
            y = int((position[1] - 1) // 2)
            x = int(position[0] // 2)
            logical_position = [x, y]
            type = "col"

        return logical_position, type

    def pointScored(self):
        global streak1, streak2, highest_streak1, highest_streak2
        if self.player1_turn:
            streak1 += 1
            streak2 = 0
            if streak1 > highest_streak1:
                highest_streak1 = streak1
        else:
            streak2 += 1
            streak1 = 0
            if streak2 > highest_streak2:
                highest_streak2 = streak2

        if self.is_gameover():
            pass
        else:
            score_sound.play()
        self.pointsScored = True

    def mark_box(self):
        boxes = np.argwhere(self.board_status == -4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = player1_color_light
                self.shade_box(box, color)

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = player2_color_light
                self.shade_box(box, color)

    def update_board(self, type, logical_position):
        x = logical_position[0]
        y = logical_position[1]
        val = 1
        playerModifier = 1
        if self.player1_turn:
            playerModifier = -1

        if y < (number_of_dots - 1) and x < (number_of_dots - 1):
            self.board_status[y][x] = (
                abs(self.board_status[y][x]) + val
            ) * playerModifier
            if abs(self.board_status[y][x]) == 4:
                self.pointScored()

        if type == "row":
            self.row_status[y][x] = 1
            if y >= 1:
                self.board_status[y - 1][x] = (
                    abs(self.board_status[y - 1][x]) + val
                ) * playerModifier
                if abs(self.board_status[y - 1][x]) == 4:
                    self.pointScored()

        elif type == "col":
            self.col_status[y][x] = 1
            if x >= 1:
                self.board_status[y][x - 1] = (
                    abs(self.board_status[y][x - 1]) + val
                ) * playerModifier
                if abs(self.board_status[y][x - 1]) == 4:
                    self.pointScored()

    def is_gameover(self):
        return (self.row_status == 1).all() and (self.col_status == 1).all()

    # ------------------------------------------------------------------
    # Drawing Functions
    # ------------------------------------------------------------------

    def make_edge(self, type, logical_position):
        if type == "row":
            start_x = (
                distance_between_dots / 2 +
                logical_position[0] * distance_between_dots
            )
            end_x = start_x + distance_between_dots
            start_y = (
                distance_between_dots / 2 +
                logical_position[1] * distance_between_dots
            )
            end_y = start_y
        elif type == "col":
            start_y = (
                distance_between_dots / 2 +
                logical_position[1] * distance_between_dots
            )
            end_y = start_y + distance_between_dots
            start_x = (
                distance_between_dots / 2 +
                logical_position[0] * distance_between_dots
            )
            end_x = start_x

        global streak1, streak2
        if self.player1_turn:
            color = player1_color
            streak1 = 0
            streak2 = 0
        else:
            color = player2_color
            streak1 = 0
            streak2 = 0
        self.canvas.create_line(
            start_x, start_y, end_x, end_y, fill=color, width=edge_width
        )

    def display_gameover(self):
        player1_score = len(np.argwhere(self.board_status == -4))
        player2_score = len(np.argwhere(self.board_status == 4))

        if player1_score > player2_score:
            text = "Winner: Player 1 "
            color = player1_color
        elif player2_score > player1_score:
            text = "Winner: Player 2 "
            color = player2_color
        else:
            text = "It's a tie"
            color = "gray"

        self.canvas.delete("all")
        self.canvas.create_text(
            size_of_board / 2,
            size_of_board / 4,
            font="cmr 60 bold",
            fill=color,
            text=text,
        )

        score_text = "Scores\n"
        self.canvas.create_text(
            size_of_board / 2,
            5 * size_of_board / 8,
            font="cmr 40 bold",
            fill=Green_color,
            text=score_text,
        )

        score_text = "Player 1 : " + str(player1_score) + "\n"
        score_text += "Player 2 : " + str(player2_score) + "\n"
        self.canvas.create_text(
            size_of_board / 2,
            3 * size_of_board / 4,
            font="cmr 30 bold",
            fill=Green_color,
            text=score_text,
        )
        global move1, move2
        self.reset_board = True
        if player1_score > player2_score:
            win_sound.play()
        else:
            lose_sound.play()

        # Create buttons for "Play Again" and "Exit"
        self.play_again_button = Button(self.window, text="Play Again", font="cmr 20 bold", command=self.refresh)
        self.exit_button = Button(self.window, text="Exit", font="cmr 20 bold", command=self.back)

        # Place the buttons at the bottom of the canvas
        self.canvas.create_window(size_of_board / 2 - 100, size_of_board - 100, window=self.play_again_button)
        self.canvas.create_window(size_of_board / 2 + 100, size_of_board - 100, window=self.exit_button)

        # Call fuzzy function and print result
        winning_rate = self.fuzzy_logic(player1_score, player2_score, move1, move2)

        print(winning_rate)
        str1 = " "
        if winning_rate <= 30:
            str1 = "Can be improved"
        elif winning_rate <= 70:
            str1 = "It was a Close game"
        else:
            str1 = "You're a Clear Winner"

        if player1_score == player2_score:
            str1 = "It was a Close game"

        self.canvas.create_text(
            size_of_board / 2,
            5 * size_of_board / 10,
            font="cmr 20 bold",
            fill=Green_color,
            text=str1,
        )

    def fuzzy_logic(self, player1_score, player2_score, move1, move2):
        # Fuzzify inputs
        score_diff_fuzzy = self.fuzzify_score_diff(player1_score - player2_score)
        move_diff_fuzzy = self.fuzzify_move_diff(move1 - move2)

        # Apply rules
        fuzzy_winning_rate = self.apply_rules(score_diff_fuzzy, move_diff_fuzzy)

        # Defuzzify to get crisp winning rate
        calculated_winning_rate = self.defuzzify(fuzzy_winning_rate)
        return calculated_winning_rate

    # Define membership functions
    def fuzzify_score_diff(self, score_diff):
        if score_diff <= -10:
            return {'negative': 1.0, 'zero': 0.0, 'positive': 0.0}
        elif score_diff <= 0:
            return {'negative': (-score_diff / 10.0), 'zero': (score_diff + 10) / 10.0, 'positive': 0.0}
        elif score_diff <= 10:
            return {'negative': 0.0, 'zero': (10 - score_diff) / 10.0, 'positive': score_diff / 10.0}
        else:
            return {'negative': 0.0, 'zero': 0.0, 'positive': 1.0}

    def fuzzify_move_diff(self, move_diff):
        if move_diff <= -5:
            return {'negative': 1.0, 'zero': 0.0, 'positive': 0.0}
        elif move_diff <= 0:
            return {'negative': (-move_diff / 5.0), 'zero': (move_diff + 5) / 5.0, 'positive': 0.0}
        elif move_diff <= 5:
            return {'negative': 0.0, 'zero': (5 - move_diff) / 5.0, 'positive': move_diff / 5.0}
        else:
            return {'negative': 0.0, 'zero': 0.0, 'positive': 1.0}

    def apply_rules(self, score_diff_fuzzy, move_diff_fuzzy):
        rule_results = []

        # Apply each rule and get the minimum membership value for each rule
        rule_results.append(min(score_diff_fuzzy['positive'], move_diff_fuzzy['negative']))
        rule_results.append(min(score_diff_fuzzy['positive'], move_diff_fuzzy['zero']))
        rule_results.append(min(score_diff_fuzzy['positive'], move_diff_fuzzy['positive']))

        rule_results.append(min(score_diff_fuzzy['zero'], move_diff_fuzzy['negative']))
        rule_results.append(min(score_diff_fuzzy['zero'], move_diff_fuzzy['zero']))
        rule_results.append(min(score_diff_fuzzy['zero'], move_diff_fuzzy['positive']))

        rule_results.append(min(score_diff_fuzzy['negative'], move_diff_fuzzy['negative']))
        rule_results.append(min(score_diff_fuzzy['negative'], move_diff_fuzzy['zero']))
        rule_results.append(min(score_diff_fuzzy['negative'], move_diff_fuzzy['positive']))

        # Aggregate rule results into fuzzy output for winning rate
        fuzzy_winning_rate = {'low': 0, 'medium': 0, 'high': 0}

        for result in rule_results:
            if result > 0.5:
                fuzzy_winning_rate['high'] = max(fuzzy_winning_rate['high'], result)
            elif result > 0.25:
                fuzzy_winning_rate['medium'] = max(fuzzy_winning_rate['medium'], result)
            else:
                fuzzy_winning_rate['low'] = max(fuzzy_winning_rate['low'], result)

        return fuzzy_winning_rate

    def defuzzify(self, fuzzy_winning_rate):
        numerator = (fuzzy_winning_rate['low'] * 25 +
                     fuzzy_winning_rate['medium'] * 50 +
                     fuzzy_winning_rate['high'] * 75)
        denominator = (fuzzy_winning_rate['low'] +
                       fuzzy_winning_rate['medium'] +
                       fuzzy_winning_rate['high'])
        if denominator == 0:
            return 50  # default value
        return numerator / denominator

    def refresh(self):
        click_sound.play()
        self.clear_window()
        self.play_again()
    def refresh_board(self):
        for i in range(number_of_dots):
            x = i * distance_between_dots + distance_between_dots / 2
            self.canvas.create_line(
                x,
                distance_between_dots / 2,
                x,
                size_of_board - distance_between_dots / 2,
                fill="gray",
                dash=(2, 2),
            )
            self.canvas.create_line(
                distance_between_dots / 2,
                x,
                size_of_board - distance_between_dots / 2,
                x,
                fill="gray",
                dash=(2, 2),
            )

        for i in range(number_of_dots):
            for j in range(number_of_dots):
                start_x = i * distance_between_dots + distance_between_dots / 2
                end_x = j * distance_between_dots + distance_between_dots / 2
                self.canvas.create_oval(
                    start_x - dot_width / 2,
                    end_x - dot_width / 2,
                    start_x + dot_width / 2,
                    end_x + dot_width / 2,
                    fill=dot_color,
                    outline=dot_color,
                )

    def display_turn_text(self):
        text = "Next turn: "
        if self.player1_turn:
            text += "Player1"
            color = player1_color
        else:
            text += "Player2"
            color = player2_color

        self.canvas.delete(self.turntext_handle)
        self.turntext_handle = self.canvas.create_text(
            size_of_board - 5 * len(text),
            size_of_board - distance_between_dots / 8,
            font="cmr 15 bold",
            text=text,
            fill=color,
        )

    def shade_box(self, box, color):
        start_x = (
            distance_between_dots / 2 + box[1] *
            distance_between_dots + edge_width / 2
        )
        start_y = (
            distance_between_dots / 2 + box[0] *
            distance_between_dots + edge_width / 2
        )
        end_x = start_x + distance_between_dots - edge_width
        end_y = start_y + distance_between_dots - edge_width
        self.canvas.create_rectangle(
            start_x, start_y, end_x, end_y, fill=color, outline=""
        )

    def display_turn_text(self):
        text = "Next turn: "
        if self.player1_turn:
            text += "Player1"
            color = player1_color
        else:
            text += "Player2"
            color = player2_color

        self.canvas.delete(self.turntext_handle)
        self.turntext_handle = self.canvas.create_text(
            size_of_board - 5 * len(text),
            size_of_board - distance_between_dots / 8,
            font="cmr 15 bold",
            text=text,
            fill=color,
        )

    def click(self, event):
        if not self.reset_board:
            grid_position = [event.x, event.y]
            logical_position, valid_input = self.convert_grid_to_logical_position(
                grid_position
            )
            self.update(valid_input, logical_position)
        else:
            self.canvas.delete("all")
            self.play_again()
            self.reset_board = False

    def update(self, valid_input, logical_position):
        if valid_input and not self.is_grid_occupied(logical_position, valid_input):
            self.window.unbind(LEFT_CLICK)
            self.update_board(valid_input, logical_position)
            self.make_edge(valid_input, logical_position)
            self.mark_box()
            self.refresh_board()
            self.player1_turn = (
                not self.player1_turn if not self.pointsScored else self.player1_turn
            )
            self.pointsScored = False

            if self.is_gameover():
                self.display_gameover()
            else:
                self.display_turn_text()
                self.turn()

    def turn(self):
        current_bot = self.bot1 if self.player1_turn else self.bot2
        if current_bot is None:
            self.window.bind(LEFT_CLICK, self.click)
        else:
            self.window.after(100, self.bot_turn, current_bot)

    def bot_turn(self, bot: Bot):
        action = bot.get_action(
            GameState(
                self.board_status.copy(),
                self.row_status.copy(),
                self.col_status.copy(),
                self.player1_turn,
            )
        )
        self.update(action.action_type, action.position)


if __name__ == "__main__":
    game_instance = Dots_and_Boxes(
        None,
        MinimaxBot()
        #GeneticAlgorithmBot()
    )
    game_instance.mainloop()
