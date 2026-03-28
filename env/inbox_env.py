# env/inbox_env.py

from env.generator import generate_email
from env.reward import calculate_reward


class InboxEnv:
    def __init__(self, max_steps=20):
        self.max_steps = max_steps
        self.current_step = 0
        self.current_email = None

    def reset(self):
        self.current_step = 0
        self.current_email = generate_email()
        return self.current_email

    def state(self):
        return self.current_email

    def step(self, action):
        true_label = self.current_email["true_label"]

        reward = calculate_reward(true_label, action)

        self.current_step += 1

        done = self.current_step >= self.max_steps

        self.current_email = generate_email()

        return self.current_email, reward, done, {
            "true_label": true_label,
            "predicted_label": action
        }