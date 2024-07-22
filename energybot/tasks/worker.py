# Process notifications
from datetime import datetime
import telebot
from energybot.db.sqlite import SQLiteDB
import energybot.helpers.messages as messages 
from energybot import config



notification_timeout = config.TIMEOUT
notification_to_on  = config.TURN_ON_NOTIFY

queues = {}

bot = telebot.TeleBot(config.BOT_TOKEN)
db = SQLiteDB()

def is_need_to_notify(date, ):
    time_now = datetime.now()
    date_format = '%Y-%m-%d %H:%M:%S'

    # Convert the date string to a datetime object
    datetime_object = datetime.strptime(date, date_format)
    time_difference = datetime_object - time_now 

    # Convert time difference to minutes
    minutes_difference = time_difference.total_seconds() / 60

    # Print the difference in minutes
    print("Difference in minutes:", minutes_difference)

    if int(notification_timeout) + 1 > minutes_difference > 0 :
        print("Need to notify:")
        return int(minutes_difference + 1)

    return False

def process_notify(user_id, q_name, is_turn_on, notify_minutes):
    if is_turn_on == 0:
        mark = messages.X_MARK
        after_text = messages.NOTIFICATION_TURN_OFF
    else:
        mark = messages.CHECK_MARK
        after_text = messages.NOTIFICATION_TURN_ON
    message = mark +  q_name + " " + messages.NOTIFICATION_BEFORE_TEXT + " " +\
         str(notify_minutes) + " " + after_text
          
    chat = db.get_user_by_id(user_id)
    bot.send_message(chat[1], message)

def chnages_notify(user_id, ):
    message = messages.CHANGES_POE
    chat = db.get_user_by_id(user_id)
    bot.send_message(chat[1], message)

def run_worker():
    subs = db.get_subs() 
    if not subs:
        print("Subscribers not found.")

    is_updated = False
    updated = db.get_global_info(name='is_updated')
    if updated[2] == "Updated":
        is_updated = True

    for sub in subs:
        user_id, q_id = sub[1], sub[2]

        if q_id not in queues:
            q_info = db.get_queue(q_id)
            queues[q_id] = q_info
        q = queues[q_id]
        q_name = q[2]
        current_state = q[4]
        next_change_mark_is_on = q[6]
        next_change_time = q[5]
        if current_state  ==  next_change_mark_is_on:
            # nothing changing
            continue
        notify_minutes = is_need_to_notify(next_change_time, )
        if notify_minutes:
            if notification_to_on or next_change_mark_is_on == 0:
                print("Processing notification...")
                process_notify(user_id, q_name, next_change_mark_is_on, notify_minutes)
            else:
                print("Not notify, ON:", notification_to_on, "next:", next_change_mark_is_on)
        
        if is_updated:
            chnages_notify(user_id, )
        
    db.close_connection()

if __name__ == "__main__":
    run_worker()