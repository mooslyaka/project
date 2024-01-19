import pygame as pg
from random import randint, choice
import os
import sys
from button import Button
from Town import MyTown, EnemyTown

FPS = 25
main_town_coords = ()
flag_buy_menu = False
farm_flag, warrior_flag = False, 0
pg.init()
board = [[0] * 100 for _ in range(100)]
cell_colors = {0: (93, 161, 48), 1: (100, 100, 100), 2: (100, 204, 204), 3: (255, 0, 0), 4: (252, 186, 3),
               5: (234, 231, 123), 6: (200, 200, 123), 7: (150, 150, 150), 8: (0, 0, 0), 9: (0, 0, 0)}
enemy_color = [(0, 255, 68), (55, 237, 198), (10, 19, 196), (106, 10, 196), (212, 4, 219), (227, 14, 106),
               (242, 238, 17), (242, 156, 17)]
price_warrior = {1: (50, 10), 2: (100, 20), 3: (170, 30), 4: (300, 50)}
top, left, cell_size = 2, 2, 50
screen = pg.display.set_mode()
main_town = MyTown(100, 10, screen, 7)
warriors = []
enemies = []
lose_flag = False
game_state = "start_menu"
sms = ""
chet = 0


# 0 - земдля 1 - гроры 2 - вода  3- город 4 - ферма 5,6,7,8- воинЫ 9 - город чужой

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
                   load_image("farm.png"), "mountain": load_image("mountain.png"),
               "warrior1": load_image("warrior1.png"), "warrior2": load_image("warrior2.png"),
               "warrior3": load_image("warrior3.png"), "warrior4": load_image("warrior4.png")}
all_sprites = pg.sprite.Group()
tiles_group = pg.sprite.Group()


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images.get(tile_type)
        self.image = pg.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect().move(
            cell_size * pos_x + left, cell_size * pos_y + top)
        screen.blit(self.image, self.rect)


def render(height, width, border):  # прорисовка карты
    global top, left, cell_size
    if cell_size < 19:
        cell_size = 19
    if top > 50:
        top = 50
    if left > 50:
        left = 50
    grid = []
    for y in range(height):
        for x in range(width):
            grid.append(pg.Rect(x * cell_size + left, y * cell_size + top, cell_size,
                                cell_size))
    grid = iter(grid)
    get_sprite = {1: "mountain", 4: "farm", 5: "warrior1", 6: "warrior2", 7: "warrior3", 8: "warrior4"}
    for y in range(len(board)):
        for x in range(len(board[y])):
            rect = next(grid)
            if board[y][x] in [1, 4, 5, 6, 7, 8]:
                Tile(get_sprite.get(board[y][x]), x, y)
            else:
                pg.draw.rect(screen, cell_colors.get(board[y][x]), rect)
            pg.draw.rect(screen, (0, 0, 0), rect, 1)
    for i in border:
        pg.draw.rect(screen, (255, 0, 0), (
            left + i[0] * cell_size, top + cell_size * i[1], cell_size, cell_size), 3)
    for i in enemies:
        pg.draw.rect(screen, i.color, (left + i.x * cell_size, top + i.y * cell_size, cell_size, cell_size))

        for j in i.border:
            pg.draw.rect(screen, i.color, (
                left + j[0] * cell_size, top + cell_size * j[1], cell_size, cell_size), 3)


class Warrior:
    def __init__(self, x, y, level, town):
        self.x = x
        self.y = y
        self.level = level
        self.move = level
        self.radius = []
        self.radius_flag = False
        self.town = town
        self.target = None
        self.target_flag = False

    def available_radius(self):
        for i in range(-self.move, self.move + 1):
            for j in range(-self.move, self.move + 1):
                if 0 <= self.y + i <= 99 and 0 <= self.x + j <= 99:
                    if board[self.y + i][self.x + j] not in [1, 2]:
                        self.radius.append((self.x + j, self.y + i))
        self.radius.append((self.x, self.y))

    def print_radius(self):  # прорисовка радиуса
        for x, y in self.radius:
            if 0 <= x <= 99 and 0 <= y <= 99:
                pg.draw.rect(screen, (255, 215, 0),
                             (
                                 left + x * cell_size, top + y * cell_size, cell_size, cell_size),
                             10)

    def moved(self, coords):  # движение
        way = int(((coords[0] - self.x) ** 2 + (coords[1] - self.y) ** 2) ** 0.5)
        if way != 0:
            self.move -= way

            board[self.y][self.x] = 0
            self.x, self.y = coords[0], coords[1]
            board[self.y][self.x] = self.level + 4
            self.radius.clear()
            self.radius_flag = False


