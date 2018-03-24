from time import time

from telebot import TeleBot
from telebot.types import Message


class MessageData:
    def __init__(self, message: Message):
        self.timestamp = time()
        self.type = message.content_type
        self.id = message.message_id

        self.caption = message.caption
        self.text = message.text
        if self.type == 'document':
            self.doc_id: int = message.document.file_id
        if self.type == 'photo':
            self.photo_id: int = message.photo[0].file_id
        if self.type == 'video':
            self.video_id: int = message.video.file_id

    def send(self, bot: TeleBot, group):
        msg: Message
        if self.type == 'text':
            msg = bot.send_message(group, self.text)
        elif self.type == 'photo':
            msg = bot.send_photo(group, self.photo_id, self.caption)
        elif self.type == 'video':
            msg = bot.send_video(group, self.video_id, caption=self.caption)
        elif self.type == 'document':
            msg = bot.send_document(group, self.doc_id, caption=self.caption)
        else:
            print('А где содержимое письма?!')

        return msg
