# -*- coding: utf-8 -*-
import cocos
from cocos.director import director
import sys
import os
import json
import datetime
from PIL import Image
import pyglet
import math
from fontTools.ttLib import TTFont  # 需要安装 fontTools 库

# 安装 fontTools 库
# pip install fonttools

# 设置资源路径
resource_path = "地图编辑器的元素类型/"  # 请替换为你的资源路径

# 定义颜色
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)
LIGHT_GREEN = (144, 238, 144, 255)
DARK_GRAY = (50, 50, 50, 255)
SEMI_TRANSPARENT_RED = (255, 0, 0, 128)
LIGHT_GRAY = (200, 200, 200, 255)

# 定义全局变量
world_width, world_height = 3200, 2400
map_tiles = []
current_tile = None
current_scale = 1.0
rotation_angle = 0
scale_levels = [1.0, 0.75, 0.5, 0.25]
camera_pos = [0, 0]
show_reference_lines = True
message = None
message_display_time = 0
show_load_menu = False
saved_maps = []
selected_map = None
show_new_map_window = False
font_size = 24
function_area_width = 700  # 功能区域宽度
map_area_width = 700  # 地图编辑区域宽度

# 加载中文字体
font_path = "/Users/liya/Documents/编程文件/我的游戏/我的肉鸽子游戏/resources/XiangJiaoDaJiangJunLingGanTi-2.ttf"  # 请替换为你的字体路径
if not os.path.exists(font_path):
    font_name = 'SimHei'  # 使用系统默认字体
else:
    pyglet.font.add_file(font_path)
    # 获取字体的真实名称
    def get_font_name(font_path):
        font = TTFont(font_path)
        name = ''
        for record in font['name'].names:
            if record.nameID == 4 and record.platformID == 3 and record.langID == 0x409:
                name = str(record.string, 'utf-16-be')
                break
            elif record.nameID == 4 and record.platformID == 3:
                name = str(record.string, 'utf-16-be')
        font.close()
        return name

    font_name = get_font_name(font_path)
    if not font_name:
        font_name = 'CustomFont'  # 如果无法获取字体名称，使用默认名称

# 加载字体
font = pyglet.font.load(font_name, font_size)

# 加载图片资源并预先计算不同大小的图像
def load_scaled_images(image_path):
    original_image = Image.open(image_path).convert('RGBA')
    sizes = [1.0, 0.75, 0.5, 0.25]
    scaled_images = {}
    for scale in sizes:
        resized_image = original_image.resize(
            (int(original_image.width * scale), int(original_image.height * scale)),
            Image.LANCZOS  # 使用抗锯齿算法
        )
        image_data = pyglet.image.ImageData(resized_image.width, resized_image.height, 'RGBA', resized_image.tobytes())
        scaled_images[scale] = image_data
    return scaled_images

# 动态加载所有地皮元素
tile_images = {}
for file_name in os.listdir(resource_path):
    if file_name.endswith(".png"):
        name = file_name.split(".")[0]  # 使用文件名作为元素名称
        tile_images[name] = load_scaled_images(os.path.join(resource_path, file_name))

# 定义输入框类
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = cocos.rect.Rect(x, y, w, h)
        self.text = text
        self.active = False
        self.font_size = 18
        self.label = pyglet.text.Label(
            self.text,
            font_name=font_name,
            font_size=self.font_size,
            color=(0, 0, 0, 255),
            x=x + 5,
            y=y + h // 2,
            anchor_x='left',
            anchor_y='center'
        )

    def handle_key_press(self, symbol, modifiers):
        if self.active:
            if symbol == pyglet.window.key.BACKSPACE:
                self.text = self.text[:-1]
            elif symbol == pyglet.window.key.ENTER:
                pass  # 在主循环中处理回车事件
            else:
                if 32 <= symbol <= 126:  # 可打印字符
                    char = chr(symbol)
                    if char.isdigit():
                        self.text += char
            self.label.text = self.text

    def draw(self):
        color = LIGHT_GRAY if self.active else DARK_GRAY
        pyglet.gl.glColor4f(*[c / 255.0 for c in color])
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                             ('v2f', [
                                 self.rect.x, self.rect.y,
                                 self.rect.x + self.rect.width, self.rect.y,
                                 self.rect.x + self.rect.width, self.rect.y + self.rect.height,
                                 self.rect.x, self.rect.y + self.rect.height
                             ])
                             )
        self.label.draw()

