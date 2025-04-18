import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, wall_type="brick"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        
        # 不同类型的墙壁
        self.wall_type = wall_type
        
        # 创建墙壁图像
        self.image = pygame.Surface((width, height))
        
        if wall_type == "brick":
            # 砖墙 - 可以被击毁
            self.image.fill((165, 42, 42))  # 砖红色
            self.health = 30
            self.destructible = True
        elif wall_type == "steel":
            # 钢墙 - 不可摧毁
            self.image.fill((128, 128, 128))  # 灰色
            self.health = 100
            self.destructible = False
        elif wall_type == "water":
            # 水 - 无法通过但可以射击
            self.image.fill((0, 0, 255))  # 蓝色
            self.health = float('inf')
            self.destructible = False
        else:
            # 默认墙壁
            self.image.fill((0, 0, 0))
            self.health = 10
            self.destructible = True
        
        # 为墙壁添加纹理
        if wall_type == "brick":
            # 添加砖块纹理
            for i in range(0, width, 10):
                for j in range(0, height, 5):
                    if (i // 10 + j // 5) % 2 == 0:
                        pygame.draw.rect(self.image, (190, 60, 60), (i, j, 10, 5))
    
    def hit_by_bullet(self, bullet):
        """当墙壁被子弹击中时调用"""
        if self.destructible:
            self.health -= bullet.damage
            if self.health <= 0:
                self.kill()
                return True
        return False 