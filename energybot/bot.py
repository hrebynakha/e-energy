"""Bot file for running bot"""

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=no-member

import os

import django
import telebot  # pylint: disable=import-error
from telebot import types  # pylint: disable=import-error
from energybot import config
from energybot.helpers.logger import logger
from energybot.helpers import messages
from energybot.handlers.process import (
    get_schedule_detail,
    get_schedule_short,
)

# from energybot.tasks.worker import run_worker
# from energybot.tasks.sync import run_sync

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "energybot.web.energyweb.settings")
django.setup()

from energybot.web.core.models import ChatUser, Subscription, Queue


ADMIN_CHAT_ID = config.ADMIN_CHAT_ID

bot = telebot.TeleBot(config.BOT_TOKEN)


def check_permissions(chat_id, permission_required):
    """Check permissions for user"""
    if permission_required == "admin":
        if str(chat_id) == ADMIN_CHAT_ID:
            return True
        logger.warning("User %s not have permission %s", chat_id, permission_required)
    raise ValueError("User not have permission.")


def get_chat_user(message):
    """Get or create ChatUser from Telegram message"""
    user, created = ChatUser.objects.get_or_create(
        chat_id=message.chat.id,
        defaults={
            "username": message.chat.username,
            "first_name": message.chat.first_name,
            "last_name": message.chat.last_name,
        },
    )

    if not created:
        updated = False
        if user.username != message.chat.username:
            user.username = message.chat.username
            updated = True
        if user.first_name != message.chat.first_name:
            user.first_name = message.chat.first_name
            updated = True
        if user.last_name != message.chat.last_name:
            user.last_name = message.chat.last_name
            updated = True
        if updated:
            user.save()
    return user


def new_sub(queue, chat_user):
    """Add new subscription"""
    Subscription.objects.create(
        queue_id=queue.id,
        user_id=chat_user.id,
    )


def add_queue_reply_keyboard(user_id):
    """Add queue reply keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    queues = Queue.objects.all()
    subs = Subscription.objects.filter(user_id=user_id)
    buttons = []
    for queue in queues:
        callback_data = "add_queue_" + str(queue.id)
        name = (
            queue.name + " " + messages.CHECK_MARK
            if queue.id in subs.values_list("queue_id", flat=True)
            else queue.name
        )
        button = types.InlineKeyboardButton(name, callback_data=callback_data)
        buttons.append(button)

    num_buttons = len(buttons)
    num_full_rows = num_buttons // 3

    # Add buttons in rows of three
    for i in range(num_full_rows):
        keyboard.add(buttons[i * 3], buttons[i * 3 + 1], buttons[i * 3 + 2])

    # Add any remaining buttons (less than a full row)
    if num_buttons % 3 == 1:
        keyboard.add(buttons[num_buttons - 1])
    elif num_buttons % 3 == 2:
        keyboard.add(buttons[num_buttons - 2], buttons[num_buttons - 1])
    return keyboard


def remove_sub_reply_keyboard(user_id):
    """Remove subscription reply keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    subs = Subscription.objects.filter(user_id=user_id)
    buttons = []
    if not subs:
        return None

    for sub in subs:
        callback_data = "remove_sub_" + str(sub.id)
        queue = Queue.objects.get(id=sub.queue_id)
        name = queue.name + " " + messages.X_MARK
        button = types.InlineKeyboardButton(name, callback_data=callback_data)
        buttons.append(button)

    num_buttons = len(buttons)
    num_full_rows = num_buttons // 3

    # Add buttons in rows of three
    for i in range(num_full_rows):
        keyboard.add(buttons[i * 3], buttons[i * 3 + 1], buttons[i * 3 + 2])

    # Add any remaining buttons (less than a full row)
    if num_buttons % 3 == 1:
        keyboard.add(buttons[num_buttons - 1])
    elif num_buttons % 3 == 2:
        keyboard.add(buttons[num_buttons - 2], buttons[num_buttons - 1])
    return keyboard


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    """Send welcome message"""
    chat_user = get_chat_user(message)
    keyboard = add_queue_reply_keyboard(chat_user.id)
    logger.info(
        "Send welcome message to user %s %s",
        chat_user.chat_id,
        chat_user.username,
    )
    bot.send_message(message.chat.id, messages.WELCOME, reply_markup=keyboard)


