from __future__ import print_function
import tkinter as tk
import tkinter.messagebox as messagebox
import sys
import random
import copy
import time


class Grid:
    def __init__(self, n):
        self.size = n
        self.cells = self.generate_empty_grid()
        self.compressed = False
        self.merged = False
        self.moved = False
        self.current_score = 0

    def random_cell(self):
        cell = random.choice(self.retrieve_empty_cells())
        i, j = cell
        self.cells[i][j] = 2 if random.random() < 0.9 else 4

    def retrieve_empty_cells(self):
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.cells[i][j] == 0]

    def generate_empty_grid(self):
        return [[0] * self.size for _ in range(self.size)]

    def transpose(self):
        self.cells = [list(row) for row in zip(*self.cells)]

    def reverse(self):
        for i in range(self.size):
            self.cells[i].reverse()

    def clear_flags(self):
        self.compressed = False
        self.merged = False
        self.moved = False

    def left_compress(self):
        self.compressed = False
        new_grid = self.generate_empty_grid()
        for i in range(self.size):
            count = 0
            for j in range(self.size):
                if self.cells[i][j] != 0:
                    new_grid[i][count] = self.cells[i][j]
                    if count != j:
                        self.compressed = True
                    count += 1
        self.cells = new_grid

    def left_merge(self):
        self.merged = False
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.cells[i][j] == self.cells[i][j + 1] and self.cells[i][j] != 0:
                    self.cells[i][j] *= 2
                    self.cells[i][j + 1] = 0
                    self.current_score += self.cells[i][j]
                    self.merged = True

    def found_2048(self):
        return any(cell >= 2048 for row in self.cells for cell in row)

    def has_empty_cells(self):
        return any(cell == 0 for row in self.cells for cell in row)

    def can_merge(self):
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.cells[i][j] == self.cells[i][j + 1]:
                    return True
        for j in range(self.size):
            for i in range(self.size - 1):
                if self.cells[i][j] == self.cells[i + 1][j]:
                    return True
        return False


class AI:
    def __init__(self, grid):
        self.grid = grid

    def get_best_move(self, depth=3):
        moves = ['up', 'down', 'left', 'right']
        best_score = -float('inf')
        best_move = None

        for move in moves:
            grid_copy = copy.deepcopy(self.grid)
            if self.simulate_move(grid_copy, move):
                score = self.expectimax(grid_copy, depth, False)
                if score > best_score:
                    best_score = score
                    best_move = move

        return best_move

    def expectimax(self, grid, depth, is_ai_turn):
        if depth == 0 or not grid.has_empty_cells() and not grid.can_merge():
            return self.evaluate_grid(grid)

        if is_ai_turn:
            best_score = -float('inf')
            for move in ['up', 'down', 'left', 'right']:
                grid_copy = copy.deepcopy(grid)
                if self.simulate_move(grid_copy, move):
                    score = self.expectimax(grid_copy, depth - 1, False)
                    best_score = max(best_score, score)
            return best_score
        else:
            scores = []
            for cell in grid.retrieve_empty_cells():
                for value in [2, 4]:
                    grid_copy = copy.deepcopy(grid)
                    grid_copy.cells[cell[0]][cell[1]] = value
                    scores.append(self.expectimax(grid_copy, depth - 1, True))
            return sum(scores) / len(scores) if scores else 0

    def simulate_move(self, grid, move):
        moved = False
        if move == 'up':
            grid.transpose()
            grid.left_compress()
            grid.left_merge()
            moved = grid.compressed or grid.merged
            grid.left_compress()
            grid.transpose()
        elif move == 'down':
            grid.transpose()
            grid.reverse()
            grid.left_compress()
            grid.left_merge()
            moved = grid.compressed or grid.merged
            grid.left_compress()
            grid.reverse()
            grid.transpose()
        elif move == 'left':
            grid.left_compress()
            grid.left_merge()
            moved = grid.compressed or grid.merged
            grid.left_compress()
        elif move == 'right':
            grid.reverse()
            grid.left_compress()
            grid.left_merge()
            moved = grid.compressed or grid.merged
            grid.left_compress()
            grid.reverse()
        return moved

    def evaluate_grid(self, grid):
        score = 0
        empty_cells = len(grid.retrieve_empty_cells())
        max_tile = max(max(row) for row in grid.cells)
        score += empty_cells * 10

        corners = [grid.cells[0][0], grid.cells[0][grid.size - 1],
                   grid.cells[grid.size - 1][0], grid.cells[grid.size - 1][grid.size - 1]]
        score += max_tile * (2 if max_tile in corners else 1)

        for row in grid.cells:
            score += self.evaluate_monotonicity(row)
        for col in zip(*grid.cells):
            score += self.evaluate_monotonicity(col)

        return score

    def evaluate_monotonicity(self, line):
        monotonic_increasing = all(line[i] <= line[i + 1] for i in range(len(line) - 1))
        monotonic_decreasing = all(line[i] >= line[i + 1] for i in range(len(line) - 1))
        return 10 if monotonic_increasing or monotonic_decreasing else 0


