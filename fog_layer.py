import pygame
from settings_constant import Settings

# 战争迷雾层
class FogLayer:
    def __init__(self):
        self.settings = Settings
        self.fog_of_war = pygame.Surface((self.settings.screen_width, self.settings.screen_height))
        self.fog_of_war.fill(self.settings.colors["black"])

    # 在主角的视野范围内创建一个白色的圆来清除战争迷雾
    def update(self, player, fog_alpha=False):
        self.fog_of_war.fill(self.settings.colors["black"])
        pygame.draw.circle(self.fog_of_war, self.settings.colors["white"], (player.screen_position[0],player.screen_position[1] - player.size // 2), self.settings.view_radius)
        if fog_alpha:
            self.fog_of_war.set_alpha(200)
        # 将战争迷雾表面设置为透明
        self.fog_of_war.set_colorkey(self.settings.colors["white"])

    # 渲染
    def draw(self, target_screen):
        target_screen.blit(self.fog_of_war, (0, 0))