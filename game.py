import random, pygame, sys, time
from enum import Enum
from collections import namedtuple
import numpy as np

check_errors = pygame.init() 
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

font = pygame.font.SysFont('ContrailOne-Regular.ttf', 50) # add font

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')


# DIFFICULTY
# Easy      -> 10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 25

# WINDOW SIZE
HEIGHT = 600
WIDTH = 600

# RGB COLORS
CYAN = (25,140,140)
DARKCYAN = (0,102,102)
WHITE = (255, 255, 255)
RED = (200,0,0)
GREY = (35,35,35)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BERRY = (187,0,73)
BERRY2 = (135,15,62)
BLACK = (0,0,0)

# SETTINGS
BLOCK_SIZE = 20
SPEED = 20



class SnakeGameAI:

    def __init__(self, width=WIDTH, height=HEIGHT):
        #window display
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self._init_game()


    def _init_game(self):
        # Initialize game state
        self.direction = Direction.RIGHT
        self.head = Point(self.width / 2, self.height / 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        self.score = 0
        self.food = None
        self.frame_iteration = 0
        self._place_food()


    def _place_food(self):
        x = random.randint(0, (self.width-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.height-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action, userControl):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        if userControl == 1:
            self._move(action) # update the head
            self.snake.insert(0, self.head)
        elif userControl == 2:
            self._move_user_controlled()
            self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.width - BLOCK_SIZE or pt.x < 0 or pt.y > self.height - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(GREY)

        for pt in self.snake:
            pygame.draw.rect(self.display, BERRY2, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BERRY, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, DARKCYAN, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, CYAN, pygame.Rect(self.food.x+4, self.food.y+4, 12, 12))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move_user_controlled(self):

        direction_map = {
        pygame.K_RIGHT: Direction.RIGHT,
        pygame.K_LEFT: Direction.LEFT,
        pygame.K_UP: Direction.UP,
        pygame.K_DOWN: Direction.DOWN
        }

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        for key, direction in direction_map.items():
            if keys[key]:
                self.direction = direction

        if self.direction == Direction.RIGHT:
            self.head = Point(self.head.x + BLOCK_SIZE, self.head.y)
        elif self.direction == Direction.LEFT:
            self.head = Point(self.head.x - BLOCK_SIZE, self.head.y)
        elif self.direction == Direction.DOWN:
            self.head = Point(self.head.x, self.head.y + BLOCK_SIZE)
        elif self.direction == Direction.UP:
            self.head = Point(self.head.x, self.head.y - BLOCK_SIZE)

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]): # str, right, left
            new_dir = clock_wise[idx] # No change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        if self.direction == Direction.RIGHT:
            self.head = Point(self.head.x + BLOCK_SIZE, self.head.y)
        elif self.direction == Direction.LEFT:
            self.head = Point(self.head.x - BLOCK_SIZE, self.head.y)
        elif self.direction == Direction.DOWN:
            self.head = Point(self.head.x, self.head.y + BLOCK_SIZE)
        elif self.direction == Direction.UP:
            self.head = Point(self.head.x, self.head.y - BLOCK_SIZE)