class Game:
    def __init__(self, grid, panel):
        self.grid = grid
        self.panel = panel
        self.ai = AI(self.grid)
        self.start_cells_num = 2
        self.over = False
        self.won = False
        self.keep_playing = False

    def is_game_terminated(self):
        return self.over or (self.won and not self.keep_playing)

    def start(self, auto_play=False):
        self.add_start_cells()
        self.panel.paint()
        if auto_play:
            self.auto_play()
        else:
            self.panel.root.bind('<Key>', self.key_handler)
            self.panel.root.mainloop()

    def add_start_cells(self):
        for _ in range(self.start_cells_num):
            self.grid.random_cell()

    def can_move(self):
        return self.grid.has_empty_cells() or self.grid.can_merge()

    def auto_play(self):
        while not self.is_game_terminated():
            self.ai_move()
            self.panel.root.update_idletasks()
            self.panel.root.update()
            self.panel.paint()
            time.sleep(0.3)

    def ai_move(self):
        if not self.is_game_terminated():
            best_move = self.ai.get_best_move()
            print(f"AI chose: {best_move}")
            if best_move == 'up':
                self.up()
            elif best_move == 'down':
                self.down()
            elif best_move == 'left':
                self.left()
            elif best_move == 'right':
                self.right()
            if self.grid.moved:
                self.grid.random_cell()
            if not self.can_move():
                self.over = True
                self.game_over()

    def key_handler(self, event):
        if self.is_game_terminated():
            return

        key_value = event.keysym
        if key_value == 'AI':
            self.auto_play()
            return

        self.grid.clear_flags()
        if key_value in GamePanel.UP_KEYS:
            self.up()
        elif key_value in GamePanel.LEFT_KEYS:
            self.left()
        elif key_value in GamePanel.DOWN_KEYS:
            self.down()
        elif key_value in GamePanel.RIGHT_KEYS:
            self.right()

        self.panel.paint()
        if self.grid.found_2048():
            self.you_win()
            if not self.keep_playing:
                return

        if self.grid.moved:
            self.grid.random_cell()

        self.panel.paint()
        if not self.can_move():
            self.over = True
            self.game_over()

    def you_win(self):
        if not self.won:
            self.won = True
            if messagebox.askyesno('2048', 'You Win!\nKeep playing?'):
                self.keep_playing = True

    def game_over(self):
        messagebox.showinfo('2048', 'Game over!')

    def up(self):
        self.grid.transpose()
        self.grid.left_compress()
        self.grid.left_merge()
        self.grid.moved = self.grid.compressed or self.grid.merged
        self.grid.left_compress()
        self.grid.transpose()

    def left(self):
        self.grid.left_compress()
        self.grid.left_merge()
        self.grid.moved = self.grid.compressed or self.grid.merged
        self.grid.left_compress()

    def down(self):
        self.grid.transpose()
        self.grid.reverse()
        self.grid.left_compress()
        self.grid.left_merge()
        self.grid.moved = self.grid.compressed or self.grid.merged
        self.grid.left_compress()
        self.grid.reverse()
        self.grid.transpose()

    def right(self):
        self.grid.reverse()
        self.grid.left_compress()
        self.grid.left_merge()
        self.grid.moved = self.grid.compressed or self.grid.merged
        self.grid.left_compress()
        self.grid.reverse()


