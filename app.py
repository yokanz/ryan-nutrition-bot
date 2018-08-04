# -*- coding: utf-8 -*-
import os, re, json
from datetime import datetime, date, timedelta
from flask import Flask, request, abort
import requests
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
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
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def print_help(event):
    help = """Usage():
    @bot help
    @bot bmr
    @bot food=<food keyword>
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
        text="""Please input your info:
        Weight (mandatory) and Fat % (Optional)
        e.g. bw=56,fat=24.6 or bw=56
        """
        line_bot_api.reply_message(event.reply_token, TextMessage(text=text))
        return
    
    if 'bw=' in text.lower() and ',' not in text.lower():
        # validate input
        weight_input = text.lower().split('=')[1]
        try:
            body_weight = float(weight_input)
            simple_bmr = int(body_weight) * 22
            line_bot_api.reply_message(event.reply_token, TextMessage(text='Your simple BMR is {0}'.format(simple_bmr)))
        except ValueError:
            print("Input is not numeric!!")
            line_bot_api.reply_message(event.reply_token, TextMessage(text='Input is not numeric!!'))
        
        return
        
    if 'bw=' in text.lower() and ',fat=' in text.lower():
        # validate order and input
        info_input = text.lower().split(',')
        body_weight = int(float(info_input[0].split('=')[1]))
        fat_percentage = float(info_input[1].split('=')[1])/100
        print('body weight: {0}, fat ratio: {1:.2f}'.format(body_weight,fat_percentage))

        cunningham_bmr = 500 + (22 * ((1-fat_percentage) * body_weight))
        line_bot_api.reply_message(event.reply_token, TextMessage(text='Your Cunningham BMR is {0:.2f}'.format(cunningham_bmr)))
        return


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, port=5000)
