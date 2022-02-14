import pygame
import random
import time

pygame.init()

playing = True

pixel_shape = {
    'width': 500,
    'height': 500
}
screen = pygame.display.set_mode(tuple(pixel_shape.values()))
# object_shape = (10, 10)
object_shape = (500/5, 500/5)
score = 0
# Directions:
dirs = {
    0: (-1*object_shape[0],0),
    1: (0,-1*object_shape[1]),
    2: (0,1*object_shape[1]),
    3: (1*object_shape[0],0)
}
current_dir = 3
font = pygame.font.SysFont('Ariel', 20)

snake_head = (pixel_shape['width'] // 2 // object_shape[0] * object_shape[0], pixel_shape['height'] // 2 // object_shape[1] * object_shape[1])
snake_body = [(snake_head[0] - object_shape[0], snake_head[1]), (snake_head[0] - object_shape[0] * 2, snake_head[1])]
apple = (random.randint(0,(pixel_shape['width']-object_shape[0])//object_shape[0])*object_shape[0], random.randint(0,(pixel_shape['height']-object_shape[1])//object_shape[1])*object_shape[1])

def display_all(screen, snake_head, snake_body, apple, score):
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(snake_head, object_shape))
    for body in snake_body:
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(body, object_shape))
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(apple, object_shape))
    text = font.render(f'Score: {score}', True, (255,255,255))
    textRect = text.get_rect()
    textRect.center = (50,50)
    screen.blit(text, textRect)
    pygame.display.flip()

def update_snake_pos(current_dir, snake_head, snake_body, score):
    temp_snake_part = snake_head
    snake_head = (snake_head[0] + dirs[current_dir][0], snake_head[1] + dirs[current_dir][1])
    new_snake_body = []
    for i in range(len(snake_body)):
        new_snake_body.append(temp_snake_part)
        temp_snake_part = snake_body[i]
    if len(new_snake_body) - 2 < score:
        new_snake_body.append(temp_snake_part)
    return snake_head, new_snake_body

def check_wall_body(snake_head, snake_body):
    if snake_head[0] < 0 or snake_head[1] < 0 or snake_head[0] >= pixel_shape['width'] or snake_head[1] >= pixel_shape['height']:
        return 0
    if snake_head in snake_body:
        return 0
    return 1

def check_apple(snake_head, snake_body, apple, score):
    if snake_head == apple:
        score += 1
        while apple == snake_head or apple in snake_body:
            apple = (random.randint(0,(pixel_shape['width']-object_shape[0])//object_shape[0])*object_shape[0], random.randint(0,(pixel_shape['height']-object_shape[1])//object_shape[1])*object_shape[1])
    return apple, score

def wait(seconds):
    time.sleep(seconds)

while playing:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and current_dir != 3:
                current_dir = 0
            elif event.key == pygame.K_UP and current_dir != 2:
                current_dir = 1
            elif event.key == pygame.K_DOWN and current_dir != 1:
                current_dir = 2
            elif event.key == pygame.K_RIGHT and current_dir != 0:
                current_dir = 3
    snake_head, snake_body = update_snake_pos(current_dir, snake_head, snake_body, score)
    apple, score = check_apple(snake_head, snake_body, apple, score)
    playing = check_wall_body(snake_head, snake_body)
    display_all(screen, snake_head, snake_body, apple, score)

    wait(0.25)