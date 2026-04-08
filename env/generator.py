# env/generator.py

import random
from env.state_schema import create_state

LABELS = ["important", "spam", "promotion", "social", "later"]

EMAIL_BANK = {
    "spam": [
        "Congratulations! You won a free iPhone. Click now!",
        "Earn money fast with this simple trick!",
        "You have been selected for a lottery prize!",
        "Claim your exclusive reward before midnight!",
        "Urgent offer: verify your account to unlock cash bonus.",
        "Your account has been flagged. Click here immediately.",
        "Win big today with this limited-time jackpot entry.",
        "Free vacation package waiting for you. Respond now!",
    ],
    "important": [
        "Meeting scheduled at 10 AM tomorrow with the client team.",
        "Project deadline is approaching. Please submit the final report.",
        "Your interview is confirmed for Monday at 2 PM.",
        "Reminder: quarterly review presentation is due by evening.",
        "Client escalation requires your response within the next hour.",
        "Action needed: approve budget sheet before 5 PM.",
        "Please join the hiring panel discussion at 4 PM today.",
        "Production issue reported. Team sync starts in 15 minutes.",
    ],
    "promotion": [
        "Flat 50% off on all products this weekend only.",
        "Big Billion Days sale is live now!",
        "Special discount just for you.",
        "Shop today and get free shipping on orders above $50.",
        "Limited-time deal on electronics ends tonight.",
        "Use promo code SAVE20 for your next purchase.",
        "Season-end fashion sale starts now.",
        "Exclusive member offer: buy one get one free.",
    ],
    "social": [
        "Your friend tagged you in a post.",
        "New message from your friend.",
        "Someone liked your photo.",
        "You have a new follow request.",
        "Your post received 12 new reactions.",
        "A contact mentioned you in the comments.",
        "You were invited to join a community group.",
        "Your friend shared a memory with you.",
    ],
    "later": [
        "Weekly newsletter update from our editorial team.",
        "Daily news digest for your morning read.",
        "Reminder: check your subscriptions.",
        "Your monthly activity summary is ready.",
        "Here is your reading list for this week.",
        "New blog posts have been published.",
        "Product update newsletter for April.",
        "A curated roundup of articles you may enjoy.",
    ],
}


def generate_email():
    true_label = random.choice(LABELS)
    email_text = random.choice(EMAIL_BANK[true_label])

    sender_domains = {
        "spam": ["prize-alerts.net", "claim-now.co", "fastcash-mail.com"],
        "important": ["company.com", "clientmail.com", "hr.company.com"],
        "promotion": ["deals.store.com", "offers.shop.com", "promo.market.com"],
        "social": ["socialapp.com", "connecthub.com", "friendspace.com"],
        "later": ["newsletter.com", "updates.media.com", "digestmail.com"],
    }

    sender_name_prefix = {
        "spam": ["reward", "bonus", "promo"],
        "important": ["manager", "hr", "client", "teamlead"],
        "promotion": ["sales", "offers", "store"],
        "social": ["friend", "notification", "community"],
        "later": ["newsletter", "digest", "updates"],
    }

    sender = (
        f"{random.choice(sender_name_prefix[true_label])}"
        f"{random.randint(1, 99)}@"
        f"{random.choice(sender_domains[true_label])}"
    )

    subject = email_text[:45] + ("..." if len(email_text) > 45 else "")

    return create_state(
        email_text=email_text,
        sender=sender,
        subject=subject,
        true_label=true_label,
    )
