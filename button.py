import pygame as pg

def print_text(message, color, coords, screen):
    font = pg.font.Font(None, 30)
    text_button = font.render(str(message), False, color)
    screen.blit(text_button, coords)

class Button:
    def __init__(self, width, height, color, active_color, screen):
        self.width = width
        self.height = height
        self.color = color
        self.active_color = active_color
        self.screen = screen

    def draw(self, x, y, text, action=None):
        self.action = action
        self.get_press = False
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pg.draw.rect(self.screen, self.active_color, (x, y, self.width, self.height))
            if click[0] == 1 and action is not None:
                action()
                pg.time.delay(300)

        else:
            pg.draw.rect(self.screen, self.color, (x, y, self.width, self.height))
        print_text(text, (18, 41, 57), (x + 15, y + 30), self.screen)
