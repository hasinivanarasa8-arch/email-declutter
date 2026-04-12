from fastapi import FastAPI
from env.inbox_env import InboxEnv

app = FastAPI()

@app.get("/")
def run_agent():
    env = InboxEnv()
    obs = env.reset(seed=0)
    total_reward = 0

    done = False
    while not done:
        action = {"type": "archive"}
        obs, reward, done, info = env.step(action)
        total_reward += reward

    return {
        "status": "ok",
        "total_reward": total_reward,
        "final_state": env.state(),
        "grade": env.grade_episode()
    }