from typing import Dict

from telebot import TeleBot

import config
from SQLighter import SQLighter
from chat import Chat

bot = TeleBot(config.token, threaded=False)
db = SQLighter(config.database_name)
chats: Dict[int, Chat] = {}  # private bot-to-user chats by chat ids


@bot.message_handler(commands=['add'])
def add(message):
    chat = message.chat
    if chat.type == 'group':
        db.add_group(chat.id, chat.title)


@bot.message_handler()
def suggest_resend(message):
    if message.chat.type != 'private':
        return

    chat_id = message.chat.id
    # save message
    chats[chat_id] = Chat(chat_id, message.text, bot, db)
    chats[chat_id].suggest_resend()


@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    chat = chats[call.message.chat.id]
    msg = chat.message_to_resend

    if call.data == "delete":
        chat.delete_sent_messages()
    else:
        res = chat.resend_by_mask(call.data, msg)
        chat.handle_resend_result(res)


if __name__ == '__main__':
    bot.polling(none_stop=True)
