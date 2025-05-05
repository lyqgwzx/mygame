import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("地图编辑器")

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LIGHT_GREEN = (144, 238, 144)

# 加载图片资源
resource_path = "地图编辑器的元素类型/"  # 请替换为你的资源路径
tile_images = {
    "草地": pygame.image.load(resource_path + "草地.png"),
    "水泥地": pygame.image.load(resource_path + "道路.png"),
    "鹅卵石路": pygame.image.load(resource_path + "鹅卵石路.png"),
    "房子": pygame.image.load(resource_path + "房子.png"),
    "路灯": pygame.image.load(resource_path + "路灯.png"),
    "树": pygame.image.load(resource_path + "树.png"),
    "灌木": pygame.image.load(resource_path + "灌木.png"),
}

# 定义按钮
button_width, button_height = 100, 50
buttons = {
    "草地": pygame.Rect(10, 50, button_width, button_height),
    "水泥地": pygame.Rect(10, 120, button_width, button_height),
    "鹅卵石路": pygame.Rect(10, 190, button_width, button_height),
    "房子": pygame.Rect(10, 260, button_width, button_height),
    "路灯": pygame.Rect(10, 330, button_width, button_height),
    "树": pygame.Rect(10, 400, button_width, button_height),
    "灌木": pygame.Rect(10, 470, button_width, button_height),
}

# 初始化地图
tile_size = 100
world_width, world_height = 1600, 1200
map_tiles = {}

# 当前选中的地皮类型
current_tile = None

# 摄像机的初始位置
camera_pos = [0, 0]

# 加载中文字体
font_path = "/System/Library/Fonts/PingFang.ttc"  # Mac系统的中文字体路径
font = pygame.font.Font(font_path, 24)

# 游戏循环
running = True
while running:
    screen.fill(BLACK)
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        current_tile = name
                        break
                else:
                    if current_tile:  # 在地图上放置地皮
                        mouse_x, mouse_y = event.pos
                        map_x = (mouse_x + camera_pos[0]) // tile_size * tile_size
                        map_y = (mouse_y + camera_pos[1]) // tile_size * tile_size
                        map_tiles[(map_x, map_y)] = current_tile
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                camera_pos[1] -= 10
            elif event.key == pygame.K_s:
                camera_pos[1] += 10
            elif event.key == pygame.K_a:
                camera_pos[0] -= 10
            elif event.key == pygame.K_d:
                camera_pos[0] += 10

    # 绘制按钮
    for name, rect in buttons.items():
        pygame.draw.rect(screen, LIGHT_GREEN if current_tile == name else WHITE, rect)
        text = font.render(name, True, BLACK)
        screen.blit(text, rect.move(10, 10))

    # 绘制地图
    for (x, y), tile in map_tiles.items():
        tile_rect = pygame.Rect(x - camera_pos[0], y - camera_pos[1], tile_size, tile_size)
        screen.blit(tile_images[tile], tile_rect)
        
    # 显示当前选中的地皮预览
    if current_tile:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        preview_rect = pygame.Rect((mouse_x // tile_size) * tile_size, (mouse_y // tile_size) * tile_size, tile_size, tile_size)
        screen.blit(tile_images[current_tile], preview_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
