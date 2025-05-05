import math
from settings_constant import Settings
import pygame

# 子弹类定义
class Bullet:
    def __init__(self, x, y, angle):
        self.settings = Settings()
        self.world_width = self.settings.world_width
        self.world_height = self.settings.world_height
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = self.settings.bullet_speed
        self.alive = True
        self.distance_travelled = 0
        self.max_distance = self.settings.max_distance
        self.start_x = x
        self.start_y = y

    def update(self):
        if self.alive:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            self.distance_travelled = math.sqrt((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2)
            if not (100 <= self.x <= self.world_width and 0 <= self.y <= self.world_height) or self.distance_travelled > self.max_distance:
                self.alive = False

    def draw(self, surface):
        RED = self.settings.colors["red"]
        if self.alive:
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 5)