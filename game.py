import pygame
import math
from settings_constant import Settings
from player import Player
from camera_system import Camera
from world_map_layer import BufferSurfaceLayer
from house import House
from utils import is_colliding_with_houses
from fog_layer import FogLayer
from UI_text_layer import UITextLayer
from bullet import Bullet
from gun import Gun

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸和模式，启用 vsync
screen_width, screen_height = Settings.screen_width, Settings.screen_height
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA, vsync=1)
pygame.display.set_caption("角色打枪游戏")

# 初始化手柄
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
if joystick_count > 0:
    print('已经连接到了手柄哦')
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

joystick_x, joystick_y = 0, 0  # 初始化手柄左摇杆坐标
right_joy_x, right_joy_y = 0, 0  # 初始化右摇杆坐标

# 创建时钟对象以控制帧率
clock = pygame.time.Clock()

# 当前物品
current_item = None
# 当前碰撞的房子
colliding_house = None
# 在初始化部分增加一个变量来跟踪 R2 扳机的状态
trigger_fired = False
# 记录下上一次攻击的时间
time_since_last_attack = 0
attack_speed = Settings.attack_speed

# 初始化所有对象
house = House()
player = Player(houses=house.houses)
player_gun = Gun()

buffer_surface_layer = BufferSurfaceLayer()
fog_layer = FogLayer()
camera = Camera()
ui_text_layer = UITextLayer()

# 子弹存储列表
bullets = []

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
            elif event.axis == 5:  # R2 扳机
                if event.value > 0.9 and not trigger_fired:  # 检查扳机是否完全按下并且之前未触发
                    trigger_fired = True
                    if current_item == "霰弹枪":
                        if time_since_last_attack >= 1.0 / attack_speed:
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

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 2:  # 正方形按键的按钮编号为2
                if current_item:
                    for i in range(3):
                        if player.inventory[i] is None:
                            player.inventory[i] = current_item
                            colliding_house["equip"] = None
                            break

    time_since_last_attack += clock.get_time() / 1000.0
    # 逻辑更新
    old_player_position = player.position[:]

    player.update(joystick_x, joystick_y)

    new_player_position = player.position[:]

    new_rect = player.get_self_rect(new_player_position)
    colliding_house = is_colliding_with_houses(houses=house.houses,player_rect=new_rect)

    if not colliding_house:
        player.position = new_player_position
        # current_item = None
    else:
        player.position = old_player_position
        current_item = colliding_house["equip"]

    player_position_copy = player.position[:]
    camera_pos = camera.update(player.position)

    player_screen_pos = [player.position[0] - camera_pos[0], player.position[1] - camera_pos[1]]
    player.screen_position = player_screen_pos
    fog_layer.update(player, fog_alpha=True)

    angle = player_gun.angle  # 枪的角度

    # 3. 绘制
    #   3.1 刷新背景
    screen.fill(Settings.colors["white"])

    #   3.2 绘制缓冲层
    #       3.2.1 绘制玩家和房子
    buffer_surface_layer.draw_player_house(player, house)


    #       3.2.2 绘制当前物品
    if colliding_house and current_item:
        buffer_surface_layer.draw_house_item(house,colliding_house)

    #   3.3 渲染缓冲层到窗口
    buffer_surface_layer.render(screen, camera_pos)

    player_gun.update(right_joy_x=right_joy_x,right_joy_y=right_joy_y,player_position=player.screen_position)
    player_gun.draw(screen)

    #   3.6 绘制子弹
    for bullet in bullets:
        bullet.update()
        if not bullet.alive:
            bullets.remove(bullet)
        bullet.draw(screen)

    #   3.4 绘制迷雾层
    fog_layer.draw(screen)

    #   3.5 绘制UI文本层
    if current_item and colliding_house:
        ui_text_layer.render_item_text(screen, item=current_item, player=player)
    ui_text_layer.render_bag_grid(screen, player.inventory, ui_text_layer.item_images)

    # 4. 刷新窗口
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)
