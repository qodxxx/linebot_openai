import sqlite3
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage
import os
import tempfile
import traceback
import openai

# Flask app 初始化
app = Flask(__name__)

# 初始化 LineBot API 和 WebhookHandler
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')

# GPT 回答函数
def GPT_response(text):
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    answer = response['choices'][0]['text'].replace('。', '')
    return answer

# 存储用户 ID 到数据库
def store_user_id(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT UNIQUE)')
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

# 向所有用户发送推播消息
def send_alert_to_all_users(alert_message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()

    for user_id in user_ids:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=alert_message))
        except Exception as e:
            print(f'推送消息给 {user_id} 失败：{e}')

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

# 处理消息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    store_user_id(user_id)
    try:
        GPT_answer = GPT_response(msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except Exception:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('发生错误，请检查日志'))

# 推播消息 API
@app.route("/send_alert", methods=['POST'])
def send_alert():
    alert_message = request.json.get('message', '这是默认警告消息')
    send_alert_to_all_users(alert_message)
    return 'Alert sent!'

# 启动应用
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
