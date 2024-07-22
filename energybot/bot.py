import argparse
import telebot
from telebot import types
from energybot import config
from energybot.db.sqlite import SQLiteDB
from energybot.db.init_queue import INIT_QUERIES
from energybot.helpers import messages
from energybot.handlers.process import get_schedule_message, get_schedule_detail
from energybot.tasks.worker import run_worker
from energybot.tasks.sync import run_sync

parser = argparse.ArgumentParser()
parser.add_argument('--run', help='Enter usage command')
args = parser.parse_args()

ADMIN_CHAT_ID = config.ADMIN_CHAT_ID

bot = telebot.TeleBot(config.BOT_TOKEN)
db = SQLiteDB()

def main(args):
    if args.run == 'sync':
        run_sync()
    elif args.run == 'worker':
        run_worker()
    else:
        db.create_tables()
        bot.infinity_polling()
        db.close_connection()

def check_permissisons(chat_id, permission_requried):
    if permission_requried == 'admin':
        if str(chat_id) == ADMIN_CHAT_ID:
            return True
    raise Exception("User not have permission.")

def get_chat(message):
    chat = db.get_user_by_chat_id(message.chat.id)
    if not chat:
        chat = db.create_user(
            message.chat.id, message.chat.username,
            message.chat.first_name, message.chat.last_name
        )
    return chat

def new_sub(q, user):
    db.new_subscribe(q[0], user[0])

def add_queue_reply_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    queues = db.get_queues()
    buttons = []
    for queue in queues:
        callback_data = 'add_queue_' + str(queue[0])
        button = types.InlineKeyboardButton(queue[2], callback_data=callback_data)
        buttons.append(button)

    num_buttons = len(buttons)
    num_full_rows = num_buttons // 3

    # Add buttons in rows of three
    for i in range(num_full_rows):
        keyboard.add(buttons[i*3], buttons[i*3 + 1], buttons[i*3 + 2])
    
    # Add any remaining buttons (less than a full row)
    if num_buttons % 3 == 1:
        keyboard.add(buttons[num_buttons - 1])
    elif num_buttons % 3 == 2:
        keyboard.add(buttons[num_buttons - 2], buttons[num_buttons - 1])
    return keyboard

def remove_sub_reply_keyboard(user_id):
    keyboard = types.InlineKeyboardMarkup()
    subs = db.get_subs_by_user(user_id)
    buttons = []
    if not subs:
        return None

    for sub in subs :
        callback_data = 'remove_sub_' + str(sub[0])
        queue = db.get_queue(queue_id=sub[2])
        name = queue[2] + " " + messages.X_MARK
        button = types.InlineKeyboardButton(name, callback_data=callback_data)
        buttons.append(button)

    num_buttons = len(buttons)
    num_full_rows = num_buttons // 3

    # Add buttons in rows of three
    for i in range(num_full_rows):
        keyboard.add(buttons[i*3], buttons[i*3 + 1], buttons[i*3 + 2])
    
    # Add any remaining buttons (less than a full row)
    if num_buttons % 3 == 1:
        keyboard.add(buttons[num_buttons - 1])
    elif num_buttons % 3 == 2:
        keyboard.add(buttons[num_buttons - 2], buttons[num_buttons - 1])
    return keyboard

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    chat = get_chat(message)
    keyboard = add_queue_reply_keyboard()
    bot.send_message(message.chat.id, messages.WELCOME, reply_markup=keyboard)


@bot.message_handler(commands=['subs', 'remove'])
def send_subscribe(message):
    chat = get_chat(message)
    keyboard = remove_sub_reply_keyboard(str(chat[0]))
    if not keyboard:
        bot.send_message(message.chat.id, messages.NONE_SUBSCRIBE_TEXT)
    else:
        bot.send_message(message.chat.id, messages.UNSUBSCRIBE_TEXT, reply_markup=keyboard)

@bot.message_handler(commands=['update'])
def send_update(message):
    check_permissisons(message.chat.id, 'admin')
    chat = get_chat(message)
    for query in INIT_QUERIES:
        db.run_query(query)
    bot.reply_to(message, messages.ADMIN_UPDATE)

@bot.message_handler(commands=['sql'])
def send_sql(message):
    check_permissisons(message.chat.id, 'admin')
    chat = get_chat(message)
    sql_text = message.text[4:]
    try:
        info = db.run_query(sql_text)
        result = "<code>" + str(info) + "</code>\n"
        msg = messages.ADMIN_RUN
    except Exception as e:
        result = "<code>" + str(e) + "</code>\n"
        msg = messages.ADMIN_FAIL
    bot.reply_to(message, result + msg, parse_mode='html')


@bot.message_handler(commands=['show'])
def send_schedule(message):
    chat = get_chat(message)
    user_id = str(chat[0])
    subs = db.get_subs_by_user(user_id)
    for sub in subs:
        sub_id, _, sub_q_name = sub
        msg = get_schedule_message(str(sub_q_name))
        bot.reply_to(message, msg, parse_mode='html')

@bot.message_handler(commands=['detail'])
def send_schedule_detail(message):
    chat = get_chat(message)
    user_id = str(chat[0])
    subs = db.get_subs_by_user(user_id)
    for sub in subs:
        sub_id, _, sub_q_name = sub
        msg = get_schedule_detail(str(sub_q_name))
        bot.reply_to(message, msg, parse_mode='html')

@bot.message_handler(commands=['all'])
def send_schedule_all(message):
    chat = get_chat(message)
    user_id = str(chat[0])
    subs = db.get_subs_by_user(user_id)
    for sub in subs:
        sub_id, _, sub_q_name = sub
        msg = get_schedule_message(str(sub_q_name), hours=24)
        bot.reply_to(message, msg, parse_mode='html')

@bot.message_handler(commands=['detailall'])
def send_schedule_detailall(message):
    chat = get_chat(message)
    user_id = str(chat[0])
    subs = db.get_subs_by_user(user_id)
    for sub in subs:
        sub_id, _, sub_q_name = sub
        msg = get_schedule_detail(str(sub_q_name), hours=24)
        bot.reply_to(message, msg, parse_mode='html')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith('add_queue_'):
        queue_id = call.data.split('_')[2]
        queue = db.get_queue(queue_id)
        chat = get_chat(call.message)
        if not chat:
            print("Chat not found by call", call)
        sub = db.get_sub_by_user_q(chat[0], queue[0])
        if sub:
            reply_text = messages.ALREDY_SUBSCRIBE_TEXT + '. ' + messages.SUB_COMMAND_TEXT
            bot.send_message(call.message.chat.id, reply_text)
        else:
            new_sub(queue, chat)
            reply_text = messages.SUBSCRIBE_TEXT + ' ' + queue[2] + '. ' + messages.SUB_COMMAND_TEXT 
            bot.send_message(call.message.chat.id, reply_text)

    elif call.data.startswith('remove_sub_'):
        sub_id = call.data.split('_')[2]
        sub = db.get_sub(sub_id)
        if sub:
            queue = db.get_queue(sub[2])
            db.delete_sub(sub_id)
            reply_text = messages.UNSUBSCRIBED + ' ' + queue[2] + '.'
        else:
            reply_text = messages.NOT_UNSUBSCRIBED
        bot.send_message(call.message.chat.id, reply_text)


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    chat = get_chat(message)
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    main(args)
    