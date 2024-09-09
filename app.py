import sqlite3
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)
line_bot_api = LineBotApi('你的CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('你的CHANNEL_SECRET')

# 创建用户表的函数
def create_users_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT UNIQUE)')
    conn.commit()
    conn.close()

# 在应用启动时确保表已创建
@app.before_first_request
def initialize():
    create_users_table()

def store_user_id(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def send_alert_to_all_users(alert_message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()

    for user_id in user_ids:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=alert_message))
            print(f'消息成功发送给 {user_id}')
        except Exception as e:
            print(f'发送消息失败给 {user_id}：{e}')

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    store_user_id(user_id)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已记录你的用户ID"))

@app.route("/send_alert", methods=['POST'])
def send_alert():
    alert_message = request.json.get('message', '默认警告消息')
    send_alert_to_all_users(alert_message)
    return 'Alert sent!'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
