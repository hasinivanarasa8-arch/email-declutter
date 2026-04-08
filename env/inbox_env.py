# env/inbox_env.py

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import copy
import random


class EmailLabel(str, Enum):
    URGENT = "urgent"
    SPAM = "spam"
    NORMAL = "normal"
    PROMOTION = "promotion"


class ActionType(str, Enum):
    ARCHIVE = "archive"
    FLAG = "flag"
    REPLY = "reply"
    DELETE = "delete"


class ReplyTemplate(str, Enum):
    NONE = "none"
    ACK = "ack"
    ESCALATE = "escalate"
    SCHEDULE = "schedule"


@dataclass
class Email:
    email_id: int
    subject: str
    sender: str
    body: str
    label: EmailLabel
    has_deadline: bool = False
    deadline_step: Optional[int] = None
    is_vip_sender: bool = False
    risk_tags: List[str] = field(default_factory=list)


@dataclass
class Observation:
    current_email_id: Optional[int]
    subject: str
    sender: str
    snippet: str
    urgency_hint: str
    unread_count: int
    spam_backlog: int
    missed_deadlines: int
    flagged_count: int
    step_number: int
    remaining_turns: int


@dataclass
class EnvState:
    episode_id: int
    step_number: int
    max_steps: int
    current_index: int
    unread_count: int
    spam_backlog: int
    missed_deadlines: int
    flagged_count: int
    replied_count: int
    archived_count: int
    deleted_count: int
    total_reward: float
    done: bool
    current_email: Optional[Email]
    pending_emails: List[Email]
    handled_email_ids: List[int]
    history: List[Dict[str, Any]]


@dataclass
class GraderResult:
    total_reward: float
    steps_taken: int
    accuracy: float
    urgent_handled_correctly: int
    spam_handled_correctly: int
    important_deleted_by_mistake: int
    missed_deadlines: int
    spam_left_unhandled: int
    final_score: float
    label_stats: Dict[str, Dict[str, Any]]
    breakdown: Dict[str, Any]