class Map:
    def __init__(self, width, height):
        self.flag = True
        self.width = width
        self.height = height
        self.visible_map = []
        self.generation()
        self.border = []
        self.update_border()

    def generation(self):  # генерация карты
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
            main_x, main_y = randint(1, 97), randint(1, 97)
            main_town_coords = main_x, main_y
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if board[main_y + y][main_x + x] != 0:
                        castle_flag = False
            if castle_flag:
                board[main_y][main_x] = 3
                break
        enemy_flag = 0
        while enemy_flag != 7:
            castle_flag = True
            main_x, main_y = randint(1, 97), randint(1, 97)
            for x in range(-2, 3):
                for y in range(-2, 3):
                    if board[main_y + y][main_x + x] != 0:
                        castle_flag = False
            if castle_flag:
                for i in enemies:
                    if int(((i.x - main_x) ** 2 + (i.y - main_y) ** 2) ** 0.5) <= 10:
                        castle_flag = False
            if castle_flag and int(((main_town_coords[0] - main_x) ** 2 + (
                    main_town_coords[1] - main_y) ** 2) ** 0.5) >= 15:
                enemies.append(
                    EnemyTown(100, 20, enemy_color[enemy_flag], main_x, main_y, screen, enemy_flag, board, enemies))
                board[main_y][main_x] = 9
                enemy_flag += 1
        for i in enemies:
            i.update_border()

    def update(self, keys):
        global left, top
        if keys[pg.K_w]:
            top += 10
        if keys[pg.K_s]:
            top += -10
        if keys[pg.K_d]:
            left += -10
        if keys[pg.K_a]:
            left += 10
        render(self.height, self.width, self.border)

    def focus_camera(self, count):
        global cell_size
        cell_size += count

    def move_camera(self, keys=None, mouse_pos=None):
        global top, left
        if keys[pg.K_w] or mouse_pos[1] < 20:
            top += 10
        if keys[pg.K_s] or mouse_pos[1] > 1060:
            top += -10
        if keys[pg.K_d] or mouse_pos[0] > 1900:
            left += -10
        if keys[pg.K_a] or mouse_pos[0] < 20:
            left += 10

    def update_border(self):
        for y in range(99):
            for x in range(99):
                if board[y][x] == 3 or board[y][x] == 4:
                    for i in range(-2, 3):
                        for j in range(-2, 3):
                            if 0 <= x + i <= 99 and 0 <= y + j <= 99:
                                self.border.append((x + i, y + j))
        self.border = list(set(self.border))
        for i in enemies:
            for j in self.border:
                if j in i.border:
                    self.border.remove(j)

    def get_click(self, mouse_pos):
        self.on_click(self.get_cell(mouse_pos), mouse_pos)

    def get_cell(self, mouse_pos):
        if (left < mouse_pos[0] < self.width * cell_size + left
                and top < mouse_pos[1] < self.height * cell_size + top):
            col = (mouse_pos[0] - left) // cell_size
            row = (mouse_pos[1] - top) // cell_size
            return col, row

    def on_click(self, cell_coords, mouse_pos):
        global flag_buy_menu, farm_flag, warrior_flag, sms
        if cell_coords:
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
            if warrior_flag and cell_coords in self.border and board[cell_coords[1]][
                cell_coords[0]] == 0:
                if main_town.money >= price_warrior.get(warrior_flag)[0]:
                    main_town.buy(price_warrior.get(warrior_flag)[0])
                    main_town.money_for_move -= price_warrior.get(warrior_flag)[1]
                    board[cell_coords[1]][cell_coords[0]] = warrior_flag + 4
                    warriors.append(Warrior(cell_coords[0], cell_coords[1], warrior_flag, 7))
                warrior_flag = 0
            if warrior_flag and cell_coords not in self.border:
                warrior_flag = 0


            elif board[cell_coords[1]][cell_coords[0]] in [5, 6, 7, 8]:
                for i in warriors:
                    if i.town == 7:
                        if i.y == cell_coords[1] and i.x == cell_coords[0]:
                            i.available_radius()
                            i.radius_flag = True
            money_for_lose = {5: 10, 6: 20, 7: 30, 8: 50}
            for i in warriors:
                for j in enemies:
                    if i.radius_flag:
                        if cell_coords in i.radius and board[cell_coords[1]][cell_coords[0]] in [5, 6, 7, 8]:
                            for h in warriors:
                                if (h.x, h.y) == cell_coords:
                                    if i.level + 4 >= board[cell_coords[1]][cell_coords[0]] and h.town != 7:
                                        for n in enemies:
                                            if (n.x, n.y) == cell_coords:
                                                warriors.remove(n)
                                                break
                                        i.moved(cell_coords)
                                        i.move = 0
                                        j.money_for_move += money_for_lose.get(board[cell_coords[1]][cell_coords[0]])
                                        break
                        elif cell_coords in i.radius and board[cell_coords[1]][
                            cell_coords[0]] == 9 and i.level >= 3 and cell_coords in j.border:
                            for k in j.border:
                                if board[k[1]][k[0]] == 4:
                                    board[k[1]][k[0]] = 0
                                    continue
                            for b in warriors:
                                if b.town == j.number:
                                    board[b.y][b.x] = 0
                            i.moved(cell_coords)
                            j.border.clear()
                            enemies.remove(j)
                            i.move = 0
                        elif cell_coords in i.radius and board[cell_coords[1]][
                            cell_coords[0]] == 9 and i.level < 3 and cell_coords in j.border:
                            sms = "Вам необходим воин более высокого уровня"
                        elif cell_coords in i.radius and board[cell_coords[1]][cell_coords[0]] == 0:
                            i.moved(cell_coords)
                        elif cell_coords in i.radius and board[cell_coords[1]][
                            cell_coords[0]] == 4 and cell_coords in j.border:
                            i.moved(cell_coords)
                            j.money_for_move -= 10
                            i.move = 0

                        elif cell_coords not in i.radius:
                            i.radius_flag = False


