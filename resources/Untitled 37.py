#!/usr/bin/env python3

import pygame
import math
import random

# 初始化 Pygame
pygame.init()

# 初始化手柄
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
# 设置屏幕尺寸和模式，启用 vsync
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA, vsync=1)
pygame.display.set_caption("角色打枪游戏")

# 创建一个缓冲表面
buffer_surface = pygame.Surface((screen_width, screen_height))

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_GREEN = (144, 238, 144)
view_radius = 100

# 创建物品形状
item_images = {
    "蛋糕": pygame.Surface((40, 40)),
    "霰弹枪": pygame.Surface((40, 10)),
}
item_images["蛋糕"].fill(ORANGE)
item_images["霰弹枪"].fill(YELLOW)

# 定义角色
player_size = 50
player_color = GREEN
player_speed = 5

# 定义世界的大小
world_width, world_height = 1600, 1200

# 摄像机的初始位置
camera_pos = [0, 0]

# 初始化玩家位置
player_pos = [random.randint(player_size // 2, world_width - player_size // 2),
              random.randint(player_size // 2, world_height - player_size // 2)]
player_rect = pygame.Rect(player_pos[0] - player_size // 2, player_pos[1] - player_size // 2, player_size, player_size)

# 子弹类定义
class Bullet:
    def __init__(self, x, y, angle, speed=10, max_distance=300):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.alive = True
        self.distance_travelled = 0
        self.max_distance = max_distance
        self.start_x = x
        self.start_y = y

    def update(self):
        if self.alive:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            self.distance_travelled = math.sqrt((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2)
            # 判断子弹是否超出屏幕或移动超过最大距离
            if not (0 <= self.x <= world_width and 0 <= self.y <= world_height) or self.distance_travelled > self.max_distance:
                self.alive = False

    def draw(self, surface):
        if self.alive:
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 5)

# 子弹存储列表
bullets = []

# 游戏循环标志
running = True
joystick_x, joystick_y = 0, 0  # 初始化手柄左摇杆坐标
right_joy_x, right_joy_y = 0, 0  # 初始化右摇杆坐标

# 初始化当前物品和背包
current_item = None
inventory = [None, None, None]  # 背包中只能装三个物品

# 创建时钟对象以控制帧率
clock = pygame.time.Clock()

# 在初始化部分增加一个变量来跟踪 R2 扳机的状态
trigger_fired = False

# 设置攻击速度变量（每秒攻击次数）
attack_speed = 2.0  # 你可以根据需要调整这个值
time_since_last_attack = 0

# 修改游戏循环中处理 R2 扳机的逻辑
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                joystick_x = event.value
            elif event.axis == 1:
                joystick_y = event.value
            elif event.axis == 2:  # 右摇杆X轴
                right_joy_x = event.value
            elif event.axis == 3:  # 右摇杆Y轴
                right_joy_y = event.value
            elif event.axis == 5:  # R2 扳机
                if event.value > 0.9 and not trigger_fired:  # 检查扳机是否完全按下并且之前未触发
                    trigger_fired = True
                    if current_item == "霰弹枪" and time_since_last_attack >= 1.0 / attack_speed:
                        # 发射多个子弹
                        num_bullets = 5  # 一次发射5颗子弹
                        spread_angle = math.pi / 6  # 扇形的总角度
                        base_angle = angle - spread_angle / 2
                        for i in range(num_bullets):
                            bullet_angle = base_angle + (spread_angle / (num_bullets - 1)) * i
                            bullets.append(Bullet(player_screen_pos[0], player_screen_pos[1], bullet_angle))
                        time_since_last_attack = 0
                elif event.value < 0.1:  # 如果扳机被释放，重置触发状态
                    trigger_fired = False
                        
    time_since_last_attack += clock.get_time() / 1000.0

    keys = pygame.key.get_pressed()
    new_player_pos = player_pos[:]
    move_x = keys[pygame.K_d] - keys[pygame.K_a]
    move_y = keys[pygame.K_s] - keys[pygame.K_w]
    
    # 添加手柄支持
    if abs(joystick_x) > 0.1:
        move_x += joystick_x
    if abs(joystick_y) > 0.1:
        move_y += joystick_y
        
    new_player_pos[0] += move_x * player_speed
    new_player_pos[1] += move_y * player_speed
    
    # 确保主角在世界边界内移动
    new_player_pos[0] = max(player_size // 2, min(new_player_pos[0], world_width - player_size // 2))
    new_player_pos[1] = max(player_size // 2, min(new_player_pos[1], world_height - player_size // 2))
    
    # 更新玩家位置
    player_rect = pygame.Rect(new_player_pos[0] - player_size // 2, new_player_pos[1] - player_size // 2, player_size, player_size)
    player_pos = new_player_pos
    
    # 更新摄像机位置，使其跟随玩家但在接近边界时限制其移动
    camera_pos[0] = player_pos[0] - screen_width // 2
    camera_pos[1] = player_pos[1] - screen_height // 2
    
    # 确保摄像机在世界边界内移动
    camera_pos[0] = max(0, min(camera_pos[0], world_width - screen_width))
    camera_pos[1] = max(0, min(camera_pos[1], world_height - screen_height))
    
    # 调整玩家位置，使其在接近边界时不再保持在屏幕中心
    player_screen_pos = [player_pos[0] - camera_pos[0], player_pos[1] - camera_pos[1]]
    
    # 使用右摇杆控制枪口方向
    if abs(right_joy_x) > 0.1 or abs(right_joy_y) > 0.1:
        angle = math.atan2(right_joy_y, right_joy_x)
    else:
        # 如果右摇杆未活动，使用鼠标作为后备
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - screen_height // 2, mouse_x - screen_width // 2)
        
    # 清屏
    buffer_surface.fill(WHITE)
    
    # 创建战争迷雾层
    fog_of_war = pygame.Surface((screen_width, screen_height))
    fog_of_war.fill(BLACK)
    fog_of_war.set_alpha(200)
    
    # 绘制角色
    pygame.draw.circle(buffer_surface, player_color, player_screen_pos, player_size // 2)
    
    # 绘制枪口
    gun_length = 40
    gun_x = player_screen_pos[0] + gun_length * math.cos(angle)
    gun_y = player_screen_pos[1] + gun_length * math.sin(angle)
    pygame.draw.line(buffer_surface, RED, player_screen_pos, (gun_x, gun_y), 5) 
    
    # 绘制子弹
    for bullet in bullets[:]:
        bullet.update()
        if not bullet.alive:
            bullets.remove(bullet)
        bullet.draw(buffer_surface)
        
    # 在主角的视野范围内创建一个白色的圆来清除战争迷雾
    pygame.draw.circle(fog_of_war, WHITE, player_screen_pos, view_radius)
    # 将战争迷雾表面设置为透明
    fog_of_war.set_colorkey(WHITE)
    
    # 显示背包中的物品
    font_path = "/Users/liya/Documents/编程文件/我的游戏/我的肉鸽子游戏/resources/XiangJiaoDaJiangJunLingGanTi-2.ttf"  # Mac系统的中文字体路径
    font = pygame.font.Font(font_path, 24)
    inventory_text = "背包: " + ", ".join([item for item in inventory if item]) if any(inventory) else "背包为空"
    text = font.render(inventory_text, True, BLACK)
    fog_of_war.blit(text, (10, 50))
    
    # 绘制背包格子
    for i in range(3):
        pygame.draw.rect(fog_of_war, LIGHT_GREEN, (10, 100 + i * 60, 50, 50), 5)
        if inventory[i] is not None:
            if inventory[i] == "蛋糕":
                fog_of_war.blit(item_images["蛋糕"], (10 + 5, 100 + i * 60 + 5))  # 图像偏移以适应格子
            elif inventory[i] == "霰弹枪":
                fog_of_war.blit(item_images["霰弹枪"], (10 + 5, 100 + i * 60 + 20))  # 垂直居中
                
    # 更新屏幕
    screen.blit(buffer_surface, (0, 0))
    screen.blit(fog_of_war, (0, 0))
    
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)
    
pygame.quit()
