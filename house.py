from settings_constant import Settings
from utils import is_colliding_with_houses
import pygame
import random

class House:
	def __init__(self, house_size = Settings.size_house ,map_width=Settings.world_width,map_height=Settings.world_height):
		self.settings = Settings
		self.nums = self.settings.nums_house
		self.size = house_size
		self.living_map_width = map_width
		self.living_map_height =  map_height
		self.equips = list(Settings.equip_pics.keys())
		self.houses = self.create_houses()

	# 生成房子
	def create_houses(self):
		houses_created = []
		for _ in range(self.nums):
			while True:
				x = random.randint(self.size, self.living_map_width - self.size)
				y = random.randint(self.size, self.living_map_height - self.size)
				new_house = pygame.Rect(x, y, self.size, self.size)
				if not is_colliding_with_houses(houses_created,new_house,):
					break
			equip = random.choice(self.equips)
			houses_created.append({"矩形":new_house,"equip":equip})
		return houses_created

	# 画房子
	def draw(self,surface):
		for house in self.houses:
			pygame.draw.rect(surface,Settings.colors["blue"],house["矩形"])

	# 给定房子的rect,画房子里的物品到相应的房子上,参数house是一个字典，包含了房子的矩形和物品,equip_pic的中心应该与房子的矩形的中心对齐
	def draw_equip(self,surface,house):
		if house["equip"] != None:
			equip_pic = Settings.equip_pics[house["equip"]]
			equip_rect = equip_pic.get_rect()
			equip_rect.center = house["矩形"].center
			surface.blit(equip_pic,equip_rect)

if __name__ == "__main__":
	# 生成800 600的游戏测试窗口来检查房子是否正常生成
	pygame.init()
	screen = pygame.display.set_mode((1600, 1200))
	pygame.display.set_caption("房子测试")
	house = House()
	print(house.houses)

	# 游戏循环
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		screen.fill(Settings.colors["white"])
		house.draw(screen)
		pygame.display.flip()
		pygame.time.delay(1000)



		