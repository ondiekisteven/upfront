from flask import Flask, request
from whatsapp import ChatApi, get_phone

app = Flask(__name__)


@app.route('/', methods=['POST'])
def chat_api():
    json = request.json
    bot = ChatApi(json)
    # allowed_chats = ['254745021668@c.us']
    allowed_chats = ['254745021668@c.us', '254705126329@c.us']
    messages = bot.dict_message
    for message in messages:
        if message['chatId'] in allowed_chats and not message['fromMe']:
            print(f'Message from {request.json["messages"][0]["chatName"]}: {request.json["messages"][0]["body"]}')
            return bot.processing()
        else:
            return ' '


if __name__ == '__main__':
    app.run()
