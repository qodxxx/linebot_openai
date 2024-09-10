from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import psycopg2
import os
import openai


app = Flask(__name__)

# Channel Access Token 和 Secret
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 連接render資料庫
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

# 儲存加入line bot 使用者 user_id
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

# 從資料庫中獲取所有用户 user_id 的函數
def get_all_user_ids():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users')
    user_ids = cur.fetchall()
    cur.close()
    conn.close()
    return [user_id[0] for user_id in user_ids]

# 發送警告給所有用戶
def send_alert_to_all_users(alert_message):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            line_bot_api.push_message(user_id, TextSendMessage(text=alert_message))
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

# 發送 Flex Message 給所有用戶
def send_flex_to_all_users(flex_message):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            line_bot_api.push_message(user_id, flex_message)
        except Exception as e:
            print(f"Failed to send Flex message to {user_id}: {e}")

# 監聽 /callback 的 POST 請求
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

# 處理 FollowEvent 事件
# 當用戶加入時儲存用戶ID
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    store_user_id(user_id)  # 儲存用户 ID
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="感謝加入我們的 Bot!")
    )

# 處理其他事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()  # 將消息轉為小寫以方便匹配
    if '你好' in msg or 'hello' in msg:
        response = "你好！有什麼我可以幫助你的嗎？"
    elif '天氣' in msg or 'weather' in msg:
        response = "今天的天氣不錯喔！"
    elif '幫助' in msg or 'help' in msg:
        response = "我在這裡隨時為你服務！你可以問我天氣，或者跟我打個招呼。"
    else:
        response = "抱歉，我不太明白你的意思。你可以試著說'你好'或'幫助'來跟我互動。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )


# 新的端點，用於接收警告消息並發送給用戶
@app.route("/send_alert", methods=['POST'])
def send_alert():
    data = request.get_json()
    alert_message = data.get('message')
    if alert_message:
        send_alert_to_all_users(alert_message)
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400

# 新的端點，用於接收 Flex Message 並發送給用戶
@app.route("/send_flex", methods=['POST'])
def send_flex():
    data = request.get_json()
    message_data = data.get('message')  # 獲取 message 字段中的內容
    if message_data:
        try:
            flex_message = FlexSendMessage(
                alt_text=message_data['altText'],
                contents=message_data['contents']
            )
            send_flex_to_all_users(flex_message)  # 發送 Flex Message 給所有用戶
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Failed to process message: {e}'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
