import pygame as pg
from random import randint, choice

FPS = 24


class Map:
    def __init__(self, width, height):
        self.flag = True
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.colors = {0: (93, 161, 48), 1: (100, 100, 100), 2: (0, 204, 204), 3:(255, 0, 0)}
        self.generation()
        self.left = 10
        self.top = 13
        self.cell_size = 50

    def generation(self):
        for i in range(randint(2, 5)):  # генерация гор
            x, y = randint(0, 37), randint(0, 20)
            offset = randint(-3, 3)
            for j in range(randint(1, 4)):
                if 0 <= y - j + offset < len(self.board):
                    self.board[y - j + offset][x] = 1
                if 0 <= y + j + offset < len(self.board):
                    self.board[y + j + offset][x] = 1
                if 0 <= x - j + offset < len(self.board):
                    self.board[y][x - j + offset] = 1
                if 0 <= x + j + offset < len(self.board):
                    self.board[y][x + j + offset] = 1
        for i in range(randint(1, 3)):  # генерация рек
            y = randint(0, 20)
            if y == 0 or y == 20:
                x = randint(0, 37)
            else:
                x = choice([0, 37])
            offset = randint(-1, 1)
            flag = randint(0, 1)
            for j in range(randint(5, 9)):
                if flag:
                    if 0 <= y - j + offset < len(self.board):
                        if self.board[y - j + offset][x] != 1:
                            self.board[y - j + offset][x] = 2
                    if 0 <= y + j + offset < len(self.board):
                        if self.board[y + j + offset][x] != 1:
                            self.board[y + j + offset][x] = 2
                else:
                    if 0 <= x - j + offset < len(self.board):
                        self.board[y][x - j + offset] = 2
                    if 0 <= x + j + offset < len(self.board):
                        self.board[y][x + j + offset] = 2
        while True:
            castle_flag = True
            main_x, main_y = randint(1, 36), randint(1, 19)
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if self.board[main_y + y][main_x + x] != 0:
                        castle_flag = False
            if castle_flag:
                self.board[main_y][main_x] = 3
                break
    def render(self, screen):
        grid = []
        for y in range(self.height):
            for x in range(self.width):
                grid.append(pg.Rect(x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                    self.cell_size))
        grid = iter(grid)
        for x in self.board:
            for y in x:
                rect = next(grid)
                pg.draw.rect(screen, self.colors.get(y), rect)
                pg.draw.rect(screen, (0, 0, 0), rect, 1)


def main():
    pg.init()
    screen = pg.display.set_mode()
    map = Map(38, 21)
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 204, 204))
        map.render(screen)
        pg.display.flip()
        clock.tick(FPS)
    pg.quit()


if __name__ == "__main__":
    main()
