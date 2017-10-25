from functools import wraps
from telegram.ext import Updater, CommandHandler
from socket import socket
import logging
from . import config


def creator_only(func):
    @wraps(func)
    def new_func(bot, update, *args, **kwargs):
        if update.message.from_user.id == 61407387:
            return func(bot, update, *args, **kwargs)
        else:
            text = ('`Username is not in the sudoers file. '
                    'This incident will be reported`')
            update.message.reply_text(text, parse_mode='Markdown')

    return new_func


def admin_only(func):
    @wraps(func)
    def new_func(bot, update, *args, **kwargs):
        user_id = update.message.from_user.id

        if user_id not in config.load()['admins']:
            text = ('`Username is not in the sudoers file. '
                    'This incident will be reported`')
            update.message.reply_text(text, parse_mode='Markdown')
        else:
            return func(bot, update, *args, **kwargs)

    return new_func


def start(bot, update):
    chat_id = update['message']['chat']['id']
    text = ('Hello! Use /unlock to unlock the hacker space door.\n'
            'To promote a user, forward me a message from him and '
            'reply to it with /allow or /disallow')
    bot.send_message(chat_id, text)


@admin_only
def unlock(bot, update):
    update.message.reply_text('Unlocking door!')
    with socket() as s:
        s.connect(('10.0.0.100', 8000))
        s.send('unlock door'.encode())


@creator_only
def allow(bot, update):
    try:
        user_id = update.message.reply_to_message.forward_from.id
    except AttributeError:
        update.message.reply_text('You must forward a message to me and '
                                  'reply to it with this command!')
        return

    c = config.load()

    admins = set(c['admins'])
    admins.add(user_id)
    c['admins'] = list(admins)

    config.save(c)

    update.message.reply_text('Admin added')


@creator_only
def disallow(bot, update):
    try:
        user_id = update.message.reply_to_message.forward_from.id
    except AttributeError:
        update.message.reply_text('You must forward a message to me and '
                                  'reply to it with this command!')
        return

    c = config.load()

    admins = set(c['admins'])
    admins.remove(user_id)
    c['admins'] = list(admins)

    config.save(c)

    update.message.reply_text('Admin removed')


def error_handler(bot, update, error):
    update.message.reply_text(error)


def main():
    logging.basicConfig()
    updater = Updater(config.load()['token'])
    updater.dispatcher.add_error_handler(error_handler)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('unlock', unlock))
    updater.dispatcher.add_handler(CommandHandler('allow', allow))
    updater.dispatcher.add_handler(CommandHandler('disallow', disallow))
    updater.start_polling()


if __name__ == '__main__':
    main()
