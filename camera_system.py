# 接下来实现一个摄像机功能
# # 摄像机始终和玩家的位置保持一致 让最终的窗口 最终显现出来的800x600的窗口中 玩家处于中心 当然靠近边界时除外
from settings_constant import Settings

class Camera:
    def __init__(self):
        self.settings = Settings()
        self.pos = [0,0]
        self.screen_width = self.settings.screen_width
        self.screen_height = self.settings.screen_height

    def update(self, player_position):

        self.pos[0] = player_position[0] - self.screen_width//2
        self.pos[1] = player_position[1] - self.screen_height//2

        self.pos[0] = max(0, min(self.pos[0], self.settings.world_width - self.screen_width))
        self.pos[1] = max(0, min(self.pos[1], self.settings.world_height - self.screen_height))

        return self.pos







