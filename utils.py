import pygame
import numpy as np

def screen_print(screen, text, color, x, y, size=30, font="Segoe UI Symbol"):

    text_font = pygame.font.SysFont(font, size)
    text_body = text_font.render(text, False, color)
    screen.blit(text_body, (x, y))

