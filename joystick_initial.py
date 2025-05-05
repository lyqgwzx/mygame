import pygame

def joystick_initial():
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
    return joystick_x,joystick_y,right_joy_x,right_joy_y

def initialize_joystick():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return joystick
    else:
        return None
