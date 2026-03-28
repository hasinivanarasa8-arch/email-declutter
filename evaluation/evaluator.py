# evaluation/evaluator.py

from env.inbox_env import InboxEnv
from evaluation.metrics import calculate_accuracy, calculate_total_reward, label_wise_accuracy


def evaluate_agent(agent, steps=50):
    env = InboxEnv(max_steps=steps)

    state = env.reset()

    results = []

    for _ in range(steps):
        action = agent.act(state)

        state, reward, done, info = env.step(action)

        results.append({
            "true": info["true_label"],
            "pred": action,
            "reward": reward
        })

        if done:
            break

    accuracy = calculate_accuracy(results)
    total_reward = calculate_total_reward(results)
    label_stats = label_wise_accuracy(results)

    return {
        "accuracy": accuracy,
        "total_reward": total_reward,
        "label_stats": label_stats
    }