import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("STARTING TEST")

from env.inbox_env import InboxEnv
from agents.learned_agent import LearnedAgent
# from agents.rule_agent import RuleAgent
# from agents.learned_agent import LearnedAgent

env = InboxEnv()

agent = LearnedAgent()   # change to RuleAgent() or LearnedAgent()

state = env.reset()

for i in range(5):
    print("\nSTEP:", i)
    print("Email:", state["email_text"])

    action = agent.act(state)

    state, reward, done, info = env.step(action)

    print("Predicted:", action)
    print("Actual:", info["true_label"])
    print("Reward:", reward)

print("END TEST")