import pygame
from settings_constant import Settings
import random
from utils import is_colliding_with_houses
import math
from gun import Gun

class Player:
    def __init__(self, houses):
        self.settings = Settings()
        # 大小 颜色 和速度
        self.size = self.settings.player_size
        self.color = self.settings.player_color
        self.speed = self.settings.player_speed

        # 加载玩家图像
        self.load_images()

        # 全图位置和视图位置
        self.position = self.get_initial_position(houses=houses)
        self.rect = self.get_self_rect(self.position)

        self.screen_position = None

        self.inventory = [None] * 3
        self.direction = math.pi / 2

        # 移动方向
        self.move_x = 0
        self.move_y = 0

        self.alive = True

        # 初始化枪支
        self.gun = Gun()
        print(self.rect)

    # 获得rect
    def get_self_rect(self,position):
        return self.current_image.get_rect(center=(int(round(position[0])), int(round(position[1]))))

    def load_images(self):
        # 单独的方法来加载图像资源
        self.back_image = pygame.transform.scale(pygame.image.load('resources/back.png'), (42, 93))
        self.man_image = pygame.transform.scale(pygame.image.load('resources/man.png'), (42, 93))
        self.flipped_man_image = pygame.transform.flip(self.man_image, True, False)
        self.current_image = self.man_image

    def update(self, joystick_x, joystick_y):
        # 更新动画和位置
        # 更新动画
        if self.move_y < 0:
            self.current_image = self.back_image
        elif self.move_x > 0:
            self.current_image = self.flipped_man_image
        else:
            self.current_image = self.man_image

        # 更新位置
        # 添加手柄支持
        self.move_x = joystick_x if abs(joystick_x) > 0.1 else 0
        self.move_y = joystick_y if abs(joystick_y) > 0.1 else 0

        self.position[0] += self.move_x * self.speed
        self.position[1] += self.move_y * self.speed

        # 确保主角在世界边界内移动
        self.position[0] = max(self.rect.size[0] // 2, min(self.position[0], self.settings.world_width - self.rect.size[0] // 2))
        self.position[1] = max(self.rect.size[1] // 2, min(self.position[1], self.settings.world_height - self.rect.size[1] // 2))

    # 随机生成玩家初始位置
    def get_initial_position(self, houses):
        if houses != None:
            while True:
                player_pos = self.generate_random_position()
                player_rect = self.get_self_rect(position=player_pos)
                if not is_colliding_with_houses(player_rect=player_rect, houses=houses):
                    break
            self.position = player_pos
            return player_pos
        else:
            return [400, 400]

    def generate_random_position(self):
        return [random.randint(self.size // 2, self.settings.world_width - self.size // 2),
                random.randint(self.size // 2, self.settings.world_height - self.size // 2)]

    # 玩家获取房子里的物品
    def get_equips(self, equip):
        for i in range(3):
            if self.inventory[i] is None:
                self.inventory[i] = equip
                return


    # 画玩家
    def draw(self, surface):
        player_rect = self.get_self_rect(self.position)
        surface.blit(self.current_image, player_rect.topleft)

if __name__ == "__main__":
    from joystick_initial import joystick_initial

    # 初始化手柄
    # 初始化 Pygame
    pygame.init()

    # 初始化手柄
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        print('已经连接到了手柄哦')
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    joystick_x, joystick_y = 0, 0  # 初始化手柄左摇杆坐标
    right_joy_x, right_joy_y = 0, 0  # 初始化右摇杆坐标
    screen = pygame.display.set_mode((800, 600), pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA,
                                     vsync=1)
    pygame.display.set_caption("玩家测试")
    player = Player(houses=None)
    print(player.position)
    # 创建时钟对象以控制帧率
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    joystick_x = event.value
                elif event.axis == 1:
                    joystick_y = event.value
                elif event.axis == 2:  # 右摇杆X轴
                    right_joy_x = event.value
                elif event.axis == 3:  # 右摇杆Y轴
                    right_joy_y = event.value

        screen.fill(player.settings.colors["white"])
        player.update(joystick_x=joystick_x,joystick_y=joystick_y)
        player.draw(screen)
        pygame.display.flip()
        # 控制帧率
        clock.tick(60)