map_ = Map(100, 100)


def set_farm():
    global farm_flag
    farm_flag = True


def set_warrior(level):
    global warrior_flag
    warrior_flag = level


def check_warrior(first, second):
    if first.level >= second.level:
        return True
    return False


farm = Button(90, 70, (87, 75, 51), (97, 85, 61), screen)
warrior_1 = Button(90, 70, (87, 75, 51), (97, 85, 61), screen)
warrior_2 = Button(90, 70, (87, 75, 51), (97, 85, 61), screen)
warrior_3 = Button(90, 70, (87, 75, 51), (97, 85, 61), screen)
warrior_4 = Button(90, 70, (87, 75, 51), (97, 85, 61), screen)


def buy_menu():
    pg.draw.rect(screen, (173, 151, 102), (200, 985, 1450, 80))
    farm.draw(250, 990, 50, set_farm)
    pg.draw.rect(screen, (252, 186, 3), (295, 1015, 30, 30))
    warrior_1.draw(400, 990, 50, lambda: set_warrior(1))
    pg.draw.rect(screen, (252, 23, 3), (445, 1015, 15, 30))
    warrior_2.draw(550, 990, 100, lambda: set_warrior(2))
    pg.draw.rect(screen, (252, 23, 3), (600, 1015, 15, 30))
    warrior_3.draw(700, 990, 170, lambda: set_warrior(3))
    pg.draw.rect(screen, (252, 23, 3), (755, 1015, 15, 30))
    warrior_4.draw(850, 990, 300, lambda: set_warrior(4))
    pg.draw.rect(screen, (252, 23, 3), (905, 1015, 15, 30))


def next_move_def():
    global flag_buy_menu, lose_flag, sms, chet, game_state
    sms = ""
    flag_buy_menu = False
    main_town.update_money()
    if main_town.money <= 0:
        for y in range(99):
            for x in range(99):
                if board[y][x] in [5, 6, 7, 8]:
                    main_town.money_for_move += price_warrior.get(board[y][x] - 4)[1]
                    board[y][x] = 0

        main_town.money = 0
    for i in enemies:
        i.update_money()
        border_target = False
        for j in warriors:
            j.move = j.level
            if (j.x, j.y) in i.border and i.number != j.town:
                i.set_warrior(i.update_coords())
                i.tacktik = (True, 7)
                border_target = (j.x, j.y)
        for j in range(5):
            coords, what = i.generate_move()
            if not what:
                continue
            if what == "farm":
                board[coords[1]][coords[0]] = 4
            if what[:-1] == "warrior":
                warriors.append(Warrior(coords[0], coords[1], int(what[-1]), i.number))
                board[coords[1]][coords[0]] = int(what[-1]) + 4

        if i.tacktik[0]:
            target = []
            if i.tacktik[1] != 7:
                for h in enemies[i.tacktik[1]].border:
                    if board[h[1]][h[0]] not in [0, 1, 2, 3]:
                        target.append(h)
            else:
                target = [i for i in map_.border if board[i[1]][i[0]] not in [0, 1, 2]]
            if border_target:
                target.append(border_target)
            for j in warriors:
                if j.town == i.number:
                    if not j.target_flag:
                        j.target = choice(target)
                        moved = (j.x, j.y)
                        if j.x > j.target[0] and 0 <= j.x - j.move <= 99 and board[j.y][j.x - j.move] not in [1, 2]:
                            moved = (j.x - j.move, j.y)
                        elif j.x < j.target[0] and 0 <= j.x + j.move <= 99 and board[j.y][j.x + j.move] not in [1, 2]:
                            moved = (j.x + j.move, j.y)
                        elif j.y > j.target[1] and 0 <= j.y - j.move <= 99 and board[j.y - j.move][j.x] not in [1, 2]:
                            moved = (j.x, j.y - j.move)
                        elif j.y < j.target[1] and 0 <= j.y + j.move <= 99 and board[j.y + j.move][j.x] not in [1, 2]:
                            moved = (j.x, j.y + j.move)
                        if board[moved[1]][moved[0]] in [5, 6, 7, 8]:
                            for h in warriors:
                                if (h.x, h.y) == moved:
                                    if check_warrior(j, h):
                                        j.moved(moved)
                                        break
                        else:
                            j.moved(moved)
    if chet > 10:
        first, first_warriors, second_warriors = choice(enemies), 0, 0
        if not first.tacktik[0]:
            for i in warriors:
                if i.town == first.number:
                    first_warriors += 1
                if i.town == 7:
                    second_warriors += 1
            if first_warriors > second_warriors:
                first.tacktik = (True, 7)
                sms = "На вас напали"
                print_text("zxc", (0, 0, 0), (50, 50))
    if board[main_town_coords[1]][main_town_coords[0]] != 3:
        draw_lose_menu()
    win_list = []
    for i in board:
        for j in i:
            win_list.append(j)
    if 9 not in win_list:
        game_state = "win"
    chet += 1


