import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time
import os
import glob
from stable_baselines3 import SAC
from LCP_CaterpillarEnv_Final import LCP_CaterpillarEnv

SAVE_DIR = "./paper_results_50k"
os.makedirs(SAVE_DIR, exist_ok=True)

SLOW_MOTION_FACTOR = 400.0 

if os.path.exists("sac_lce_final_model.zip"):
    model_path = "sac_lce_final_model"
else:
    list_of_files = glob.glob('./models/*.zip')
    if not list_of_files:
        print("!! 오류: 학습된 모델 파일이 없습니다.")
        exit()
    latest_file = max(list_of_files, key=os.path.getctime)
    model_path = latest_file

print(f"--- 검증 시작: {model_path} 로드 중 ---")

plt.rcParams.update({
    'font.size': 12, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 10
})

env = LCP_CaterpillarEnv(render=True)
model = SAC.load(model_path)

obs, _ = env.reset()
action_log = []
pos_log = []

TEST_STEPS = 1000 

print(f"--- 시뮬레이션 주행 시작 ({TEST_STEPS} Steps) ---")
print(f">> 슬로우 모션({SLOW_MOTION_FACTOR}x) 적용됨. 넘어지면 리스폰됩니다.")

for i in range(TEST_STEPS):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    
    action_log.append(action)
    base_pos = obs[0:3] 
    pos_log.append(base_pos[0]) 

    time.sleep((1./1240.) * SLOW_MOTION_FACTOR)

    if done or truncated:
        print(f"!! 에피소드 종료 (Step: {i+1}). 로봇을 리스폰합니다.")
        obs, _ = env.reset() 

env.close()
print("--- 데이터 수집 완료. 그래프 생성 중... ---")

actual_steps = len(action_log)
actions = np.array(action_log).T # (Joints, Time)
positions = np.array(pos_log)
time_steps = np.arange(actual_steps) * (1./240.) 

fig1, ax1 = plt.subplots(figsize=(10, 5))
im = ax1.imshow(actions, aspect='auto', cmap='magma', origin='upper', 
                extent=[0, time_steps[-1], 8, 0], vmin=0, vmax=1)

ax1.set_title('Fig 1. Emergent Spatiotemporal Gait Pattern', fontweight='bold')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Joint Index (Head -> Tail)')
ax1.set_yticks(np.arange(9))
ax1.set_yticklabels([f'J{i}' for i in range(9)])
cbar = plt.colorbar(im, ax=ax1)
cbar.set_label('Action Intensity', rotation=270, labelpad=15)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/Fig1_Heatmap.png", dpi=300)
print(">> Fig 1 저장 완료")

fig2, ax2 = plt.subplots(figsize=(12, 5))
target_joints = [0, 4, 8] 
colors = ['red', 'green', 'blue']

zoom_steps = min(1000, actual_steps)
t_zoom = time_steps[:zoom_steps]

for idx, j_idx in enumerate(target_joints):
    ax2.plot(t_zoom, actions[j_idx, :zoom_steps], 
             color=colors[idx], label=f'Joint {j_idx}', linewidth=2, alpha=0.8)

ax2.set_title('Fig 2. Phase Lag Analysis', fontweight='bold')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Action Value')
ax2.legend(loc='upper right')
ax2.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/Fig2_PhaseShift.png", dpi=300)
print(">> Fig 2 저장 완료")

fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.plot(time_steps, positions, color='#1f77b4', linewidth=2.5)
ax3.set_title('Fig 3. Robot Forward Displacement', fontweight='bold')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('X Position (m)')
ax3.grid(True, linestyle=':', alpha=0.7)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/Fig3_Displacement.png", dpi=300)
print(">> Fig 3 저장 완료 (리스폰 시 그래프가 0으로 떨어지는 것은 정상입니다)")

print(f"\n✅ 분석 완료. '{SAVE_DIR}' 폴더를 확인하세요.")
