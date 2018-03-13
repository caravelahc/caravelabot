import logging

from functools import wraps
from socket import socket

import dataset

from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton

from .config import TOKEN, DB_PATH
from .strings import (ACCESS_DENIED, ACCESS_GRANTED,
                      MALFUNCTION, REQUIRE_FORWARD, GREETING)


def creator_only(func):
    @wraps(func)
    def new_func(bot, update, *args, **kwargs):
        if update.message.from_user.id == 61407387:
            return func(bot, update, *args, **kwargs)
        else:
            update.message.reply_text(ACCESS_DENIED, parse_mode='Markdown')

    return new_func


def admin_only(func):
    @wraps(func)
    def new_func(bot, update, *args, **kwargs):
        db = dataset.connect(f'sqlite:///{DB_PATH}')
        table = db.get_table('admins', primary_id='id')
        user = table.find_one(id=update.message.from_user.id)
        if not user:
            update.message.reply_text(ACCESS_DENIED, parse_mode='Markdown')
        else:
            return func(bot, update, *args, **kwargs)

    return new_func


def start(bot, update):
    button = KeyboardButton('Unlock!')
    keyboard = ReplyKeyboardMarkup([[button]])

    update.message.reply_text(GREETING, reply_markup=keyboard)


@admin_only
def unlock(bot, update):
    try:
        with socket() as s:
            s.connect(('10.0.0.100', 8000))
            message = 'unlock door'
            s.send(message.encode())
            response = s.recv(32).decode()
        assert response == message
    except Exception:
        update.message.reply_text(MALFUNCTION)
    else:
        db = dataset.connect(f'sqlite:///{DB_PATH}')
        table = db.get_table('access_log', primary_id='datetime',
                             primary_type=db.types.datetime)
        user = update.message.from_user
        table.insert(dict(id=user.id, datetime=update.message.date))
        update.message.reply_text(ACCESS_GRANTED, disable_notification=True)


def text_handler(bot, update):
    if update.message.text == 'Unlock!':
        unlock(bot, update)


def change_permission(bot, update, operation):
    user = update.message.reply_to_message.forward_from
    if user is None:
        update.message.reply_text(REQUIRE_FORWARD)
        return

    db = dataset.connect(f'sqlite:///{DB_PATH}')
    table = db.get_table('admins', primary_id='id')

    if operation == 'allow':
        full_name = f'{user.first_name} {user.last_name}'
        data = dict(id=user.id, user_name=user.username, full_name=full_name)
        table.upsert(data, ['id'])
        response = 'Admin added'

    elif operation == 'disallow':
        table.delete(id=user.id)
        response = 'Admin removed'

    else:
        raise ValueError('Invalid operation')

    update.message.reply_text(response)


@creator_only
def allow(bot, update):
    change_permission(bot, update, 'allow')


@creator_only
def disallow(bot, update):
    change_permission(bot, update, 'disallow')


def error_handler(bot, update, error):
    update.message.reply_text(error)


def main():
    logging.basicConfig()
    updater = Updater(TOKEN)
    updater.dispatcher.add_error_handler(error_handler)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('unlock', unlock))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))
    updater.dispatcher.add_handler(CommandHandler('allow', allow))
    updater.dispatcher.add_handler(CommandHandler('disallow', disallow))
    updater.start_polling()


if __name__ == '__main__':
    main()
