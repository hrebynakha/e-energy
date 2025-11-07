# import importlib
import os
import django
from energybot.helpers.time import convert_minutes_to_hours, get_current_minutes

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "energybot.web.energyweb.settings")
django.setup()

from energybot.web.core.models import Queue
from energybot.helpers.messages import STATUS_MAP


def get_schedule_detail(queue_id, hours=4):
    queue = Queue.objects.get(id=queue_id)
    if not queue:
        raise ValueError("Queue not found.")
    if not queue.current_state:
        raise ValueError("Queue current state not found.")

    schedule = queue.current_state
    current_minutes = get_current_minutes()
    not_process_after_minutes = current_minutes + hours * 60
    if hours == 24:
        next_text = ", до кінця поточного дня"
    else:
        next_text = ", на наступні " + str(hours) + " години"
    message = (
        "<b>Детальна інформація по черзі 🔋" + str(queue.name) + next_text + "</b>\n"
    )

    for items in schedule:
        start_time_min = items["start_time_min"]
        end_time_min = items["end_time_min"]
        state = items["state"]

        if start_time_min > current_minutes:
            date_str = (
                convert_minutes_to_hours(start_time_min)
                + " - "
                + convert_minutes_to_hours(end_time_min)
            )
            message += "<i>" + date_str + "</i> " + STATUS_MAP[state] + "\n"
        if start_time_min > not_process_after_minutes:
            break

    return message


def get_schedule_short(queue_id, hours=4):
    """
    Get short grouped schedule for queue.
    Shows merged time ranges for consecutive slots with same state.
    Example:
    13:30 - 20:00  ✅ Присутнє
    20:00 - 22:30  ❌ Відсутнє
    22:30 - 23:30  ✅ Присутнє
    """
    queue = Queue.objects.get(id=queue_id)
    if not queue:
        raise ValueError("Queue not found.")
    if not queue.current_state:
        raise ValueError("Queue current state not found.")

    schedule = queue.current_state
    current_minutes = get_current_minutes()
    not_process_after_minutes = current_minutes + hours * 60

    if hours == 24:
        next_text = ", до кінця поточного дня"
    else:
        next_text = ", на наступні " + str(hours) + " години"

    message = (
        "<b>Коротка інформація по черзі 🔋" + str(queue.name) + next_text + "</b>\n"
    )

    future_slots = [
        s
        for s in schedule
        if s["start_time_min"] >= current_minutes
        and s["start_time_min"] <= not_process_after_minutes
    ]

    if not future_slots:
        message += "Немає запланованих змін."
        return message

    grouped = []
    current_group = None

    for s in future_slots:
        start = s["start_time_min"]
        end = s["end_time_min"]
        state = s["state"]

        if current_group is None:
            current_group = {"start": start, "end": end, "state": state}
        elif state == current_group["state"]:
            current_group["end"] = end  # extend same state
        else:
            grouped.append(current_group)
            current_group = {"start": start, "end": end, "state": state}

    if current_group:
        grouped.append(current_group)

    for g in grouped:
        start_str = convert_minutes_to_hours(g["start"])
        end_str = convert_minutes_to_hours(g["end"])
        message += f"<i>{start_str} - {end_str}</i> {STATUS_MAP[g['state']]}\n"

    return message
