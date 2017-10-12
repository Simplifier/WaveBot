from typing import List

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import SQLighter


class Chat:
    def __init__(self, id: int, message_to_resend: str, bot: TeleBot, db: SQLighter):
        self.id = id
        self.message_to_resend = message_to_resend
        self.bot = bot
        self.db: SQLighter = db
        self.sent_messages: List = None

    def suggest_resend(self):
        markup = self._create_wave_markup()
        self.bot.send_message(self.id, 'Переслать сообщение в диалоги:', parse_mode='Markdown', reply_markup=markup)

    def _create_wave_markup(self):
        masks = self.db.get_masks()
        btns = []
        for mask in masks:
            btns.append(InlineKeyboardButton(mask['name'], callback_data=mask['name']))

        markup = InlineKeyboardMarkup()
        markup.add(*btns)

        return markup

    def resend_by_mask(self, mask, msg):
        groups = self._filter_groups(mask)
        msgs = list()

        for group in groups:
            res = self.bot.send_message(group, msg)
            msgs.append({'chat': group, 'msg': res.message_id})

        return msgs

    def handle_resend_result(self, res):
        self.sent_messages = res

        if len(res):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('Удалить', callback_data='delete'))
            self.bot.send_message(self.id, 'Сообщение отправлено!', parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(self.id, 'Диалоги, соответствующие запросу, не найдены =(')

    def _filter_groups(self, mask):
        groups = self.db.get_groups()
        chats = list()
        for group in groups:
            if group['title'].find(mask) != -1:
                chats.append(group['id'])

        return chats

    def delete_sent_messages(self):
        for msg in self.sent_messages:
            self.bot.delete_message(msg['chat'], msg['msg'])
