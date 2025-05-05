import pygame

# 用来检测物体是否与房子重叠 通常是用来生成玩家的位置
def is_overlapping(rect, houses):
	for house in houses:
		if rect.colliderect(house["矩形"]):
			return True
	return False

# 用来检测玩家移动的过程中是否与房子碰撞
def is_colliding_with_houses(houses,player_rect):
	for house in houses:
		if player_rect.colliderect(house["矩形"]):
			return house
	return None