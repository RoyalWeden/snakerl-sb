from stable_baselines3 import PPO
import os
from snakeenv import SnakeEnv
from snakeenv1 import SnakeEnv as SnakeEnv1
from snakeenv2 import SnakeEnv as SnakeEnv2
import time

models_dir = ''
logdir = ''
model = None
TIMESTEPS = 10000

learn_type = input('Model type \'new\' or \'continue\': ')

if learn_type == 'new':
    models_dir = f'models/{int(time.time())}'
    logdir = f'logs/{int(time.time())}'

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    env = SnakeEnv1(snake_speed_time=0.00001, game_shape=(5,5), auto_update_shape=True, auto_update_count_needed=5)
    env.reset()

    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)

    iters = 0
elif learn_type == 'continue':
    model_number_selection = input('Which model number: ')
    model_step_selection = int(input('What step of the model to run: '))

    game_shape_list = input('Game shape (i.e. 5,5; 7,7): ').split(',')
    game_shape_str = f'{game_shape_list[0]},{game_shape_list[1]}'
    game_shape = (int(game_shape_list[0]), int(game_shape_list[1]))

    auto_update_count_needed = int(input('Number of max length snakes needed to '))

    models_dir = f'models/{model_number_selection}'
    logdir = f'logs/{model_number_selection}'
    model_path = f'{models_dir}/{game_shape_str}-{model_step_selection}'

    env = SnakeEnv1(snake_speed_time=0.00001, game_shape=game_shape, auto_update_shape=True)
    env.reset()

    model = PPO.load(model_path, env=env)

    iters = int(model_step_selection / TIMESTEPS)

while True:
    iters += 1
    log_name_addition = str(env.game_shape).replace(' ','')[1:-1]
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f'{log_name_addition}-PPO')
    model.save(f'{models_dir}/{log_name_addition}-{TIMESTEPS*iters}')