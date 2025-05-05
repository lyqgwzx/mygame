import pygame.image
import math

from settings_constant import Settings

class Gun:
    def __init__(self):
        self.settings = Settings
        self.image = pygame.image.load('resources/gun.png')
        self.image = pygame.transform.scale(self.image, (self.settings.gun_length, self.settings.gun_length // 2))
        self.angle = math.pi / 2
        self.gun_image = pygame.transform.rotate(self.image, -180)
        self.last_shot_time = 0 # 上一次射击的时间
        self.attack_speed = self.settings.attack_speed
        self.gun_x = 0
        self.gun_y = 0

        # 设置攻击速度变量（每秒攻击次数）
        self.attack_speed = 2.0  # 你可以根据需要调整这个值

        self.alive = True

    def shoot(self):
        # 限制射速
        if pygame.time.get_ticks() - self.last_shot_time >= 1000 / self.attack_speed:
            self.last_shot_time = pygame.time.get_ticks()
            return True
    def update(self, right_joy_x, right_joy_y,player_position):
        # 更新位置
        self.gun_x = player_position[0] + self.settings.gun_length * math.cos(self.angle)
        self.gun_y = player_position[1] + self.settings.gun_length * math.sin(self.angle)
        # 更新方向
        # 使用右摇杆控制枪口方向
        if abs(right_joy_x) > 0.1 or abs(right_joy_y) > 0.1:
            self.angle = math.atan2(right_joy_y, right_joy_x)
        else:
            # 否则默认朝向正上方
            self.angle = - math.pi / 2

    def draw(self, surface):

        rotated_gun_image = pygame.transform.rotate(self.gun_image, -math.degrees(self.angle))
        gun_rect = rotated_gun_image.get_rect(center=(self.gun_x, self.gun_y))
        surface.blit(rotated_gun_image, gun_rect.topleft)

if __name__ == '__main__':
    pygame.init()

    # 设置屏幕尺寸和标题
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("枪支测试")

    gun = Gun()

    # 玩家位置初始化
    player_position = [screen_width // 2, screen_height // 2]

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(Settings.colors["white"])
        gun.draw(screen)
        pygame.display.flip()
        clock.tick(60)

        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 模拟右摇杆的输入（可以用键盘输入来模拟）
            keys = pygame.key.get_pressed()
            right_joy_x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]  # 左右键模拟水平输入
            right_joy_y = keys[pygame.K_DOWN] - keys[pygame.K_UP]  # 上下键模拟垂直输入

            # 更新枪口方向
            gun.update(right_joy_x, right_joy_y, player_position)

            # 绘制
            screen.fill((255, 255, 255))  # 清屏
            gun.draw(screen)  # 绘制枪支
            pygame.display.flip()

            clock.tick(60)  # 控制帧率

        pygame.quit()