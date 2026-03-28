# env/generator.py

import random
from env.state_schema import create_state

LABELS = ["important", "spam", "promotion", "social", "later"]

SPAM_EMAILS = [
    "Congratulations! You won a free iPhone. Click now!",
    "Earn money fast with this simple trick!",
    "You have been selected for a lottery prize!",
]

IMPORTANT_EMAILS = [
    "Meeting scheduled at 10 AM tomorrow",
    "Project deadline is approaching",
    "Your interview is confirmed",
]

PROMOTION_EMAILS = [
    "Flat 50% off on all products!",
    "Big Billion Days sale is live now!",
    "Special discount just for you",
]

SOCIAL_EMAILS = [
    "Your friend tagged you in a post",
    "New message from your friend",
    "Someone liked your photo",
]

LATER_EMAILS = [
    "Weekly newsletter update",
    "Daily news digest",
    "Reminder: check your subscriptions",
]


def generate_email():
    label = random.choice(LABELS)

    if label == "spam":
        text = random.choice(SPAM_EMAILS)
    elif label == "important":
        text = random.choice(IMPORTANT_EMAILS)
    elif label == "promotion":
        text = random.choice(PROMOTION_EMAILS)
    elif label == "social":
        text = random.choice(SOCIAL_EMAILS)
    else:
        text = random.choice(LATER_EMAILS)

    sender = f"user{random.randint(1,100)}@mail.com"
    subject = text[:30]

    return create_state(text, sender, subject, label)


def generate_batch(n=10):
    return [generate_email() for _ in range(n)]
    return create_state(text, sender, subject, label)


def generate_batch(n=10):
    return [generate_email() for _ in range(n)]