import pygame
import math

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color, control_type="player", speed=3):
        super().__init__()
        # 坦克基础属性
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.angle = 0
        self.control_type = control_type
        
        # 创建坦克表面
        self.original_image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.original_image, color, (0, 0, 40, 30))
        pygame.draw.rect(self.original_image, (50, 50, 50), (10, 0, 20, 10))  # 炮塔
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 坦克状态
        self.health = 100
        self.reload_time = 0
        self.reload_max = 30  # 30帧 (0.5秒) 射击冷却
    
    def update(self):
        # 减少射击冷却时间
        if self.reload_time > 0:
            self.reload_time -= 1
    
    def move(self, dx, dy):
        if dx != 0 and dy != 0:
            # 计算新角度（当有输入时）
            self.angle = math.degrees(math.atan2(-dy, dx))
        
        # 更新坦克位置
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # 边界检查
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        if self.x < 20:
            self.x = 20
        elif self.x > screen_width - 20:
            self.x = screen_width - 20
            
        if self.y < 15:
            self.y = 15
        elif self.y > screen_height - 15:
            self.y = screen_height - 15
        
        # 旋转坦克
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def shoot(self):
        if self.reload_time <= 0:
            self.reload_time = self.reload_max
            # 计算子弹的起始位置（炮管前端）
            rad_angle = math.radians(self.angle)
            bullet_x = self.x + math.cos(rad_angle) * 25
            bullet_y = self.y - math.sin(rad_angle) * 25
            
            from bullet import Bullet
            return Bullet(bullet_x, bullet_y, self.angle, self)
        return None
    
    def take_damage(self, damage=10):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False 