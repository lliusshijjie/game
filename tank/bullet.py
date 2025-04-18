import pygame
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, owner, speed=7, damage=10):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner = owner  # 发射子弹的坦克
        
        # 子弹图像
        self.image = pygame.Surface((8, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 0), (0, 0, 8, 4))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        
        # 计算子弹速度的向量分量
        rad_angle = math.radians(angle)
        self.dx = math.cos(rad_angle) * speed
        self.dy = -math.sin(rad_angle) * speed
        
        # 子弹生命时间（防止无限飞行）
        self.lifetime = 180  # 3秒（60帧/秒）
    
    def update(self):
        # 更新子弹位置
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        
        # 减少生命时间，到期自动消失
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        
        # 检查是否超出屏幕边界
        screen_width, screen_height = pygame.display.get_surface().get_size()
        if (self.x < 0 or self.x > screen_width or 
            self.y < 0 or self.y > screen_height):
            self.kill()
    
    def hit(self, target):
        """当子弹击中目标时调用"""
        # 自动消失
        self.kill() 