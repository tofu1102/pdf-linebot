from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, StickerMessage, StickerSendMessage, CarouselTemplate, CarouselColumn, TemplateSendMessage
)
import os
import io
import re
import psycopg2
import psycopg2.extras
import datetime
from PIL import Image

from pdf2url import *
from png2pdf import *
from upload2DataBase import *


app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

DATABASE_URL = os.environ.get('DATABASE_URL')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

FQDN = "https://pdf-linebot.herokuapp.com/"

#pdfの最大ページ数
PAGE_LIMIT = 5

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

    Done = False
    dt = datetime.datetime.now()

    #DBに登録
    conn= psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    #ファイルを開いてデータを取得
    pic = open(P, 'rb').read()
    cur.execute(f"INSERT INTO Img (date,user_id,done,img) VALUES ('{dt.year}-{dt.month}-{dt.day} {dt.hour}:{dt.minute}:{dt.second}', '{event.source.user_id}',{Done}, {psycopg2.Binary(pic)})")
    conn.commit()
    cur.close()

    if not os.path.exists(P):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Error"))

    #pdfFileName = "pdfFileName"

    #pdfPath = png2pdf(pdfFileName,P)

    #image_url=uploadFile(pdfPath)

    #line_bot_api.reply_message(
    #    event.reply_token,
    #    ImageSendMessage(
    #        original_content_url = FQDN + "static/" + message_id + ".jpg",
    #        preview_image_url = FQDN + "static/" + message_id + ".jpg"
    #    )
    #)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="保存完了"))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if not (event.message.text.startswith("[[") and event.message.text.endswith("]]")):

        conn= psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT img, id FROM Img WHERE user_id = '{event.source.user_id}' ORDER BY date DESC OFFSET 0 LIMIT {PAGE_LIMIT}")
        #byteaデータの取り出し
        row = cur.fetchall()
        filePathList = []


        for i in row:
            pic = i['img']
            #ファイルに内容を書き込み
            f = open("static/" + event.source.user_id + "-" + str(i["id"]) + '.jpg', 'wb')
            f.write(pic)
            f.close()
            filePathList.append("static/" + event.source.user_id + "-" + str(i["id"]) + '.jpg')
        cur.close()
        conn.close()

        if len(row) == 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="画像を送信してください。"))
            return 0
        else:
            FileNum = len(row)

        notes = []

        for i in range(FileNum):
            notes.append(CarouselColumn(thumbnail_image_url=FQDN + filePathList[FileNum-i-1],
                                title=f"{FileNum-i}ページのpdfを作成",
                                text=f"この画像から右の{FileNum-i}枚を1つのpdfにまとめます。",
                                actions=[{"type": "message","label": "作成する","text": f"[[{event.message.text}/{FileNum-i}]]"}]))

        messages = [
            TextSendMessage(text=f"{event.message.text}.pdfを作成します。"),
            TemplateSendMessage(
                alt_text='template',
                template=CarouselTemplate(columns=notes),
                )
            ]

        line_bot_api.reply_message(event.reply_token, messages=messages)

    else:
        pdfFileName,page = event.message.text[2:-2].split("/")
        #GoogleDriveにアップロード
        pdfFileName = re.sub(r'[\\/:*?"<>|\.]+','',pdfFileName)
        if pdfFileName == "":
            line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text="""これらの文字はファイル名に含めることができません。\/:*?"<>|."""),]
            )

            return 0

        #ファイルのリストを取得
        conn= psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT img, id FROM Img WHERE user_id = '{event.source.user_id}' ORDER BY date DESC OFFSET 0 LIMIT {page}")
        #byteaデータの取り出し
        row = cur.fetchall()
        filePathList = []

        for i in row:

            filePathList.append("static/" + event.source.user_id + "-" + str(i["id"]) + '.jpg')

            if os.path.exists("static/" + event.source.user_id + "-" + str(i["id"]) + '.jpg'):continue

            pic = i['img']
            #ファイルに内容を書き込み
            f = open("static/" + event.source.user_id + "-" + str(i["id"]) + '.jpg', 'wb')
            f.write(pic)
            f.close()
        cur.close()
        conn.close()


        pdfPath = png2pdf(pdfFileName,filePathList)
        image_url=uploadFile(pdfPath)


        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=image_url),
            ])

#@handler.add(MessageEvent, message=TextMessage)
def response_message(event):
    # notesのCarouselColumnの各値は、変更してもらって結構です。
    notes = [CarouselColumn(thumbnail_image_url="https://pdf-linebot.herokuapp.com/static/鳳えむ.png",
                            title="【ReleaseNote】トークルームを実装しました。",
                            text="creation(創作中・考え中の何かしらのモノ・コト)に関して、意見を聞けるようにトークルーム機能を追加しました。",
                            actions=[{"type": "message","label": "サイトURL","text": "https://pjsekai.sega.jp/character/unite04/emu/index.html"}]),

             CarouselColumn(thumbnail_image_url="https://pdf-linebot.herokuapp.com/static/鳳えむ.png",
                            title="ReleaseNote】創作中の活動を報告する機能を追加しました。",
                            text="創作中や考え中の時点の活動を共有できる機能を追加しました。",
                            actions=[
                                {"type": "message", "label": "サイトURL", "text": "https://pjsekai.sega.jp/character/unite04/emu/index.html"}]),

             CarouselColumn(thumbnail_image_url="https://pdf-linebot.herokuapp.com/static/鳳えむ.png",
                            title="【ReleaseNote】タグ機能を追加しました。",
                            text="「イベントを作成」「記事を投稿」「本を登録」にタグ機能を追加しました。",
                            actions=[
                                {"type": "message", "label": "サイトURL", "text": "https://pjsekai.sega.jp/character/unite04/emu/index.html"}])]

    messages = TemplateSendMessage(
        alt_text='template',
        template=CarouselTemplate(columns=notes),
    )

    line_bot_api.reply_message(event.reply_token, messages=messages)





@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="このメッセージがすぐに帰ってきたら起動成功です。"))





if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
