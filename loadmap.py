import pygame
import json
import os

class LoadMap:
    def __init__(self):
        # 动态加载所有地皮元素
        self.resource_path = "/Users/liya/Documents/编程文件/我的游戏/我的肉鸽子游戏/resources/地图编辑器的元素类型"
        self.tile_images = self.get_tiles()

    def get_tiles(self):
        # 获得文件夹中所有的元素
        tile_images = {}
        for file_name in os.listdir(self.resource_path):
            if file_name.endswith(".png"):
                name = file_name.split(".")[0]  # 使用文件名作为元素名称
                tile_images[name] = self.load_scaled_images(os.path.join(self.resource_path, file_name))
        return tile_images

    def load_scaled_images(self, image_path):
        # 加载图片资源并预先计算不同大小的图像
        original_image = pygame.image.load(image_path)
        sizes = [1.0, 0.8, 0.6, 0.4, 0.25, 0.2, 0.1]
        return {scale: pygame.transform.scale(original_image,
                                              (int(original_image.get_width() * scale),
                                               int(original_image.get_height() * scale)))
                for scale in sizes}

    def load_saved_maps(self):
        # 读取已经保存的地图
        global saved_maps
        saved_maps = [f for f in os.listdir() if f.endswith('.json')]

    def load_map(self,filename, screen):
        # 加载地图到世界中
        with open(filename, 'r') as f:
            map_data = json.load(f)
        map_tiles = []
        for tile_data in map_data:
            tile_rect = pygame.Rect(tile_data["x"], tile_data["y"],
                                    self.tile_images[tile_data["tile"]][tile_data["scale"]].get_width(),
                                    self.tile_images[tile_data["tile"]][tile_data["scale"]].get_height())
            map_tiles.append({"tile": tile_data["tile"], "rect": tile_rect,
                              "scale": tile_data["scale"], "angle": tile_data["angle"], "selected": False})

        # 绘制地图上的元素
        for tile in map_tiles:
            rotated_image = pygame.transform.rotate(self.tile_images[tile["tile"]][tile["scale"]], tile["angle"])
            screen.blit(rotated_image, tile["rect"])


if __name__ == '__main__':

