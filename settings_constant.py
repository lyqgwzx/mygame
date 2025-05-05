# settings_constant.py
import pygame

class Settings:
    colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "green": (0, 255, 0),
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "orange": (255, 165, 0),
        "light_green": (144, 238, 144),
    }

    equip_pics = {
        "蛋糕": pygame.Surface((40, 40)),
        "霰弹枪": pygame.Surface((40, 10)),
    }
    equip_pics["蛋糕"].fill(colors["orange"])
    equip_pics["霰弹枪"].fill(colors["yellow"])

    player_size = 50
    player_color = colors["green"]
    player_speed = 5

    view_radius = 2 * player_size

    world_width, world_height = 3200, 2400

    screen_width, screen_height = 1200, 800

    gun_length = 40

    houses = []
    nums_house = 10
    size_house = 100

    font_path = "/Users/shiqi/Documents/编程文件/我的游戏/我的肉鸽子游戏/resources/XiangJiaoDaJiangJunLingGanTi-2.ttf"

    # 子弹的设定
    max_distance = 300
    bullet_speed = 10
    attack_speed = 5.0

    # 环境资源的图片和动画序列帧
    # environment = {
    #     "tree": pygame.image.load("tree.png"),
    #     "rock": pygame.image.load("rock.png"),
    #     "water": pygame.image.load("water.png"),
    # }