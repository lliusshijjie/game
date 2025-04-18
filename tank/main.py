import pygame
import sys
import random
from tank import Tank
from bullet import Bullet
from wall import Wall

# 初始化Pygame
pygame.init()

# 设置游戏窗口
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("坦克大战")

# 初始化时钟
clock = pygame.time.Clock()
FPS = 60

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# 创建精灵组
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
tanks = pygame.sprite.Group()
walls = pygame.sprite.Group()

# 创建玩家坦克
player = Tank(WIDTH // 4, HEIGHT // 2, GREEN)
all_sprites.add(player)
tanks.add(player)

# 创建敌人坦克
enemy = Tank(WIDTH * 3 // 4, HEIGHT // 2, RED, control_type="enemy")
all_sprites.add(enemy)
tanks.add(enemy)

# 创建墙壁
def create_walls():
    # 创建边界墙
    wall_thickness = 20
    
    # 上下边界
    for x in range(0, WIDTH, wall_thickness):
        walls.add(Wall(x, 0, wall_thickness, wall_thickness, "steel"))
        walls.add(Wall(x, HEIGHT - wall_thickness, wall_thickness, wall_thickness, "steel"))
    
    # 左右边界
    for y in range(wall_thickness, HEIGHT - wall_thickness, wall_thickness):
        walls.add(Wall(0, y, wall_thickness, wall_thickness, "steel"))
        walls.add(Wall(WIDTH - wall_thickness, y, wall_thickness, wall_thickness, "steel"))
    
    # 创建随机的内部墙壁
    for _ in range(20):
        x = random.randint(wall_thickness * 2, WIDTH - wall_thickness * 3)
        y = random.randint(wall_thickness * 2, HEIGHT - wall_thickness * 3)
        width = random.choice([20, 40, 60])
        height = random.choice([20, 40, 60])
        wall_type = random.choice(["brick", "brick", "steel", "water"])  # 砖墙较多
        
        # 确保墙壁不会直接挡住坦克
        wall_rect = pygame.Rect(x, y, width, height)
        player_rect = pygame.Rect(player.x - 60, player.y - 60, 120, 120)
        enemy_rect = pygame.Rect(enemy.x - 60, enemy.y - 60, 120, 120)
        
        if not wall_rect.colliderect(player_rect) and not wall_rect.colliderect(enemy_rect):
            new_wall = Wall(x, y, width, height, wall_type)
            walls.add(new_wall)
    
    # 将所有墙壁添加到所有精灵组
    all_sprites.add(walls)

create_walls()

# 游戏结束标志
game_over = False
winner = None

# 主游戏循环
def game_loop():
    global game_over, winner
    
    # 玩家控制变量
    player_dx, player_dy = 0, 0
    
    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 键盘按下事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                # 游戏结束后按空格重新开始
                if game_over and event.key == pygame.K_SPACE:
                    restart_game()
        
        # 如果游戏结束，显示结束界面
        if game_over:
            display_game_over()
            continue
            
        # 获取按键状态
        keys = pygame.key.get_pressed()
        
        # 玩家坦克移动
        player_dx, player_dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_dx = 1
        
        # 射击
        if keys[pygame.K_SPACE]:
            bullet = player.shoot()
            if bullet:
                bullets.add(bullet)
                all_sprites.add(bullet)
        
        # 移动玩家坦克
        player.move(player_dx, player_dy)
        
        # 敌人AI控制
        control_enemy()
        
        # 更新所有精灵
        all_sprites.update()
        
        # 检测碰撞
        handle_collisions()
        
        # 渲染
        render()
        
        # 控制帧率
        clock.tick(FPS)

# 敌人AI控制
def control_enemy():
    if random.random() < 0.02:  # 2%的几率改变方向
        enemy.angle = random.randint(0, 360)
    
    # 根据当前角度移动
    rad_angle = pygame.math.Vector2(1, 0).rotate(-enemy.angle)
    enemy.move(rad_angle.x, rad_angle.y)
    
    # 有10%的几率射击
    if random.random() < 0.1:
        bullet = enemy.shoot()
        if bullet:
            bullets.add(bullet)
            all_sprites.add(bullet)

# 处理碰撞
def handle_collisions():
    global game_over, winner
    
    # 坦克与墙壁的碰撞
    for tank in tanks:
        # 碰撞后将坦克推回
        tank_collisions = pygame.sprite.spritecollide(tank, walls, False)
        if tank_collisions:
            # 简单的碰撞响应 - 后退
            if tank == player:
                player.move(-player_dx * 2, -player_dy * 2)
            else:
                # 敌人遇到墙壁后随机改变方向
                enemy.angle = random.randint(0, 360)
    
    # 子弹与坦克的碰撞
    for bullet in bullets:
        # 跳过自己发射的子弹
        hit_tanks = pygame.sprite.spritecollide(bullet, tanks, False)
        for tank in hit_tanks:
            if bullet.owner != tank:  # 不会被自己的子弹击中
                if tank.take_damage(bullet.damage):
                    # 坦克被摧毁，游戏结束
                    game_over = True
                    winner = "玩家" if tank == enemy else "敌人"
                bullet.hit(tank)
    
    # 子弹与墙壁的碰撞
    for bullet in bullets:
        hit_walls = pygame.sprite.spritecollide(bullet, walls, False)
        for wall in hit_walls:
            wall.hit_by_bullet(bullet)
            bullet.kill()

# 渲染函数
def render():
    # 清屏
    screen.fill(BLACK)
    
    # 绘制所有精灵
    all_sprites.draw(screen)
    
    # 显示坦克血量
    font = pygame.font.SysFont(None, 24)
    player_health_text = font.render(f"玩家血量: {player.health}", True, WHITE)
    enemy_health_text = font.render(f"敌人血量: {enemy.health}", True, WHITE)
    screen.blit(player_health_text, (10, 10))
    screen.blit(enemy_health_text, (WIDTH - 150, 10))
    
    # 刷新屏幕
    pygame.display.flip()

# 显示游戏结束界面
def display_game_over():
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 48)
    game_over_text = font.render(f"游戏结束! {winner}胜利!", True, WHITE)
    restart_text = font.render("按空格键重新开始", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    
    pygame.display.flip()

# 重新开始游戏
def restart_game():
    global game_over, winner, player, enemy, all_sprites, bullets, tanks, walls
    
    # 重置游戏状态
    game_over = False
    winner = None
    
    # 清空所有精灵组
    all_sprites.empty()
    bullets.empty()
    tanks.empty()
    walls.empty()
    
    # 重新创建坦克
    player = Tank(WIDTH // 4, HEIGHT // 2, GREEN)
    all_sprites.add(player)
    tanks.add(player)
    
    enemy = Tank(WIDTH * 3 // 4, HEIGHT // 2, RED, control_type="enemy")
    all_sprites.add(enemy)
    tanks.add(enemy)
    
    # 重新创建墙壁
    create_walls()

# 启动游戏
if __name__ == "__main__":
    game_loop() 