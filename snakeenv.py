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
object_shape = (10, 10)
dirs = {
    0: (-1*object_shape[0],0),
    1: (0,-1*object_shape[1]),
    2: (0,1*object_shape[1]),
    3: (1*object_shape[0],0)
}
font = pygame.font.SysFont('Ariel', 20)

SNAKE_LEN_GOAL = 50

def display_all(screen, snake_head, snake_body, apple, score):
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(snake_head, object_shape))
    for body in snake_body:
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(body, object_shape))
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(apple, object_shape))
    text = font.render(f'Score: {score}', True, (255,255,255))
    textRect = text.get_rect()
    textRect.center = (50,35)
    screen.blit(text, textRect)
    pygame.display.flip()

def update_snake_pos(dir, snake_head, snake_body, score):
    temp_snake_part = snake_head
    snake_head = (snake_head[0] + dirs[dir][0], snake_head[1] + dirs[dir][1])
    new_snake_body = []
    for i in range(len(snake_body)):
        new_snake_body.append(temp_snake_part)
        temp_snake_part = snake_body[i]
    if len(new_snake_body) - 2 < score:
        new_snake_body.append(temp_snake_part)
    return snake_head, new_snake_body

def check_wall_body(snake_head, snake_body):
    if snake_head[0] < 0 or snake_head[1] < 0 or snake_head[0] >= pixel_shape['width'] or snake_head[1] >= pixel_shape['height']:
        return 1
    if snake_head in snake_body:
        return 1
    return 0

def check_apple(snake_head, snake_body, apple, score):
    if snake_head == apple:
        score += 1
        while apple == snake_head or apple in snake_body:
            apple = (random.randint(0,(pixel_shape['width']-1)//object_shape[0])*10, random.randint(0,(pixel_shape['height']-1)//object_shape[1])*10)
    return apple, score
    
class SnakeEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    # observation = [head_x, head_y, apple_delta_x, apple_delta_y, snake_length] + list(self.prev_actions)
    # self.total_reward = len(self.snake_position) - 3  # start length is 3

    def __init__(self):
        super(SnakeEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(4)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=-500, high=500, shape=(5 + SNAKE_LEN_GOAL,), dtype=np.float32)

    def step(self, action):
        self.prev_actions.append(action)
        cv2.waitKey(1)
        # display screen, snake, and apple
        display_all(self.screen, self.snake_head, self.snake_body, self.apple, self.score)

        t_end = time.time() + 0.00025
        k = -1
        while time.time() < t_end:
            if k == -1:
                k = cv2.waitKey(1)
            else:
                continue

        dir = action
        self.apple, self.score = check_apple(self.snake_head, self.snake_body, self.apple, self.score)
        self.snake_head, self.snake_body = update_snake_pos(dir, self.snake_head, self.snake_body, self.score)
        if check_wall_body(self.snake_head, self.snake_body):
            self.done = True

        self.total_reward = len(self.snake_body) - 2
        self.reward = self.total_reward - self.prev_reward
        self.prev_reward = self.total_reward

        if self.done:
            self.reward = -10
        info = {}

        head_x = self.snake_head[0]
        head_y = self.snake_head[1]

        snake_length = len(self.snake_body)
        apple_delta_x = self.apple[0] - head_x
        apple_delta_y = self.apple[1] - head_y

        observation = [head_x, head_y, apple_delta_x, apple_delta_y, snake_length] + list(self.prev_actions)
        observation = np.array(observation)
        return observation, self.reward, self.done, info
    def reset(self):
        self.screen = pygame.display.set_mode(tuple(pixel_shape.values()))
        self.snake_head = (pixel_shape['width'] // 2, pixel_shape['height'] // 2)
        self.snake_body = [(self.snake_head[0] - object_shape[0], self.snake_head[1]), (self.snake_head[0] - object_shape[0] * 2, self.snake_head[1])]
        self.apple = (random.randint(0,pixel_shape['width']//object_shape[0])*10, random.randint(0,pixel_shape['height']//object_shape[1])*10)
        self.score = 0
        self.dir = 3
        self.done = False
        self.prev_reward = 0

        head_x = self.snake_head[0]
        head_y = self.snake_head[1]

        snake_length = len(self.snake_body)
        apple_delta_x = self.apple[0] - head_x
        apple_delta_y = self.apple[1] - head_y

        self.prev_actions = deque(maxlen=SNAKE_LEN_GOAL)
        for i in range(SNAKE_LEN_GOAL):
            self.prev_actions.append(-1)

        observation = [head_x, head_y, apple_delta_x, apple_delta_y, snake_length] + list(self.prev_actions)
        observation = np.array(observation)
        return observation  # reward, done, info can't be included
    def render(self, mode='human'):
        pass
    def close (self):
        pass