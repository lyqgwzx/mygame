import pygame
import sys
import os

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
DARK_GRAY = (50, 50, 50)
SEMI_TRANSPARENT_RED = (255, 0, 0, 128)

# 设置资源路径
resource_path = "地图编辑器的元素类型/"  # 请替换为你的资源路径

# 加载图片资源并预先计算不同大小的图像
def load_scaled_images(image_path):
    original_image = pygame.image.load(image_path)
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

# 动态生成按钮
button_width, button_height = 100, 50  # 按钮初始尺寸
button_margin = 10
buttons = {}
scroll_offset = 0  # 按钮滚动条的偏移量

# 动态生成按钮的布局
def generate_buttons():
    global buttons, button_width, button_height
    buttons = {}
    y_offset = 50 + scroll_offset
    for idx, name in enumerate(tile_images.keys()):
        rect = pygame.Rect(10, y_offset, button_width, button_height)
        buttons[name] = rect
        y_offset += button_height + button_margin

generate_buttons()

# 初始化地图
world_width, world_height = 1600, 1200
map_tiles = []

# 当前选中的地皮类型
current_tile = None
current_scale = 1.0
rotation_angle = 0

# 定义缩放比例
scale_levels = [1.0, 0.75, 0.5, 0.25]

# 摄像机的初始位置
camera_pos = [0, 0]

# 加载中文字体
font_path = "/System/Library/Fonts/PingFang.ttc"  # Mac系统的中文字体路径
font = pygame.font.Font(font_path, 24)

# 设置帧率
clock = pygame.time.Clock()

# 功能状态开关
show_reference_lines = True
show_ui = True

# 获取下一个缩放级别
def get_next_scale(current, direction):
    idx = scale_levels.index(current)
    if direction == 'up' and idx > 0:
        return scale_levels[idx - 1]
    elif direction == 'down' and idx < len(scale_levels) - 1:
        return scale_levels[idx + 1]
    return current

# 在 map_tiles 中移动选中的 tile
def move_tile_down(selected_tile):
    if selected_tile in map_tiles:
        index = map_tiles.index(selected_tile)
        map_tiles.pop(index)
        if index == len(map_tiles):  # 如果已经在最下层
            map_tiles.insert(0, selected_tile)  # 移动到最上层
        else:
            map_tiles.insert(index + 1, selected_tile)  # 否则向下移动一层

# 定义吸附的距离阈值
snap_threshold = 10  # 吸附到参考线的距离
detect_threshold = 50  # 检测是否显示参考线的距离
max_distance_threshold = 500  # 最大考虑距离

def draw_reference_lines(screen, line_positions, camera_pos, color=RED):
    for line_pos in line_positions:
        if line_pos['type'] == 'vertical':
            pygame.draw.line(screen, color, 
                             (line_pos['pos'] - camera_pos[0], 0), 
                             (line_pos['pos'] - camera_pos[0], screen_height), 1)
        elif line_pos['type'] == 'horizontal':
            pygame.draw.line(screen, color, 
                             (0, line_pos['pos'] - camera_pos[1]), 
                             (screen_width, line_pos['pos'] - camera_pos[1]), 1)

# 游戏循环
running = True
w_pressed = False
s_pressed = False
r_pressed = False
tab_pressed = False
selected_tile = None
hovered_tiles = []
hovered_index = 0

