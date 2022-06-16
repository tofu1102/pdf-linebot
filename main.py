from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, StickerMessage, StickerSendMessage,
)
import os
import io
import psycopg2
import datetime
from PIL import Image

from pdf2url import *
from png2pdf import *
from upload2DataBase import *


app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

FQDN = "https://pdf-linebot.herokuapp.com/"

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

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    img = message_content.content


    P = "static/"+message_id+".jpg"
    mode = 'w+b'
    with open(P,mode) as f:
        f.write(img)

        #DBに登録
        insert_img(event.source.user_id,psycopg2.Binary(f.read()))

    if not os.path.exists(P):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Error"))

    pdfFileName = "pdfFileName"

    pdfPath = png2pdf(pdfFileName,P)

    image_url=uploadFile(pdfPath)

    #line_bot_api.reply_message(
    #    event.reply_token,
    #    ImageSendMessage(
    #        original_content_url = FQDN + "static/" + message_id + ".jpg",
    #        preview_image_url = FQDN + "static/" + message_id + ".jpg"
    #    )
    #)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=image_url))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):


    img_data = select_img()
    f = open("static/" + event.message.text + '.png', 'wb')
    f.write(img_data["img"])
    f.close()

    line_bot_api.reply_message(
       event.reply_token,
       [TextSendMessage(text=event.source.user_id),
       ImageSendMessage(
               original_content_url = FQDN + "static/" + event.message.text + '.png',
               preview_image_url = FQDN + "static/" + event.message.text + '.png'
           )])


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="このメッセージがすぐに帰ってきたら起動成功です。"))





if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
