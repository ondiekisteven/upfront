from flask import Flask, request
from json import dumps
from whatsapp import ChatApi, get_phone
from send_to_queue import to_queue


app = Flask(__name__)


@app.route('/', methods=['POST'])
def chat_api():
    json = request.json
    bot = ChatApi(json)
    # allowed_chats = ['254745021668@c.us']
    allowed_chats = ['254745021668@c.us', '254705126329@c.us', '254726422225@c.us']
    messages = bot.dict_message
    for message in messages:
        # if not message['fromMe']:
        if message['chatId'] in allowed_chats and not message['fromMe']:
            print(f'Message from {request.json["messages"][0]["chatName"]}: {request.json["messages"][0]["body"]}')
            # return bot.processing()
            ##################################################
            return to_queue(dumps(message))
            ##################################################
        else:
            return ' '


if __name__ == '__main__':
    app.run()
