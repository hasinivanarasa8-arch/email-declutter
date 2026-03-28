# evaluation/metrics.py

def calculate_accuracy(results):
    correct = 0

    for r in results:
        if r["true"] == r["pred"]:
            correct += 1

    return correct / len(results) if results else 0


def calculate_total_reward(results):
    return sum(r["reward"] for r in results)


def label_wise_accuracy(results):
    stats = {}

    for r in results:
        label = r["true"]

        if label not in stats:
            stats[label] = {"correct": 0, "total": 0}

        stats[label]["total"] += 1

        if r["true"] == r["pred"]:
            stats[label]["correct"] += 1

    for label in stats:
        stats[label]["accuracy"] = stats[label]["correct"] / stats[label]["total"]

    return stats