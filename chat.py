from time import time
from typing import Dict

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import SQLighter
import config
from message_data import MessageData


class Chat:
    def __init__(self, id: int, bot: TeleBot, db: SQLighter):
        self.id = id
        self.messages_to_resend: Dict[int, MessageData] = {}
        self.bot = bot
        self.db: SQLighter = db
        self.sent_messages = {}

    def suggest_resend(self, msg_id):
        markup = self._create_wave_markup(msg_id)
        self.bot.send_message(self.id, 'Переслать сообщение _{}_ в диалоги:'.format(msg_id),
                              parse_mode='Markdown', reply_markup=markup)

    def _create_wave_markup(self, msg_id):
        masks = self.db.get_masks()
        btns = []
        for mask in masks:
            btns.append(InlineKeyboardButton(mask['name'], callback_data='{}|{}'.format(mask['name'], msg_id)))

        markup = InlineKeyboardMarkup()
        markup.add(*btns)

        return markup

    def resend_by_mask(self, mask, msg: MessageData):
        groups = self._filter_groups(mask)
        msgs = self.sent_messages.setdefault(msg.id, {})

        for group in groups:
            if group in msgs:
                continue

            res = None
            if msg.text is not None:
                res = self.bot.send_message(group, msg.text)
            elif msg.photo_id != 0:
                res = self.bot.send_photo(group, msg.photo_id)
            elif msg.doc_id != 0:
                res = self.bot.send_document(group, msg.doc_id)
            else:
                print('А где содержимое письма?!')

            msgs[group] = res.message_id

        return len(groups) > 0

    def handle_resend_result(self, msg_id, res):
        if res:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('Удалить', callback_data='delete|' + str(msg_id)))
            self.bot.send_message(self.id, 'Сообщение _{}_ отправлено!'.format(msg_id),
                                  parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(self.id, 'Диалоги, соответствующие запросу, не найдены =(')

    def _filter_groups(self, mask):
        groups = self.db.get_groups()
        chats = list()
        for group in groups:
            if group['title'].find(mask) != -1:
                chats.append(group['id'])

        return chats

    def delete_sent_messages(self, msg_id):
        msgs = self.sent_messages.get(msg_id)
        if not msgs:
            return

        for group in msgs:
            self.bot.delete_message(group, msgs[group])

        del self.sent_messages[msg_id]

    def harvest_dead_messages(self):
        msgs = self.messages_to_resend
        if len(msgs) <= config.max_msgs:
            return

        while len(msgs) > config.max_msgs:
            min_time = time()
            oldest_id = 0
            for msg_id in msgs:
                if msgs[msg_id].timestamp < min_time:
                    min_time = msgs[msg_id].timestamp
                    oldest_id = msg_id

            self.messages_to_resend.pop(oldest_id, None)
            self.sent_messages.pop(oldest_id, None)
