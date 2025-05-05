import pygame
from utils import is_overlapping
import random
from settings_constant import Settings

class StreetLight:
    def __init__(self, x, y):
        self.Settings = Settings
        self.rect = pygame.Rect(x, y, 40, 40)  # 路灯的大小为40x40
        self.image = pygame.image.load("resources/street lights1.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 10, self.image.get_height() // 10))

    def create_streetlights(self):
        for _ in range(num_street_lights):
            while True:
                light_x = random.randint(0, world_width - 40)
                light_y = random.randint(0, world_height - 40)
                new_light = StreetLight(light_x, light_y)
                if not is_overlapping(new_light.rect, houses) and not new_light.rect.colliderect(player_rect):
                    street_lights.append(new_light)
                    break
