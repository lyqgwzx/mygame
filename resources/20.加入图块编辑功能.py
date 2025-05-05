import pygame
import sys
import os
import json
import datetime
from PIL import Image
import copy  # 导入 copy 模块用于深拷贝


def save_map(filename):
    global message, message_display_time

    # 保存地图数据
    map_data = {
        "resolution": {
            "width": world_width,
            "height": world_height
        },
        "tiles": []
    }

    for tile in map_tiles:
        tile_data = {
            "category": tile["category"],
            "tile": tile["tile"],
            "x": tile["rect"].x,
            "y": tile["rect"].y,
            "scale": tile["scale"],
            "angle": tile["angle"]
        }

        # 新增功能：保存图块属性
        if "properties" in tile:
            tile_data["properties"] = copy.deepcopy(tile["properties"])

        map_data["tiles"].append(tile_data)

    # 确保文件名以 .json 结尾
    if not filename.endswith('.json'):
        filename += '.json'

    # 写入json文件，使用 ensure_ascii=False 和 encoding='utf-8'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(map_data, f, indent=4, ensure_ascii=False)

    message = f"已保存地图：{filename}"
    message_display_time = pygame.time.get_ticks()  # 获取当前时间毫秒数

# 初始化 Pygame
pygame.init()

# 确保捕获 TEXTINPUT 事件
pygame.event.set_allowed(
    [pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTINPUT, pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
     pygame.MOUSEMOTION])

# 设置屏幕尺寸
screen_width, screen_height = 1400, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("地图编辑器")

# 分配屏幕区域：左边为功能区域，右边为地图编辑区域
function_area_width = screen_width // 2  # 功能区域宽度
map_area_width = screen_width - function_area_width  # 地图编辑区域宽度

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GRAY = (50, 50, 50)
SEMI_TRANSPARENT_RED = (255, 0, 0, 128)
SEMI_TRANSPARENT_BLUE = (0, 0, 255, 128)
LIGHT_GRAY = (200, 200, 200, 100)  # 半透明浅灰色，用于网格线

# 设置资源路径
resource_path = "地图编辑器的元素类型/"  # 请替换为你的资源路径


# 加载图片资源并预先计算不同大小的图像
def load_scaled_images(image_path):
    original_image = Image.open(image_path).convert('RGBA')
    sizes = [1.0, 0.75, 0.5, 0.25]
    scaled_images = {}
    for scale in sizes:
        if scale == 1.0:
            # 直接使用原始图像，避免重复缩放
            pygame_image = pygame.image.fromstring(original_image.tobytes(), original_image.size,
                                                   original_image.mode).convert_alpha()
            scaled_images[scale] = pygame_image
        else:
            resized_image = original_image.resize(
                (int(original_image.width * scale), int(original_image.height * scale)),
                Image.LANCZOS  # 使用抗锯齿算法
            )
            pygame_image = pygame.image.fromstring(resized_image.tobytes(), resized_image.size,
                                                   resized_image.mode).convert_alpha()
            scaled_images[scale] = pygame_image
    return scaled_images


# 新增：加载旋转后的图像
def load_rotated_images(scaled_images):
    rotated_images = {}
    for scale, image in scaled_images.items():
        rotated_images[scale] = {}
        for angle in [0, 90, 180, 270]:
            rotated_image = pygame.transform.rotate(image, angle)
            rotated_images[scale][angle] = rotated_image
    return rotated_images


# 动态加载所有地皮元素
tile_images = {}
for category_name in os.listdir(resource_path):
    category_path = os.path.join(resource_path, category_name)
    if os.path.isdir(category_path):
        tile_images[category_name] = {}
        for file_name in os.listdir(category_path):
            if file_name.endswith(".png"):
                name = file_name.split(".")[0]  # 使用文件名作为元素名称
                scaled_images = load_scaled_images(os.path.join(category_path, file_name))
                rotated_images = load_rotated_images(scaled_images)
                tile_images[category_name][name] = rotated_images

# 动态生成按钮
button_width, button_height = 120, 120  # 调整按钮尺寸以适应缩略图和文字
button_margin = 10
buttons = []
scroll_offset = 0  # 按钮滚动条的偏移量
total_button_height = 0  # 总按钮高度

# 滑动条设置
scroll_bar_width = 15
scroll_bar_color = WHITE
scroll_bar_dragging = False
scroll_start_y = 0
scroll_start_offset = 0


# 动态生成按钮的布局
def generate_buttons():
    global buttons, button_width, button_height, total_button_height
    buttons = []
    x_offset, y_offset = button_margin, button_margin + scroll_offset
    total_button_height = 0  # 初始化总高度
    for category_name, elements in tile_images.items():
        # 添加类别标签
        category_rect = pygame.Rect(x_offset + scroll_bar_width, y_offset,
                                    screen_width // 2 - 2 * button_margin - scroll_bar_width, 30)
        buttons.append({'type': 'category', 'name': category_name, 'rect': category_rect})
        y_offset += 30 + button_margin
        total_button_height += 30 + button_margin
        x_offset = button_margin
        for element_name in elements.keys():
            rect = pygame.Rect(x_offset + scroll_bar_width, y_offset, button_width, button_height)
            buttons.append({'type': 'button', 'category': category_name, 'name': element_name, 'rect': rect})
            x_offset += button_width + button_margin
            if x_offset + button_width + scroll_bar_width > screen_width // 2:  # 到达右边界时换行
                x_offset = button_margin
                y_offset += button_height + button_margin
                total_button_height += button_height + button_margin
        # 检查是否需要增加 y_offset 和 total_button_height
        if x_offset != button_margin:
            # 如果 x_offset 不等于初始值，说明最后一行未满，需要增加 y_offset
            y_offset += button_height + button_margin
            total_button_height += button_height + button_margin
            x_offset = button_margin  # 重置 x_offset
        y_offset += button_margin  # 类别之间的额外间距
        total_button_height += button_margin


generate_buttons()

# 初始化地图
world_width, world_height = 3200, 2400
map_tiles = []

# 当前选中的地皮类型
current_tile = None
current_category = None
current_scale = 1.0
rotation_angle = 0

# 定义缩放比例
scale_levels = [1.0, 0.75, 0.5, 0.25]

# 摄像机的初始位置
camera_pos = [0, 0]

# 加载中文字体
font_path = "/Users/liya/Documents/编程文件/我的游戏/我的肉鸽子游戏/resources/XiangJiaoDaJiangJunLingGanTi-2.ttf"  # 请替换为你的字体路径
font = pygame.font.Font(font_path, 24)
small_font = pygame.font.Font(font_path, 18)  # 新增：小号字体用于属性编辑器

# 设置帧率
clock = pygame.time.Clock()

# 功能状态开关
show_reference_lines = True

# 用于显示底部消息的变量
message = None
message_display_time = 0

# 用于加载地图菜单的变量
show_load_menu = False  # 加载菜单显示状态
load_menu_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 150, 200, 300)
load_button_rect = pygame.Rect(load_menu_rect.x + 20, load_menu_rect.y + 20, 160, 50)

saved_maps = []  # 保存的地图列表
selected_map = None  # 当前选中的地图

# 新建地图窗口的变量
show_new_map_window = False
new_map_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 100, 300, 200)
close_button_rect = pygame.Rect(new_map_rect.right - 30, new_map_rect.y + 10, 20, 20)
confirm_button_rect = pygame.Rect(new_map_rect.centerx - 50, new_map_rect.bottom - 60, 100, 40)
input_boxes = []
active_input = 0  # 当前激活的输入框（0：宽度，1：高度）

