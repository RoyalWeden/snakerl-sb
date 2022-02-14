import gym
from gym import spaces
from collections import deque
import numpy as np
import cv2

import pygame
import random
import time	

pygame.init()

pixel_shape = {
    'width': 500,
    'height': 500
}
dirs = [(-1,0), (0,-1), (0,1), (1,0)]
font = pygame.font.SysFont('Ariel', 20)
big_font = pygame.font.SysFont('Ariel', 60)
cardinal_dirs = [
    (1,0),
    (1,-1),
    (0,-1),
    (-1,-1),
    (-1,0),
    (-1,1),
    (0,1),
    (1,1)
]
SNAKE_LEN_GOAL = 50

def display_all(screen, snake_head, snake_body, apple, score, object_shape:tuple, snake_speed, change_speed_text, hunger):
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(snake_head, object_shape))
    for body in snake_body:
        pygame.draw.rect(screen, (0,200,0), pygame.Rect(body, object_shape))
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(apple, object_shape))

    # text for the speed of the snake's movement
    snake_speed = round(float(0.5/snake_speed), 2)
    snake_speed_str = f'Speed: {snake_speed}x'

    text = font.render(f'Score: {score}', True, (255,255,255))
    textRect = text.get_rect()
    textRect.bottomleft = (25,30)

    text2 = font.render(f'Hunger Level: {hunger}', True, (255,255,255))
    textRect2 = text2.get_rect()
    textRect2.bottomleft = (25,55)

    text3 = font.render(f'{snake_speed_str}', True, (255,255,255))
    textRect3 = text3.get_rect()
    textRect3.bottomleft = (25,80)

    if change_speed_text:
        text3 = big_font.render(f'{change_speed_text}', True, (255,255,255))
        textRect3 = text3.get_rect()
        textRect3.bottomleft = (25,470)
        screen.blit(text3, textRect3)

    screen.blit(text, textRect)
    screen.blit(text2, textRect2)
    screen.blit(text3, textRect3)
    pygame.display.flip()

def update_snake_pos(dir, snake_head, snake_body, score, object_shape):
    temp_snake_part = snake_head
    snake_head = (snake_head[0] + dirs[dir][0]*object_shape[0], snake_head[1] + dirs[dir][1]*object_shape[1])
    new_snake_body = []
    for i in range(len(snake_body)):
        new_snake_body.append(temp_snake_part)
        temp_snake_part = snake_body[i]
    if len(new_snake_body) - 2 < score:
        new_snake_body.append(temp_snake_part)
    return snake_head, new_snake_body

