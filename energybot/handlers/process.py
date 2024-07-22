import importlib
from datetime import datetime, timedelta
from energybot import config
from energybot.helpers.data import load_data


def get_schedule_message(q_num, hours=4):
    data = load_data()
    table = data['table']
    q_schedul = table[q_num]
    current_date = datetime.now()
    not_process_after = current_date + timedelta(hours=hours)
    q_query = []
    for time_, value in q_schedul.items():
        if time_ > current_date:
            q_query.append((time_, value))
        if time_ > not_process_after:
            break
    if hours == 24:
        next_text = ", до кінця поточного дня"
    else:
        next_text = ", на наступні " + str(hours) + " години"
    message = "<b>Інформація по черзі №" +  str(q_num) + next_text + "</b>\n"
    start_time, prev_state = q_query[0]
    output_data = []
    for time_, energy_state in q_query[1:]:
        if energy_state['text']  != prev_state['text']:
            end_time = time_
            output_data.append((start_time, end_time, prev_state['text']))
            start_time = time_
        prev_state = energy_state

    output_data.append((start_time, time_, prev_state['text']))

    for start_time, end_time, status in output_data:
        if start_time == end_time:
            end_time = "?"
        else:
            end_time = end_time.strftime("%H:%M")
        date_str = start_time.strftime("%H:%M") + " - " + end_time
        if status == 'ON':
            check_mark = " ✅ Присутнє"
        else:
            check_mark = " ❌ Відсутнє"
        message += "<i>" + date_str + "</i> " + check_mark   + "\n"
    return message


def get_schedule_detail(q_num, hours=4):
    data = load_data()
    table = data['table']
    q_schedul = table[q_num]
    current_date = datetime.now()
    not_process_after = current_date + timedelta(hours=hours)
    q_query = []
    for time_, value in q_schedul.items():
        if time_ > current_date:
            q_query.append((time_, value))
        if time_ > not_process_after:
            break
    if hours == 24:
        next_text = ", до кінця поточного дня"
    else:
        next_text = ", на наступні " + str(hours) + " години"
    message = "<b>Інформація по черзі №" +  str(q_num) + next_text + "</b>\n"
    for time_, energy_state in q_query:
        date_str = time_.strftime("%H:%M")
        if energy_state['text'] == 'ON':
            check_mark = " ✅ Присутнє"
        else:
            check_mark = " ❌ Відсутнє"
        message += "<i>" + date_str + "</i> -" + check_mark   + "\n"
    return message