import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# 定义食物类型及其分数
FOOD_TYPES = [
    {'color': RED, 'score': 1},
    {'color': WHITE, 'score': 2},
    {'color': YELLOW, 'score': 3},
    {'color': BLUE, 'score': 4},
    {'color': GREEN, 'score': 5}
]

# 设置游戏窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 20
GAME_SPEED = 5  # 进一步降低初始速度

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇游戏')
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        self.body = [
            (center_x, center_y),
            (center_x - BLOCK_SIZE, center_y),
            (center_x - 2 * BLOCK_SIZE, center_y)
        ]
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.speed = GAME_SPEED
        self.score = 0
        self.reset_count = 0  # 添加重置次数计数器

    def reset_length(self):
        # 重置蛇的长度为3，保持当前头部位置
        head = self.body[0]
        if self.direction == 'RIGHT':
            self.body = [
                head,
                (head[0] - BLOCK_SIZE, head[1]),
                (head[0] - 2 * BLOCK_SIZE, head[1])
            ]
        elif self.direction == 'LEFT':
            self.body = [
                head,
                (head[0] + BLOCK_SIZE, head[1]),
                (head[0] + 2 * BLOCK_SIZE, head[1])
            ]
        elif self.direction == 'UP':
            self.body = [
                head,
                (head[0], head[1] + BLOCK_SIZE),
                (head[0], head[1] + 2 * BLOCK_SIZE)
            ]
        elif self.direction == 'DOWN':
            self.body = [
                head,
                (head[0], head[1] - BLOCK_SIZE),
                (head[0], head[1] - 2 * BLOCK_SIZE)
            ]
        self.reset_count += 1  # 增加重置次数
        
        # 当重置次数超过6次时，重置速度和计数器
        if self.reset_count > 6:
            self.speed = GAME_SPEED
            self.reset_count = 0

    def change_direction(self):
        if self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'
        elif self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'

    def move(self, food_pos):
        if self.direction == 'RIGHT':
            new_head = (self.body[0][0] + BLOCK_SIZE, self.body[0][1])
        elif self.direction == 'LEFT':
            new_head = (self.body[0][0] - BLOCK_SIZE, self.body[0][1])
        elif self.direction == 'UP':
            new_head = (self.body[0][0], self.body[0][1] - BLOCK_SIZE)
        elif self.direction == 'DOWN':
            new_head = (self.body[0][0], self.body[0][1] + BLOCK_SIZE)

        # 检查是否吃到食物
        if new_head == food_pos:
            self.body.insert(0, new_head)
            return True
        else:
            self.body.insert(0, new_head)
            self.body.pop()
            return False

    def check_collision(self):
        # 检查是否撞墙
        if (self.body[0][0] >= WINDOW_WIDTH or self.body[0][0] < 0 or
            self.body[0][1] >= WINDOW_HEIGHT or self.body[0][1] < 0):
            return True
        # 检查是否撞到自己
        for block in self.body[1:]:
            if self.body[0] == block:
                return True
        return False

def generate_food(snake_body):
    while True:
        food_x = random.randrange(0, WINDOW_WIDTH, BLOCK_SIZE)
        food_y = random.randrange(0, WINDOW_HEIGHT, BLOCK_SIZE)
        food_pos = (food_x, food_y)
        if food_pos not in snake_body:
            # 随机选择一个食物类型
            food_type = random.choice(FOOD_TYPES)
            return food_pos, food_type

def main():
    snake = Snake()
    food_pos, food_type = generate_food(snake.body)

    # 修改字体设置，使用系统默认中文字体
    try:
        # Windows系统
        font = pygame.font.SysFont('SimHei', 36)
    except:
        try:
            # macOS系统
            font = pygame.font.SysFont('STHeiti', 36)
        except:
            try:
                # Linux系统
                font = pygame.font.SysFont('WenQuanYi Micro Hei', 36)
            except:
                # 如果以上都失败，使用系统默认字体
                font = pygame.font.Font(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    snake.change_to = 'RIGHT'
                elif event.key == pygame.K_LEFT:
                    snake.change_to = 'LEFT'
                elif event.key == pygame.K_UP:
                    snake.change_to = 'UP'
                elif event.key == pygame.K_DOWN:
                    snake.change_to = 'DOWN'

        snake.change_direction()
        
        # 移动蛇并检查是否吃到食物
        food_eaten = snake.move(food_pos)
        if food_eaten:
            # 根据食物类型增加对应分数
            snake.score += food_type['score']
            food_pos, food_type = generate_food(snake.body)
            snake.speed = min(snake.speed + 0.2, 25)
            
            # 当蛇长度大于15时，重置长度并奖励分数
            if len(snake.body) > 15:
                snake.reset_length()
                snake.score += 8

        # 检查碰撞
        if snake.check_collision():
            pygame.quit()
            sys.exit()

        # 绘制游戏画面
        screen.fill(BLACK)
        
        # 绘制食物（使用对应的颜色）
        pygame.draw.rect(screen, food_type['color'], 
                        (food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
        
        # 绘制蛇（保持绿色）
        for pos in snake.body:
            pygame.draw.rect(screen, GREEN, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # 显示分数、长度和重置信息
        score_text = font.render(f'得分：{snake.score}', True, WHITE)
        length_text = font.render(f'长度：{len(snake.body)}', True, WHITE)
        reset_text = font.render(f'重置次数：{snake.reset_count}/6', True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(length_text, (10, 50))
        screen.blit(reset_text, (10, 90))

        pygame.display.update()
        clock.tick(snake.speed)

if __name__ == '__main__':
    main()
