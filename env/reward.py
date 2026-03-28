# env/reward.py

def calculate_reward(true_label, predicted_label):
    
    # correct prediction
    if true_label == predicted_label:
        reward = 4

        # bonus for correctly identifying spam
        if true_label == "spam":
            reward += 2

        return reward

    # wrong prediction
    else:
        penalty = -5

        # extra penalty if important email is missed
        if true_label == "important":
            penalty -= 3

        return penalty