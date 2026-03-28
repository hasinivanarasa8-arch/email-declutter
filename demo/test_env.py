import sys
import os

# 🔥 THIS FIXES THE ERROR
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("STARTING TEST")

from env.inbox_env import InboxEnv

env = InboxEnv()

state = env.reset()
print("FIRST STATE:", state)

for i in range(3):
    print("\nSTEP:", i)
    print("Email:", state["email_text"])
    
    action = "spam"
    
    state, reward, done, info = env.step(action)
    
    print("Reward:", reward)
    print("Info:", info)

print("END TEST")