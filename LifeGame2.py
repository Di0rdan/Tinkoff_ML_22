import pygame
import random
import numpy as np
import sys
from PIL import Image


class Grid:
    def __init__(self, height, width):

        self.height = height
        self.width = width
        self.data = np.empty(shape=(height, width), dtype="bool")
        self.clear()
        print(self.data.shape)

    def update(self):
        new_grid = np.empty(shape=self.data.shape, dtype="bool")
        n_rows, n_columns = self.data.shape

        for row in range(n_rows):
            for column in range(n_columns):
                neighbours_count = 0
                neighbours_count += self.data[
                    (row - 1) % n_rows, (column - 1) % n_columns
                ]
                neighbours_count += self.data[(row - 1) % n_rows, column]
                neighbours_count += self.data[
                    (row - 1) % n_rows, (column + 1) % n_columns
                ]
                neighbours_count += self.data[row, (column - 1) % n_columns]
                neighbours_count += self.data[row, (column + 1) % n_columns]
                neighbours_count += self.data[
                    (row + 1) % n_rows, (column - 1) % n_columns
                ]
                neighbours_count += self.data[(row + 1) % n_rows, column]
                neighbours_count += self.data[
                    (row + 1) % n_rows, (column + 1) % n_columns
                ]

                if self.data[row, column] and (
                    neighbours_count == 2 or neighbours_count == 3
                ):
                    new_grid[row, column] = True
                elif not self.data[row, column] and neighbours_count == 3:
                    new_grid[row, column] = True
                else:
                    new_grid[row, column] = False

        self.data = new_grid

    def save(self, active_color):
        arr = np.zeros((self.data.shape[0], self.data.shape[1], 3), dtype=np.uint8)
        for row in range(self.data.shape[0]):
            for column in range(self.data.shape[1]):
                if self.data[row, column]:
                    arr[row, column] = active_color
        img = Image.fromarray(arr, "RGB")
        img.save("data.png")

    def load(self):
        try:
            img = Image.open("data.png")
        except:
            self.clear()
            return
        arr = np.array(img)
        self.data = np.empty(shape=(arr.shape[0], arr.shape[1]), dtype="bool")
        for row in range(self.data.shape[0]):
            for column in range(self.data.shape[1]):
                if arr[row, column].sum() > 255:
                    self.data[row, column] = True
                else:
                    self.data[row, column] = False
        self.height, self.width = self.data.shape

    def clear(self):
        for row in range(self.data.shape[0]):
            for column in range(self.data.shape[1]):
                self.data[row, column] = False


class LifeGame:
    def __init__(
        self,
        screen_width=240 * 4,
        screen_height=135 * 4,
        grid_width=240,
        grid_height=135,
        active_color=(0, 255, 255),
        background_color=(0, 0, 0),
        speed=10,
    ):

        pygame.init()
        self.active_color = active_color
        self.background_color = background_color
        self.speed = speed

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill(self.background_color)
        pygame.display.flip()

        self.paused_ = False
        self.game_over = False

        self.last_update_completed = 0
        self.desired_millisecs_between_updates = (1.0 / self.speed) * 1000.0

        self.grid = Grid(grid_height, grid_width)

    def cap_frame_rate(self):
        now = pygame.time.get_ticks()
        millisecs_since_last_update = now - self.last_update_completed
        time_to_sleep = (
            self.desired_millisecs_between_updates - millisecs_since_last_update
        )

        if time_to_sleep > 0:
            pygame.time.delay(int(time_to_sleep))
        self.last_update_completed = now

    def cell_size(self):
        cell_size = min(
            self.screen.get_width() / self.grid.width,
            self.screen.get_height() / self.grid.height,
        )
        return int(cell_size)

    def draw_cell(self, x, y, color):
        radius = int(self.cell_size() / 2)
        pygame.draw.circle(
            self.screen,
            color,
            (y * self.cell_size() + radius, x * self.cell_size() + radius),
            radius,
        )

    def draw_grid(self):

        self.screen.fill(self.background_color)

        for row in range(self.grid.height):
            for column in range(self.grid.width):
                if self.grid.data[row, column]:
                    self.draw_cell(row, column, self.active_color)

    def event_handler(self):
        """
        p - pause
        s - save
        l - load
        c - clear
        q - quit
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.unicode == "p":
                    self.paused_ = not self.paused_
                elif event.unicode == "s":
                    self.grid.save(self.active_color)
                elif event.unicode == "l":
                    self.grid.load()
                elif event.unicode == "c":
                    self.grid.clear()
                elif event.unicode == "q":
                    self.game_over = True

    def edit(self):

        y, x = pygame.mouse.get_pos()
        x //= self.cell_size()
        y //= self.cell_size()

        # print(x, y)

        if pygame.mouse.get_pressed()[0]:
            self.grid.data[x, y] = True
            self.draw_cell(x, y, self.active_color)
        elif pygame.mouse.get_pressed()[2]:
            self.grid.data[x, y] = False
            self.draw_cell(x, y, color=self.background_color)

    def run(self):
        self.grid.load()
        while True:
            if self.game_over:
                return

            self.event_handler()

            self.edit()

            if self.paused_:
                self.edit()
            else:
                self.grid.update()

            self.draw_grid()

            pygame.display.flip()

            self.cap_frame_rate()


def main():
    game = LifeGame()
    game.run()


if __name__ == "__main__":
    main()