class GamePanel:
    CELL_PADDING = 10
    BACKGROUND_COLOR = '#92877d'
    EMPTY_CELL_COLOR = '#9e948a'
    CELL_BACKGROUND_COLOR_DICT = {
        '2': '#eee4da',
        '4': '#ede0c8',
        '8': '#f2b179',
        '16': '#f59563',
        '32': '#f67c5f',
        '64': '#f65e3b',
        '128': '#edcf72',
        '256': '#edcc61',
        '512': '#edc850',
        '1024': '#edc53f',
        '2048': '#edc22e',
        'beyond': '#3c3a32'
    }
    CELL_COLOR_DICT = {
        '2': '#776e65',
        '4': '#776e65',
        '8': '#f9f6f2',
        '16': '#f9f6f2',
        '32': '#f9f6f2',
        '64': '#f9f6f2',
        '128': '#f9f6f2',
        '256': '#f9f6f2',
        '512': '#f9f6f2',
        '1024': '#f9f6f2',
        '2048': '#f9f6f2',
        'beyond': '#f9f6f2'
    }
    FONT = ('Verdana', 24, 'bold')
    UP_KEYS = ('w', 'W', 'Up')
    LEFT_KEYS = ('a', 'A', 'Left')
    DOWN_KEYS = ('s', 'S', 'Down')
    RIGHT_KEYS = ('d', 'D', 'Right')

    def __init__(self, grid):
        self.grid = grid
        self.root = tk.Tk()
        self.root.title('2048')
        self.root.resizable(False, False)
        self.background = tk.Frame(self.root, bg=GamePanel.BACKGROUND_COLOR)
        self.cell_labels = []
        for i in range(self.grid.size):
            row_labels = []
            for j in range(self.grid.size):
                label = tk.Label(self.background, text='',
                                 bg=GamePanel.EMPTY_CELL_COLOR,
                                 justify=tk.CENTER, font=GamePanel.FONT,
                                 width=4, height=2)
                label.grid(row=i, column=j, padx=10, pady=10)
                row_labels.append(label)
            self.cell_labels.append(row_labels)
        self.background.pack(side=tk.TOP)

    def paint(self):
        for i in range(self.grid.size):
            for j in range(self.grid.size):
                if self.grid.cells[i][j] == 0:
                    self.cell_labels[i][j].configure(
                         text='',
                         bg=GamePanel.EMPTY_CELL_COLOR)
                else:
                    cell_text = str(self.grid.cells[i][j])
                    if self.grid.cells[i][j] > 2048:
                        bg_color = GamePanel.CELL_BACKGROUND_COLOR_DICT.get('beyond')
                        fg_color = GamePanel.CELL_COLOR_DICT.get('beyond')
                    else:
                        bg_color = GamePanel.CELL_BACKGROUND_COLOR_DICT.get(cell_text)
                        fg_color = GamePanel.CELL_COLOR_DICT.get(cell_text)
                    self.cell_labels[i][j].configure(
                        text=cell_text,
                        bg=bg_color, fg=fg_color)


if __name__ == '__main__':
    size = 4
    grid = Grid(size)
    panel = GamePanel(grid)
    game2048 = Game(grid, panel)
    game2048.start(auto_play=True)  # Enable AI auto-play