# 新增功能：属性编辑模式变量
edit_properties_mode = False  # 是否处于属性编辑模式
property_mode_button_rect = pygame.Rect(function_area_width - 140, 10, 130, 40)
editing_collision = False  # 是否正在编辑碰撞区域
collision_start_pos = None  # 碰撞区域起始位置
current_collision_rect = None  # 当前正在编辑的碰撞区域

# 新增功能：属性类型
tile_property_types = [
    "可通过",
    "不可通过",
    "可破坏",
    "触发器",
    "物品",
    "装饰"
]
current_property_type = "可通过"  # 默认属性类型

# 新增功能：属性编辑面板相关变量
property_panels = []
active_property_panel = None


def load_saved_maps():
    global saved_maps
    saved_maps = [f for f in os.listdir() if f.endswith('.json')]


def draw_load_menu():
    # 绘制加载菜单背景
    pygame.draw.rect(screen, RED, load_menu_rect)

    # 绘制"加载地图"按钮
    pygame.draw.rect(screen, LIGHT_GREEN, load_button_rect)
    load_button_text = font.render("加载地图", True, BLACK)
    screen.blit(load_button_text, (load_button_rect.x + 20, load_button_rect.y + 10))

    # 如果有保存的地图，绘制右侧保存地图文件列表
    if saved_maps:
        map_list_rect = pygame.Rect(load_menu_rect.right + 20, load_menu_rect.top, 200, 300)
        pygame.draw.rect(screen, RED, map_list_rect)

        y_offset = map_list_rect.y + 20
        for map_file in saved_maps:
            map_rect = pygame.Rect(map_list_rect.x + 20, y_offset, 160, 30)
            pygame.draw.rect(screen, LIGHT_GREEN if map_file == selected_map else WHITE, map_rect)
            map_text = font.render(map_file, True, BLACK)
            screen.blit(map_text, (map_rect.x + 10, map_rect.y + 5))
            y_offset += 40


def load_map(filename):
    global map_tiles, world_width, world_height
    with open(filename, 'r', encoding='utf-8') as f:
        map_data = json.load(f)
    world_width = map_data["resolution"]["width"]
    world_height = map_data["resolution"]["height"]
    map_tiles = []
    for tile_data in map_data["tiles"]:
        category = tile_data["category"]
        tile_name = tile_data["tile"]
        tile_rect = pygame.Rect(
            tile_data["x"],
            tile_data["y"],
            tile_images[category][tile_name][tile_data["scale"]][tile_data["angle"]].get_width(),
            tile_images[category][tile_name][tile_data["scale"]][tile_data["angle"]].get_height()
        )

        tile_info = {
            "category": category,
            "tile": tile_name,
            "rect": tile_rect,
            "scale": tile_data["scale"],
            "angle": tile_data["angle"],
            "selected": False
        }

        # 新增功能：加载图块属性
        if "properties" in tile_data:
            tile_info["properties"] = tile_data["properties"]
        else:
            # 如果没有属性，初始化默认属性
            tile_info["properties"] = {
                "type": "可通过",
                "collision": [],
                "interaction": "none",
                "triggers": [],
                "custom": {}
            }

        map_tiles.append(tile_info)


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
            map_tiles.insert(index + 1, selected_tile)  # 向下移动一层


# 定义吸附的距离阈值
snap_threshold = 10  # 吸附到参考线的距离
detect_threshold = 50  # 检测是否显示参考线的距离
max_distance_threshold = 500  # 最大考虑距离


def draw_reference_lines(screen, line_positions, camera_pos, color=RED):
    for line_pos in line_positions:
        if line_pos['type'] == 'vertical':
            pygame.draw.line(screen, color,
                             (line_pos['pos'] - camera_pos[0] + function_area_width, 0),
                             (line_pos['pos'] - camera_pos[0] + function_area_width, screen_height), 1)
        elif line_pos['type'] == 'horizontal':
            pygame.draw.line(screen, color,
                             (function_area_width, line_pos['pos'] - camera_pos[1]),
                             (screen_width, line_pos['pos'] - camera_pos[1]), 1)


# 计算滑动条的位置和尺寸
def calculate_scroll_bar():
    global total_button_height
    visible_height = screen_height - 2 * button_margin
    if total_button_height > visible_height:
        scroll_bar_height = max(int(visible_height * visible_height / total_button_height), 20)
    else:
        scroll_bar_height = visible_height
    scroll_bar_position = int(-scroll_offset * visible_height / total_button_height)
    return scroll_bar_position, scroll_bar_height


# 平滑滚动
def smooth_scroll(mouse_scroll_amount):
    global total_button_height
    visible_height = screen_height - 2 * button_margin
    # 平滑滚动：每次移动滚动条较少的距离，增加流畅性
    scroll_speed = button_height // 16  # 调整滑动速度为按钮高度的1/16
    new_scroll_offset = scroll_offset + mouse_scroll_amount * scroll_speed
    # 限制滚动范围
    max_scroll_offset = visible_height - total_button_height
    if max_scroll_offset > 0:  # 当内容不足以需要滚动时
        new_scroll_offset = 0
    else:
        new_scroll_offset = min(0, max(new_scroll_offset, max_scroll_offset))
    return new_scroll_offset


# 初始化撤销和重做栈
undo_stack = []
redo_stack = []


# 保存当前状态的函数
def save_state():
    undo_stack.append(copy.deepcopy(map_tiles))
    redo_stack.clear()
    # 限制撤销栈大小，防止占用过多内存
    if len(undo_stack) > 50:
        undo_stack.pop(0)


# 网格控制变量
show_grid = True  # 是否显示网格
grid_size = 50  # 网格大小（像素）


def draw_grid():
    if not show_grid:
        return  # 如果不显示网格，直接返回

    # 计算起始位置，确保网格随摄像机移动
    start_x = -camera_pos[0] % grid_size
    start_y = -camera_pos[1] % grid_size

    # 创建一个半透明的 Surface 来绘制网格线
    grid_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    # 绘制垂直网格线
    for x in range(start_x + function_area_width, screen_width, grid_size):
        pygame.draw.line(grid_surface, LIGHT_GRAY, (x, 0), (x, screen_height))

    # 绘制水平网格线
    for y in range(start_y, screen_height, grid_size):
        pygame.draw.line(grid_surface, LIGHT_GRAY, (function_area_width, y), (screen_width, y))

    # 将网格 Surface 绘制到屏幕上
    screen.blit(grid_surface, (0, 0))


# 对齐模式定义
alignment_modes = [
    '中心',
    '上边缘',
    '下边缘',
    '左边缘',
    '右边缘',
    '左上角',
    '右上角',
    '左下角',
    '右下角',
    '上边缘中央',
    '下边缘中央',
    '左边缘中央',
    '右边缘中央'
]
current_alignment_mode = '中心'  # 默认对齐模式


# 定义获取对齐偏移的函数
def get_alignment_offset(alignment_mode, image_width, image_height):
    if alignment_mode == '中心':
        return image_width // 2, image_height // 2
    elif alignment_mode == '上边缘':
        return image_width // 2, 0
    elif alignment_mode == '下边缘':
        return image_width // 2, image_height
    elif alignment_mode == '左边缘':
        return 0, image_height // 2
    elif alignment_mode == '右边缘':
        return image_width, image_height // 2
    elif alignment_mode == '左上角':
        return 0, 0
    elif alignment_mode == '右上角':
        return image_width, 0
    elif alignment_mode == '左下角':
        return 0, image_height
    elif alignment_mode == '右下角':
        return image_width, image_height
    elif alignment_mode == '上边缘中央':
        return image_width // 2, 0
    elif alignment_mode == '下边缘中央':
        return image_width // 2, image_height
    elif alignment_mode == '左边缘中央':
        return 0, image_height // 2
    elif alignment_mode == '右边缘中央':
        return image_width, image_height // 2
    else:
        return image_width // 2, image_height // 2  # 默认使用中心


