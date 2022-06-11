from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
"""
おうむ返し
"""

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["u3asXUAKrYxyzcy3Fdq5AUpONrWB8P+02kGLgHyy0phW6m6KLmbQBs7hP0nfW71uJvrZg1+6NdU3MVrsjNNDsBkadupOe89aPJLonsDlmip6nbGwJgSwqjj6iBl5r4EicIb4CxI/tKRtlPi7kwC58QdB04t89/1O/w1cDnyilFU="]
YOUR_CHANNEL_SECRET = os.environ["0193134bd0f48224d76d5c3c67e61847"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    print("koko")
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