def draw_lose_menu():
    global game_state
    game_state = "lose"


def draw_start_menu():
    text = ["Правила игры:", "Вы упраете городом красного цвета.",
            "При нажатии на центр города вы можете построить ферму или обучить войнов",
            "Ваша главная цель захватить все вражеские города"]
    text_coords = 200
    screen.fill((34, 42, 150))
    for i in text:
        print_text(i, (230, 230, 230), (50, text_coords))
        text_coords += 25


def start_game():
    global game_state
    game_state = "game"


def retry_game():
    global main_town_coords, flag_buy_menu, farm_flag, warrior_flag, board, main_town, warriors, enemies, lose_flag, game_state, map_, sms, chet
    main_town_coords = ()
    flag_buy_menu = False
    farm_flag, warrior_flag = False, 0
    pg.init()
    board = [[0] * 100 for _ in range(100)]
    main_town = MyTown(100, 10, screen, 7)
    warriors = []
    enemies = []
    lose_flag = False
    game_state = "game"
    map_ = Map(100, 100)
    sms = ""
    chet = 0


def main():
    global game_state
    next_move = Button(200, 80, (42, 94, 131), (70, 121, 157), screen)
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or lose_flag:
                running = False
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    map_.get_click(event.pos)
                if event.button == 4:
                    map_.focus_camera(1)
                if event.button == 5:
                    map_.focus_camera(-1)
        if game_state == "start_menu":
            draw_start_menu()
            start = Button(300, 100, (200, 200, 200), (230, 230, 230), screen)
            start.draw(50, 50, "СТАРТ", start_game)
        if game_state == "lose":
            screen.fill((0, 0, 0))
            print_text("Вы проиграли", (255, 255, 255), (50, 200))
            print_text(f"Вы смогли продержаться:{chet} ходов", (255, 255, 255), (50, 225))

            start = Button(300, 100, (200, 200, 200), (230, 230, 230), screen)
            start.draw(50, 50, "Начать заново", retry_game)
        if game_state == "win":
            screen.fill((0, 204, 204))
            print_text("Вы выиграли!", (255, 255, 255), (50, 200))
            print_text(f"Вам понадобилось {chet} ходов", (255, 255, 255), (50, 225))
        if game_state == "game":
            keys = pg.key.get_pressed()
            map_.move_camera(keys, pg.mouse.get_pos())
            screen.fill((0, 204, 204))
            map_.update(keys)
            for i in warriors:
                if i.radius_flag:
                    i.print_radius()
            pg.draw.rect(screen, (131, 79, 42), (0, 970, 2000, 110))
            next_move.draw(1700, 985, "Следующий ход", next_move_def)
            main_town.print_money()
            if flag_buy_menu:
                buy_menu()
            if farm_flag:
                pg.draw.rect(screen, (252, 186, 3), (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 30, 30))
            if warrior_flag:
                pg.draw.rect(screen, (252, 23, 3), (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 15, 30))
            print_text(sms, (0, 0, 0), (1000, 1020))
        pg.display.flip()
        clock.tick(FPS)
    pg.quit()


if __name__ == "__main__":
    main()
