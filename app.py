from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import psycopg2
import os

app = Flask(__name__)

# Channel Access Token 和 Secret
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 数据库连接函数
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

# 存储用户 ID 的函数
def store_user_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT UNIQUE
        )
    ''')
    cur.execute('INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING;', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# 监听 /callback 的 POST 请求
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 处理 FollowEvent 事件
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    store_user_id(user_id)  # 存储用户 ID
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="感谢关注我们的 Bot!")
    )

# 处理其他事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"你发的消息是: {msg}")
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
