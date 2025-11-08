from datetime import datetime
from zoneinfo import ZoneInfo
from energybot.web.core.models import Queue


def minutes_since_midnight(dt: datetime) -> int:
    """Convert datetime to minutes from midnight in its local timezone."""
    return dt.hour * 60 + dt.minute


def get_upcoming_slots(minutes_ahead=15):
    tz = ZoneInfo("Europe/Kyiv")
    now = datetime.now(tz)
    now_min = minutes_since_midnight(now)
    soon_min = now_min + minutes_ahead

    upcoming = []
    for queue in Queue.objects.all():
        slots = queue.current_state or []
        for i, slot in enumerate(slots):
            start = slot["start_time_min"]

            if now_min <= start < soon_min:
                prev_slot = slots[i - 1] if i > 0 else None
                if not prev_slot or prev_slot["state"] != slot["state"]:
                    upcoming.append((queue, slot))
                    break
    return upcoming


def get_changed_slots():
    tz = ZoneInfo("Europe/Kyiv")
    now = datetime.now(tz)
    now_min = minutes_since_midnight(now) + 1

    changed = []

    for q in Queue.objects.all():
        if not q.prev_state or not q.current_state:
            continue

        prev = {s["start_time_min"]: s["state"] for s in q.prev_state}
        curr = {s["start_time_min"]: s["state"] for s in q.current_state}

        # collect all changed future slots
        changed_slots = []
        for t, state in curr.items():
            if t < now_min:
                continue  # skip past slots
            if prev.get(t) != state:
                changed_slots.append(
                    {
                        "start_time_min": t,
                        "old_state": prev.get(t),
                        "new_state": state,
                    }
                )

        if changed_slots:
            changed.append(
                {
                    "queue": q,
                    "changed_slots": changed_slots,
                }
            )

    return changed
