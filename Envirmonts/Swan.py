import pygame
import os

class Swan:
    def __init__(self, image_folder, x, y, screen, hp=100, scale=0.2, angle=0):
        self.image_folder = image_folder
        self.screen = screen
        self.scale_factor = scale
        self.angle = angle
        self.x = x
        self.y = y
        self.hp = hp
        self.is_destroyed = False
        
        # 存储多个动画
        self.animations = {
            'walking': [],  # 走路动画
            'flying': []    # 飞翔动画
        }
        
        # 默认当前动画为走路动画
        self.current_animation = 'walking'
        self.current_frame = 0
        self.is_animating = True
        self.animation_speed = 5  # 调整动画切换速度 (每5帧切换一次)
        self.frame_count = 0

        # 加载动画帧
        self.load_images()

    def load_images(self):
        # 加载不同的动画帧
        for animation_name in self.animations:
            animation_folder = os.path.join(self.image_folder, animation_name)
            if not os.path.exists(animation_folder):
                print(f"动画文件夹 '{animation_folder}' 不存在")
                continue

            for i in range(1, 61):  # 假设每个动画有60帧
                img_path = os.path.join(animation_folder, f"{str(i).zfill(5)}.png")
                if os.path.exists(img_path):
                    image = pygame.image.load(img_path).convert_alpha()
                    scaled_image = pygame.transform.smoothscale(
                        image, 
                        (int(image.get_width() * self.scale_factor), int(image.get_height() * self.scale_factor))
                    )
                    self.animations[animation_name].append(scaled_image)
                else:
                    print(f"图片 '{img_path}' 不存在")

    def start_animation(self, animation_name):
        """切换到指定动画"""
        if animation_name in self.animations and len(self.animations[animation_name]) > 0:
            self.current_animation = animation_name
            self.current_frame = 0  # 重置帧数
            self.is_animating = True
            print(f"切换到动画：{animation_name}")
        else:
            print(f"动画 '{animation_name}' 未找到或没有加载帧")

    def update(self):
        if self.is_animating:
            self.frame_count += 1
            if self.frame_count >= self.animation_speed:
                self.frame_count = 0
                self.current_frame += 1
                if self.current_frame >= len(self.animations[self.current_animation]):
                    self.current_frame = 0  # 循环播放

    def draw(self):
        # 获取当前帧
        if self.current_animation in self.animations:
            current_images = self.animations[self.current_animation]
            if current_images:
                rotated_image = pygame.transform.rotate(current_images[self.current_frame], self.angle)
                rect = rotated_image.get_rect(center=(self.x, self.y))
                self.screen.blit(rotated_image, rect.topleft)
            else:
                print(f"动画 '{self.current_animation}' 没有帧图像")
        else:
            print(f"动画 '{self.current_animation}' 不存在")

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.start_animation('destroy')  # 切换到摧毁动画
            print("Swan is destroyed!")


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