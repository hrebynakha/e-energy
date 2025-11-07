#!/usr/bin/env python3
import fcntl
import sys
import os
import telebot
import django
from energybot import config
from energybot.handlers.process import get_schedule_short
from energybot.helpers.logger import logger
import energybot.helpers.messages as messages
from energybot.helpers.time import convert_minutes_to_hours, get_current_minutes

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "energybot.web.energyweb.settings")
django.setup()

from energybot.web.core.models import Subscription
from energybot.web.core.utils import get_changed_slots, get_upcoming_slots


notification_timeout = config.TIMEOUT
notification_to_on = config.TURN_ON_NOTIFY

queues = {}

bot = telebot.TeleBot(config.BOT_TOKEN)

LOCK_FILE = "/tmp/worker.lock"


def get_changed_slots_message(slot):

    start_str = convert_minutes_to_hours(slot["start_time_min"])
    old_state = messages.STATUS_MAP[slot["old_state"]]
    new_state = messages.STATUS_MAP[slot["new_state"]]

    return f"<i>{start_str}</i> {old_state} → {new_state}"


def get_notification_message(queue, slot):
    mark = messages.MARKS_MAP[slot["state"]]
    alert_text_map = {
        "OFF": messages.NOTIFICATION_TURN_OFF,
        "ON": messages.NOTIFICATION_TURN_ON,
        "WAIT": messages.NOTIFICATION_TURN_WAIT,
        "NO_INFO": messages.NOTIFICATION_TURN_NO_INFO,
    }
    after_text = alert_text_map[slot["state"]]
    current_minutes = get_current_minutes()
    minutes_difference = slot["start_time_min"] - current_minutes

    message = (
        mark
        + queue.name
        + " "
        + messages.NOTIFICATION_BEFORE_TEXT
        + " "
        + str(minutes_difference)
        + " "
        + after_text
    )
    return message


def notify_upcoming_outages():
    slots = get_upcoming_slots(notification_timeout)
    for queue, slot in slots:
        logger.info(
            "Processing notification for queue: %s , state: %s",
            queue.name,
            slot["state"],
        )
        subs = Subscription.objects.filter(queue=queue)
        for sub in subs:
            msg = get_notification_message(queue, slot)
            logger.info(
                "Sending notification to %s: %s, user: %s",
                sub.user.chat_id,
                msg,
                sub.user.username,
            )
            bot.send_message(sub.user.chat_id, msg)
    logger.info("Notification about upcoming outages sent for %s queues", len(slots))


def notify_changed_slots():
    slots = get_changed_slots()
    for item in slots:
        q = item["queue"]
        logger.info("Processing notification for queue: %s", q.name)
        subs = Subscription.objects.filter(queue=q)
        for sub in subs:
            msg = messages.NOTIFICATION_CHANGED + "\n"
            for slot in item["changed_slots"]:
                time_str = convert_minutes_to_hours(slot["start_time_min"])
                logger.info(
                    "Queue has been changed: %s, Time: %s → %s → %s",
                    q.name,
                    time_str,
                    slot["old_state"],
                    slot["new_state"],
                )
                msg += get_changed_slots_message(slot) + "\n"
            msg += "\n"
            msg += get_schedule_short(q.id, hours=24)
            logger.info(
                "Sending notification about queue changes %s to %s: %s",
                q.name,
                sub.user.chat_id,
                sub.user.username,
            )
            bot.send_message(sub.user.chat_id, msg, parse_mode="HTML")
    logger.info("Notification about queue changes sent for %s queues", len(slots))


def run_worker():
    with open(LOCK_FILE, "w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            notify_upcoming_outages()
            notify_changed_slots()
        except BlockingIOError:
            sys.exit("Worker already running, skipping...")


if __name__ == "__main__":
    run_worker()
