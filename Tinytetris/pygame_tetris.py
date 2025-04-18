import pygame
import random
import time
import os
import math

# 初始化Pygame
pygame.init()
pygame.mixer.init()  # 初始化音频混合器

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 游戏设置
CELL_SIZE = 30  # 每个方块的像素大小
GRID_WIDTH = 15  # 游戏区域宽度（以方块数计）
GRID_HEIGHT = 25  # 游戏区域高度（以方块数计）
SCREEN_WIDTH = CELL_SIZE * (GRID_WIDTH + 8)  # 屏幕宽度
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT  # 屏幕高度

# 设置游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 设置游戏时钟
clock = pygame.time.Clock()
FPS = 60

# 设置字体 - 使用系统默认字体以支持中文
try:
    # 尝试加载系统中文字体
    system_fonts = pygame.font.get_fonts()
    font_name = None
    for font in ["simhei", "microsoftyahei", "simsun", "nsimsun", "fangson"]:
        if font in system_fonts:
            font_name = font
            break
    
    if font_name:
        game_font = pygame.font.SysFont(font_name, 36)
    else:
        # 如果找不到中文字体，尝试使用系统默认字体
        game_font = pygame.font.SysFont(None, 36)
except:
    # 最后的备选方案
    game_font = pygame.font.Font(None, 36)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# 方块颜色
