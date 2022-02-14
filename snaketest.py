from stable_baselines3 import PPO
from snakeenv1 import SnakeEnv as SnakeEnv1

model_number_selection = input('Which model number: ')
model_step_selection = int(input('What step of the model to run: '))

game_shape_list = input('Game shape (i.e. 5,5; 6,6): ').split(',')
game_shape_str = f'{game_shape_list[0]},{game_shape_list[1]}'
game_shape = (int(game_shape_list[0]), int(game_shape_list[1]))

models_dir = f'models/{model_number_selection}'
model_path = f'{models_dir}/{game_shape_str}-{model_step_selection}'

episodes = int(input('Number of episodes: '))

env = SnakeEnv1(snake_speed_time=0.5, game_shape=game_shape, testing=True)
env.reset()

model = PPO.load(model_path, env=env)

def change_speed(env):
    key = env.key_press
    if key == '>':
        env.snake_speed_time /= 2
        env.change_speed_text = '>>>'
    elif key == '<':
        env.snake_speed_time *= 2
        env.change_speed_text = '<<<'
    env.key_press = None

for ep in range(episodes):
    obs = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, info = env.step(action)
        change_speed(env)