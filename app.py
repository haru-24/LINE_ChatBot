from flask import Flask, request, abort
import requests
import os
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)


load_dotenv()
API_KEY = os.environ["A3RT_API_KEY"]
TALK_API_URL = "https://api.a3rt.recruit.co.jp/talk/v1/smalltalk"
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
LINE_CHANNEL_SERCRET = os.environ["LINE_CHANNEL_SERCRET"]
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SERCRET)


app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=bot_talk(event.message.text))
    )


def bot_talk(message):
    """A3RT TALK_APIにHTTPリクエストを送る
    成功  文字列で返答を返す
    失敗 「わかりませんでした」とエラーのステータスを返す
    """
    payload = {"apikey": API_KEY, "callback": "", "query": message}
    response = requests.post(TALK_API_URL, data=payload)

    try:
        return response.json()["results"][0]["reply"]
    except requests.exceptions.RequestException:
        print(response.json())
        return "わかりませんでした"


if __name__ == "__main__":
    app.run()
