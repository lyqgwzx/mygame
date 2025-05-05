import pygame
import os

class House:
    def __init__(self, image_folder, x, y, screen, collision_offsets, hp=100, is_collidable=True, scale=0.2, angle=0):
        self.image_folder = image_folder
        self.screen = screen
        self.images = []
        self.scale_factor = scale  # 从地图数据中获取缩放比例
        self.angle = angle  # 从地图数据中获取旋转角度
        self.x = x  # 从地图数据中获取位置
        self.y = y
        self.load_images()
        self.current_frame = 0
        self.is_animating = False
        self.animation_speed = 1  # 每隔1帧切换图片
        self.frame_count = 0
        self.is_collidable = is_collidable
        self.collision_rect = None
        self.set_collision_rect(collision_offsets)
        self.is_destroyed = False
        self.hp = hp  # 房子的总生命值
        
    def load_images(self):
        for i in range(1, 61):  # 假设动画有60帧（1-60）
            img_path = os.path.join(self.image_folder, f"{str(i).zfill(5)}.png")
            image = pygame.image.load(img_path).convert_alpha()
            # 缩放图片
            scaled_image = pygame.transform.scale(
                image, 
                (int(image.get_width() * self.scale_factor), int(image.get_height() * self.scale_factor))
            )
            self.images.append(scaled_image)
    
    def set_collision_rect(self, offsets):
        """设置碰撞矩形区域，offsets 参数为(左偏移百分比, 右偏移百分比, 上偏移百分比, 下偏移百分比)"""
        image = self.images[0]
        width = image.get_width()
        height = image.get_height()
        left_offset = int(width * offsets[0])
        right_offset = int(width * (1 - offsets[1]))
        top_offset = int(height * offsets[2])
        bottom_offset = int(height * (1 - offsets[3]))
        self.collision_rect = pygame.Rect(left_offset, top_offset, right_offset - left_offset, bottom_offset - top_offset)

    def start_animation(self):
        self.is_animating = True
        self.current_frame = 0  # 从第0帧开始静止状态

    def update(self):
        if self.is_animating:
            self.frame_count += 1
            if self.frame_count >= self.animation_speed:
                self.frame_count = 0
                self.current_frame += 1
                if self.current_frame >= len(self.images):
                    self.current_frame = 0  # 动画结束后回到第0帧（静止状态）
                    self.is_animating = False

    def draw(self):
        # 处理旋转
        rotated_image = pygame.transform.rotate(self.images[self.current_frame], self.angle)
        
        # 获取图像的矩形对象以计算其放置位置
        rect = rotated_image.get_rect(center=(self.x, self.y))
        
        # 绘制图片
        self.screen.blit(rotated_image, rect.topleft)
        
        # 重新计算并绘制碰撞范围
        if self.is_collidable and self.collision_rect:
            # 将碰撞框与当前的位置、缩放、旋转相匹配
            collision_rect = self.collision_rect.copy()
            collision_rect.x = self.x - rect.width // 2 + self.collision_rect.x
            collision_rect.y = self.y - rect.height // 2 + self.collision_rect.y
            
            pygame.draw.rect(self.screen, (255, 0, 0), collision_rect, 2)

    def check_collision(self, player_rect):
        """检查与玩家的碰撞"""
        if self.is_collidable and self.collision_rect.colliderect(player_rect):
            return True
        return False

    def interact_with_player(self, player):
        """定义与玩家的交互逻辑"""
        if self.check_collision(player.rect):
            # 在这里添加与玩家的交互逻辑，例如减少玩家生命值或触发其他事件
            print("Interacted with player!")

    def take_damage(self, damage):
        """承受伤害并减少生命值"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.play_destroy_animation()  # 生命值为0时播放摧毁动画
            print("House is destroyed!")

    def play_destroy_animation(self):
        """播放被摧毁的动画"""
        self.is_animating = True
        self.current_frame = 0  # 重新开始播放动画
        self.is_destroyed = True  # 标记为摧毁状态

    def update_and_destroy(self):
        """更新动画并在结束时销毁对象"""
        self.update()
        if self.is_destroyed and not self.is_animating:
            self.destroy()

    def destroy(self):
        """销毁该实例的内存"""
        print("House instance destroyed")
        # 你不能在Python中显式调用del self，只能依靠Python的垃圾回收机制
        # 在需要时可以将该实例从包含它的列表或字典中删除，这样它会被自动销毁

# Pygame 主循环示例
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
collision_offsets = (0.1, 0.1, 0.1, 0)  # 设置碰撞区域的偏移百分比
house = House("/Users/liya/Documents/编程文件/我的游戏/我的肉鸽子游戏/resources/动画/房子开门关门/房子动画", 400, 300, screen, collision_offsets)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # 按空格键开始动画
                house.start_animation()
            if event.key == pygame.K_d:  # 按 'd' 键模拟承受伤害
                house.take_damage(10)

    screen.fill((0, 0, 0))  # 清屏
    house.update_and_destroy()  # 更新动画并检测是否需要销毁
    house.draw()

    pygame.display.flip()
    clock.tick(60)  # 保持每秒60帧

pygame.quit()
