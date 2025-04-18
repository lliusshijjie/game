import pygame
import random
import sys
import math

# 初始化Pygame
pygame.init()

# 游戏常量
BLOCK_SIZE = 50
GRID_SIZE = 8
SCREEN_SIZE = BLOCK_SIZE * GRID_SIZE
COLORS = [
    (255, 0, 0),     # 红色
    (0, 255, 0),     # 绿色
    (0, 0, 255),     # 蓝色
    (255, 255, 0),   # 黄色
    (255, 0, 255),   # 紫色
    (0, 255, 255),   # 青色
]

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 50))
pygame.display.set_caption('消消乐')

# 初始化字体
pygame.font.init()
try:
    font_paths = [
        'simhei.ttf',
        'C:/Windows/Fonts/simhei.ttf',
        '/System/Library/Fonts/PingFang.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
    ]
    font = None
    for path in font_paths:
        try:
            font = pygame.font.Font(path, 24)
            break
        except:
            continue
    if font is None:
        raise Exception("No font found")
except:
    print("警告：无法加载中文字体，使用系统默认字体")
    font = pygame.font.SysFont(None, 24)

class Block:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.target_y = row * BLOCK_SIZE + 50
        self.current_y = 50  # 从顶部开始
        self.alpha = 255
        self.removing = False
        self.swapping = False
        self.swap_target = None
        self.original_pos = None
        self.swap_progress = 0
        self.successful_swap = False
        self.flash_timer = 0

    def update(self):
        if self.removing:
            # 闪烁效果
            self.flash_timer += 1
            if self.flash_timer < 10:
                self.alpha = 255 if self.flash_timer % 2 == 0 else 128
            else:
                self.alpha = max(0, self.alpha - 25)
            return self.alpha <= 0
        elif self.swapping:
            self.swap_progress += 0.08
            if self.swap_progress >= 1:
                self.swapping = False
                self.current_y = self.target_y
                return False
                
            # 交换动画
            progress = -(self.swap_progress * (self.swap_progress - 2))
            
            # 添加效果
            bounce = 0
            if self.successful_swap:
                bounce = math.sin(self.swap_progress * math.pi * 2) * 5 * (1 - self.swap_progress)
            else:
                bounce = math.sin(self.swap_progress * math.pi * 10) * 3 * (1 - self.swap_progress)
                
            if self.original_pos and self.swap_target:
                orig_x, orig_y = self.original_pos
                target_x, target_y = self.swap_target
                self.current_y = orig_y + (target_y - orig_y) * progress + bounce
            return False
        else:
            # 掉落动画
            if self.current_y < self.target_y:
                self.current_y += (self.target_y - self.current_y) * 0.2
                if abs(self.current_y - self.target_y) < 1:
                    self.current_y = self.target_y
            return False

    def draw(self, screen):
        if self.color:
            s = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            s.fill(self.color)
            s.set_alpha(self.alpha)
            x = self.col * BLOCK_SIZE + 1
            y = self.current_y + 1
            
            # 交换时的高亮效果
            if self.swapping:
                border_color = (0, 255, 0) if self.successful_swap else (255, 0, 0)
                pygame.draw.rect(screen, border_color, 
                               (x-2, y-2, BLOCK_SIZE+2, BLOCK_SIZE+2), 3)
            
            screen.blit(s, (x, y))