class InboxEnv:
    """
    Gym-style inbox environment.

    Public API:
        - reset(seed=None) -> observation dict
        - step(action) -> observation dict, reward, done, info
        - state() -> full state dict
        - grade_episode() -> grading summary
    """

    def __init__(
        self,
        seed: int = 42,
        max_steps: int = 12,
        scenario: Optional[List[Email]] = None,
    ) -> None:
        self.base_seed = seed
        self.rng = random.Random(seed)
        self.max_steps = max_steps
        self.episode_counter = 0

        self._base_scenario = scenario if scenario is not None else self._default_scenario()
        self._emails: List[Email] = []
        self._state: Optional[EnvState] = None
        self._deadline_penalized_ids: set[int] = set()

    # =====================================================
    # PUBLIC API
    # =====================================================

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Starts a new episode:
        - clears prior counters/history
        - creates a reproducible shuffled scenario
        - returns initial observation
        """
        if seed is not None:
            self.base_seed = seed

        episode_seed = self.base_seed + self.episode_counter
        self.rng = random.Random(episode_seed)
        self.episode_counter += 1

        self._emails = copy.deepcopy(self._base_scenario)
        self.rng.shuffle(self._emails)
        self._deadline_penalized_ids = set()

        current_email = self._emails[0] if self._emails else None

        self._state = EnvState(
            episode_id=self.episode_counter,
            step_number=0,
            max_steps=self.max_steps,
            current_index=0,
            unread_count=len(self._emails),
            spam_backlog=sum(1 for e in self._emails if e.label == EmailLabel.SPAM),
            missed_deadlines=0,
            flagged_count=0,
            replied_count=0,
            archived_count=0,
            deleted_count=0,
            total_reward=0.0,
            done=False,
            current_email=current_email,
            pending_emails=self._emails.copy(),
            handled_email_ids=[],
            history=[],
        )

        return self._observation_dict()

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Applies one action and advances one turn.

        Action format:
            {"type": "flag"}
            {"type": "archive"}
            {"type": "delete"}
            {"type": "reply", "template": "ack"}
        """
        self._assert_initialized()

        if self._state.done:
            return self._observation_dict(), 0.0, True, {
                "warning": "Episode already finished. Call reset() to start a new episode."
            }

        current_email = self._state.current_email
        if current_email is None:
            self._state.done = True
            return self._observation_dict(), 0.0, True, {
                "warning": "No current email available."
            }

        normalized_action = self._normalize_action(action)
        reward, outcome = self._score_action(current_email, normalized_action)

        self._state.total_reward += reward
        self._state.handled_email_ids.append(current_email.email_id)

        action_type = normalized_action["type"]
        template = normalized_action.get("template", ReplyTemplate.NONE.value)

        if action_type == ActionType.FLAG.value:
            self._state.flagged_count += 1
        elif action_type == ActionType.REPLY.value:
            self._state.replied_count += 1
        elif action_type == ActionType.ARCHIVE.value:
            self._state.archived_count += 1
        elif action_type == ActionType.DELETE.value:
            self._state.deleted_count += 1

        self._state.history.append(
            {
                "step": self._state.step_number,
                "email_id": current_email.email_id,
                "subject": current_email.subject,
                "sender": current_email.sender,
                "true_label": current_email.label.value,
                "action": action_type,
                "template": template,
                "reward": reward,
                "outcome": outcome,
            }
        )

        self._advance_time_and_penalties()
        self._move_to_next_email()

        done = self._state.done
        info = {
            "outcome": outcome,
            "step_number": self._state.step_number,
            "total_reward": self._state.total_reward,
            "handled_email_ids": self._state.handled_email_ids.copy(),
            "state": self.state(),
        }

        return self._observation_dict(), reward, done, info

    def state(self) -> Dict[str, Any]:
        """Returns the current structured environment state."""
        self._assert_initialized()
        return self._state_to_dict()

    def grade_episode(self) -> Dict[str, Any]:
        """
        Grades episode behavior into a measurable score.
        """
        self._assert_initialized()

        history = self._state.history
        label_stats: Dict[str, Dict[str, Any]] = {
            EmailLabel.URGENT.value: {"correct": 0, "total": 0, "accuracy": 0.0},
            EmailLabel.SPAM.value: {"correct": 0, "total": 0, "accuracy": 0.0},
            EmailLabel.NORMAL.value: {"correct": 0, "total": 0, "accuracy": 0.0},
            EmailLabel.PROMOTION.value: {"correct": 0, "total": 0, "accuracy": 0.0},
        }

        urgent_correct = 0
        spam_correct = 0
        important_deleted = 0

        for item in history:
            label = item["true_label"]
            action = item["action"]
            template = item["template"]

            if label in label_stats:
                label_stats[label]["total"] += 1

            is_correct = False

            if label == EmailLabel.URGENT.value:
                if action == ActionType.FLAG.value:
                    urgent_correct += 1
                    is_correct = True
                elif action == ActionType.REPLY.value and template in {
                    ReplyTemplate.ACK.value,
                    ReplyTemplate.ESCALATE.value,
                }:
                    urgent_correct += 1
                    is_correct = True
                if action == ActionType.DELETE.value:
                    important_deleted += 1

            elif label == EmailLabel.SPAM.value:
                if action in {ActionType.DELETE.value, ActionType.ARCHIVE.value}:
                    spam_correct += 1
                    is_correct = True

            elif label == EmailLabel.NORMAL.value:
                if action in {ActionType.REPLY.value, ActionType.ARCHIVE.value, ActionType.FLAG.value}:
                    is_correct = True
                if action == ActionType.DELETE.value:
                    important_deleted += 1

            elif label == EmailLabel.PROMOTION.value:
                if action in {ActionType.ARCHIVE.value, ActionType.DELETE.value}:
                    is_correct = True

            if is_correct and label in label_stats:
                label_stats[label]["correct"] += 1

        total_correct = 0
        total_seen = 0
        for label, stats in label_stats.items():
            total = stats["total"]
            correct = stats["correct"]
            stats["accuracy"] = (correct / total) if total else 0.0
            total_correct += correct
            total_seen += total

        accuracy = (total_correct / total_seen) if total_seen else 0.0
        spam_left = self._state.spam_backlog

        final_score = (
            self._state.total_reward
            + (urgent_correct * 5)
            + (spam_correct * 3)
            - (important_deleted * 10)
            - (self._state.missed_deadlines * 12)
            - (spam_left * 2)
        )

        grader = GraderResult(
            total_reward=self._state.total_reward,
            steps_taken=self._state.step_number,
            accuracy=round(accuracy, 4),
            urgent_handled_correctly=urgent_correct,
            spam_handled_correctly=spam_correct,
            important_deleted_by_mistake=important_deleted,
            missed_deadlines=self._state.missed_deadlines,
            spam_left_unhandled=spam_left,
            final_score=round(final_score, 2),
            label_stats=label_stats,
            breakdown={
                "history_length": len(history),
                "deadline_penalty": self._state.missed_deadlines * 12,
                "important_delete_penalty": important_deleted * 10,
                "spam_left_penalty": spam_left * 2,
            },
        )

        return asdict(grader)

    # =====================================================
    # INTERNALS
    # =====================================================

    def _normalize_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(action, dict):
            return {"type": "archive", "template": ReplyTemplate.NONE.value}

        action_type = str(action.get("type", ActionType.ARCHIVE.value)).lower().strip()
        template = str(action.get("template", ReplyTemplate.NONE.value)).lower().strip()

        if action_type not in {a.value for a in ActionType}:
            action_type = ActionType.ARCHIVE.value

        if template not in {t.value for t in ReplyTemplate}:
            template = ReplyTemplate.NONE.value

        return {"type": action_type, "template": template}

    def _score_action(self, email: Email, action: Dict[str, Any]) -> Tuple[float, str]:
        action_type = action["type"]
        template = action.get("template", ReplyTemplate.NONE.value)

        if email.label == EmailLabel.URGENT:
            if action_type == ActionType.FLAG.value:
                return 15.0, "urgent_flagged_correctly"
            if action_type == ActionType.REPLY.value:
                if template == ReplyTemplate.ESCALATE.value:
                    return 15.0, "urgent_escalated_correctly"
                if template == ReplyTemplate.ACK.value:
                    return 12.0, "urgent_acknowledged"
                if template == ReplyTemplate.SCHEDULE.value:
                    return 4.0, "urgent_replied_suboptimally"
                return 3.0, "urgent_replied_generic"
            if action_type == ActionType.ARCHIVE.value:
                return -8.0, "urgent_archived_wrongly"
            if action_type == ActionType.DELETE.value:
                return -12.0, "urgent_deleted_wrongly"

        if email.label == EmailLabel.SPAM:
            if action_type == ActionType.DELETE.value:
                return 8.0, "spam_deleted_correctly"
            if action_type == ActionType.ARCHIVE.value:
                return 5.0, "spam_archived_correctly"
            if action_type == ActionType.FLAG.value:
                return 1.0, "spam_flagged_but_not_removed"
            if action_type == ActionType.REPLY.value:
                return -6.0, "replied_to_spam"

        if email.label == EmailLabel.NORMAL:
            if action_type == ActionType.REPLY.value:
                if template == ReplyTemplate.ACK.value:
                    return 8.0, "normal_replied_ack"
                if template == ReplyTemplate.SCHEDULE.value:
                    return 7.0, "normal_replied_schedule"
                if template == ReplyTemplate.ESCALATE.value:
                    return 2.0, "normal_escalated_unnecessarily"
                return 4.0, "normal_replied_generic"
            if action_type == ActionType.ARCHIVE.value:
                return 3.0, "normal_archived"
            if action_type == ActionType.FLAG.value:
                return 2.0, "normal_flagged"
            if action_type == ActionType.DELETE.value:
                return -10.0, "normal_deleted_wrongly"

        if email.label == EmailLabel.PROMOTION:
            if action_type == ActionType.ARCHIVE.value:
                return 5.0, "promotion_archived_correctly"
            if action_type == ActionType.DELETE.value:
                return 4.0, "promotion_deleted"
            if action_type == ActionType.FLAG.value:
                return -1.0, "promotion_flagged_unnecessarily"
            if action_type == ActionType.REPLY.value:
                return -3.0, "replied_to_promotion"

        return -2.0, "fallback_penalty"

    def _advance_time_and_penalties(self) -> None:
        self._state.step_number += 1

        remaining = self._state.pending_emails[self._state.current_index + 1 :]

        for email in remaining:
            if (
                email.label == EmailLabel.URGENT
                and email.has_deadline
                and email.deadline_step is not None
                and self._state.step_number > email.deadline_step
                and email.email_id not in self._state.handled_email_ids
                and email.email_id not in self._deadline_penalized_ids
            ):
                self._state.missed_deadlines += 1
                self._state.total_reward -= 12
                self._deadline_penalized_ids.add(email.email_id)

        self._state.spam_backlog = sum(1 for e in remaining if e.label == EmailLabel.SPAM)
        if self._state.spam_backlog >= 3:
            self._state.total_reward -= 2

        self._state.unread_count = len(remaining)

    def _move_to_next_email(self) -> None:
        self._state.current_index += 1

        no_more_emails = self._state.current_index >= len(self._state.pending_emails)
        max_steps_reached = self._state.step_number >= self._state.max_steps

        if no_more_emails or max_steps_reached:
            self._state.done = True
            self._state.current_email = None
            self._state.unread_count = 0 if no_more_emails else self._state.unread_count
        else:
            self._state.current_email = self._state.pending_emails[self._state.current_index]

    def _observation(self) -> Observation:
        self._assert_initialized()

        email = self._state.current_email
        remaining_turns = max(self._state.max_steps - self._state.step_number, 0)

        if email is None:
            return Observation(
                current_email_id=None,
                subject="No pending email",
                sender="N/A",
                snippet="Episode complete.",
                urgency_hint="none",
                unread_count=self._state.unread_count,
                spam_backlog=self._state.spam_backlog,
                missed_deadlines=self._state.missed_deadlines,
                flagged_count=self._state.flagged_count,
                step_number=self._state.step_number,
                remaining_turns=remaining_turns,
            )

        urgency_hint = "high" if email.label == EmailLabel.URGENT or email.is_vip_sender else "low"

        return Observation(
            current_email_id=email.email_id,
            subject=email.subject,
            sender=email.sender,
            snippet=self._make_snippet(email.body),
            urgency_hint=urgency_hint,
            unread_count=self._state.unread_count,
            spam_backlog=self._state.spam_backlog,
            missed_deadlines=self._state.missed_deadlines,
            flagged_count=self._state.flagged_count,
            step_number=self._state.step_number,
            remaining_turns=remaining_turns,
        )

    def _observation_dict(self) -> Dict[str, Any]:
        return asdict(self._observation())

    def _state_to_dict(self) -> Dict[str, Any]:
        current_email = asdict(self._state.current_email) if self._state.current_email else None
        return {
            "episode_id": self._state.episode_id,
            "step_number": self._state.step_number,
            "max_steps": self._state.max_steps,
            "current_index": self._state.current_index,
            "unread_count": self._state.unread_count,
            "spam_backlog": self._state.spam_backlog,
            "missed_deadlines": self._state.missed_deadlines,
            "flagged_count": self._state.flagged_count,
            "replied_count": self._state.replied_count,
            "archived_count": self._state.archived_count,
            "deleted_count": self._state.deleted_count,
            "total_reward": self._state.total_reward,
            "done": self._state.done,
            "current_email": current_email,
            "handled_email_ids": list(self._state.handled_email_ids),
            "history": copy.deepcopy(self._state.history),
        }

    def _assert_initialized(self) -> None:
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

    @staticmethod
    def _make_snippet(text: str, max_len: int = 140) -> str:
        clean = " ".join(text.split())
        return clean[:max_len] + ("..." if len(clean) > max_len else "")

    def _default_scenario(self) -> List[Email]:
        return [
            Email(
                email_id=1,
                subject="Client escalation: production outage by 5 PM",
                sender="vip.client@company.com",
                body="We need an immediate response. Production issue is impacting users. Please confirm owner and ETA.",
                label=EmailLabel.URGENT,
                has_deadline=True,
                deadline_step=2,
                is_vip_sender=True,
                risk_tags=["deadline", "vip", "outage"],
            ),
            Email(
                email_id=2,
                subject="Congratulations! You won a free vacation",
                sender="promo@spammy-offers.biz",
                body="Claim your free vacation now by clicking this suspicious link.",
                label=EmailLabel.SPAM,
                risk_tags=["spam", "phishing"],
            ),
            Email(
                email_id=3,
                subject="Weekly team sync agenda",
                sender="manager@company.com",
                body="Please review the agenda and reply with any discussion items before tomorrow.",
                label=EmailLabel.NORMAL,
                risk_tags=["reply_needed"],
            ),
            Email(
                email_id=4,
                subject="Limited-time enterprise software discount",
                sender="marketing@vendor.com",
                body="Explore our new AI productivity suite with a 30 percent discount this quarter.",
                label=EmailLabel.PROMOTION,
                risk_tags=["promo"],
            ),
            Email(
                email_id=5,
                subject="Need approval for customer proposal by noon",
                sender="sales.lead@company.com",
                body="Please review and approve the proposal. The customer is waiting for confirmation.",
                label=EmailLabel.URGENT,
                has_deadline=True,
                deadline_step=4,
                risk_tags=["deadline", "approval"],
            ),
            Email(
                email_id=6,
                subject="Your account has been suspended",
                sender="alert@totally-real-security.io",
                body="Immediate action required. Log in here to verify your account credentials.",
                label=EmailLabel.SPAM,
                risk_tags=["spam", "credential_theft"],
            ),
            Email(
                email_id=7,
                subject="Can we reschedule tomorrow's architecture review?",
                sender="architect@company.com",
                body="Something came up. Please reply with alternative slots for the meeting.",
                label=EmailLabel.NORMAL,
                risk_tags=["schedule"],
            ),
            Email(
                email_id=8,
                subject="Quarter-end pricing brochure",
                sender="noreply@newsletter.vendor.com",
                body="Please find the latest brochure and pricing updates attached.",
                label=EmailLabel.PROMOTION,
                risk_tags=["promo"],
            ),
        ]