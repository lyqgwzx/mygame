

# 初始化Pygame
pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 创建天鹅对象
swan = Swan(image_folder="swan", x=400, y=300, screen=screen)

# 游戏主循环
running = True
while running:
    screen.fill((0, 0, 0))

    # 更新天鹅动画
    swan.update()

    # 绘制天鹅
    swan.draw()

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:  # 按下 W 键播放走路动画
                swan.start_animation('walking')
            elif event.key == pygame.K_f:  # 按下 F 键播放飞翔动画
                swan.start_animation('flying')

    # 更新屏幕
    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()