while running:
    screen.fill(BLACK)
    
    # 事件处理
    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_in_map = True if 0 <= mouse_x <= screen_width and 0 <= mouse_y <= screen_height else False

    # 存储将要显示的参考线
    reference_lines = []

    if current_tile and show_reference_lines:
        nearest_snap = {"x": None, "y": None}
        for tile in map_tiles:
            tile_rect = tile["rect"]

            # 计算鼠标与元素中心的距离
            distance_to_tile = ((mouse_x + camera_pos[0] - tile_rect.centerx) ** 2 + (mouse_y + camera_pos[1] - tile_rect.centery) ** 2) ** 0.5

            # 只有当距离在阈值范围内时，才考虑该元素的参考线
            if distance_to_tile > max_distance_threshold:
                continue

            # 计算每个方向上的距离
            distances = {
                "left": abs(mouse_x + camera_pos[0] - tile_rect.left),
                "right": abs(mouse_x + camera_pos[0] - tile_rect.right),
                "centerx": abs(mouse_x + camera_pos[0] - tile_rect.centerx),
                "top": abs(mouse_y + camera_pos[1] - tile_rect.top),
                "bottom": abs(mouse_y + camera_pos[1] - tile_rect.bottom),
                "centery": abs(mouse_y + camera_pos[1] - tile_rect.centery)
            }

            # 如果距离在检测阈值范围内，则绘制参考线
            if distances["left"] < detect_threshold:
                reference_lines.append({'type': 'vertical', 'pos': tile_rect.left})
            if distances["right"] < detect_threshold:
                reference_lines.append({'type': 'vertical', 'pos': tile_rect.right})
            if distances["centerx"] < detect_threshold:
                reference_lines.append({'type': 'vertical', 'pos': tile_rect.centerx})
            if distances["top"] < detect_threshold:
                reference_lines.append({'type': 'horizontal', 'pos': tile_rect.top})
            if distances["bottom"] < detect_threshold:
                reference_lines.append({'type': 'horizontal', 'pos': tile_rect.bottom})
            if distances["centery"] < detect_threshold:
                reference_lines.append({'type': 'horizontal', 'pos': tile_rect.centery})

            # 计算最接近的吸附点
            if distances["left"] < snap_threshold:
                nearest_snap["x"] = tile_rect.left
            elif distances["right"] < snap_threshold:
                nearest_snap["x"] = tile_rect.right
            elif distances["centerx"] < snap_threshold:
                nearest_snap["x"] = tile_rect.centerx
            
            if distances["top"] < snap_threshold:
                nearest_snap["y"] = tile_rect.top
            elif distances["bottom"] < snap_threshold:
                nearest_snap["y"] = tile_rect.bottom
            elif distances["centery"] < snap_threshold:
                nearest_snap["y"] = tile_rect.centery

        # 根据最近的吸附点调整鼠标位置
        if nearest_snap["x"] is not None:
            mouse_x = nearest_snap["x"] - camera_pos[0]
        if nearest_snap["y"] is not None:
            mouse_y = nearest_snap["y"] - camera_pos[1]

    # 绘制参考线
    if show_reference_lines:
        draw_reference_lines(screen, reference_lines, camera_pos)

    # 检查鼠标悬停位置下的所有地皮元素，按从上到下顺序排列
    if not current_tile and not (selected_tile and selected_tile['selected']):
        hovered_tiles = []
        for tile in reversed(map_tiles):  # 从最上层元素开始检测
            if tile['rect'].collidepoint(mouse_x + camera_pos[0], mouse_y + camera_pos[1]):
                hovered_tiles.append(tile)
        
        if hovered_tiles:
            hovered_index = hovered_index % len(hovered_tiles)  # 确保 hovered_index 在有效范围内
            selected_tile = hovered_tiles[hovered_index]
        else:
            selected_tile = None
            hovered_index = 0

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                # 优先处理按钮点击
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        current_tile = name
                        current_scale = 1.0  # 重置为初始大小
                        rotation_angle = 0  # 重置旋转角度
                        selected_tile = None
                        break
                else:
                    # 如果没有按钮被点击，再处理地皮选择
                    if not current_tile and selected_tile:
                        selected_tile['selected'] = True
                    elif current_tile:  # 在地图上放置地皮
                        tile_rect = pygame.Rect(mouse_x + camera_pos[0] - tile_images[current_tile][current_scale].get_width() // 2, 
                                                mouse_y + camera_pos[1] - tile_images[current_tile][current_scale].get_height() // 2, 
                                                tile_images[current_tile][current_scale].get_width(), 
                                                tile_images[current_tile][current_scale].get_height())
                        map_tiles.append({"tile": current_tile, "rect": tile_rect, "scale": current_scale, "angle": rotation_angle, "selected": False})
                        selected_tile = None
            elif event.button == 4:  # 滚轮向上
                if scroll_offset < 0:
                    scroll_offset += button_height + button_margin
                    generate_buttons()
            elif event.button == 5:  # 滚轮向下
                if (len(buttons) * (button_height + button_margin)) > screen_height:
                    scroll_offset -= button_height + button_margin
                    generate_buttons()
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_DELETE, pygame.K_BACKSPACE]:
                if event.key == pygame.K_ESCAPE:
                    if selected_tile:
                        selected_tile['selected'] = False
                        selected_tile = None
                    current_tile = None
                if event.key in [pygame.K_DELETE, pygame.K_BACKSPACE]:
                    if selected_tile and selected_tile['selected']:
                        map_tiles.remove(selected_tile)
                        selected_tile = None
                        # 删除后更新 hovered_tiles
                        hovered_tiles = [tile for tile in reversed(map_tiles) if tile['rect'].collidepoint(mouse_x + camera_pos[0], mouse_y + camera_pos[1])]
                        hovered_index = 0 if hovered_tiles else -1
            if event.key == pygame.K_w:
                w_pressed = True
            if event.key == pygame.K_s:
                s_pressed = True
            if event.key == pygame.K_r:
                r_pressed = True
            if event.key == pygame.K_TAB:
                tab_pressed = True
            if event.key == pygame.K_c:
                show_reference_lines = not show_reference_lines  # 切换参考线开关
            if event.key == pygame.K_h:
                show_ui = not show_ui  # 切换界面信息开关
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w and w_pressed:
                current_scale = get_next_scale(current_scale, 'up')
                w_pressed = False
            if event.key == pygame.K_s and s_pressed:
                current_scale = get_next_scale(current_scale, 'down')
                s_pressed = False
            if event.key == pygame.K_r and r_pressed:
                rotation_angle = (rotation_angle + 90) % 360
                r_pressed = False
            if event.key == pygame.K_TAB and tab_pressed:
                if selected_tile and selected_tile['selected']:
                    move_tile_down(selected_tile)  # 移动选中的地皮元素
                else:
                    if hovered_tiles:
                        hovered_index = (hovered_index + 1) % len(hovered_tiles)
                        selected_tile = hovered_tiles[hovered_index]
                tab_pressed = False

    if not current_tile:
        if keys[pygame.K_w]:
            camera_pos[1] -= 10
        if keys[pygame.K_s]:
            camera_pos[1] += 10
        if keys[pygame.K_a]:
            camera_pos[0] -= 10
        if keys[pygame.K_d]:
            camera_pos[0] += 10

    # 边界检查，确保摄像机位置在地图范围内
    camera_pos[0] = max(0, min(camera_pos[0], world_width - screen_width))
    camera_pos[1] = max(0, min(camera_pos[1], world_height - screen_height))

    # 绘制地图上的元素
    for tile in map_tiles:
        rotated_image = pygame.transform.rotate(tile_images[tile["tile"]][tile["scale"]], tile["angle"])
        screen.blit(rotated_image, tile["rect"].move(-camera_pos[0], -camera_pos[1]))

        # 如果该地皮被选中，填充半透明红色
        if tile["selected"]:
            overlay_rect = tile["rect"].move(-camera_pos[0], -camera_pos[1])
            overlay = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            overlay.fill(SEMI_TRANSPARENT_RED)
            screen.blit(overlay, overlay_rect)
        # 如果鼠标悬停在该地皮上，绘制红色边框
        elif selected_tile == tile:
            pygame.draw.rect(screen, RED, tile["rect"].move(-camera_pos[0], -camera_pos[1]), 3)

    # 显示当前选中的地皮预览，保持比例，中心位于鼠标位置
    if current_tile:
        preview_image = pygame.transform.rotate(tile_images[current_tile][current_scale], rotation_angle)
        preview_rect = preview_image.get_rect(center=(mouse_x, mouse_y))
        screen.blit(preview_image, preview_rect)

    # 绘制按钮和界面信息，确保按钮在最上层显示
    if show_ui:
        for name, rect in buttons.items():
            pygame.draw.rect(screen, LIGHT_GREEN if current_tile == name else WHITE, rect)
            text = font.render(name, True, BLACK)
            screen.blit(text, rect.move(10, 10))

        # 显示参考线状态和界面信息状态
        reference_text = f"参考线: {'开' if show_reference_lines else '关'}"
        ui_text = f"界面信息: {'显示' if show_ui else '隐藏'}"
        reference_surface = font.render(reference_text, True, WHITE)
        ui_surface = font.render(ui_text, True, WHITE)
        screen.blit(reference_surface, (screen_width - 200, 10))
        screen.blit(ui_surface, (screen_width - 200, 40))

    # 将小地图绘制到屏幕右下角
    thumbnail_width, thumbnail_height = 200, 150
    thumbnail_surface = pygame.Surface((thumbnail_width, thumbnail_height))
    thumbnail_surface.fill(DARK_GRAY)

    # 绘制地图内容到缩略图
    scale_factor = thumbnail_width / world_width
    for tile in map_tiles:
        thumb_rect = pygame.Rect(tile["rect"].x * scale_factor, tile["rect"].y * scale_factor, 
                                 tile["rect"].width * scale_factor, tile["rect"].height * scale_factor)
        scaled_thumb_image = pygame.transform.scale(tile_images[tile["tile"]][tile["scale"]], (thumb_rect.width, thumb_rect.height))
        rotated_thumb_image = pygame.transform.rotate(scaled_thumb_image, tile["angle"])
        thumbnail_surface.blit(rotated_thumb_image, thumb_rect)

    # 绘制缩略图边框和视野范围
    thumbnail_rect = pygame.Rect(screen_width - thumbnail_width - 10, screen_height - thumbnail_height - 10, thumbnail_width, thumbnail_height)
    pygame.draw.rect(screen, WHITE, thumbnail_rect, 2)
    
    # 绘制视野范围在缩略图中的位置
    view_rect = pygame.Rect(
        camera_pos[0] * thumbnail_width // world_width,
        camera_pos[1] * thumbnail_height // world_height,
        screen_width * thumbnail_width // world_width,
        screen_height * thumbnail_height // world_height,
    )
    pygame.draw.rect(thumbnail_surface, RED, view_rect, 2)

    # 将缩略图绘制到屏幕右下角
    screen.blit(thumbnail_surface, (screen_width - thumbnail_width - 10, screen_height - thumbnail_height - 10))

    # 只有在没有选择元素按钮的情况下显示提示
    if not current_tile and show_ui:
        if hovered_tiles:
            info_text = "当前元素：" + " -> ".join([tile["tile"] for tile in hovered_tiles[::-1]])
        else:
            info_text = "当前元素：无"
        
        info_surface = font.render(info_text, True, WHITE)
        screen.blit(info_surface, (10, screen_height - 30))

    pygame.display.flip()
    clock.tick(60)  # 设置刷新率为60帧

pygame.quit()
sys.exit()
