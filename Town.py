import pygame as pg
from random import choice, randint


def print_text(message, color, coords, screen):
    font = pg.font.Font(None, 30)
    text_button = font.render(str(message), False, color)
    screen.blit(text_button, coords)


class Town:
    def __init__(self, money, money_for_move, screen, number):
        self.money = money
        self.money_for_move = money_for_move
        self.screen = screen
        self.number = number

    def update_money(self):
        self.money += self.money_for_move

    def buy(self, price):
        self.money -= price


class MyTown(Town):
    def print_money(self):
        pg.draw.rect(self.screen, (213, 160, 51), (10, 985, 150, 80))
        print_text(self.money, (18, 41, 57), (20, 1012), self.screen)


class EnemyTown(Town):
    def __init__(self, money, money_for_move, color, x, y, screen, number, board, enemises):
        self.color = color
        self.money = money
        self.money_for_move = money_for_move
        self.screen = screen
        self.x = x
        self.y = y
        self.number = number
        self.border = []
        self.board = board
        self.tacktik = (False, False)
        self.enemies = enemises

    def update_border(self):
        for y in range(99):
            for x in range(99):
                if self.board[y][x] == 4 or self.board[y][x] == 9:
                    for i in range(-2, 3):
                        for j in range(-2, 3):
                            if 0 <= y + i <= 99 and 0 <= x + j <= 99:
                                self.border.append((self.x + i, self.y + j))
        self.border.append((self.x, self.y))
        for i in self.enemies:
            for j in self.border:
                if j in i.border and i.number != self.number:
                    self.border.remove(j)
    def update_coords(self):
        coords = choice(self.border)
        return coords

    def generate_move(self):
        what = randint(1, 4)
        flag = True
        while flag:
            coords = self.update_coords()
            if self.board[coords[1]][coords[0]] == 0:
                flag = False
        if what == 1 and self.money >= 50:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if 0 <= coords[0] + i < 99 and 0 <= coords[1] + j <= 99:
                        self.border.append((coords[0] + i, coords[1] + j))
            self.buy(50)
            self.money_for_move += 10
            return coords, "farm"
        elif what == 2:
            return self.set_warrior(coords)
        if self.tacktik:
            pass

        return False, False
    def set_warrior(self, coords):
        if self.money >= 300 and self.money_for_move - 50 > 0:
            self.money -= 300
            self.money_for_move -= 50
            return coords, "warrior4"
        if self.money >= 170 and self.money_for_move - 30 > 0:
            self.money -= 170
            self.money_for_move -= 30
            return coords, "warrior3"
        if self.money >= 100 and self.money_for_move - 20 > 0:
            self.money -= 100
            self.money_for_move -= 20
            return coords, "warrior2"
        if self.money >= 50 and self.money_for_move - 10 > 0:
            self.money -= 50
            self.money_for_move -= 10
            return coords, "warrior1"
        return False, False

    def lose(self):
        self.border.clear()
