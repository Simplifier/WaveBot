from time import time
from typing import Dict

from telebot import TeleBot
from telebot.types import Message

import config
from message_data import MessageData
from SQLighter import SQLighter
from chat import Chat

bot = TeleBot(config.token, threaded=False)
db = SQLighter(config.database_name)
chats: Dict[int, Chat] = {}  # private bot-to-user chats by chat ids


@bot.message_handler(commands=['add'])
def add(message):
    chat = message.chat
    if chat.type in ('group', 'supergroup'):
        db.add_group(chat.id, chat.title, chat.type)


@bot.message_handler(func=lambda m: True, content_types=['text', 'document', 'photo'])
def suggest_resend(message: Message) -> None:
    if message.chat.type != 'private':
        return

    admins = bot.get_chat_administrators(config.admin_chat)
    user_id = message.from_user.id
    is_user_admin = any(admin.user.id == user_id for admin in admins)
    if not is_user_admin:
        return

    chat_id = message.chat.id

    # save message
    msg: MessageData = MessageData(message.message_id, time(), message.text)
    if message.content_type == 'photo':
        msg.photo_id = message.photo[0].file_id
    elif message.content_type == 'document':
        msg.doc_id = message.document.file_id

    chat = chats.setdefault(chat_id, Chat(chat_id, bot, db))
    chat.messages_to_resend[msg.id] = msg
    chat.suggest_resend(msg.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    chat = chats.get(call.message.chat.id)
    if not chat:
        return

    command, msg_id = call.data.split('|')
    msg_id = int(msg_id)

    if command == "delete":
        chat.delete_sent_messages(msg_id)
    else:
        msg = chat.messages_to_resend.get(msg_id)
        if not msg:
            return

        success = chat.resend_by_mask(command, msg)
        chat.handle_resend_result(msg.id, success)

    chat.harvest_dead_messages()


if __name__ == '__main__':
    bot.polling(none_stop=True)
