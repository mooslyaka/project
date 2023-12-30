import pygame as pg
from random import randint, choice
from time import monotonic

FPS = 75
pg.init()
screen = pg.display.set_mode()


# 0 - пустая земля, 1 - горы, 2 - вода, 3 - основной город

class Map:
    def __init__(self, width, height):
        self.flag = True
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.visible_map = []
        self.colors = {0: (93, 161, 48), 1: (100, 100, 100), 2: (0, 204, 204), 3: (255, 0, 0)}
        self.generation()
        self.left = 10
        self.top = 10
        self.cell_size = 50

    def generation(self):
        for i in range(randint(40, 60)):  # генерация гор
            x, y = randint(0, 99), randint(0, 99)
            offset = randint(-3, 3)
            for j in range(randint(5, 10)):
                a = randint(1, 2)
                if a == 1:
                    if 0 <= y - j + offset < len(self.board):
                        self.board[y - j + offset][x] = 1
                    if 0 <= y + j + offset < len(self.board):
                        self.board[y + j + offset][x] = 1
                else:
                    if 0 <= x - j + offset < len(self.board):
                        self.board[y][x - j + offset] = 1
                    if 0 <= x + j + offset < len(self.board):
                        self.board[y][x + j + offset] = 1
        for i in range(randint(19, 26)):  # генерация рек
            y = randint(0, 99)
            if y == 0 or y == 20:
                x = randint(0, 10)
            else:
                x = choice([0, 99])
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
        while True:  # генерация города
            castle_flag = True
            main_x, main_y = randint(1, 48), randint(1, 48)
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if self.board[main_y + y][main_x + x] != 0:
                        castle_flag = False
            if castle_flag:
                self.board[main_y][main_x] = 3
                break

    def update(self, keys):
        if keys[pg.K_w]:
            self.top += 10
        if keys[pg.K_s]:
            self.top += -10
        if keys[pg.K_d]:
            self.left += -10
        if keys[pg.K_a]:
            self.left += 10

    def set_visible_map(self):
        out_y = []
        itog_out = []
        qwe, index = 0, 0
        for i in self.board:
            if 3 in i:
                index = self.board.index(i)
                if index + 2 <= 100:  # + меняьб
                    qwe = 1
                    chet = -2  # сдез меняем шаг назад
                else:
                    qwe = -1
                    chet = -1
                while len(out_y) != 5:  # меняем колово
                    if qwe == 1:
                        if index + chet >= 0:
                            out_y.append(self.board[index + chet])
                    else:
                        out_y.append(self.board[chet])
                    chet += qwe
        if qwe == -1:
            out_y.reverse()
        first_sres, secons_sres = 0, 0
        for i in out_y:
            if 3 in i:
                index = out_y.index(i)
        if out_y[index].index(1) <= 2:
            secons_sres = 6
        elif out_y[index].index(1) >= 8:
            first_sres, secons_sres = 5, 10
        else:
            first_sres, secons_sres = out_y[index].index(1) - 2, out_y[index].index(1) + 3
        for i in out_y:
            itog_out.append(i[first_sres:secons_sres])
        return itog_out

    def render(self):
        if self.cell_size < 19:
            self.cell_size = 19
        if self.top > 50:
            self.top = 50
        if self.left > 50:
            self.left = 50
        if self.top < -940:
            self.top = -940
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
        pg.draw.rect(screen, (131, 79, 42), (0, 970, 2000, 110))

    def focus_camera(self, count):
        self.cell_size += count

    def get_click(self, mouse_pos):
        self.on_click(self.get_cell(mouse_pos))

    def get_cell(self, mouse_pos):
        if (self.left < mouse_pos[0] < self.width * self.cell_size + self.left
                and self.top < mouse_pos[1] < self.height * self.cell_size + self.top):
            col = (mouse_pos[0] - self.left) // self.cell_size
            row = (mouse_pos[1] - self.top) // self.cell_size
            return col, row
        return None

    def on_click(self, cell_coords):
        print(cell_coords)
        print(self.cell_size)
        print(self.top)


class Town:
    def __init__(self, money, money_for_move):
        self.money = money
        self.money_for_move = money_for_move

    def update_money(self):
        self.money += self.money_for_move

    def print_money(self):
        pg.draw.rect(screen, (213, 160, 51), (10, 985, 150, 80))
        font = pg.font.Font(None, 30)
        text_button = font.render(str(self.money), False, (18, 41, 57))
        screen.blit(text_button, (20, 1012))


class Button:
    def __init__(self, width, height, color, active_color):
        self.width = width
        self.height = height
        self.color = color
        self.active_color = active_color

    def draw(self, x, y, text, action=None):
        self.action = action
        self.get_press = False
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pg.draw.rect(screen, self.active_color, (x, y, self.width, self.height))
            if click[0] == 1 and action is not None:
                action()
                pg.time.delay(300)

        else:
            pg.draw.rect(screen, self.color, (x, y, self.width, self.height))
        font = pg.font.Font(None, 30)
        text_button = font.render(text, False, (18, 41, 57))
        screen.blit(text_button, (x + 15, y + 30))


main_town = Town(100, 10)


def next_move_def():
    main_town.update_money()


def main():
    map_ = Map(100, 100)
    next_move = Button(200, 80, (42, 94, 131), (70, 121, 157))
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    map_.get_click(event.pos)
                if event.button == 4:
                    map_.focus_camera(1)
                if event.button == 5:
                    map_.focus_camera(-1)
        keys = pg.key.get_pressed()
        map_.update(keys)
        screen.fill((0, 204, 204))
        map_.render()
        next_move.draw(1700, 985, "Следующий ход", next_move_def)
        main_town.print_money()
        pg.display.flip()
        clock.tick(FPS)
    pg.quit()


if __name__ == "__main__":
    main()