@bot.message_handler(commands=["subs", "remove"])
def send_subscribe(message):
    """Send subscribe message"""
    chat_user = get_chat_user(message)
    keyboard = remove_sub_reply_keyboard(chat_user.id)
    if not keyboard:
        logger.info(
            "Send message about unsubscribe text to user %s %s",
            chat_user.chat_id,
            chat_user.username,
        )
        bot.send_message(chat_user.chat_id, messages.NONE_SUBSCRIBE_TEXT)
    else:
        logger.info(
            "Send message about unsubscribe to user %s %s",
            chat_user.chat_id,
            chat_user.username,
        )
        bot.send_message(
            chat_user.chat_id, messages.UNSUBSCRIBE_TEXT, reply_markup=keyboard
        )


@bot.message_handler(commands=["show"])
def send_schedule(message):
    """Send schedule message"""
    chat_user = get_chat_user(message)
    subs = Subscription.objects.filter(user_id=chat_user.id)
    for sub in subs:
        try:
            msg = get_schedule_short(sub.queue_id)
            bot.reply_to(message, msg, parse_mode="html")
        except Exception as e:
            logger.error("Error getting schedule short message: %s", e)
            logger.info(
                "Send error message about schedule short to user %s %s",
                chat_user.chat_id,
                chat_user.username,
            )
            bot.reply_to(message, messages.ERROR, parse_mode="html")


@bot.message_handler(commands=["all"])
def send_schedule_all(message):
    """Send schedule all message"""
    chat_user = get_chat_user(message)
    subs = Subscription.objects.filter(user_id=chat_user.id)
    for sub in subs:
        try:
            msg = get_schedule_short(sub.queue_id, hours=24)
            bot.reply_to(message, msg, parse_mode="html")
        except Exception as e:
            logger.error("Error getting schedule short all message: %s", e)
            logger.info(
                "Send error message about schedule short all to user %s %s",
                chat_user.chat_id,
                chat_user.username,
            )
            bot.reply_to(message, messages.ERROR, parse_mode="html")


@bot.message_handler(commands=["detail"])
def send_schedule_detail(message):
    """Send schedule detail message"""
    chat_user = get_chat_user(message)
    subs = Subscription.objects.filter(user_id=chat_user.id)
    for sub in subs:
        try:
            msg = get_schedule_detail(sub.queue_id)
            bot.reply_to(message, msg, parse_mode="html")
        except Exception as e:
            logger.error("Error getting schedule detail message: %s", e)
            logger.info(
                "Send error message about schedule detail to user %s %s",
                chat_user.chat_id,
                chat_user.username,
            )
            bot.reply_to(message, messages.ERROR, parse_mode="html")


@bot.message_handler(commands=["detailall"])
def send_schedule_detail_all(message):
    """Send schedule detail all message"""
    chat_user = get_chat_user(message)
    subs = Subscription.objects.filter(user_id=chat_user.id)
    for sub in subs:
        try:
            msg = get_schedule_detail(sub.queue_id, hours=24)
            bot.reply_to(message, msg, parse_mode="html")
        except Exception as e:
            logger.error("Error getting schedule detail all message: %s", e)
            logger.info(
                "Send error message about schedule detail all to user %s %s",
                chat_user.chat_id,
                chat_user.username,
            )
            bot.reply_to(message, messages.ERROR, parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Callback handler"""
    chat_user = get_chat_user(call.message)
    if not chat_user:
        logger.error("Chat user %s not found by call %s", chat_user, call)
        return
    if call.data.startswith("add_queue_"):
        queue_id = call.data.split("_")[2]
        queue = Queue.objects.get(id=queue_id)
        sub = Subscription.objects.filter(user_id=chat_user.id, queue_id=queue_id)
        if sub:
            reply_text = (
                messages.ALREADY_SUBSCRIBE_TEXT + ". " + messages.SUB_COMMAND_TEXT
            )
            bot.send_message(chat_user.chat_id, reply_text)
        else:
            new_sub(queue, chat_user)
            reply_text = (
                messages.SUBSCRIBE_TEXT
                + " "
                + queue.name
                + ". "
                + messages.SUB_COMMAND_TEXT
            )
            logger.info(
                "Send message about subscription to user %s %s",
                chat_user.chat_id,
                chat_user.username,
            )
            bot.send_message(chat_user.chat_id, reply_text)

    elif call.data.startswith("remove_sub_"):
        sub_id = call.data.split("_")[2]
        sub = Subscription.objects.filter(id=sub_id).first()
        if sub:
            queue = Queue.objects.get(id=sub.queue_id)
            sub.delete()
            reply_text = messages.UNSUBSCRIBED + " " + queue.name + "."
        else:
            reply_text = messages.NOT_UNSUBSCRIBED
        logger.info(
            "Send message about un subscription to user %s %s",
            chat_user.chat_id,
            chat_user.username,
        )
        bot.send_message(chat_user.chat_id, reply_text)


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    """Echo all message"""
    get_chat_user(message)
    bot.reply_to(message, message.text)
