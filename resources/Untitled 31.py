import pygame
import math
import os
import json

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸和模式
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

# 定义世界的大小
world_width, world_height = 3200, 2400

# 摄像机的初始位置
camera_pos = [0, 0]

# 定义角色
player_size = 50
player_color = GREEN
player_speed = 5
player_pos = [100, 100]

# 定义资源路径
resource_path = "地图编辑器的元素类型/"

# 加载图片资源并预先计算不同大小的图像
def load_scaled_images(image_path):
    original_image = pygame.image.load(image_path).convert_alpha()
    sizes = [1.0, 0.75, 0.5, 0.25]
    return {scale: pygame.transform.scale(original_image, 
                                          (int(original_image.get_width() * scale), 
                                           int(original_image.get_height() * scale)))
            for scale in sizes}

# 动态加载所有地皮元素
tile_images = {}
for file_name in os.listdir(resource_path):
    if file_name.endswith(".png"):
        name = file_name.split(".")[0]  # 使用文件名作为元素名称
        tile_images[name] = load_scaled_images(os.path.join(resource_path, file_name))

# 加载地图
def load_map(filename):
    global map_tiles
    with open(filename, 'r') as f:
        map_data = json.load(f)
    map_tiles = []
    for tile_data in map_data:
        tile_rect = pygame.Rect(tile_data["x"], tile_data["y"], 
                                tile_images[tile_data["tile"]][tile_data["scale"]].get_width(), 
                                tile_images[tile_data["tile"]][tile_data["scale"]].get_height())
        map_tiles.append({
            "tile": tile_data["tile"], 
            "rect": tile_rect, 
            "scale": tile_data["scale"], 
            "angle": tile_data["angle"], 
            "selected": False
        })

# 初始化地图
map_tiles = []
load_map("saved_map_2024年08月18日13点29.json")

# 游戏循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    new_player_pos = player_pos[:]
    if keys[pygame.K_w]:
        new_player_pos[1] -= player_speed
    if keys[pygame.K_s]:
        new_player_pos[1] += player_speed
    if keys[pygame.K_a]:
        new_player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        new_player_pos[0] += player_speed
    
    # 确保主角在世界边界内移动
    new_player_pos[0] = max(player_size // 2, min(new_player_pos[0], world_width - player_size // 2))
    new_player_pos[1] = max(player_size // 2, min(new_player_pos[1], world_height - player_size // 2))

    player_pos = new_player_pos

    # 更新摄像机位置
    camera_pos[0] = player_pos[0] - screen_width // 2
    camera_pos[1] = player_pos[1] - screen_height // 2

    camera_pos[0] = max(0, min(camera_pos[0], world_width - screen_width))
    camera_pos[1] = max(0, min(camera_pos[1], world_height - screen_height))

    player_screen_pos = [player_pos[0] - camera_pos[0], player_pos[1] - camera_pos[1]]

    # 清屏
    buffer_surface.fill(BLACK)

    # 绘制地图元素
    for tile in map_tiles:
        rotated_image = pygame.transform.rotate(tile_images[tile["tile"]][tile["scale"]], tile["angle"])
        screen.blit(rotated_image, tile["rect"].move(-camera_pos[0], -camera_pos[1]))

    # 绘制角色
    pygame.draw.circle(buffer_surface, player_color, player_screen_pos, player_size // 2)

    # 更新屏幕
    screen.blit(buffer_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
