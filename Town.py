import pygame as pg

def print_text(message, color, coords, screen):
    font = pg.font.Font(None, 30)
    text_button = font.render(str(message), False, color)
    screen.blit(text_button, coords)

class Town:
    def __init__(self, money, money_for_move, screen):
        self.money = money
        self.money_for_move = money_for_move
        self.screen = screen

    def update_money(self):
        self.money += self.money_for_move

    def buy(self, price):
        self.money -= price
    def print_money(self):
        pg.draw.rect(self.screen, (213, 160, 51), (10, 985, 150, 80))
        print_text(self.money, (18, 41, 57), (20, 1012), self.screen)