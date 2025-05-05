#   显示提示文字层，用于显示游戏中的提示信息，如得分、游戏结束等，层级最高，覆盖在所有层之上，背景必须是透明的

import pygame
from settings_constant import Settings

class UITextLayer:
    def __init__(self):
        self.settings = Settings
        self.font_path = self.settings.font_path
        self.font = pygame.font.Font(self.font_path, 24)
        self.color = self.settings.colors["red"]
        self.item_images = self.settings.equip_pics

    # 渲染物品文字
    def render_item_text(self, screen, item,player):
        self.text = "当前物品"+ item
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (player.screen_position[0], player.screen_position[1] - player.size // 2 - self.text_rect.height)
        screen.blit(self.text_surface, self.text_rect)
        # print("Text rendered successfully")

    # 渲染背包格子
    def render_bag_grid(self,screen,inventory,item_images,):
        # 绘制背包格子
        for i in range(3):
            pygame.draw.rect(screen, self.settings.colors["light_green"], (10, 100 + i * 60, 50, 50), 5)
            if inventory[i] is not None:
                if inventory[i] == "蛋糕":
                    screen.blit(item_images["蛋糕"], (10 + 5, 100 + i * 60 + 5))  # 图像偏移以适应格子
                elif inventory[i] == "霰弹枪":
                    screen.blit(item_images["霰弹枪"], (10 + 5, 100 + i * 60 + 20))  # 垂直居中
