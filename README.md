
![Image](https://github.com/user-attachments/assets/6dddfb8d-df61-42bc-a258-0bdc81f344b0)

# 🤖 Flask LINE Bot Server

A simple **Flask-based LINE Bot** server built with Python.  
It can receive messages, store user IDs, and broadcast alerts or Flex Messages to all users.

（中文說明在下方）

---

## 🚀 Features
- ✅ Handle LINE Webhook events (Follow, Message)
- 💬 Auto-reply to text messages
- 🗄️ Store user IDs in a PostgreSQL database
- 📢 Broadcast text or Flex Message to all users
- 🌐 Easily deployable to Render, Railway, or Heroku

---

## ⚙️ Installation

### 1️⃣ Clone this repository
```bash
git clone https://github.com/yourname/line-bot-flask-server.git
cd line-bot-flask-server
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set environment variables
Create a `.env` file and add:
```
CHANNEL_ACCESS_TOKEN=your_line_token
CHANNEL_SECRET=your_line_secret
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
OPENAI_API_KEY=your_openai_key
```

---

## 🧠 Usage

Run locally:
```bash
python app.py
```

Deploy to Render or any cloud:
- Add your environment variables in Render Dashboard  
- Set **Start Command:**  
  ```
  gunicorn app:app
  ```

---

## 📘 中文說明

這是一個使用 **Flask + LINE Messaging API** 製作的伺服器，
具備以下功能：

- 自動回覆訊息  
- 使用 PostgreSQL 儲存使用者 ID  
- 可從後端 API 群發警告訊息或 Flex Message  

### 🧩 可用的端點
| Endpoint | 功能說明 |
|-----------|-----------|
| `/callback` | LINE 官方 Webhook，用於接收事件 |
| `/send_alert` | 從後端發送群體文字通知 |
| `/send_flex` | 從後端發送群體 Flex Message |

---

## 🪄 Example Flex Message JSON
```json
{
  "message": {
    "altText": "警報通知",
    "contents": {
      "type": "bubble",
      "body": {
        "contents": [
          {"type": "text", "text": "Rack 1 溫度過高！"}
        ]
      }
    }
  }
}
```

---

## 🧩 License
Based on a **GPT-3 example** and modified for use with LINE Messaging API.  
You are free to use or modify under the MIT License.

---

**Author:** qodxxx  
**Project:** Flask LINE Bot Server