def check_wall_body(snake_head, snake_body, object_shape, game_shape):
    snake_head = (snake_head[0] // object_shape[0], snake_head[1] // object_shape[1])
    snake_body = [(body[0] // object_shape[0], body[1] // object_shape[1]) for body in snake_body]
    if snake_head[0] < 0 or snake_head[1] < 0 or snake_head[0] >= game_shape[0] or snake_head[1] >= game_shape[1]:
        return 1
    if snake_head in snake_body:
        return 1
    return 0

def check_apple(snake_head, snake_body, apple, score, object_shape):
    hit_apple = False
    if snake_head == apple:
        hit_apple = True
        score += 1
        while apple == snake_head or apple in snake_body:
            apple = (random.randint(0,(pixel_shape['width']-object_shape[0])//object_shape[0])*object_shape[0], random.randint(0,(pixel_shape['height']-object_shape[1])//object_shape[1])*object_shape[1])
    return apple, score, hit_apple
    
class SnakeEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    # observation = [head_x, head_y, apple_delta_x, apple_delta_y, snake_length] + list(self.prev_actions)
    # self.total_reward = len(self.snake_position) - 3  # start length is 3

    def __init__(self, snake_speed_time=0.0001, game_shape:tuple=(50,50), auto_update_shape:bool=False, auto_update_count_needed:int=1, testing=False):
        super(SnakeEnv, self).__init__()

        # how fast the snake moves
        self.snake_speed_time = snake_speed_time

        # how big the game is in dimensions
        self.game_shape = (max(game_shape[0], 5), max(game_shape[1], 5))

        # how many pixels each square takes up
        self.object_shape = (pixel_shape['width']//self.game_shape[0], pixel_shape['height']//self.game_shape[1])

        # will the game shape increase over time
        self.auto_update_shape = auto_update_shape

        # how many snake completions will be needed to increase the game shape
        self.auto_update_count_needed = auto_update_count_needed

        self.testing = testing

        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(4)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=-500, high=500, shape=(14 + SNAKE_LEN_GOAL,), dtype=np.float32)

    def step(self, action):
        # check key presses
        if self.testing:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.key_press = '<'
                    elif event.key == pygame.K_RIGHT:
                        self.key_press = '>'

        self.prev_actions.append(action)
        cv2.waitKey(1)

        t_end = time.time() + self.snake_speed_time
        k = -1
        while time.time() < t_end:
            if k == -1:
                k = cv2.waitKey(1)
            else:
                continue

        dir = action
        self.snake_head, self.snake_body = update_snake_pos(dir, self.snake_head, self.snake_body, self.score, self.object_shape)
        self.apple, self.score, hit_apple = check_apple(self.snake_head, self.snake_body, self.apple, self.score, self.object_shape)
        if check_wall_body(self.snake_head, self.snake_body, self.object_shape, self.game_shape):
            self.done = True

        # display screen, snake, and apple
        display_all(self.screen, self.snake_head, self.snake_body, self.apple, self.score, self.object_shape, self.snake_speed_time, self.change_speed_text, self.hunger)
        self.change_speed_text = None

        self.reward = 0
        apple_reward = 0
        if hit_apple:
            # increase hunger when apple has been eaten
            self.hunger = self.game_shape[0] * self.game_shape[1]
            apple_reward = 10
            # adjust to 5
        else:
            # decrease hunger over time and when reaches zero, snake dies
            self.hunger -= 1

        if self.hunger == 0:
            self.done = True

        # increase game size when taking up most of map
        if len(self.snake_body) >= 0.6*(self.game_shape[0]*self.game_shape[1]) and self.auto_update_shape:
            self.auto_update_count += 1

        # update game shape when update count reaches the requirement
        if self.auto_update_count == self.auto_update_count_needed * 1000:
            self.auto_update_count = 0
            self.game_shape = (self.game_shape[0]+1, self.game_shape[1]+1)
            self.object_shape = (pixel_shape['width']//self.game_shape[0], pixel_shape['height']//self.game_shape[1])

        # calcluate distance to apple and add reward
        dist_to_apple:float = abs(self.snake_head[0] - self.apple[0]) + abs(self.snake_head[1] - self.apple[1])
        
        # determine rewards
        if not hit_apple:
            if dist_to_apple < self.prev_dist_to_apple:
                self.reward = 1
                # adjust to 0.5
            elif dist_to_apple > self.prev_dist_to_apple:
                self.reward = -1
                # adjust to -0.5
            else:
                self.reward = 0
        else:
            self.reward = apple_reward

        self.prev_dist_to_apple = dist_to_apple        
        self.prev_reward = self.reward

        # give negative reward when losing
        if self.done:
            self.reward = -100
        info = {}

        total_hunger = self.hunger

        head_x = self.snake_head[0] // self.object_shape[0]
        head_y = self.snake_head[1] // self.object_shape[1]

        snake_length = len(self.snake_body)
        # distance to apple
        apple_delta_x = self.apple[0] // self.object_shape[0] - head_x
        apple_delta_y = self.apple[1] // self.object_shape[1] - head_y

        # distances to closest snake body part
        body_delta_left = -1
        body_delta_up = -1
        body_delta_down = -1
        body_delta_right = -1
        for i in range(1, int(np.linalg.norm(np.array(self.game_shape)))):
            body_x = [elem[0] for elem in self.snake_body]
            body_y = [elem[1] for elem in self.snake_body]
            if i in body_x and body_delta_right < 0:
                body_delta_right = i
            if -i in body_x and body_delta_left < 0:
                body_delta_left = i
            if i in body_y and body_delta_up < 0:
                body_delta_up = i
            if -i in body_y and body_delta_down < 0:
                body_delta_down = i

        # distance to wall
        wall_delta_left = head_x
        wall_delta_up = head_y
        wall_delta_down = self.game_shape[1] - head_y
        wall_delta_right = self.game_shape[0] - head_x

        observation = [head_x, head_y, apple_delta_x, apple_delta_y, body_delta_left, body_delta_up, body_delta_down,
                    body_delta_right, snake_length, wall_delta_left, wall_delta_up, wall_delta_down, wall_delta_right,
                    total_hunger] + list(self.prev_actions)
        observation = np.array(observation)
        return observation, self.reward, self.done, info
    def reset(self):
        self.screen = pygame.display.set_mode(tuple(pixel_shape.values()))
        self.snake_head = (pixel_shape['width'] // 2 // self.object_shape[0] * self.object_shape[0], pixel_shape['height'] // 2 // self.object_shape[1] * self.object_shape[1])
        self.snake_body = [(self.snake_head[0] - self.object_shape[0], self.snake_head[1]), (self.snake_head[0] - self.object_shape[0] * 2, self.snake_head[1])]
        self.apple = (random.randint(0,(pixel_shape['width']-self.object_shape[0])//self.object_shape[0])*self.object_shape[0],
                    random.randint(0,(pixel_shape['height']-self.object_shape[1])//self.object_shape[1])*self.object_shape[1])
        self.score = 0
        self.dir = 3
        self.done = False
        self.prev_reward = 0
        self.prev_dist_to_apple = np.linalg.norm(np.array(self.game_shape))
        try:
            self.auto_update_count
        except:
            self.auto_update_count = 0
        self.hunger = self.game_shape[0] * self.game_shape[1]
        self.key_press = None
        self.change_speed_text = None

        total_hunger = self.hunger

        # display screen, snake, and apple
        display_all(self.screen, self.snake_head, self.snake_body, self.apple, self.score, self.object_shape, self.snake_speed_time, self.change_speed_text, total_hunger)
        self.change_speed_text = None

        head_x = self.snake_head[0] // self.object_shape[0]
        head_y = self.snake_head[1] // self.object_shape[1]

        snake_length = len(self.snake_body)
        apple_delta_x = self.apple[0] // self.object_shape[0] - head_x
        apple_delta_y = self.apple[1] // self.object_shape[1] - head_y

        body_delta_left = -1
        body_delta_up = -1
        body_delta_down = -1
        body_delta_right = -1
        for i in range(1, int(np.linalg.norm(np.array(self.game_shape)))):
            body_x = [elem[0] for elem in self.snake_body]
            body_y = [elem[1] for elem in self.snake_body]
            if i in body_x and body_delta_right < 0:
                body_delta_right = i
            if -i in body_x and body_delta_left < 0:
                body_delta_left = i
            if i in body_y and body_delta_up < 0:
                body_delta_up = i
            if -i in body_y and body_delta_down < 0:
                body_delta_down = i

        wall_delta_left = head_x
        wall_delta_up = head_y
        wall_delta_down = self.game_shape[1] - head_y
        wall_delta_right = self.game_shape[0] - head_x

        self.prev_actions = deque(maxlen=SNAKE_LEN_GOAL)
        for _ in range(SNAKE_LEN_GOAL):
            self.prev_actions.append(-1)

        observation = [head_x, head_y, apple_delta_x, apple_delta_y, body_delta_left, body_delta_up, body_delta_down,
                    body_delta_right, snake_length, wall_delta_left, wall_delta_up, wall_delta_down, wall_delta_right,
                    total_hunger] + list(self.prev_actions)
        observation = np.array(observation)
        return observation  # reward, done, info can't be included
    def render(self, mode='human'):
        pass
    def close (self):
        pass