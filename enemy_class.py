import pygame
import random
import json

# from .sprites import *
from pygame import image
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.sprite_sheet = pygame.image.load('sprites/spritesheet.png').convert()
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width // 2.3)
        self.number = number
        self.colour = self.set_colour()
        self.sprite = self.get_sprite(209, 261, 50, 50)
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = self.set_speed()
        with open("sprites/spritesheet.json") as f:
            self.data = json.load(f)
        f.close()

    def update(self):
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()

        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0] - TOP_BOTTOM_BUFFER +
                            self.app.cell_width // 2) // self.app.cell_width + 1
        self.grid_pos[1] = (self.pix_pos[1] - TOP_BOTTOM_BUFFER +
                            self.app.cell_height // 2) // self.app.cell_height + 1

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, pygame.Rect(-x, -y, w, h))
        sprite = pygame.transform.scale(sprite, (30, 30))
        return sprite

    def draw(self):

        if self.colour == "red":
            if self.direction == vec(-1, 0):  # left
                self.sprite = self.get_sprite(209, 261, 50, 50)
            if self.direction == vec(1, 0):  # right
                self.sprite = self.get_sprite(261, 261, 50, 50)
            if self.direction == vec(0, 1):  # down
                self.sprite = self.get_sprite(157, 261, 50, 50)
            if self.direction == vec(0, -1):  # up
                self.sprite = self.get_sprite(313, 1, 50, 50)

        if self.colour == "green":
            if self.direction == vec(-1, 0):  # left
                self.sprite = self.get_sprite(105, 53, 50, 50)
            if self.direction == vec(1, 0):  # right
                self.sprite = self.get_sprite(157, 53, 50, 50)
            if self.direction == vec(0, 1):  # down
                self.sprite = self.get_sprite(53, 53, 50, 50)
            if self.direction == vec(0, -1):  # up
                self.sprite = self.get_sprite(209, 53, 50, 50)

        if self.colour == "pink":
            if self.direction == vec(-1, 0):  # left
                self.sprite = self.get_sprite(53, 209, 50, 50)
            if self.direction == vec(1, 0):  # right
                self.sprite = self.get_sprite(157, 209, 50, 50)
            if self.direction == vec(0, 1):  # down
                self.sprite = self.get_sprite(53, 209, 50, 50)
            if self.direction == vec(0, -1):  # up
                self.sprite = self.get_sprite(209, 209, 50, 50)

        if self.colour == "orange":
            if self.direction == vec(-1, 0):  # left
                self.sprite = self.get_sprite(53, 105, 50, 50)
            if self.direction == vec(1, 0):  # right
                self.sprite = self.get_sprite(105, 105, 50, 50)
            if self.direction == vec(0, 1):  # down
                self.sprite = self.get_sprite(1, 105, 50, 50)
            if self.direction == vec(0, -1):  # up
                self.sprite = self.get_sprite(157, 105, 50, 50)

        self.app.screen.blit(self.sprite, (self.pix_pos[0] - 15, self.pix_pos[1] - 15))

    def set_speed(self):
        if self.personality in ["speedy", "scared"]:
            speed = 2
        else:
            speed = 1
        return speed

    def set_target(self):
        if self.personality == "speedy" or self.personality == "slow":
            return self.app.player.grid_pos
        else:
            if self.app.player.grid_pos[0] > COLS // 2 and self.app.player.grid_pos[1] > ROWS // 2:
                return vec(1, 1)
            if self.app.player.grid_pos[0] > COLS // 2 and self.app.player.grid_pos[1] < ROWS // 2:
                return vec(1, ROWS - 2)
            if self.app.player.grid_pos[0] < COLS // 2 and self.app.player.grid_pos[1] > ROWS // 2:
                return vec(COLS - 2, 1)
            else:
                return vec(COLS - 2, ROWS - 2)

    def time_to_move(self):
        if int(self.pix_pos.x + TOP_BOTTOM_BUFFER // 2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y + TOP_BOTTOM_BUFFER // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        if self.personality == "random":
            self.direction = self.get_random_direction()
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]

        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
            int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if 0 <= neighbour[0] + current[0] < len(grid[0]):
                        if 0 <= neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    def get_pix_pos(self):
        return vec((self.grid_pos.x * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2 + self.app.cell_width // 2,
                   (self.grid_pos.y * self.app.cell_height) + TOP_BOTTOM_BUFFER // 2 +
                   self.app.cell_height // 2)

    def set_colour(self):
        if self.number == 0:
            return "red"
        if self.number == 1:
            return "green"
        if self.number == 2:
            return "orange"
        if self.number == 3:
            return "pink"

    def set_personality(self):
        if self.number == 0:
            return "speedy"
        elif self.number == 1:
            return "slow"
        elif self.number == 2:
            return "random"
        else:
            return "scared"
