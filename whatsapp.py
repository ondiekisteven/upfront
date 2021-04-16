import os

import requests
from json import dumps
from main import main
from db import get_instance


def get_phone(message):
    return message['author'].replace('@c.us', '')


def remove_first_word(text):
    words = text.split(' ')
    return " ".join(words[1:])


class ChatApi:
    def __init__(self, json):
        self.json = json
        self.dict_message = json['messages']
        self.APIUrl = os.environ.get('API_URL')
        self.token = os.environ.get('API_TOKEN')

    def send_requests(self, method, data):
        url = f'{self.APIUrl}{method}?token={self.token}'
        headers = {'content-type': 'application/json'}
        answer = requests.post(url, data=dumps(data), headers=headers)
        y = answer.text
        return y

    def send_message(self, chat_id, text):
        data = {
            'chatId': chat_id,
            'body': text
        }
        answer = self.send_requests('sendMessage', data)
        return answer

    def processing(self):
        if self.dict_message:
            for message in self.dict_message:
                text = message['body']
                phone = get_phone(message)
                # name = message['author']

                if not get_instance(phone):  # if user is using for first time, start with this message
                    self.send_message(message['chatId'], 'Hello, I am your online assistant. \nWhat can i do for you..')
                reply = main(phone, text)
                for txt in reply['body']:
                    self.send_message(message['chatId'], txt)
                return reply
