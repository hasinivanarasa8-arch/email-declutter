print("RUNNING DEMO FILE")

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.random_agent import RandomAgent
from agents.rule_agent import RuleAgent
from agents.learned_agent import LearnedAgent
from evaluation.evaluator import evaluate_agent


agents = {
    "Random": RandomAgent(),
    "Rule": RuleAgent(),
    "Learned (HF)": LearnedAgent()
}

for name, agent in agents.items():
    print(f"\n===== Evaluating {name} Agent =====")

    result = evaluate_agent(agent, steps=50)

    print("Accuracy:", round(result["accuracy"], 2))
    print("Total Reward:", result["total_reward"])
    print("Label-wise Accuracy:", result["label_stats"])