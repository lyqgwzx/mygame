# 这个缓冲区图层我们就用来绘制世界地图 因为我们的游戏主要分为几个窗口 首先是最底层的窗口 第二就是缓冲层 然后第三就是那些提示信息层 现在我们先来绘制缓冲层 缓冲层就是包括房子,玩家

import pygame
from settings_constant import Settings

class BufferSurfaceLayer:
    def __init__(self):
        self.settings = Settings
        self.world_width = self.settings.world_width
        self.world_height = self.settings.world_height
        # 创建一个缓冲表面
        self.buffer_surface = pygame.Surface((self.world_width, self.world_height))
        # 设置背景颜色
        self.backgroundcolor = self.settings.colors["white"]

        self.objects = []

    # 把loadmap.py中加载的地图加载到这里
    def load_map(self, map):
        self.map = map

    # 添加要素
    def add_object(self,obj):
        self.objects.append(obj)

    # 移除要素
    def remove_object(self,obj):
        self.objects.remove(obj)

    # 更新要素
    def update_objects(self):
        for obj in self.objects:
            obj.update()

    # 绘制要素
    def draw_objects(self):
        for obj in self.objects:
            obj.draw(surface=self.buffer_surface)

    # 绘制玩家
    def draw_player(self,player):
        player.draw(surface=self.buffer_surface)

    # 绘制房子
    def draw_house(self,house):
        house.draw(surface=self.buffer_surface)

    # 绘制玩家和房子
    def draw_player_house(self,player,houses):
        self.buffer_surface.fill(Settings.colors["white"])
        self.draw_player(player)
        self.draw_house(houses)

    # 绘制房子内的物品
    def draw_house_item(self,house,house_dict):
        house.draw_equip(self.buffer_surface,house_dict)

    # 渲染
    def render(self, screen, camera_pos):
        screen.blit(self.buffer_surface, (0, 0), (camera_pos[0], camera_pos[1], screen.get_width(), screen.get_height()))


if __name__ == "__main__":
    from house import House
    from player import Player
    # 生成800 600的游戏测试窗口来检查房子是否正常生成
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
    screen = pygame.display.set_mode((800, 600))

    pygame.display.set_caption("缓冲层测试")
    house = House()
    player = Player(houses=house.houses)
    buffer_surface_layer = BufferSurfaceLayer()

    # 创建时钟对象以控制帧率
    clock = pygame.time.Clock()

    # 游戏循环
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
        screen.fill(Settings.colors["white"])
        buffer_surface_layer.draw_player_house(player,house)
        buffer_surface_layer.render(screen,[800,600])
        pygame.display.flip()
        # 控制帧率
        clock.tick(60)
