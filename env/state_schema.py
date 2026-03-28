# env/state_schema.py

def create_state(email_text, sender, subject, true_label):
    return {
        "email_text": email_text,
        "sender": sender,
        "subject": subject,
        "true_label": true_label
    }