# 定义地图层
class MapLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True  # 使层能够处理事件

    def __init__(self):
        super(MapLayer, self).__init__()
        self.selected_tile = None
        self.hovered_tiles = []
        self.hovered_index = 0
        self.w_pressed = False
        self.s_pressed = False
        self.r_pressed = False
        self.tab_pressed = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.current_tile_sprite = None
        self.camera_pos = [0, 0]
        self.function_area_width = function_area_width
        self.map_area_width = map_area_width
        self.world_width = world_width
        self.world_height = world_height
        self.message = None
        self.message_display_time = 0
        self.schedule(self.update)

    def on_mouse_press(self, x, y, buttons, modifiers):
        global current_tile, current_scale, rotation_angle, map_tiles, selected_tile

        # 将屏幕坐标转换为地图坐标
        map_x, map_y = self.point_to_local(x, y)
        ui_clicked = False

        # 判断是否在地图区域内
        if x >= self.function_area_width:
            if buttons & pyglet.window.mouse.LEFT:
                if current_tile:
                    image = tile_images[current_tile][current_scale]
                    tile_sprite = cocos.sprite.Sprite(image)
                    tile_sprite.position = map_x, map_y
                    tile_sprite.scale = current_scale
                    tile_sprite.rotation = rotation_angle
                    self.add(tile_sprite)
                    map_tiles.append({
                        "tile": current_tile,
                        "sprite": tile_sprite,
                        "scale": current_scale,
                        "angle": rotation_angle,
                        "selected": False
                    })
                    selected_tile = None
                else:
                    # 检测点击的tile
                    for tile in reversed(map_tiles):
                        if tile["sprite"].get_rect().contains(map_x, map_y):
                            selected_tile = tile
                            selected_tile["selected"] = True
                            break
            elif buttons & pyglet.window.mouse.SCROLL_UP:
                self.camera_pos[1] -= 50
            elif buttons & pyglet.window.mouse.SCROLL_DOWN:
                self.camera_pos[1] += 50

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x, self.mouse_y = x, y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if x >= self.function_area_width:
            if buttons & pyglet.window.mouse.LEFT:
                self.camera_pos[0] -= dx
                self.camera_pos[1] -= dy

    def on_key_press(self, symbol, modifiers):
        global current_scale, rotation_angle, current_tile, selected_tile

        if symbol == pyglet.window.key.W:
            self.w_pressed = True
        if symbol == pyglet.window.key.S:
            self.s_pressed = True
        if symbol == pyglet.window.key.R:
            self.r_pressed = True
        if symbol == pyglet.window.key.TAB:
            self.tab_pressed = True
        if symbol == pyglet.window.key.ESCAPE:
            if selected_tile:
                selected_tile['selected'] = False
                selected_tile = None
            current_tile = None
        if symbol == pyglet.window.key.DELETE:
            if selected_tile and selected_tile['selected']:
                self.remove(selected_tile["sprite"])
                map_tiles.remove(selected_tile)
                selected_tile = None

    def on_key_release(self, symbol, modifiers):
        global current_scale, rotation_angle, scale_levels

        if symbol == pyglet.window.key.W and self.w_pressed:
            idx = scale_levels.index(current_scale)
            if idx > 0:
                current_scale = scale_levels[idx - 1]
            self.w_pressed = False
        if symbol == pyglet.window.key.S and self.s_pressed:
            idx = scale_levels.index(current_scale)
            if idx < len(scale_levels) - 1:
                current_scale = scale_levels[idx + 1]
            self.s_pressed = False
        if symbol == pyglet.window.key.R and self.r_pressed:
            rotation_angle = (rotation_angle + 90) % 360
            self.r_pressed = False

    def update(self, dt):
        # 更新摄像机位置
        x = min(max(self.camera_pos[0], 0), self.world_width - self.map_area_width)
        y = min(max(self.camera_pos[1], 0), self.world_height - director.get_window_size()[1])
        self.parent.set_focus(x, y)

    def draw(self):
        super(MapLayer, self).draw()
        # 绘制选中的tile
        if current_tile:
            map_x, map_y = self.point_to_local(self.mouse_x, self.mouse_y)
            image = tile_images[current_tile][current_scale]
            if self.current_tile_sprite:
                self.remove(self.current_tile_sprite)
            self.current_tile_sprite = cocos.sprite.Sprite(image)
            self.current_tile_sprite.position = map_x, map_y
            self.current_tile_sprite.scale = current_scale
            self.current_tile_sprite.rotation = rotation_angle
            self.add(self.current_tile_sprite)

