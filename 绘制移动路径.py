import pygame
import sys

# 初始化pygame
pygame.init()

# 设置屏幕尺寸
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# 路径点列表
path = []
drawing = False  # 是否正在绘制路径
running = True
index = 0  # 路径点的索引

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True  # 开始绘制路径
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                index = 0  # 重置路径点索引

    # 如果正在绘制路径，记录鼠标位置
    if drawing:
        position = pygame.mouse.get_pos()
        path.append(position)

    # 清屏
    screen.fill(WHITE)

    # 如果路径点至少有两个，则绘制路径
    if len(path) > 1:
        pygame.draw.lines(screen, BLUE, False, path, 3)

    # 如果有足够的路径点，并且空格已按下，绘制移动的圆
    if index < len(path):
        pygame.draw.circle(screen, BLUE, path[index], 10)
        index += 1  # 移动到路径的下一个点

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
