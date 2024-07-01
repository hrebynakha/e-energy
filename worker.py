# Process notifications
import os
import telebot
from datetime import datetime
from db import SQLiteDB

import messages 

db = SQLiteDB()
subs = db.get_subs() 


# move to DB ?
notification_timeout = 30
notification_to_on = True
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

queues = {}


def is_need_to_notify(date, ):
    time_now = datetime.now()
    date_format = '%m/%d/%Y %H:%M:%S'

    # Convert the date string to a datetime object
    datetime_object = datetime.strptime(date, date_format)
    time_difference = datetime_object - time_now 

    # Convert time difference to minutes
    minutes_difference = time_difference.total_seconds() / 60

    # Print the difference in minutes
    print("Difference in minutes:", minutes_difference)

    if notification_timeout + 1 > minutes_difference > 0 :
        print("Need to notify:")
        return True

    return False


def process_notify(user_id, queue):
    if queue[4] == 1:
        mark = messages.X_MARK
        after_text = messages.NOTIFICATION_TURN_OFF
    else:
        mark = messages.CHECK_MARK
        after_text = messages.NOTIFICATION_TURN_ON
    message = mark +  queue[2] + " " + messages.NOTIFICATION_BEFORE_TEXT + " " +\
         str(notification_timeout) + " " + after_text
          
    chat = db.get_user_by_id(user_id)
    bot.send_message(chat[1], message)

    


for sub in subs:
    print("Processing sub", sub)
    if sub[2] not in queues:
        q_info = db.get_queue(sub[2])
        queues[sub[2]] = q_info
    q = queues[sub[2]]
    if is_need_to_notify(q[3],):
        if notification_to_on == True or q[4] == 1:
            print("Processing notification...")
            process_notify(sub[1], q)
    


print(queues)
db.close_connection()


