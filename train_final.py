import gymnasium as gym
from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import CheckpointCallback
import os
import shutil
from LCP_CaterpillarEnv_Final import LCP_CaterpillarEnv


env = LCP_CaterpillarEnv(render=False) 

print("--- 🚀 S자 주행 학습 시작 (Residual RL) ---")
checkpoint_callback = CheckpointCallback(
save_freq=10000,
save_path="./models",
name_prefix="sac_lce"
)


model = SAC(
"MlpPolicy",
env,
verbose=1,
tensorboard_log="./final_logs",
learning_rate=3e-4,
batch_size=256,
ent_coef='auto'
)

model.learn(total_timesteps=50000, log_interval=1, callback=checkpoint_callback)

model.save("sac_lce_final_model")

print("--- ✅ 학습 완료! 이제 verify 코드를 돌려보세요. ---")
