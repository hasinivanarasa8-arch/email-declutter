from env.inbox_env import InboxEnv

def main():
    env = InboxEnv()
    obs = env.reset(seed=0)
    total_reward = 0

    done = False
    while not done:
        action = {"type": "archive"}
        obs, reward, done, info = env.step(action)
        total_reward += reward

    print({
        "status": "ok",
        "total_reward": total_reward,
        "final_state": env.state(),
        "grade": env.grade_episode()
    })

if __name__ == "__main__":
    main()