# 定义UI层
class UILayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(UILayer, self).__init__()
        self.buttons = {}
        self.font_size = 18
        self.function_area_width = function_area_width
        self.scroll_offset = 0
        self.scroll_speed = 50
        self.create_buttons()  # 确保在调用之前定义了 function_area_width

    def create_buttons(self):
        x_offset, y_offset = 10, director.get_window_size()[1] - 130
        button_width, button_height = 120, 120
        button_margin = 10
        for idx, name in enumerate(tile_images.keys()):
            image = tile_images[name][1.0]
            button = cocos.sprite.Sprite(image, position=(x_offset + button_width // 2, y_offset))
            button.scale = 0.5
            self.add(button)
            self.buttons[name] = {'sprite': button, 'rect': cocos.rect.Rect(x_offset, y_offset - button_height // 2, button_width, button_height)}
            x_offset += button_width + button_margin
            if x_offset + button_width > self.function_area_width:
                x_offset = 10
                y_offset -= button_height + button_margin

    def on_mouse_press(self, x, y, buttons, modifiers):
        global current_tile
        if x <= self.function_area_width:
            if buttons & pyglet.window.mouse.LEFT:
                for name, info in self.buttons.items():
                    if info['rect'].contains(x, y):
                        current_tile = name
                        break
            elif buttons & pyglet.window.mouse.SCROLL_UP:
                self.scroll_offset += self.scroll_speed
                self.update_button_positions()
            elif buttons & pyglet.window.mouse.SCROLL_DOWN:
                self.scroll_offset -= self.scroll_speed
                self.update_button_positions()

    def update_button_positions(self):
        x_offset, y_offset = 10, director.get_window_size()[1] - 130 + self.scroll_offset
        button_width, button_height = 120, 120
        button_margin = 10
        for idx, (name, info) in enumerate(self.buttons.items()):
            info['sprite'].position = (x_offset + button_width // 2, y_offset)
            info['rect'] = cocos.rect.Rect(x_offset, y_offset - button_height // 2, button_width, button_height)
            x_offset += button_width + button_margin
            if x_offset + button_width > self.function_area_width:
                x_offset = 10
                y_offset -= button_height + button_margin

    def draw(self):
        # 绘制功能区域背景
        pyglet.gl.glColor4f(*[c / 255.0 for c in [DARK_GRAY[0] / 255.0, DARK_GRAY[1] / 255.0, DARK_GRAY[2] / 255.0, 1]])
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                             ('v2f', [
                                 0, 0,
                                 self.function_area_width, 0,
                                 self.function_area_width, director.get_window_size()[1],
                                 0, director.get_window_size()[1]
                             ])
                             )
        super(UILayer, self).draw()

# 主函数
def main():
    director.init(width=1400, height=800, caption="地图编辑器")

    # 创建地图层和UI层
    map_layer = MapLayer()
    ui_layer = UILayer()

    # 创建滚动管理器
    scroller = cocos.layer.ScrollingManager()
    scroller.add(map_layer)

    # 创建场景并运行
    main_scene = cocos.scene.Scene(scroller, ui_layer)
    director.run(main_scene)

if __name__ == "__main__":
    main()
