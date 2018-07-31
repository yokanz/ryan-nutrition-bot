# -*- coding: utf-8 -*-
import os, re, json
from datetime import datetime, date, timedelta
from flask import Flask, request, abort
import requests
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ConfirmTemplate ,TemplateSendMessage
)

app = Flask(__name__)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello Translator-Bot</h1>
    <p>It is currently {time}.</p>
    <img src="http://loremflickr.com/600/400">
    """.format(time=the_time)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def print_help(event):
    help = """Usage():
    @bot help
    @bot bmr
    @bot tdee
    """
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help))

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text.lower() == '@bot help':
        print_help(event)
        return

    if text.lower() == '@bot bmr':
        # get weight
        line_bot_api.reply_message(event.reply_token, TextMessage(text='Please input your weight (kg)'))

        # get % fat if available

        # unknown % fat, bmr = body weight * 22

        # valid % fat, bmr = 500 + (22 * lean body mass) , lean body mass = (1 - %fat) * body weight

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
    

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
