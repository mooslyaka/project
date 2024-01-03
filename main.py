import pygame as pg
from random import randint, choice
import os
import sys
from button import Button
from Town import Town

FPS = 75
main_town_coords = ()
flag_buy_menu = False
farm_flag = False
pg.init()
board = [[0] * 100 for _ in range(100)]
colors = {0: (93, 161, 48), 1: (100, 100, 100), 2: (0, 204, 204), 3: (255, 0, 0), 4: (252, 186, 3)}
screen = pg.display.set_mode()
main_town = Town(100, 10, screen)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image
def print_text(message, color, coords):
    font = pg.font.Font(None, 30)
    text_button = font.render(str(message), False, color)
    screen.blit(text_button, coords)

tile_images = {"farm":
               load_image("sprites/farm.png")}
all_sprites = pg.sprite.Group()
tiles_group = pg.sprite.Group()
# 0 - пустая земля, 1 - горы, 2 - вода, 3 - основной город, 4 - ферма

class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)

        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            0 * pos_x, 0 * pos_y)
class Map:
    def __init__(self, width, height):
        self.flag = True
        self.width = width
        self.height = height
        self.visible_map = []

        self.generation()
        self.border = []
        self.update_border()
        self.left = 10
        self.top = 10
        self.cell_size = 50

    def generation(self):
        global main_town_coords
        for i in range(randint(40, 60)):  # генерация гор
            x, y = randint(0, 99), randint(0, 99)
            offset = randint(-3, 3)
            for j in range(randint(5, 10)):
                a = randint(1, 2)
                if a == 1:
                    if 0 <= y - j + offset < len(board):
                        board[y - j + offset][x] = 1
                    if 0 <= y + j + offset < len(board):
                        board[y + j + offset][x] = 1
                else:
                    if 0 <= x - j + offset < len(board):
                        board[y][x - j + offset] = 1
                    if 0 <= x + j + offset < len(board):
                        board[y][x + j + offset] = 1
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
                    if 0 <= y - j + offset < len(board):
                        if board[y - j + offset][x] != 1:
                            board[y - j + offset][x] = 2
                    if 0 <= y + j + offset < len(board):
                        if board[y + j + offset][x] != 1:
                            board[y + j + offset][x] = 2
                else:
                    if 0 <= x - j + offset < len(board):
                        board[y][x - j + offset] = 2
                    if 0 <= x + j + offset < len(board):
                        board[y][x + j + offset] = 2
        while True:  # генерация города
            castle_flag = True
            main_x, main_y = randint(1, 48), randint(1, 48)
            main_town_coords = main_x, main_y
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if board[main_y + y][main_x + x] != 0:
                        castle_flag = False
            if castle_flag:
                board[main_y][main_x] = 3
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

    # def set_visible_map(self):
    #     out_y = []
    #     itog_out = []
    #     qwe, index = 0, 0
    #     for i in self.board:
    #         if 3 in i:
    #             index = self.board.index(i)
    #             if index + 2 <= 100:  # + меняьб
    #                 qwe = 1
    #                 chet = -2  # сдез меняем шаг назад
    #             else:
    #                 qwe = -1
    #                 chet = -1
    #             while len(out_y) != 5:  # меняем колово
    #                 if qwe == 1:
    #                     if index + chet >= 0:
    #                         out_y.append(self.board[index + chet])
    #                 else:
    #                     out_y.append(self.board[chet])
    #                 chet += qwe
    #     if qwe == -1:
    #         out_y.reverse()
    #     first_sres, secons_sres = 0, 0
    #     for i in out_y:
    #         if 3 in i:
    #             index = out_y.index(i)
    #     if out_y[index].index(1) <= 2:
    #         secons_sres = 6
    #     elif out_y[index].index(1) >= 8:
    #         first_sres, secons_sres = 5, 10
    #     else:
    #         first_sres, secons_sres = out_y[index].index(1) - 2, out_y[index].index(1) + 3
    #     for i in out_y:
    #         itog_out.append(i[first_sres:secons_sres])
    #     return itog_out

    def render(self):
        if self.cell_size < 19:
            self.cell_size = 19
        if self.top > 50:
            self.top = 50
        if self.left > 50:
            self.left = 50
        # if self.top < -940:
        #     self.top = -940
        grid = []
        for y in range(self.height):
            for x in range(self.width):
                grid.append(pg.Rect(x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                    self.cell_size))
        grid = iter(grid)
        # for y in self.board:
        #     for x in y:
        #         rect = next(grid)
        #         if x == 4:
        #             Tile("sprites/farm.png", x, y)
        #         else:
        #             pg.draw.rect(screen, self.colors.get(x), rect)
        #             pg.draw.rect(screen, (0, 0, 0), rect, 1)
        for y in range(len(board)):
            for x in range(len(board[y])):
                rect = next(grid)
                if board[y][x] == 4:
                    Tile("farm", x, y)
                else:
                    pg.draw.rect(screen, colors.get(board[y][x]), rect)
                    pg.draw.rect(screen, (0, 0, 0), rect, 1)

        for i in self.border:
            pg.draw.rect(screen, (255, 0, 0), (
                self.left + i[0] * self.cell_size, self.top + self.cell_size * i[1], self.cell_size, self.cell_size), 2)
        pg.draw.rect(screen, (131, 79, 42), (0, 970, 2000, 110))

    def focus_camera(self, count):
        self.cell_size += count

    def move_camera(self, keys=None, mouse_pos=None):
        if keys[pg.K_w] or mouse_pos[1] < 20:
            self.top += 10
        if keys[pg.K_s] or mouse_pos[1] > 1060:
            self.top += -10
        if keys[pg.K_d] or mouse_pos[0] > 1900:
            self.left += -10
        if keys[pg.K_a] or mouse_pos[0] < 20:
            self.left += 10

    def update_border(self):
        for y in range(99):
            for x in range(99):
                if board[y][x] == 3 or board[y][x] == 4:
                    for i in range(-2, 3):
                        for j in range(-2, 3):
                            self.border.append((x + i, y + j))

    def get_click(self, mouse_pos):
        self.on_click(self.get_cell(mouse_pos), mouse_pos)

    def get_cell(self, mouse_pos):
        if (self.left < mouse_pos[0] < self.width * self.cell_size + self.left
                and self.top < mouse_pos[1] < self.height * self.cell_size + self.top):
            col = (mouse_pos[0] - self.left) // self.cell_size
            row = (mouse_pos[1] - self.top) // self.cell_size
            return col, row
        return None

    def on_click(self, cell_coords, mouse_pos):
        print(board[cell_coords[1]][cell_coords[0]])
        global flag_buy_menu, farm_flag
        if cell_coords == main_town_coords:
            flag_buy_menu = True
        elif mouse_pos[1] < 970:
            flag_buy_menu = False
        if farm_flag and cell_coords in self.border and board[cell_coords[1]][
            cell_coords[0]] == 0 and main_town.money >= 50:
            board[cell_coords[1]][cell_coords[0]] = 4
            farm_flag = False
            main_town.buy(50)
            main_town.money_for_move += 10
            self.update_border()
        elif farm_flag and cell_coords not in self.border:
            farm_flag = False

map_ = Map(100, 100)
def set_farm():
    global farm_flag
    farm_flag = True


def buy_menu():
    pg.draw.rect(screen, (173, 151, 102), (200, 985, 1450, 80))
    farm = Button(90, 70, (87, 75, 51), (97, 85, 61), screen)
    farm.draw(250, 990, 50, set_farm)
    pg.draw.rect(screen, (252, 186, 3), (295, 1015, 30, 30))


def next_move_def():
    global flag_buy_menu
    flag_buy_menu = False
    main_town.update_money()


def main():
    next_move = Button(200, 80, (42, 94, 131), (70, 121, 157), screen)
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
        map_.move_camera(keys, pg.mouse.get_pos())
        screen.fill((0, 204, 204))
        map_.render()
        next_move.draw(1700, 985, "Следующий ход", next_move_def)
        main_town.print_money()
        if flag_buy_menu:
            buy_menu()
        if farm_flag:
            pg.draw.rect(screen, (252, 186, 3), (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 30, 30))
        pg.display.flip()
        clock.tick(FPS)
    pg.quit()


if __name__ == "__main__":
    main()