class Game:
    def __init__(self):
        self.grid = []
        self.score = 0
        self.blocks = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.processing_animation = False
        self.initialize_grid()
        
    def initialize_grid(self):
        # 初始化网格
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # 生成随机颜色
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color = random.choice(COLORS)
                self.grid[row][col] = color
                self.blocks[row][col] = Block(color, row, col)
        
        # 检查初始匹配并消除
        self.check_and_remove_all_matches()
    
    def create_block(self, row, col, color):
        block = Block(color, row, col)
        return block

    def get_matches(self):
        matches = set()
        
        # 检查行
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE:
                if self.grid[row][col] is None:
                    col += 1
                    continue
                
                current_color = self.grid[row][col]
                match_start = col
                
                # 查找连续相同颜色
                while (col < GRID_SIZE and 
                      self.grid[row][col] is not None and 
                      self.grid[row][col] == current_color):
                    col += 1
                
                # 计算匹配长度
                match_length = col - match_start
                
                # 如果找到3个或以上匹配
                if match_length >= 3:
                    for c in range(match_start, col):
                        matches.add((row, c))
                
                if match_length == 0:
                    col += 1
            
        # 检查列
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE:
                if self.grid[row][col] is None:
                    row += 1
                    continue
                
                current_color = self.grid[row][col]
                match_start = row
                
                # 查找连续相同颜色
                while (row < GRID_SIZE and 
                      self.grid[row][col] is not None and 
                      self.grid[row][col] == current_color):
                    row += 1
                
                # 计算匹配长度
                match_length = row - match_start
                
                # 如果找到3个或以上匹配
                if match_length >= 3:
                    for r in range(match_start, row):
                        matches.add((r, col))
                
                if match_length == 0:
                    row += 1
        
        return matches

    def check_and_remove_matches(self):
        self.processing_animation = True
        matches = self.get_matches()
        
        if matches:
            # 标记要消除的方块
            for row, col in matches:
                if self.blocks[row][col]:
                    self.blocks[row][col].removing = True
                    self.blocks[row][col].flash_timer = 0
                self.grid[row][col] = None
            
            self.score += len(matches)
            return True
        
        self.processing_animation = False
        return False

    def check_and_remove_all_matches(self):
        """持续消除所有匹配直到没有更多匹配"""
        while self.check_and_remove_matches():
            self.wait_for_animations()
            self.fill_empty_spaces()
            self.wait_for_animations()
    
    def wait_for_animations(self, frames=20):
        """等待动画完成"""
        for _ in range(frames):
            all_done = True
            
            # 更新所有方块
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.blocks[row][col]:
                        # 如果方块还在移动或消除
                        if (self.blocks[row][col].removing or 
                            self.blocks[row][col].swapping or 
                            abs(self.blocks[row][col].current_y - self.blocks[row][col].target_y) > 1):
                            all_done = False
                        
                        # 更新方块状态
                        if self.blocks[row][col].update():
                            self.blocks[row][col] = None
            
            # 如果所有动画都完成了，可以提前退出
            if all_done:
                break
            
            # 重绘屏幕
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(16)  # 约60fps

    def fill_empty_spaces(self):
        """填充空位并让方块下落"""
        # 首先检查并填充任何空位
        self.ensure_no_empty_spaces()
        
        # 处理每一列
        for col in range(GRID_SIZE):
            # 计算从底部到顶部的空位
            empty_rows = []
            for row in range(GRID_SIZE-1, -1, -1):
                if self.grid[row][col] is None:
                    empty_rows.append(row)
            
            # 如果没有空位，继续下一列
            if not empty_rows:
                continue
            
            # 从底部向上移动非空方块
            for row in range(min(empty_rows)-1, -1, -1):
                if self.grid[row][col] is not None:
                    # 获取最底部的空位
                    target_row = empty_rows.pop(0)
                    
                    # 移动网格数据
                    self.grid[target_row][col] = self.grid[row][col]
                    self.grid[row][col] = None
                    
                    # 移动方块对象
                    if self.blocks[row][col]:
                        block = self.blocks[row][col]
                        block.row = target_row
                        block.target_y = target_row * BLOCK_SIZE + 50
                        self.blocks[target_row][col] = block
                        self.blocks[row][col] = None
                    
                    # 更新空位列表
                    empty_rows.append(row)
                    empty_rows.sort(reverse=True)
            
            # 在顶部空位生成新方块
            for row in empty_rows:
                color = random.choice(COLORS)
                self.grid[row][col] = color
                
                # 创建新方块
                new_block = Block(color, row, col)
                self.blocks[row][col] = new_block
        
        # 再次检查确保没有空位
        self.ensure_no_empty_spaces()
        
        # 等待下落动画
        self.wait_for_animations()
        
        # 检查新生成的方块是否形成匹配
        matches = self.get_matches()
        if matches:
            self.check_and_remove_matches()
            self.wait_for_animations()
            self.fill_empty_spaces()

    def ensure_no_empty_spaces(self):
        """确保网格中没有空位"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # 如果网格位置为空但方块对象存在
                if self.grid[row][col] is None and self.blocks[row][col] is not None:
                    self.blocks[row][col] = None
                
                # 如果网格位置有颜色但方块对象不存在
                elif self.grid[row][col] is not None and self.blocks[row][col] is None:
                    color = self.grid[row][col]
                    self.blocks[row][col] = Block(color, row, col)
                    self.blocks[row][col].current_y = self.blocks[row][col].target_y
                
                # 如果都为空，创建新方块
                elif self.grid[row][col] is None:
                    color = random.choice(COLORS)
                    self.grid[row][col] = color
                    self.blocks[row][col] = Block(color, row, col)
    
    def swap_blocks(self, pos1, pos2):
        """交换两个方块并检查是否形成匹配"""
        if self.processing_animation:
            return False
            
        row1, col1 = pos1
        row2, col2 = pos2
        
        # 检查位置有效性
        if not (0 <= row1 < GRID_SIZE and 0 <= col1 < GRID_SIZE and 
                0 <= row2 < GRID_SIZE and 0 <= col2 < GRID_SIZE):
            return False
        
        # 获取方块
        block1 = self.blocks[row1][col1]
        block2 = self.blocks[row2][col2]
        
        if not block1 or not block2:
            return False
        
        # 临时交换以检查是否形成匹配
        self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
        
        # 检查是否形成匹配
        matches = self.get_matches()
        has_match = len(matches) > 0
        
        # 设置交换动画
        block1.swapping = True
        block2.swapping = True
        block1.swap_progress = 0
        block2.swap_progress = 0
        block1.successful_swap = has_match
        block2.successful_swap = has_match
        block1.original_pos = (col1, block1.current_y)
        block2.original_pos = (col2, block2.current_y)
        block1.swap_target = (col2, block2.current_y)
        block2.swap_target = (col1, block1.current_y)
        
        # 如果没有匹配，还原交换
        if not has_match:
            self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
            
            # 等待动画
            self.wait_for_animations()
            
            return False
        
        # 完成交换
        self.blocks[row1][col1], self.blocks[row2][col2] = self.blocks[row2][col2], self.blocks[row1][col1]
        block1.row, block1.col = row2, col2
        block2.row, block2.col = row1, col1
        
        # 特别处理垂直交换
        if row1 != row2:
            block1.target_y = row2 * BLOCK_SIZE + 50
            block2.target_y = row1 * BLOCK_SIZE + 50
        
        # 等待交换动画
        self.wait_for_animations()
        
        # 执行消除
        self.check_and_remove_all_matches()
        
        return True

    def shuffle_grid(self):
        """打乱方块"""
        if self.score < 15:
            return False
        
        # 收集所有颜色
        colors = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] is not None:
                    colors.append(self.grid[row][col])
        
        # 打乱颜色
        random.shuffle(colors)
        
        # 重新分配颜色
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.blocks[row][col]:
                    color = colors.pop(0)
                    self.grid[row][col] = color
                    self.blocks[row][col].color = color
        
        self.score -= 15
        
        # 检查是否形成新的匹配
        self.check_and_remove_all_matches()
        
        return True

    def update(self):
        """更新游戏状态"""
        # 检查并确保没有空位
        self.ensure_no_empty_spaces()
        
        # 如果没有正在处理的动画，检查是否有新的匹配
        if not self.processing_animation:
            matches = self.get_matches()
            if matches:
                self.check_and_remove_all_matches()

    def draw(self, screen):
        """绘制游戏"""
        # 绘制网格线
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                pygame.draw.rect(screen, (30, 30, 30), 
                               (col * BLOCK_SIZE, row * BLOCK_SIZE + 50, 
                                BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 绘制方块
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.blocks[row][col]:
                    self.blocks[row][col].draw(screen)
        
        # 绘制分数
        score_text = f'得分：{self.score}'
        # 先绘制阴影
        shadow_surface = font.render(score_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (12, 12))
        # 再绘制文本
        text_surface = font.render(score_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # 绘制打乱按钮
        pygame.draw.rect(screen, (100, 100, 100), (200, 10, 100, 30))
        pygame.draw.rect(screen, (128, 128, 128), (198, 8, 100, 30))
        shuffle_text = font.render('打乱', True, (255, 255, 255))
        screen.blit(shuffle_text, (220, 12))

def main():
    game = Game()
    clock = pygame.time.Clock()
    selected_pos = None

    while True:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and not game.processing_animation:
                x, y = event.pos
                if 198 <= x <= 298 and 8 <= y <= 38:
                    game.shuffle_grid()
                elif y >= 50:
                    col = x // BLOCK_SIZE
                    row = (y - 50) // BLOCK_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if selected_pos is None:
                            selected_pos = (row, col)
                        else:
                            if (abs(selected_pos[0] - row) + abs(selected_pos[1] - col) == 1):
                                game.swap_blocks(selected_pos, (row, col))
                            selected_pos = None

        # 更新游戏
        game.update()
        
        # 绘制游戏
        game.draw(screen)
        
        # 绘制选中方块的边框
        if selected_pos and not game.processing_animation:
            row, col = selected_pos
            pygame.draw.rect(screen, (255, 255, 255),
                           (col * BLOCK_SIZE, row * BLOCK_SIZE + 50,
                            BLOCK_SIZE, BLOCK_SIZE), 3)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