# 计算对齐按钮的位置
function_area_width = screen_width // 2  # 功能区域宽度
alignment_button_rect = pygame.Rect(function_area_width - 130, screen_height - 50, 120, 30)
alignment_menu_visible = False
alignment_menu_rect = pygame.Rect(alignment_button_rect.x, alignment_button_rect.y - len(alignment_modes) * 30 - 10,
                                  150, len(alignment_modes) * 30)

# 游戏循环
running = True
w_pressed = False
s_pressed = False
r_pressed = False
tab_pressed = False
selected_tile = None
hovered_tiles = []
hovered_index = 0

# 分配屏幕区域：左边为功能区域，右边为地图编辑区域
function_area_width = screen_width // 2  # 功能区域宽度
map_area_width = screen_width - function_area_width  # 地图编辑区域宽度


# 输入框类
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = LIGHT_GRAY
        self.color_active = WHITE
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pass  # 在主循环中处理回车事件
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.txt_surface = font.render(self.text, True, BLACK)
            elif event.type == pygame.TEXTINPUT:
                # 处理中文输入
                self.text += event.text
                self.txt_surface = font.render(self.text, True, BLACK)

    def draw(self, screen):
        # 绘制输入框
        pygame.draw.rect(screen, self.color, self.rect)
        # 绘制文本
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))


def draw_new_map_window():
    # 绘制新建地图窗口背景
    pygame.draw.rect(screen, DARK_GRAY, new_map_rect)
    # 绘制关闭按钮
    pygame.draw.rect(screen, RED, close_button_rect)
    x_text = font.render('X', True, WHITE)
    screen.blit(x_text, (close_button_rect.x + 5, close_button_rect.y))
    # 绘制提示文字
    width_label = font.render('宽度：', True, WHITE)
    height_label = font.render('高度：', True, WHITE)
    screen.blit(width_label, (new_map_rect.x + 20, new_map_rect.y + 50))
    screen.blit(height_label, (new_map_rect.x + 20, new_map_rect.y + 100))
    # 绘制输入框
    for box in input_boxes:
        box.draw(screen)
    # 绘制"确定"按钮
    pygame.draw.rect(screen, LIGHT_GREEN, confirm_button_rect)
    confirm_text = font.render('确定', True, BLACK)
    text_rect = confirm_text.get_rect(center=confirm_button_rect.center)
    screen.blit(confirm_text, text_rect)


def create_new_map(width, height):
    global world_width, world_height, map_tiles, camera_pos
    world_width = int(width)
    world_height = int(height)
    map_tiles = []
    camera_pos = [0, 0]


# 初始化输入框
input_boxes = [
    InputBox(new_map_rect.x + 100, new_map_rect.y + 45, 150, 32),
    InputBox(new_map_rect.x + 100, new_map_rect.y + 95, 150, 32)
]

# 保存对话框的变量
show_save_dialog = False
save_dialog_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 100, 300, 200)
save_close_button_rect = pygame.Rect(save_dialog_rect.right - 30, save_dialog_rect.y + 10, 20, 20)
save_confirm_button_rect = pygame.Rect(save_dialog_rect.centerx - 50, save_dialog_rect.bottom - 60, 100, 40)
save_input_box = None  # 保存文件名的输入框


def draw_save_dialog():
    # 绘制保存对话框背景
    pygame.draw.rect(screen, DARK_GRAY, save_dialog_rect)
    # 绘制关闭按钮
    pygame.draw.rect(screen, RED, save_close_button_rect)
    x_text = font.render('X', True, WHITE)
    screen.blit(x_text, (save_close_button_rect.x + 5, save_close_button_rect.y))
    # 绘制提示文字
    filename_label = font.render('文件名：', True, WHITE)
    screen.blit(filename_label, (save_dialog_rect.x + 20, save_dialog_rect.y + 80))
    # 绘制输入框
    save_input_box.draw(screen)
    # 绘制"保存"按钮
    pygame.draw.rect(screen, LIGHT_GREEN, save_confirm_button_rect)
    confirm_text = font.render('保存', True, BLACK)
    text_rect = confirm_text.get_rect(center=save_confirm_button_rect.center)
    screen.blit(confirm_text, text_rect)


# 保存提示对话框的变量
show_save_prompt_dialog = False
save_prompt_dialog_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 - 100, 300, 200)
save_prompt_close_button_rect = pygame.Rect(save_prompt_dialog_rect.right - 30, save_prompt_dialog_rect.y + 10, 20, 20)
save_prompt_save_button_rect = pygame.Rect(save_prompt_dialog_rect.x + 20, save_prompt_dialog_rect.bottom - 60, 80, 40)
save_prompt_dont_save_button_rect = pygame.Rect(save_prompt_dialog_rect.centerx - 40,
                                                save_prompt_dialog_rect.bottom - 60, 80, 40)
save_prompt_cancel_button_rect = pygame.Rect(save_prompt_dialog_rect.right - 100, save_prompt_dialog_rect.bottom - 60,
                                             80, 40)


def draw_save_prompt_dialog():
    # 绘制对话框背景
    pygame.draw.rect(screen, DARK_GRAY, save_prompt_dialog_rect)
    # 绘制关闭按钮
    pygame.draw.rect(screen, RED, save_prompt_close_button_rect)
    x_text = font.render('X', True, WHITE)
    screen.blit(x_text, (save_prompt_close_button_rect.x + 5, save_prompt_close_button_rect.y))
    # 绘制提示文字
    prompt_text = font.render('是否保存当前地图？', True, WHITE)
    text_rect = prompt_text.get_rect(center=(save_prompt_dialog_rect.centerx, save_prompt_dialog_rect.y + 60))
    screen.blit(prompt_text, text_rect)
    # 绘制"保存"按钮
    pygame.draw.rect(screen, LIGHT_GREEN, save_prompt_save_button_rect)
    save_text = font.render('保存', True, BLACK)
    save_text_rect = save_text.get_rect(center=save_prompt_save_button_rect.center)
    screen.blit(save_text, save_text_rect)
    # 绘制"不保存"按钮
    pygame.draw.rect(screen, WHITE, save_prompt_dont_save_button_rect)
    dont_save_text = font.render('不保存', True, BLACK)
    dont_save_text_rect = dont_save_text.get_rect(center=save_prompt_dont_save_button_rect.center)
    screen.blit(dont_save_text, dont_save_text_rect)
    # 绘制"取消"按钮
    pygame.draw.rect(screen, WHITE, save_prompt_cancel_button_rect)
    cancel_text = font.render('取消', True, BLACK)
    cancel_text_rect = cancel_text.get_rect(center=save_prompt_cancel_button_rect.center)
    screen.blit(cancel_text, cancel_text_rect)


# 新增功能：绘制属性编辑按钮
def draw_property_mode_button():
    button_color = LIGHT_GREEN if edit_properties_mode else LIGHT_GRAY
    pygame.draw.rect(screen, button_color, property_mode_button_rect)
    button_text = font.render("属性编辑", True, BLACK)
    text_rect = button_text.get_rect(center=property_mode_button_rect.center)
    screen.blit(button_text, text_rect)