SHAPE_COLORS = [
    CYAN,    # I
    BLUE,    # J
    ORANGE,  # L
    YELLOW,  # O
    GREEN,   # S
    MAGENTA, # T
    RED      # Z
]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.fall_speed = 0.5  # 方块下落速度（秒）
        self.last_fall_time = time.time()
        self.paused = False
        # 添加消除特效相关属性
        self.lines_to_clear = []  # 存储要消除的行
        self.clear_effect_start = 0  # 特效开始时间
        self.clear_effect_duration = 0.8  # 特效持续时间(秒)
        self.is_clearing = False  # 是否正在显示消除特效
        self.particles = []  # 消除特效粒子
        
        # 加载音效
        try:
            self.clear_sound = pygame.mixer.Sound("clear_sound.wav")
            # 如果音效文件不存在，创建一个简单的音效
        except:
            # 创建简单的音效
            self.create_clear_sound()
        
    def new_piece(self):
        # 随机选择一个方块形状
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = SHAPE_COLORS[shape_idx]
        
        # 方块起始位置（居中，顶部）
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {
            "shape": shape,
            "color": color,
            "x": x,
            "y": y,
            "rotation": 0
        }
    
    def rotate_piece(self, piece):
        # 创建方块的副本
        new_piece = piece.copy()
        shape = piece["shape"]
        
        # 计算转置矩阵并翻转行以实现90度旋转
        rows = len(shape)
        cols = len(shape[0])
        rotated = [[shape[rows - 1 - j][i] for j in range(rows)] for i in range(cols)]
        
        new_piece["shape"] = rotated
        return new_piece
    
    def is_valid_position(self, piece, x=None, y=None):
        if x is None:
            x = piece["x"]
        if y is None:
            y = piece["y"]
        
        shape = piece["shape"]
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    # 检查是否超出界限
                    if (y + row_idx >= GRID_HEIGHT or 
                        x + col_idx < 0 or 
                        x + col_idx >= GRID_WIDTH):
                        return False
                    
                    # 检查是否与已有方块重叠
                    if y + row_idx >= 0 and self.grid[y + row_idx][x + col_idx]:
                        return False
        return True
    
    def merge_piece(self):
        # 将当前方块合并到游戏网格中
        shape = self.current_piece["shape"]
        color_idx = SHAPE_COLORS.index(self.current_piece["color"]) + 1
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece["y"] + row_idx
                    grid_x = self.current_piece["x"] + col_idx
                    
                    # 如果方块顶部超出屏幕，游戏结束
                    if grid_y < 0:
                        self.game_over = True
                        return
                    
                    self.grid[grid_y][grid_x] = color_idx
    
    def clear_lines(self):
        # 检查已填满的行
        lines_to_clear = []
        for y in range(GRID_HEIGHT - 1, -1, -1):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # 如果有行需要消除
        if lines_to_clear:
            # 开始消除特效
            self.lines_to_clear = lines_to_clear
            self.clear_effect_start = time.time()
            self.is_clearing = True
            
            # 播放消除音效
            try:
                self.clear_sound.play()
            except:
                pass  # 如果播放失败，忽略错误
            
            # 更新分数
            lines_cleared = len(lines_to_clear)
            if lines_cleared == 1:
                self.score += 100 * self.level
            elif lines_cleared == 2:
                self.score += 300 * self.level
            elif lines_cleared == 3:
                self.score += 500 * self.level
            elif lines_cleared == 4:
                self.score += 800 * self.level
            
            # 每10000分提高一级
            self.level = max(1, self.score // 10000 + 1)
            # 调整下落速度
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
            
            return True
        return False
    
    def apply_line_clear(self):
        # 实际执行行消除（在特效结束后调用）
        for y in sorted(self.lines_to_clear):
            # 移除该行
            for y2 in range(y, 0, -1):
                self.grid[y2] = self.grid[y2 - 1][:]
            self.grid[0] = [0] * GRID_WIDTH
        
        # 重置特效状态
        self.lines_to_clear = []
        self.is_clearing = False
        self.particles = []  # 清除所有粒子
    
    def draw_clear_effect(self):
        # 绘制消除特效
        current_time = time.time()
        effect_time = current_time - self.clear_effect_start
        
        if effect_time > self.clear_effect_duration:
            # 特效结束，执行实际的行消除
            self.apply_line_clear()
            return
        
        # 计算特效动画参数
        effect_progress = effect_time / self.clear_effect_duration
        flash_intensity = abs(math.sin(effect_progress * math.pi * 8))
        
        # 创建粒子效果（只在特效开始时创建）
        if effect_time < 0.05 and not self.particles:
            self.create_particles()
        
        # 更新并绘制粒子
        self.update_particles(effect_progress)
        self.draw_particles()
        
        # 绘制闪烁效果
        for y in self.lines_to_clear:
            for x in range(GRID_WIDTH):
                # 计算闪烁颜色（从白色逐渐变为彩虹色）
                hue = (effect_progress * 360) % 360  # 色相值 0-360
                s = 1.0  # 饱和度
                v = flash_intensity  # 明度
                
                # HSV转RGB
                c = v * s
                x_comp = c * (1 - abs((hue / 60) % 2 - 1))
                m = v - c
                
                if 0 <= hue < 60:
                    r, g, b = c, x_comp, 0
                elif 60 <= hue < 120:
                    r, g, b = x_comp, c, 0
                elif 120 <= hue < 180:
                    r, g, b = 0, c, x_comp
                elif 180 <= hue < 240:
                    r, g, b = 0, x_comp, c
                elif 240 <= hue < 300:
                    r, g, b = x_comp, 0, c
                else:
                    r, g, b = c, 0, x_comp
                
                flash_color = (
                    int((r + m) * 255),
                    int((g + m) * 255),
                    int((b + m) * 255)
                )
                
                # 方块缩小效果
                shrink = int(CELL_SIZE * (1 - effect_progress * 0.5))
                offset = (CELL_SIZE - shrink) // 2
                
                # 绘制闪烁方块
                pygame.draw.rect(
                    screen, 
                    flash_color, 
                    (x * CELL_SIZE + offset, y * CELL_SIZE + offset, shrink, shrink)
                )
                
                # 绘制边框
                border_color = (255, 255, 255)
                pygame.draw.rect(
                    screen, 
                    border_color, 
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 
                    2
                )

    def create_particles(self):
        # 为每一行创建粒子效果
        for y in self.lines_to_clear:
            for x in range(GRID_WIDTH):
                # 为每个方块创建多个粒子
                for _ in range(5):
                    particle = {
                        'x': x * CELL_SIZE + CELL_SIZE // 2,
                        'y': y * CELL_SIZE + CELL_SIZE // 2,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-3, 3),
                        'size': random.randint(2, 6),
                        'color': random.choice(SHAPE_COLORS),
                        'life': random.uniform(0.5, 1.0)  # 粒子生命周期（相对于特效持续时间）
                    }
                    self.particles.append(particle)
    
    def update_particles(self, effect_progress):
        # 更新粒子位置和大小
        for particle in self.particles[:]:
            # 如果粒子超过了生命周期，移除它
            if effect_progress > particle['life']:
                self.particles.remove(particle)
                continue
            
            # 更新位置
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # 粒子逐渐变小
            particle['size'] = max(1, particle['size'] * (1 - effect_progress / particle['life']))
    
    def draw_particles(self):
        # 绘制所有粒子
        for particle in self.particles:
            pygame.draw.circle(
                screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                int(particle['size'])
            )
    
    def move_left(self):
        if not self.game_over and not self.paused:
            if self.is_valid_position(self.current_piece, x=self.current_piece["x"] - 1):
                self.current_piece["x"] -= 1
    
    def move_right(self):
        if not self.game_over and not self.paused:
            if self.is_valid_position(self.current_piece, x=self.current_piece["x"] + 1):
                self.current_piece["x"] += 1
    
    def move_down(self):
        if not self.game_over and not self.paused and not self.is_clearing:
            if self.is_valid_position(self.current_piece, y=self.current_piece["y"] + 1):
                self.current_piece["y"] += 1
                return True
            else:
                # 如果不能再下落，合并方块并生成新方块
                self.merge_piece()
                lines_cleared = self.clear_lines()
                if not self.game_over and not lines_cleared:
                    self.current_piece = self.new_piece()
                return False
    
    def rotate(self):
        if not self.game_over and not self.paused:
            rotated_piece = self.rotate_piece(self.current_piece)
            if self.is_valid_position(rotated_piece):
                self.current_piece = rotated_piece
            else:
                # 尝试左右移动以适应旋转后的形状
                for x_offset in [-1, 1, -2, 2]:
                    rotated_piece["x"] = self.current_piece["x"] + x_offset
                    if self.is_valid_position(rotated_piece):
                        self.current_piece = rotated_piece
                        return
    
    def drop(self):
        if not self.game_over and not self.paused:
            while self.move_down():
                pass
    
    def toggle_pause(self):
        self.paused = not self.paused
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        # 如果正在显示消除特效
        if self.is_clearing:
            current_time = time.time()
            if current_time - self.clear_effect_start > self.clear_effect_duration:
                self.apply_line_clear()
                if not self.game_over:
                    self.current_piece = self.new_piece()
            return
            
        # 控制方块下落
        current_time = time.time()
        if current_time - self.last_fall_time > self.fall_speed:
            self.move_down()
            self.last_fall_time = current_time
    
    def draw(self):
        # 绘制游戏背景
        screen.fill(BLACK)
        
        # 绘制游戏区域边框
        pygame.draw.rect(screen, WHITE, (0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT), 2)
        
        # 绘制网格中的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    color_idx = self.grid[y][x] - 1
                    pygame.draw.rect(screen, SHAPE_COLORS[color_idx], 
                                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        
        # 绘制当前方块
        if not self.game_over and not self.is_clearing:
            shape = self.current_piece["shape"]
            color = self.current_piece["color"]
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = (self.current_piece["x"] + col_idx) * CELL_SIZE
                        y = (self.current_piece["y"] + row_idx) * CELL_SIZE
                        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE), 1)
        
        # 如果正在显示消除特效，绘制特效
        if self.is_clearing:
            self.draw_clear_effect()
        
        # 绘制信息面板
        info_x = CELL_SIZE * (GRID_WIDTH + 1)
        
        # 绘制分数 - 简化显示，使用英文避免中文乱码
        score_text = game_font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (info_x, 30))
        
        # 绘制等级
        level_text = game_font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (info_x, 70))
        
        # 如果游戏结束，显示结束信息
        if self.game_over:
            game_over_text = game_font.render("Game Over!", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)
            
            restart_text = game_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)
        
        # 如果游戏暂停，显示暂停信息
        if self.paused:
            pause_text = game_font.render("Paused", True, YELLOW)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text, text_rect)
            
            resume_text = game_font.render("Press P to continue", True, WHITE)
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(resume_text, resume_rect)
        
        pygame.display.update()

    def create_clear_sound(self):
        # 创建一个简单的清除音效（如果无法加载外部音效）
        # 使用pygame内置的合成声音功能
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        self.clear_sound = pygame.mixer.Sound(buffer=self.synthesize_clear_sound())
    
    def synthesize_clear_sound(self):
        # 合成一个简单的清除音效
        # 生成一个频率逐渐上升的正弦波
        import array
        import math
        
        sample_rate = 44100
        duration = 0.3  # 音效持续时间（秒）
        samples = int(sample_rate * duration)
        buffer = array.array('h', [0] * samples)  # 'h'表示有符号16位整数
        
        # 生成一个音调上升的"升琴"音效
        for i in range(samples):
            t = float(i) / sample_rate  # 时间点 (秒)
            frequency = 220 + 880 * t  # 从220Hz上升到1100Hz
            value = int(32767 * 0.7 * math.sin(2 * math.pi * frequency * t))  # 最大振幅的70%
            # 添加渐变效果
            if i < samples // 10:
                value = value * i // (samples // 10)  # 淡入
            elif i > samples * 9 // 10:
                value = value * (samples - i) // (samples // 10)  # 淡出
            buffer[i] = value
            
        return buffer

def main():
    game = Tetris()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 键盘事件处理
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                elif event.key == pygame.K_RIGHT:
                    game.move_right()
                elif event.key == pygame.K_DOWN:
                    game.move_down()
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    game.drop()
                elif event.key == pygame.K_p:
                    game.toggle_pause()
                elif event.key == pygame.K_r:
                    if game.game_over:
                        game = Tetris()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # 更新游戏状态
        game.update()
        
        # 绘制游戏画面
        game.draw()
        
        # 控制游戏帧率
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()