# 新增功能：绘制属性编辑界面
def draw_property_editor(tile):
    if not tile:
        return

    # 绘制编辑界面背景
    pygame.draw.rect(screen, DARK_GRAY, (function_area_width, 0, map_area_width, screen_height))

    # 绘制被编辑的图块
    scaled_image = tile_images[tile["category"]][tile["tile"]][tile["scale"]][tile["angle"]]
    tile_preview_rect = scaled_image.get_rect(center=(function_area_width + map_area_width // 2, 200))
    screen.blit(scaled_image, tile_preview_rect)

    # 绘制图块信息
    tile_info_text = f"类型: {tile['category']}/{tile['tile']} (比例: {tile['scale']}, 角度: {tile['angle']}°)"
    info_surface = font.render(tile_info_text, True, WHITE)
    screen.blit(info_surface, (function_area_width + 20, 50))

    # 初始化属性（如果不存在）
    if "properties" not in tile:
        tile["properties"] = {
            "type": "可通过",
            "collision": [],
            "interaction": "none",
            "triggers": [],
            "custom": {}
        }

    # 绘制属性类型选择器
    property_type_text = font.render("属性类型:", True, WHITE)
    screen.blit(property_type_text, (function_area_width + 20, 380))

    # 绘制属性类型按钮
    type_button_width = 120
    type_button_height = 30
    button_spacing = 10
    x_offset = function_area_width + 20

    for idx, prop_type in enumerate(tile_property_types):
        type_rect = pygame.Rect(x_offset, 420, type_button_width, type_button_height)
        button_color = LIGHT_GREEN if tile["properties"]["type"] == prop_type else WHITE
        pygame.draw.rect(screen, button_color, type_rect)

        type_text = small_font.render(prop_type, True, BLACK)
        text_rect = type_text.get_rect(center=type_rect.center)
        screen.blit(type_text, text_rect)

        x_offset += type_button_width + button_spacing
        # 如果超出区域宽度，则换行
        if x_offset + type_button_width > screen_width:
            x_offset = function_area_width + 20

    # 绘制碰撞区域编辑按钮
    collision_button_rect = pygame.Rect(function_area_width + 20, 480, 200, 40)
    collision_button_color = LIGHT_GREEN if editing_collision else WHITE
    pygame.draw.rect(screen, collision_button_color, collision_button_rect)
    collision_text = font.render("编辑碰撞区域", True, BLACK)
    collision_text_rect = collision_text.get_rect(center=collision_button_rect.center)
    screen.blit(collision_text, collision_text_rect)

    # 使用说明
    if editing_collision:
        instruction_text = [
            "点击并拖动鼠标绘制碰撞区域",
            "按Delete键删除选中的碰撞区域"
        ]
        for i, text in enumerate(instruction_text):
            instruction_surface = small_font.render(text, True, YELLOW)
            screen.blit(instruction_surface, (function_area_width + 250, 480 + i * 25))

    # 绘制当前碰撞区域
    for i, collision in enumerate(tile["properties"]["collision"]):
        # 计算碰撞区域在预览中的位置
        collision_rect = pygame.Rect(
            tile_preview_rect.x + collision["x"],
            tile_preview_rect.y + collision["y"],
            collision["width"],
            collision["height"]
        )

        # 使用半透明蓝色显示碰撞区域
        collision_surface = pygame.Surface((collision["width"], collision["height"]), pygame.SRCALPHA)
        collision_surface.fill(SEMI_TRANSPARENT_BLUE)
        screen.blit(collision_surface, (collision_rect.x, collision_rect.y))

        # 绘制边框
        pygame.draw.rect(screen, BLUE, collision_rect, 2)

        # 标记碰撞区域索引
        index_text = small_font.render(str(i + 1), True, WHITE)
        screen.blit(index_text, (collision_rect.x + 5, collision_rect.y + 5))

    # 绘制新正在创建的碰撞区域
    if current_collision_rect:
        collision_surface = pygame.Surface((current_collision_rect.width, current_collision_rect.height),
                                           pygame.SRCALPHA)
        collision_surface.fill((0, 255, 0, 128))  # 半透明绿色
        screen.blit(collision_surface, (current_collision_rect.x, current_collision_rect.y))
        pygame.draw.rect(screen, GREEN, current_collision_rect, 2)

    # 绘制自定义属性编辑区域
    custom_props_rect = pygame.Rect(function_area_width + 20, 540, map_area_width - 40, 200)
    pygame.draw.rect(screen, DARK_GRAY, custom_props_rect)
    custom_props_text = font.render("自定义属性:", True, WHITE)
    screen.blit(custom_props_text, (custom_props_rect.x + 10, custom_props_rect.y + 10))

    # 显示当前自定义属性（简单显示，未实现编辑功能）
    y_offset = custom_props_rect.y + 50
    if tile["properties"]["custom"]:
        for key, value in tile["properties"]["custom"].items():
            prop_text = small_font.render(f"{key}: {value}", True, WHITE)
            screen.blit(prop_text, (custom_props_rect.x + 20, y_offset))
            y_offset += 30
    else:
        no_props_text = small_font.render("(无自定义属性)", True, LIGHT_GRAY)
        screen.blit(no_props_text, (custom_props_rect.x + 20, y_offset))


# 新增功能：处理碰撞区域创建
def handle_collision_creation(tile, mouse_pos, start_pos):
    if not tile or not editing_collision:
        return None

    # 获取图块预览的位置
    scaled_image = tile_images[tile["category"]][tile["tile"]][tile["scale"]][tile["angle"]]
    tile_preview_rect = scaled_image.get_rect(center=(function_area_width + map_area_width // 2, 200))

    # 计算鼠标相对于图块预览的位置
    rel_start_x = start_pos[0] - tile_preview_rect.x
    rel_start_y = start_pos[1] - tile_preview_rect.y
    rel_end_x = mouse_pos[0] - tile_preview_rect.x
    rel_end_y = mouse_pos[1] - tile_preview_rect.y

    # 确保碰撞区域在图块内部
    rel_start_x = max(0, min(rel_start_x, scaled_image.get_width()))
    rel_start_y = max(0, min(rel_start_y, scaled_image.get_height()))
    rel_end_x = max(0, min(rel_end_x, scaled_image.get_width()))
    rel_end_y = max(0, min(rel_end_y, scaled_image.get_height()))

    # 计算碰撞区域的宽度和高度
    width = abs(rel_end_x - rel_start_x)
    height = abs(rel_end_y - rel_start_y)

    # 计算左上角坐标
    x = min(rel_start_x, rel_end_x)
    y = min(rel_start_y, rel_end_y)

    # 计算相对于屏幕的绘制位置（这是用于预览，不会保存）
    screen_x = tile_preview_rect.x + x
    screen_y = tile_preview_rect.y + y

    # 创建一个矩形表示当前正在创建的碰撞区域
    return pygame.Rect(screen_x, screen_y, width, height)


# 新增功能：保存碰撞区域
def save_collision_area(tile, collision_rect):
    if not tile or not collision_rect:
        return

    # 获取图块预览的位置
    scaled_image = tile_images[tile["category"]][tile["tile"]][tile["scale"]][tile["angle"]]
    tile_preview_rect = scaled_image.get_rect(center=(function_area_width + map_area_width // 2, 200))

    # 计算碰撞区域相对于图块的位置
    rel_x = collision_rect.x - tile_preview_rect.x
    rel_y = collision_rect.y - tile_preview_rect.y

    # 新的碰撞区域
    new_collision = {
        "x": rel_x,
        "y": rel_y,
        "width": collision_rect.width,
        "height": collision_rect.height
    }

    # 将碰撞区域添加到图块属性中
    if "properties" not in tile:
        tile["properties"] = {
            "type": "可通过",
            "collision": [],
            "interaction": "none",
            "triggers": [],
            "custom": {}
        }

    tile["properties"]["collision"].append(new_collision)
    return True


# 新增功能：检查碰撞区域点击
def check_collision_area_click(tile, mouse_pos):
    if not tile or "properties" not in tile or not tile["properties"]["collision"]:
        return -1

    # 获取图块预览的位置
    scaled_image = tile_images[tile["category"]][tile["tile"]][tile["scale"]][tile["angle"]]
    tile_preview_rect = scaled_image.get_rect(center=(function_area_width + map_area_width // 2, 200))

    # 检查每个碰撞区域
    for i, collision in enumerate(tile["properties"]["collision"]):
        collision_rect = pygame.Rect(
            tile_preview_rect.x + collision["x"],
            tile_preview_rect.y + collision["y"],
            collision["width"],
            collision["height"]
        )
        if collision_rect.collidepoint(mouse_pos):
            return i

    return -1


# 新增功能：删除选中的碰撞区域
def delete_collision_area(tile, index):
    if not tile or "properties" not in tile or index < 0 or index >= len(tile["properties"]["collision"]):
        return False

    tile["properties"]["collision"].pop(index)
    return True


# 添加 pending_new_map 标志
pending_new_map = False  # 标志保存完成后是否需要显示新建地图窗口

while running:
    screen.fill(BLACK)

    # 事件处理
    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    mouse_in_map = mouse_x >= function_area_width and not edit_properties_mode  # 只考虑在地图区域内的鼠标位置

    # 更新鼠标坐标相对地图区域的偏移量
    if mouse_in_map:
        mouse_x -= function_area_width

    # 存储将要显示的参考线
    reference_lines = []

    if current_tile and show_reference_lines and not edit_properties_mode:
        nearest_snap = {"x": None, "y": None}
        for tile in map_tiles:
            tile_rect = tile["rect"]

            # 计算鼠标与元素中心的距离
            distance_to_tile = ((mouse_x + camera_pos[0] - tile_rect.centerx) ** 2 + (
                        mouse_y + camera_pos[1] - tile_rect.centery) ** 2) ** 0.5

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
    if show_reference_lines and not edit_properties_mode:
        draw_reference_lines(screen, reference_lines, camera_pos)

    # 绘制网格
    if not edit_properties_mode:
        draw_grid()

    # 检查鼠标悬停位置下的所有地皮元素，按从上到下顺序排列
    if not current_tile and not (selected_tile and selected_tile['selected']) and mouse_in_map:
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

    moving_up = False
    moving_down = False
    moving_left = False
    moving_right = False

    # 属性编辑模式下的特殊处理
    if edit_properties_mode and selected_tile:
        # 如果在编辑碰撞区域
        if editing_collision and collision_start_pos:
            current_collision_rect = handle_collision_creation(selected_tile, (mouse_x, mouse_y), collision_start_pos)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if show_save_prompt_dialog:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_prompt_close_button_rect.collidepoint(event.pos) or save_prompt_cancel_button_rect.collidepoint(
                        event.pos):
                    show_save_prompt_dialog = False  # 关闭对话框
                elif save_prompt_save_button_rect.collidepoint(event.pos):
                    show_save_prompt_dialog = False
                    show_save_dialog = True  # 显示保存对话框
                    # 初始化保存输入框
                    save_input_box = InputBox(save_dialog_rect.x + 100, save_dialog_rect.y + 75, 150, 32)
                    # 设置一个标志，表示保存完成后需要显示新建地图窗口
                    pending_new_map = True
                elif save_prompt_dont_save_button_rect.collidepoint(event.pos):
                    show_save_prompt_dialog = False
                    show_new_map_window = True  # 显示新建地图窗口
                    # 重置输入框
                    input_boxes[0].text = ''
                    input_boxes[1].text = ''
                    for box in input_boxes:
                        box.txt_surface = font.render(box.text, True, BLACK)
                    active_input = 0
                    for idx, box in enumerate(input_boxes):
                        box.active = idx == active_input
                        box.color = box.color_active if box.active else box.color_inactive
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_save_prompt_dialog = False
        elif show_save_dialog:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_close_button_rect.collidepoint(event.pos):
                    show_save_dialog = False
                    pending_new_map = False  # 取消保存，重置标志
                elif save_confirm_button_rect.collidepoint(event.pos):
                    # 获取输入的文件名并保存
                    filename = save_input_box.text.strip()
                    if filename:
                        save_map(filename)
                        show_save_dialog = False
                        if pending_new_map:
                            pending_new_map = False
                            show_new_map_window = True  # 显示新建地图窗口
                            # 重置输入框
                            input_boxes[0].text = ''
                            input_boxes[1].text = ''
                            for box in input_boxes:
                                box.txt_surface = font.render(box.text, True, BLACK)
                            active_input = 0
                            for idx, box in enumerate(input_boxes):
                                box.active = idx == active_input
                                box.color = box.color_active if box.active else box.color_inactive
                    else:
                        message = "文件名不能为空"
                        message_display_time = pygame.time.get_ticks()
                else:
                    if save_input_box.rect.collidepoint(event.pos):
                        save_input_box.active = True
                        save_input_box.color = save_input_box.color_active
                    else:
                        save_input_box.active = False
                        save_input_box.color = save_input_box.color_inactive
            elif event.type == pygame.KEYDOWN or event.type == pygame.TEXTINPUT:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    show_save_dialog = False
                    pending_new_map = False  # 取消保存，重置标志
                else:
                    save_input_box.handle_event(event)
            elif event.type == pygame.KEYUP:
                pass  # 在保存对话框中，不处理 KEYUP 事件
        elif show_new_map_window:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if close_button_rect.collidepoint(event.pos):
                    show_new_map_window = False
                elif confirm_button_rect.collidepoint(event.pos):
                    # 点击了"确定"按钮
                    width = input_boxes[0].text
                    height = input_boxes[1].text
                    if width.isdigit() and height.isdigit():
                        create_new_map(width, height)
                        show_new_map_window = False
                    else:
                        message = "请输入有效的数字"
                        message_display_time = pygame.time.get_ticks()
                else:
                    for idx, box in enumerate(input_boxes):
                        if box.rect.collidepoint(event.pos):
                            active_input = idx
                            box.active = True
                            box.color = box.color_active
                        else:
                            box.active = False
                            box.color = box.color_inactive
            elif event.type == pygame.KEYDOWN or event.type == pygame.TEXTINPUT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        active_input = (active_input + 1) % 2
                        for idx, box in enumerate(input_boxes):
                            box.active = idx == active_input
                            box.color = box.color_active if box.active else box.color_inactive
                    elif event.key == pygame.K_RETURN:
                        # 按下回车键，功能与点击"确定"按钮相同
                        width = input_boxes[0].text
                        height = input_boxes[1].text
                        if width.isdigit() and height.isdigit():
                            create_new_map(width, height)
                            show_new_map_window = False
                        else:
                            message = "请输入有效的数字"
                            message_display_time = pygame.time.get_ticks()
                    else:
                        input_boxes[active_input].handle_event(event)
                elif event.type == pygame.TEXTINPUT:
                    input_boxes[active_input].handle_event(event)
        elif edit_properties_mode and selected_tile:
            # 属性编辑模式下的事件处理
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    # 检查属性类型按钮
                    type_button_width = 120
                    type_button_height = 30
                    button_spacing = 10
                    x_offset = function_area_width + 20

                    for idx, prop_type in enumerate(tile_property_types):
                        type_rect = pygame.Rect(x_offset, 420, type_button_width, type_button_height)
                        if type_rect.collidepoint(event.pos):
                            # 更改属性类型
                            selected_tile["properties"]["type"] = prop_type
                            break
                        x_offset += type_button_width + button_spacing
                        # 如果超出区域宽度，则换行
                        if x_offset + type_button_width > screen_width:
                            x_offset = function_area_width + 20

                    # 检查碰撞区域编辑按钮
                    collision_button_rect = pygame.Rect(function_area_width + 20, 480, 200, 40)
                    if collision_button_rect.collidepoint(event.pos):
                        editing_collision = not editing_collision
                    elif editing_collision:
                        # 当点击时，开始创建新的碰撞区域
                        collision_start_pos = event.pos

                # 检查属性模式按钮
                if property_mode_button_rect.collidepoint(event.pos):
                    edit_properties_mode = not edit_properties_mode
                    editing_collision = False  # 退出碰撞编辑模式
                    collision_start_pos = None
                    current_collision_rect = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and editing_collision and collision_start_pos:
                    # 完成碰撞区域的创建
                    if current_collision_rect and current_collision_rect.width > 5 and current_collision_rect.height > 5:
                        save_collision_area(selected_tile, current_collision_rect)
                    collision_start_pos = None
                    current_collision_rect = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if editing_collision:
                        editing_collision = False
                        collision_start_pos = None
                        current_collision_rect = None
                    else:
                        edit_properties_mode = False
                elif event.key == pygame.K_DELETE and editing_collision:
                    # 删除选中的碰撞区域
                    clicked_collision_index = check_collision_area_click(selected_tile, (mouse_x, mouse_y))
                    if clicked_collision_index >= 0:
                        delete_collision_area(selected_tile, clicked_collision_index)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    ui_clicked = False
                    # 检查属性模式按钮
                    if property_mode_button_rect.collidepoint(event.pos):
                        if selected_tile:
                            edit_properties_mode = not edit_properties_mode
                            if edit_properties_mode:
                                # 确保选中的图块有属性字段
                                if "properties" not in selected_tile:
                                    selected_tile["properties"] = {
                                        "type": "可通过",
                                        "collision": [],
                                        "interaction": "none",
                                        "triggers": [],
                                        "custom": {}
                                    }
                        else:
                            message = "请先选择一个图块"
                            message_display_time = pygame.time.get_ticks()
                        ui_clicked = True

                    if alignment_button_rect.collidepoint(event.pos):
                        alignment_menu_visible = not alignment_menu_visible
                        ui_clicked = True
                    elif alignment_menu_visible and alignment_menu_rect.collidepoint(event.pos):
                        idx = (event.pos[1] - alignment_menu_rect.y) // 30
                        if 0 <= idx < len(alignment_modes):
                            current_alignment_mode = alignment_modes[idx]
                            alignment_menu_visible = False
                        ui_clicked = True
                    else:
                        alignment_menu_visible = False  # 点击其他区域时关闭菜单

                    if show_load_menu:  # 当加载菜单显示时
                        if load_button_rect.collidepoint(event.pos):
                            load_saved_maps()  # 点击"加载地图"按钮，加载已保存的地图列表
                            ui_clicked = True
                        elif saved_maps:  # 如果有保存的地图
                            map_list_rect = pygame.Rect(load_menu_rect.right + 20, load_menu_rect.top, 200, 300)
                            y_offset = map_list_rect.y + 20
                            for map_file in saved_maps:
                                map_rect = pygame.Rect(map_list_rect.x + 20, y_offset, 160, 30)
                                if map_rect.collidepoint(event.pos):
                                    load_map(map_file)  # 加载选中的地图
                                    show_load_menu = False  # 关闭加载菜单
                                    ui_clicked = True
                                    break
                                y_offset += 40
                    else:  # 处理地图编辑逻辑
                        for item in buttons:
                            if item['type'] == 'button' and item['rect'].collidepoint(event.pos):
                                current_tile = item['name']
                                current_category = item['category']
                                current_scale = 1.0  # 重置为初始大小
                                rotation_angle = 0  # 重置旋转角度
                                selected_tile = None
                                ui_clicked = True
                                break

                    # 如果没有点击UI，则处理地图放置逻辑
                    if not ui_clicked and mouse_in_map:
                        if current_tile:  # 在地图上放置地皮
                            save_state()  # 在修改前保存状态

                            # 获取图片尺寸
                            image_width = tile_images[current_category][current_tile][current_scale][
                                rotation_angle].get_width()
                            image_height = tile_images[current_category][current_tile][current_scale][
                                rotation_angle].get_height()

                            # 获取对齐偏移
                            alignment_offset_x, alignment_offset_y = get_alignment_offset(current_alignment_mode,
                                                                                          image_width, image_height)

                            # 计算预览图片在鼠标位置的对齐点（世界坐标）
                            alignment_point_x = mouse_x + camera_pos[0] - image_width // 2 + alignment_offset_x
                            alignment_point_y = mouse_y + camera_pos[1] - image_height // 2 + alignment_offset_y

                            # 将对齐点吸附到网格
                            if show_grid:
                                snapped_alignment_x = (alignment_point_x // grid_size) * grid_size
                                snapped_alignment_y = (alignment_point_y // grid_size) * grid_size
                            else:
                                snapped_alignment_x = alignment_point_x
                                snapped_alignment_y = alignment_point_y

                            # 计算 tile_x 和 tile_y，使得图片的对齐点与吸附后的网格点重合
                            tile_x = snapped_alignment_x - alignment_offset_x
                            tile_y = snapped_alignment_y - alignment_offset_y

                            # 创建 tile_rect
                            tile_rect = pygame.Rect(
                                tile_x,
                                tile_y,
                                image_width,
                                image_height
                            )

                            # 添加到 map_tiles，包含属性
                            map_tiles.append({
                                "category": current_category,
                                "tile": current_tile,
                                "rect": tile_rect,
                                "scale": current_scale,
                                "angle": rotation_angle,
                                "selected": False,
                                "properties": {
                                    "type": "可通过",
                                    "collision": [],
                                    "interaction": "none",
                                    "triggers": [],
                                    "custom": {}
                                }
                            })
                            selected_tile = None

                        if not current_tile and selected_tile:
                            selected_tile['selected'] = True

                elif event.button == 4:  # 滚轮向上
                    scroll_offset = smooth_scroll(1)
                    generate_buttons()  # 重新生成按钮布局
                elif event.button == 5:  # 滚轮向下
                    scroll_offset = smooth_scroll(-1)
                    generate_buttons()

                # 检查滑动条是否被点击
                scroll_bar_position, scroll_bar_height = calculate_scroll_bar()
                if pygame.Rect(0, scroll_bar_position, scroll_bar_width, scroll_bar_height).collidepoint(event.pos):
                    scroll_bar_dragging = True
                    scroll_start_y = event.pos[1]
                    scroll_start_offset = scroll_offset

            elif event.type == pygame.MOUSEBUTTONUP:
                scroll_bar_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if scroll_bar_dragging:
                    total_button_height = total_button_height  # 使用全局变量
                    visible_height = screen_height - 2 * button_margin
                    move_amount = event.pos[1] - scroll_start_y
                    scroll_offset = scroll_start_offset - int(move_amount * total_button_height / visible_height)
                    scroll_offset = min(0, max(scroll_offset, visible_height - total_button_height))
                    generate_buttons()

            elif event.type == pygame.KEYDOWN or event.type == pygame.TEXTINPUT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j:
                        show_load_menu = not show_load_menu
                        if not show_load_menu:
                            selected_map = None  # 重置选中地图

                    if event.key in [pygame.K_ESCAPE, pygame.K_DELETE, pygame.K_BACKSPACE]:
                        if event.key == pygame.K_ESCAPE:
                            if selected_tile:
                                selected_tile['selected'] = False
                                selected_tile = None
                            current_tile = None
                            current_category = None
                        if event.key in [pygame.K_DELETE, pygame.K_BACKSPACE]:
                            if selected_tile and selected_tile['selected']:
                                save_state()  # 在删除前保存状态
                                map_tiles.remove(selected_tile)
                                selected_tile = None
                                # 删除后更新 hovered_tiles
                                hovered_tiles = [tile for tile in reversed(map_tiles) if
                                                 tile['rect'].collidepoint(mouse_x + camera_pos[0],
                                                                           mouse_y + camera_pos[1])]
                                hovered_index = 0 if hovered_tiles else -1
                    if mouse_in_map:  # 只在地图区域内响应WASD
                        if event.key == pygame.K_w:
                            w_pressed = True
                        if event.key == pygame.K_s:
                            s_pressed = True

                    if event.key == pygame.K_q:
                        w_pressed = True
                    if event.key == pygame.K_e:
                        s_pressed = True
                    if event.key == pygame.K_r:
                        r_pressed = True
                    if event.key == pygame.K_TAB:
                        tab_pressed = True
                    if event.key == pygame.K_c:
                        show_reference_lines = not show_reference_lines  # 切换参考线开关
                    if event.key == pygame.K_g:
                        show_grid = not show_grid  # 切换网格显示
                    if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        grid_size += 10  # 增大网格大小
                    if event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                        grid_size = max(10, grid_size - 10)  # 减小网格大小，最小为10

                    if current_tile:
                        # 检测方向键以调整预览位置
                        if event.key == pygame.K_UP:
                            mouse_y -= 1
                        if event.key == pygame.K_DOWN:
                            mouse_y += 1
                        if event.key == pygame.K_LEFT:
                            mouse_x -= 1
                        if event.key == pygame.K_RIGHT:
                            mouse_x += 1
                        pygame.mouse.set_pos(mouse_x + function_area_width, mouse_y)

                    # 新建地图
                    if event.key == pygame.K_n and (
                            keys[pygame.K_LMETA] or keys[pygame.K_RMETA] or keys[pygame.K_LCTRL] or keys[
                        pygame.K_RCTRL]):
                        show_save_prompt_dialog = True  # 显示保存提示对话框

                    # 检测重做操作（CMD + Shift + Z）
                    if event.key == pygame.K_z and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA]) and (
                            keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                        if redo_stack:
                            undo_stack.append(copy.deepcopy(map_tiles))
                            map_tiles = redo_stack.pop()
                    # 检测撤销操作（CMD + Z）
                    elif event.key == pygame.K_z and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA]):
                        if undo_stack:
                            redo_stack.append(copy.deepcopy(map_tiles))
                            map_tiles = undo_stack.pop()

                    # 检测保存操作（Ctrl + S 或 Cmd + S）
                    if event.key == pygame.K_s and (
                            keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_LMETA] or keys[
                        pygame.K_RMETA]):
                        show_save_dialog = True
                        # 初始化保存输入框
                        save_input_box = InputBox(save_dialog_rect.x + 100, save_dialog_rect.y + 75, 150, 32)
                elif event.type == pygame.TEXTINPUT:
                    pass  # 在此处不需要处理，输入框会自行处理

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q and w_pressed:
                    current_scale = get_next_scale(current_scale, 'up')
                    w_pressed = False
                if event.key == pygame.K_e and s_pressed:
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

    # 在主循环中使用按键状态更新摄像机位置
    if not show_new_map_window and not show_save_dialog and not show_save_prompt_dialog and mouse_in_map:
        if keys[pygame.K_w]:
            camera_pos[1] -= 10
        if keys[pygame.K_s]:
            camera_pos[1] += 10
        if keys[pygame.K_a]:
            camera_pos[0] -= 10
        if keys[pygame.K_d]:
            camera_pos[0] += 10

    # 边界检查，确保摄像机位置在地图范围内
    camera_pos[0] = max(0, min(camera_pos[0], world_width - map_area_width))
    camera_pos[1] = max(0, min(camera_pos[1], world_height - screen_height))

    # 属性编辑模式下，直接绘制属性编辑界面
    if edit_properties_mode:
        # 绘制功能区域背景
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, function_area_width, screen_height))
        # 绘制属性编辑按钮
        draw_property_mode_button()
        # 绘制属性编辑界面
        draw_property_editor(selected_tile)
    else:
        # 绘制地图上的元素
        for tile in map_tiles:
            # 使用预先加载的旋转图像
            rotated_image = tile_images[tile["category"]][tile["tile"]][tile["scale"]][tile["angle"]]
            screen.blit(rotated_image, tile["rect"].move(-camera_pos[0] + function_area_width, -camera_pos[1]))

            # 如果该地皮被选中，填充半透明红色
            if tile["selected"]:
                overlay_rect = tile["rect"].move(-camera_pos[0] + function_area_width, -camera_pos[1])
                overlay = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
                overlay.fill(SEMI_TRANSPARENT_RED)
                screen.blit(overlay, overlay_rect)
            # 如果鼠标悬停在该地皮上，绘制红色边框
            elif selected_tile == tile:
                pygame.draw.rect(screen, RED, tile["rect"].move(-camera_pos[0] + function_area_width, -camera_pos[1]),
                                 3)

        # 绘制功能区域背景
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, function_area_width, screen_height))

        # 绘制属性编辑按钮
        draw_property_mode_button()

        # 绘制对齐模式按钮和菜单
        pygame.draw.rect(screen, LIGHT_GRAY, alignment_button_rect)
        alignment_text = font.render(f'对齐：{current_alignment_mode}', True, BLACK)
        screen.blit(alignment_text, (alignment_button_rect.x + 5, alignment_button_rect.y + 5))

        if alignment_menu_visible:
            pygame.draw.rect(screen, DARK_GRAY, alignment_menu_rect)
            for idx, mode in enumerate(alignment_modes):
                mode_rect = pygame.Rect(alignment_menu_rect.x, alignment_menu_rect.y + idx * 30,
                                        alignment_menu_rect.width, 30)
                pygame.draw.rect(screen, LIGHT_GRAY if mode == current_alignment_mode else WHITE, mode_rect)
                mode_text = font.render(mode, True, BLACK)
                screen.blit(mode_text, (mode_rect.x + 5, mode_rect.y + 5))

        # 显示当前选中的地皮预览，保持比例，按对齐方式显示
        if current_tile:
            # 获取图片尺寸
            original_image = tile_images[current_category][current_tile][current_scale][rotation_angle]
            image_width = original_image.get_width()
            image_height = original_image.get_height()

            # 获取对齐偏移
            alignment_offset_x, alignment_offset_y = get_alignment_offset(current_alignment_mode, image_width,
                                                                          image_height)

            # 计算预览图片在鼠标位置的对齐点（世界坐标）
            alignment_point_x = mouse_x + camera_pos[0] - image_width // 2 + alignment_offset_x
            alignment_point_y = mouse_y + camera_pos[1] - image_height // 2 + alignment_offset_y

            # 将对齐点吸附到网格
            if show_grid:
                snapped_alignment_x = (alignment_point_x // grid_size) * grid_size
                snapped_alignment_y = (alignment_point_y // grid_size) * grid_size
            else:
                snapped_alignment_x = alignment_point_x
                snapped_alignment_y = alignment_point_y

            # 计算预期放置位置的 tile_x 和 tile_y
            placement_tile_x = snapped_alignment_x - alignment_offset_x
            placement_tile_y = snapped_alignment_y - alignment_offset_y

            # 计算预期放置位置在屏幕上的坐标
            placement_screen_x = placement_tile_x - camera_pos[0] + function_area_width
            placement_screen_y = placement_tile_y - camera_pos[1]

            # 绘制预期放置位置的预览（30%透明度）
            placement_preview_image = original_image.copy()
            placement_preview_image.set_alpha(77)  # 30%透明度（255 * 0.3 ≈ 77）
            placement_preview_rect = placement_preview_image.get_rect(topleft=(placement_screen_x, placement_screen_y))
            screen.blit(placement_preview_image, placement_preview_rect)

            # 计算对齐点在屏幕上的坐标（预期放置位置）
            alignment_point_screen_x = placement_preview_rect.x + alignment_offset_x
            alignment_point_screen_y = placement_preview_rect.y + alignment_offset_y

            # 绘制对齐标记（预期放置位置）
            pygame.draw.circle(screen, RED, (alignment_point_screen_x, alignment_point_screen_y), 5)

            # 绘制鼠标位置的预览（50%透明度）
            mouse_preview_image = original_image.copy()
            mouse_preview_image.set_alpha(128)  # 50%透明度
            mouse_preview_rect = mouse_preview_image.get_rect(center=(mouse_x + function_area_width, mouse_y))
            screen.blit(mouse_preview_image, mouse_preview_rect)

            # 在鼠标预览图片上绘制对齐标记
            # 计算对齐点在鼠标预览图像上的坐标
            alignment_point_mouse_x = mouse_preview_rect.x + alignment_offset_x
            alignment_point_mouse_y = mouse_preview_rect.y + alignment_offset_y

            # 绘制对齐标记（鼠标预览图片）
            pygame.draw.circle(screen, RED, (alignment_point_mouse_x, alignment_point_mouse_y), 5)

        # 绘制按钮和界面信息，确保按钮在最上层显示
        for item in buttons:
            if item['type'] == 'category':
                rect = item['rect']
                pygame.draw.rect(screen, DARK_GRAY, rect)
                text = font.render(item['name'], True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif item['type'] == 'button':
                rect = item['rect']
                pygame.draw.rect(screen, WHITE, rect)

                # 缩略图保持原比例
                category = item['category']
                name = item['name']
                original_image = tile_images[category][name][1.0][0]  # 获取原始比例和角度的图像
                original_ratio = original_image.get_width() / original_image.get_height()
                if original_ratio >= 1:  # 如果宽大于高，限制宽度
                    target_width = button_width - 20
                    target_height = int(target_width / original_ratio)
                else:  # 如果高大于宽，限制高度
                    target_height = button_height - 40  # 给文字预留空间
                    target_width = int(target_height * original_ratio)

                thumbnail = pygame.transform.smoothscale(original_image, (target_width, target_height))

                # 将缩略图绘制到按钮内部，居中对齐
                thumbnail_rect = thumbnail.get_rect(center=(rect.centerx, rect.y + target_height // 2 + 10))
                screen.blit(thumbnail, thumbnail_rect)

                # 将按钮文字移到缩略图下方
                text = font.render(name, True, BLACK)
                text_rect = text.get_rect(center=(rect.centerx, rect.y + target_height + 25))
                screen.blit(text, text_rect)

        # 绘制滑动条
        scroll_bar_position, scroll_bar_height = calculate_scroll_bar()
        pygame.draw.rect(screen, scroll_bar_color,
                         pygame.Rect(0, scroll_bar_position, scroll_bar_width, scroll_bar_height))

        # 将小地图绘制到屏幕右下角
        thumbnail_width, thumbnail_height = 200, 200 * world_height / world_width
        thumbnail_surface = pygame.Surface((thumbnail_width, thumbnail_height))
        thumbnail_surface.fill(DARK_GRAY)

        # 绘制地图内容到缩略图
        scale_factor = thumbnail_width / world_width
        for tile in map_tiles:
            thumb_rect = pygame.Rect(tile["rect"].x * scale_factor, tile["rect"].y * scale_factor,
                                     tile["rect"].width * scale_factor, tile["rect"].height * scale_factor)
            # 使用预加载的旋转图像
            scaled_thumb_image = pygame.transform.smoothscale(
                tile_images[tile["category"]][tile["tile"]][tile["scale"]][tile["angle"]],
                (thumb_rect.width, thumb_rect.height))
            thumbnail_surface.blit(scaled_thumb_image, thumb_rect)

        # 绘制缩略图边框和视野范围
        thumbnail_rect = pygame.Rect(screen_width - thumbnail_width - 10, screen_height - thumbnail_height - 10,
                                     thumbnail_width, thumbnail_height)
        pygame.draw.rect(screen, WHITE, thumbnail_rect, 2)

        # 绘制视野范围在缩略图中的位置
        view_rect = pygame.Rect(
            camera_pos[0] * thumbnail_width // world_width,
            camera_pos[1] * thumbnail_height // world_height,
            map_area_width * thumbnail_width // world_width,
            screen_height * thumbnail_height // world_height,
        )
        pygame.draw.rect(thumbnail_surface, RED, view_rect, 2)

        # 将缩略图绘制到屏幕右下角
        screen.blit(thumbnail_surface, (screen_width - thumbnail_width - 10, screen_height - thumbnail_height - 10))

        # 显示参考线状态
        reference_text = f"参考线: {'开' if show_reference_lines else '关'}"
        reference_surface = font.render(reference_text, True, WHITE)
        screen.blit(reference_surface, (10, screen_height - 60))

        # 显示网格状态
        grid_text = f"网格: {'开' if show_grid else '关'} (大小: {grid_size})"
        grid_surface = font.render(grid_text, True, WHITE)
        screen.blit(grid_surface, (10, screen_height - 90))

        # 只有在没有选择元素按钮的情况下显示提示
        if not current_tile:
            if hovered_tiles:
                info_text = "当前元素：" + " -> ".join(
                    [f"{tile['category']}/{tile['tile']}" for tile in hovered_tiles[::-1]])
            else:
                info_text = "当前元素：无"

            info_surface = font.render(info_text, True, WHITE)
            screen.blit(info_surface, (10, screen_height - 30))

    current_time = pygame.time.get_ticks()
    if message and (current_time - message_display_time > 5000):  # 5秒后清除消息
        message = None

    # 在屏幕底部显示消息
    if message:
        message_surface = font.render(message, True, WHITE)
        screen.blit(message_surface, (10, screen_height - 30))

    # 确保加载菜单在最上层绘制
    if show_load_menu:
        draw_load_menu()

    # 绘制新建地图窗口
    if show_new_map_window:
        draw_new_map_window()

    # 绘制保存对话框
    if show_save_dialog:
        draw_save_dialog()

    # 绘制保存提示对话框
    if show_save_prompt_dialog:
        draw_save_prompt_dialog()

    pygame.display.flip()
    clock.tick(60)  # 设置刷新率为60帧

pygame.quit()
sys.exit()